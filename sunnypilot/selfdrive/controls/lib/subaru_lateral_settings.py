import numpy as np

from openpilot.common.params import Params
from openpilot.common.pid import PIDController
from openpilot.selfdrive.modeld.constants import ModelConstants


class SubaruLateralSettings:
  CURVATURE_LOOKUP_TIME = 0.2
  PATH_OFFSET_LOOKUP_TIME = 0.2
  MIN_LANELINE_CONFIDENCE_BP = [0.6, 0.8]
  LANE_WIDTH_TOLERANCE_BP = [3.75, 4.25]
  LANE_WIDTH_TOLERANCE_V = [0.81, 0.59]
  PC_BLEND_RATIO_BP = [0.0, 0.001]
  LANE_CHANGE_FACTOR_BP = [4.4, 40.23]
  LANE_CHANGE_FACTOR_V = [0.95, 0.85]
  LC_PID_SPEED_BP = [0.0, 9.0, 15.0]
  LC_PID_SPEED_V = [0.0, 0.0, 1.0]
  CORRECTION_RATE_BP = [5.0, 15.0, 25.0]
  CORRECTION_RATE_V = [0.00035, 0.0002, 0.00012]
  MAX_LANE_POSITION_CURVATURE = 0.003
  DRIVER_OVERRIDE_RESET_FRAMES = 150
  HUMAN_TURN_STEER_ANGLE_THRESHOLD = 45.0

  def __init__(self, CP, params: Params | None = None):
    self.CP = CP
    self.params = params or Params()
    self.frame = 0

    self.enable_human_turn_detection = True
    self.enable_lane_positioning = False
    self.enable_lane_full_mode = False
    self.custom_profile = 0
    self.custom_path_offset = 0.0
    self.lane_change_factor_high = self.LANE_CHANGE_FACTOR_V[1]
    self.pc_blend_ratio_high = 0.4
    self.pc_blend_ratio_low = 0.4
    self.lc_pid_gain_ui = 3.0
    self.disable_bp_lat_ui = False

    self.driver_override_frames = 0
    self.lane_position_correction_last = 0.0
    self.lane_position_pid = PIDController(k_p=0.25, k_i=0.05, rate=100)

    self._update_params(force=True)

  @staticmethod
  def _get_model_y(model_v2, idx: int):
    try:
      return float(model_v2.laneLines[idx].y[0])
    except (AttributeError, IndexError, TypeError, ValueError):
      return None

  @staticmethod
  def _model_has_curvature_data(model_v2) -> bool:
    try:
      return len(model_v2.orientation.x) >= 17 and len(model_v2.orientationRate.z) >= 17
    except (AttributeError, TypeError):
      return False

  @staticmethod
  def _model_has_position_data(model_v2) -> bool:
    try:
      return len(model_v2.position.y) > 0
    except (AttributeError, TypeError):
      return False

  @staticmethod
  def _lane_change_state(model_v2) -> tuple[bool, int]:
    try:
      state = int(model_v2.meta.laneChangeState)
      direction = int(model_v2.meta.laneChangeDirection)
    except (AttributeError, TypeError, ValueError):
      return False, 0

    return state in (1, 2, 3), direction

  @staticmethod
  def _safe_float(value, default: float) -> float:
    try:
      return float(value)
    except (TypeError, ValueError):
      return default

  def _get_float_param(self, key: str, default: float) -> float:
    return self._safe_float(self.params.get(key, return_default=True), default)

  def _get_int_param(self, key: str, default: int) -> int:
    try:
      return int(self.params.get(key, return_default=True))
    except (TypeError, ValueError):
      return default

  def _update_params(self, force: bool = False):
    if not force and (self.frame % 20) != 0:
      return

    self.enable_human_turn_detection = self.params.get_bool("enable_human_turn_detection")
    self.enable_lane_positioning = self.params.get_bool("enable_lane_positioning")
    self.enable_lane_full_mode = self.params.get_bool("enable_lane_full_mode")
    self.custom_profile = self._get_int_param("custom_profile", 0)
    self.custom_path_offset = self._get_float_param("custom_path_offset", 0.0)
    self.lane_change_factor_high = self._get_float_param("lane_change_factor_high", self.LANE_CHANGE_FACTOR_V[1])
    self.pc_blend_ratio_high = self._get_float_param("pc_blend_ratio_high_C_UI", 0.4)
    self.pc_blend_ratio_low = self._get_float_param("pc_blend_ratio_low_C_UI", 0.4)
    self.lc_pid_gain_ui = self._get_float_param("LC_PID_gain_UI", 3.0)
    self.disable_bp_lat_ui = self.params.get_bool("disable_BP_lat_UI")

  def reset(self):
    self.driver_override_frames = 0
    self.lane_position_correction_last = 0.0
    self.lane_position_pid.reset()

  def _get_predicted_curvature(self, model_v2, v_ego_raw: float) -> float:
    curvatures = np.array(model_v2.orientationRate.z) / max(0.01, v_ego_raw)
    return float(np.interp(self.CURVATURE_LOOKUP_TIME, ModelConstants.T_IDXS, curvatures))

  def _blend_requested_curvature(self, desired_curvature: float, predicted_curvature: float) -> float:
    if self.custom_profile != 1:
      return desired_curvature

    blend_ratio = float(np.interp(abs(desired_curvature), self.PC_BLEND_RATIO_BP, [self.pc_blend_ratio_low, self.pc_blend_ratio_high]))
    return (predicted_curvature * blend_ratio) + (desired_curvature * (1.0 - blend_ratio))

  def _apply_lane_change_factor(self, requested_curvature: float, lane_change_active: bool, lane_change_direction: int, v_ego_raw: float) -> float:
    if not lane_change_active:
      return requested_curvature

    lane_change_factor = float(np.interp(v_ego_raw, self.LANE_CHANGE_FACTOR_BP, [self.LANE_CHANGE_FACTOR_V[0], self.lane_change_factor_high]))

    if lane_change_direction == 1 and requested_curvature < 0.0:
      return requested_curvature * lane_change_factor
    if lane_change_direction == 2 and requested_curvature > 0.0:
      return requested_curvature * lane_change_factor

    return requested_curvature

  def _lane_line_scale(self, model_v2) -> float:
    left_y = self._get_model_y(model_v2, 1)
    right_y = self._get_model_y(model_v2, 2)
    if left_y is None or right_y is None:
      return 0.0

    try:
      left_prob = float(model_v2.laneLineProbs[1])
      right_prob = float(model_v2.laneLineProbs[2])
    except (AttributeError, IndexError, TypeError, ValueError):
      return 0.0

    lane_width = right_y + (-left_y)
    width_tolerance = float(np.interp(lane_width, self.LANE_WIDTH_TOLERANCE_BP, self.LANE_WIDTH_TOLERANCE_V))
    confidence = min(left_prob, right_prob, width_tolerance)
    return float(np.interp(confidence, self.MIN_LANELINE_CONFIDENCE_BP, [0.0, 1.0]))

  def _get_path_offset(self, model_v2) -> float:
    path_offset_position = float(np.interp(self.PATH_OFFSET_LOOKUP_TIME, ModelConstants.T_IDXS, model_v2.position.y))
    path_offset = path_offset_position

    if self.enable_lane_full_mode:
      left_y = self._get_model_y(model_v2, 1)
      right_y = self._get_model_y(model_v2, 2)
      if left_y is not None and right_y is not None:
        lane_center = (left_y + right_y) / 2.0
        lane_scale = self._lane_line_scale(model_v2)
        path_offset = (path_offset_position * (1.0 - lane_scale)) + (lane_center * lane_scale)

    return path_offset + self.custom_path_offset

  def _should_reset_for_human_turn(self, CS) -> bool:
    return self.enable_human_turn_detection and CS.steeringPressed and abs(CS.steeringAngleDeg) > self.HUMAN_TURN_STEER_ANGLE_THRESHOLD

  def _compute_lane_position_correction(self, CS, model_v2, lane_change_active: bool) -> float:
    if not self.enable_lane_positioning or not self._model_has_position_data(model_v2) or lane_change_active:
      self.reset()
      return 0.0

    if self._should_reset_for_human_turn(CS):
      self.reset()
      return 0.0

    path_offset = self._get_path_offset(model_v2)
    speed_factor = float(np.interp(CS.vEgoRaw, self.LC_PID_SPEED_BP, self.LC_PID_SPEED_V))
    path_offset_error = path_offset * (self.lc_pid_gain_ui / 100.0) * speed_factor

    if CS.steeringPressed:
      self.driver_override_frames += 1
    else:
      self.driver_override_frames = 0

    if self.driver_override_frames > self.DRIVER_OVERRIDE_RESET_FRAMES:
      self.lane_position_pid.reset()

    correction = float(self.lane_position_pid.update(path_offset_error))
    max_delta = float(np.interp(abs(CS.vEgoRaw), self.CORRECTION_RATE_BP, self.CORRECTION_RATE_V))
    correction = float(np.clip(correction,
                               self.lane_position_correction_last - max_delta,
                               self.lane_position_correction_last + max_delta))
    correction = float(np.clip(correction, -self.MAX_LANE_POSITION_CURVATURE, self.MAX_LANE_POSITION_CURVATURE))

    self.lane_position_correction_last = correction
    return correction

  def update(self, lat_active: bool, CS, model_v2, desired_curvature: float) -> float:
    self.frame += 1
    self._update_params()

    if not lat_active or self.disable_bp_lat_ui or model_v2 is None:
      self.reset()
      return desired_curvature

    lane_change_active, lane_change_direction = self._lane_change_state(model_v2)
    requested_curvature = desired_curvature

    if self._model_has_curvature_data(model_v2):
      predicted_curvature = self._get_predicted_curvature(model_v2, CS.vEgoRaw)
      requested_curvature = self._blend_requested_curvature(desired_curvature, predicted_curvature)

    requested_curvature = self._apply_lane_change_factor(requested_curvature, lane_change_active, lane_change_direction, CS.vEgoRaw)
    lane_position_correction = self._compute_lane_position_correction(CS, model_v2, lane_change_active)
    return requested_curvature + lane_position_correction
