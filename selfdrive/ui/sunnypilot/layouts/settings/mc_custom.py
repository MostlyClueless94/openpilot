"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.params import Params
from openpilot.selfdrive.ui.bp.widgets.section_header import SectionHeader
from openpilot.selfdrive.ui.sunnypilot.onroad.path_colors import CUSTOM_MODEL_PATH_COLOR_LABELS
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import multiple_button_item_sp, option_item_sp, toggle_item_sp
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller_tici import Scroller


RESUME_SOFTNESS_LABELS = ["Standard", "Soft", "Softer", "Very Soft", "Extra Soft", "Softest", "Max Soft"]
RELEASE_GUARD_LEVEL_LABELS = ["Light", "Medium", "Strong"]
ADVANCED_TUNING_DESC = "Show Subaru lateral tuning controls. Hidden controls keep their saved values active."
RESUME_SOFTNESS_DESC = (
  "Adjust how gently steering re-engages after manual override. Higher levels reduce the initial reclaim bite."
)
CUSTOM_RESUME_SOFTNESS_DESC = (
  "Enable a custom post-manual-yield steering reclaim ramp. When off, no SubiPilot reclaim ramp is applied "
  + "and your saved softness selection is kept for later testing."
)
RELEASE_GUARD_DESC = (
  "Keep Subaru manual-yield override active a bit longer after steering input briefly drops. "
  + "This can reduce false reclaim jerks when you are still holding the wheel at a steady angle."
)
RELEASE_GUARD_STRENGTH_DESC = (
  "Adjust how much confirmation Subaru waits for before reclaim begins after manual override. "
  + "Higher levels wait longer for a clean release before the existing resume ramp starts."
)
MADS_TIGHTER_TURNS_DESC = (
  "Cap Subaru MADS lateral-only requested steering angle so tight-turn testing cannot request more than the selected value. "
  + "The cap also remains a measured-angle guard; it does not bypass panda safety or normal driving limits."
)
MADS_STEERING_ANGLE_CAP_DESC = (
  "Choose the Subaru MADS lateral-only requested steering angle cap. 120 deg is stock/current behavior. "
  + "Higher values allow more MADS-only turning while still capping requested angle and inhibiting LKAS "
  + "when the measured wheel angle reaches the cap. 545 deg is the existing angle-LKAS safety maximum, not unlimited."
)
CUSTOM_YIELD_TORQUE_DESC = (
  "Enable a custom Subaru manual-yield torque threshold. When off, manual override detection falls back to the stock Subaru "
  + "threshold for your platform while keeping your saved test value. Settings near the minimum may falsely detect manual "
  + "override while openpilot is steering through turns. Values above 80 require more driver torque and may be slower to "
  + "detect manual override. Values above 150 are high experimental test points and may effectively disable manual-yield "
  + "detection. 40 is the minimum allowed test value."
)
YIELD_TORQUE_DESC = (
  "Adjust the steering torque required to count as manual yield. Lower values detect lighter steady driver input sooner. "
  + "Settings near the minimum may falsely detect manual override while openpilot is steering through turns. 80 matches "
  + "the stock threshold on modern Subaru angle-LKAS platforms. Values above 80 are test values that require more driver "
  + "torque and may be slower to detect manual override. Values above 150 are high experimental test points and may "
  + "effectively disable manual-yield detection. 40 is the minimum allowed test value."
)
FILTERED_YIELD_DETECTION_DESC = (
  "Use Ford-style filtering for Subaru manual-yield detection so light hand torque can stay latched through brief "
  + "dropouts. This keeps the selected torque threshold, but requires persistent input before latching."
)
SOFT_CAPTURE_DESC = (
  "Smooth the transition when openpilot takes back steering control. "
  + "When enabled, the wheel angle blends gradually toward the model target "
  + "instead of snapping instantly. Experiment — MostlyClueless only."
)
SOFT_CAPTURE_STRENGTH_DESC = (
  "Adjust how gently openpilot reclaims steering on engage. "
  + "Level 1 is a light blend (0.15 s). Level 5 is the most damped "
  + "(0.50 s, near-zero start). Higher levels reduce snap-to-target feel "
  + "but extend the handoff window."
)
SOFT_CAPTURE_STRENGTH_LABELS = ["1 - Light", "2 - Mild", "3 - Medium", "4 - Strong", "5 - Max"]
DYNAMIC_PATH_COLOR_DESC = (
  "Color the driving path by drive mode. Light gray when inactive or truly "
  + "overriding, teal when steering-only, and green for full control."
)
CUSTOM_MODEL_PATH_COLOR_DESC = (
  "Use preset colors for the driving path overlay. Stock keeps the normal "
  + "path behavior, and Dynamic Path Color still takes priority when enabled."
)
SHOW_VEHICLE_BRAKE_STATUS_DESC = (
  "Display current speed in red whenever the vehicle is braking, "
  + "including ACC/openpilot braking when available."
)
MATCH_VEHICLE_SPEEDOMETER_DESC = (
  "When enabled, the Subaru on-road speedometer matches the vehicle dash or cluster speed when supported. "
  + "Turn it off to show true wheel-speed-based speed instead."
)
MANUAL_YIELD_TORQUE_THRESHOLD_MIN = 40
MANUAL_YIELD_TORQUE_THRESHOLD_STEP = 5
MANUAL_YIELD_TORQUE_THRESHOLD_FINE_MAX = 150
MANUAL_YIELD_TORQUE_THRESHOLD_MAX = 500
MANUAL_YIELD_TORQUE_THRESHOLD_VALUES = (
  *range(MANUAL_YIELD_TORQUE_THRESHOLD_MIN, MANUAL_YIELD_TORQUE_THRESHOLD_FINE_MAX + MANUAL_YIELD_TORQUE_THRESHOLD_STEP, MANUAL_YIELD_TORQUE_THRESHOLD_STEP),
  *range(200, MANUAL_YIELD_TORQUE_THRESHOLD_MAX + 50, 50),
)
MANUAL_YIELD_TORQUE_THRESHOLD_VALUE_MAP = {idx: value for idx, value in enumerate(MANUAL_YIELD_TORQUE_THRESHOLD_VALUES)}
MADS_STEERING_ANGLE_CAP_VALUES = (120, 180, 190, 199, 200, 240, 360, 545)
MADS_STEERING_ANGLE_CAP_VALUE_MAP = {idx: value for idx, value in enumerate(MADS_STEERING_ANGLE_CAP_VALUES)}


class MCCustomLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _get_int_param(self, key: str, default: int = 0) -> int:
    value = self._params.get(key, return_default=True)
    try:
      return int(value)
    except (TypeError, ValueError):
      return default

  def _get_bool_param(self, key: str, default: bool = False) -> bool:
    value = self._params.get(key, return_default=True)
    if value is None:
      return default
    if isinstance(value, bool):
      return value
    if isinstance(value, bytes):
      return value not in (b"", b"0")
    if isinstance(value, str):
      return value not in ("", "0", "false", "False")
    return bool(value)

  def _initialize_items(self):
    self._dynamic_path_color = toggle_item_sp(
      title=lambda: tr("Dynamic Path Color"),
      description=lambda: tr(DYNAMIC_PATH_COLOR_DESC),
      param="DynamicPathColor",
      initial_state=self._params.get_bool("DynamicPathColor"),
    )
    self._custom_model_path_color = multiple_button_item_sp(
      title=lambda: tr("Custom Model Path Color"),
      description=lambda: tr(CUSTOM_MODEL_PATH_COLOR_DESC),
      buttons=[lambda label=label: tr(label) for label in CUSTOM_MODEL_PATH_COLOR_LABELS],
      param="CustomModelPathColor",
      button_width=160,
      inline=False
    )
    self._show_vehicle_brake_status = toggle_item_sp(
      title=lambda: tr("Show Vehicle Brake Status"),
      description=lambda: tr(SHOW_VEHICLE_BRAKE_STATUS_DESC),
      param="MCShowVehicleBrakeStatus",
      initial_state=self._params.get_bool("MCShowVehicleBrakeStatus"),
    )
    self._subaru_header = SectionHeader(tr("Subaru"))
    self._subaru_match_vehicle_speedometer = toggle_item_sp(
      title=lambda: tr("Match Vehicle Speedometer"),
      description=lambda: tr(MATCH_VEHICLE_SPEEDOMETER_DESC),
      param="MCSubaruMatchVehicleSpeedometer",
      initial_state=self._get_bool_param("MCSubaruMatchVehicleSpeedometer", True),
    )
    self._subaru_advanced_tuning = toggle_item_sp(
      title=lambda: tr("Advanced Tuning"),
      description=lambda: tr(ADVANCED_TUNING_DESC),
      param="MCSubaruAdvancedTuning",
      initial_state=self._get_bool_param("MCSubaruAdvancedTuning"),
    )
    self._manual_yield_torque_threshold_enabled = toggle_item_sp(
      title=lambda: tr("Custom Yield Torque"),
      description=lambda: tr(CUSTOM_YIELD_TORQUE_DESC),
      param="MCSubaruManualYieldTorqueThresholdEnabled",
      initial_state=self._get_bool_param("MCSubaruManualYieldTorqueThresholdEnabled"),
    )
    self._manual_yield_torque_threshold = option_item_sp(
      title=lambda: tr("Manual Yield Torque Threshold"),
      description=lambda: tr(YIELD_TORQUE_DESC),
      param="MCSubaruManualYieldTorqueThreshold",
      min_value=0,
      max_value=len(MANUAL_YIELD_TORQUE_THRESHOLD_VALUES) - 1,
      value_change_step=1,
      value_map=MANUAL_YIELD_TORQUE_THRESHOLD_VALUE_MAP,
      label_callback=self._format_manual_yield_torque_threshold_label,
      inline=False,
    )
    self._manual_yield_filtered_detection = toggle_item_sp(
      title=lambda: tr("Filtered Yield Detection"),
      description=lambda: tr(FILTERED_YIELD_DETECTION_DESC),
      param="MCSubaruManualYieldFilteredDetectionEnabled",
      initial_state=self._get_bool_param("MCSubaruManualYieldFilteredDetectionEnabled"),
    )
    self._manual_yield_resume_softness_enabled = toggle_item_sp(
      title=lambda: tr("Custom Resume Softness"),
      description=lambda: tr(CUSTOM_RESUME_SOFTNESS_DESC),
      param="MCSubaruManualYieldResumeSoftnessEnabled",
      initial_state=self._get_bool_param("MCSubaruManualYieldResumeSoftnessEnabled"),
    )
    self._manual_yield_resume_softness = option_item_sp(
      title=lambda: tr("Manual Yield Resume Softness"),
      description=lambda: tr(RESUME_SOFTNESS_DESC),
      param="MCSubaruManualYieldResumeSoftness",
      min_value=0,
      max_value=6,
      value_change_step=1,
      label_callback=self._format_resume_softness_label,
      inline=False,
    )
    self._manual_yield_release_guard_enabled = toggle_item_sp(
      title=lambda: tr("Manual Yield Release Guard"),
      description=lambda: tr(RELEASE_GUARD_DESC),
      param="MCSubaruManualYieldReleaseGuardEnabled",
      initial_state=self._get_bool_param("MCSubaruManualYieldReleaseGuardEnabled"),
    )
    self._manual_yield_release_guard_level = option_item_sp(
      title=lambda: tr("Release Guard Strength"),
      description=lambda: tr(RELEASE_GUARD_STRENGTH_DESC),
      param="MCSubaruManualYieldReleaseGuardLevel",
      min_value=1,
      max_value=3,
      value_change_step=1,
      label_callback=self._format_release_guard_label,
      inline=False,
    )
    self._subaru_mads_tighter_turns = toggle_item_sp(
      title=lambda: tr("Tighter MADS Turns"),
      description=lambda: tr(MADS_TIGHTER_TURNS_DESC),
      param="MCSubaruMadsTighterTurnsEnabled",
      initial_state=self._get_bool_param("MCSubaruMadsTighterTurnsEnabled"),
    )
    self._subaru_mads_steering_angle_cap = option_item_sp(
      title=lambda: tr("MADS Steering Angle Cap"),
      description=lambda: tr(MADS_STEERING_ANGLE_CAP_DESC),
      param="MCSubaruMadsMaxSteeringAngle",
      min_value=0,
      max_value=len(MADS_STEERING_ANGLE_CAP_VALUES) - 1,
      value_change_step=1,
      value_map=MADS_STEERING_ANGLE_CAP_VALUE_MAP,
      label_callback=self._format_mads_steering_angle_cap_label,
      inline=False,
    )
    self._subaru_soft_capture = toggle_item_sp(
      title=lambda: tr("Soft-Capture Engage Blend"),
      description=lambda: tr(SOFT_CAPTURE_DESC),
      param="MCSubaruSoftCaptureEnabled",
      initial_state=self._get_bool_param("MCSubaruSoftCaptureEnabled"),
    )
    self._subaru_soft_capture_strength = option_item_sp(
      title=lambda: tr("Soft-Capture Strength"),
      description=lambda: tr(SOFT_CAPTURE_STRENGTH_DESC),
      param="MCSubaruSoftCaptureLevel",
      min_value=1,
      max_value=5,
      value_change_step=1,
      label_callback=self._format_soft_capture_label,
      inline=False,
    )

    return [
      SectionHeader(tr("Pathing")),
      self._dynamic_path_color,
      self._custom_model_path_color,
      SectionHeader(tr("Driving Status")),
      self._show_vehicle_brake_status,
      self._subaru_header,
      self._subaru_match_vehicle_speedometer,
      self._subaru_advanced_tuning,
      self._manual_yield_torque_threshold_enabled,
      self._manual_yield_torque_threshold,
      self._manual_yield_filtered_detection,
      self._manual_yield_resume_softness_enabled,
      self._manual_yield_resume_softness,
      self._manual_yield_release_guard_enabled,
      self._manual_yield_release_guard_level,
      self._subaru_mads_tighter_turns,
      self._subaru_mads_steering_angle_cap,
      self._subaru_soft_capture,
      self._subaru_soft_capture_strength,
    ]

  @staticmethod
  def _format_resume_softness_label(value: int) -> str:
    return tr(RESUME_SOFTNESS_LABELS[max(0, min(value, len(RESUME_SOFTNESS_LABELS) - 1))])

  @staticmethod
  def _format_release_guard_label(value: int) -> str:
    return tr(RELEASE_GUARD_LEVEL_LABELS[max(0, min(value - 1, len(RELEASE_GUARD_LEVEL_LABELS) - 1))])

  @staticmethod
  def _clamp_manual_yield_torque_threshold(value: int) -> int:
    return min(
      MANUAL_YIELD_TORQUE_THRESHOLD_VALUES,
      key=lambda threshold: (abs(threshold - value), threshold),
    )

  @staticmethod
  def _manual_yield_torque_threshold_index(value: int) -> int:
    clamped = MCCustomLayout._clamp_manual_yield_torque_threshold(value)
    return MANUAL_YIELD_TORQUE_THRESHOLD_VALUES.index(clamped)

  @staticmethod
  def _format_manual_yield_torque_threshold_label(value: int) -> str:
    clamped = MCCustomLayout._clamp_manual_yield_torque_threshold(value)
    if clamped <= 55:
      return f"{clamped} - {tr('Caution')}"
    if clamped == 80:
      return tr("80 - Stock")
    if clamped >= 200:
      return f"{clamped} - {tr('High')}"
    return str(clamped)

  @staticmethod
  def _format_soft_capture_label(value: int) -> str:
    idx = max(0, min(value - 1, len(SOFT_CAPTURE_STRENGTH_LABELS) - 1))
    return tr(SOFT_CAPTURE_STRENGTH_LABELS[idx])

  @staticmethod
  def _format_mads_steering_angle_cap_label(value: int) -> str:
    if value == 120:
      return tr("120 - Stock")
    if value == 545:
      return tr("545 - Max Safe")
    return str(value)

  @staticmethod
  def _mads_steering_angle_cap_index(value: int) -> int:
    return min(
      range(len(MADS_STEERING_ANGLE_CAP_VALUES)),
      key=lambda idx: abs(MADS_STEERING_ANGLE_CAP_VALUES[idx] - value),
    )

  def _set_subaru_section_visibility(self, advanced_tuning_enabled: bool) -> None:
    self._subaru_header.set_visible(True)
    self._subaru_match_vehicle_speedometer.set_visible(True)
    self._subaru_advanced_tuning.set_visible(True)
    self._manual_yield_torque_threshold_enabled.set_visible(advanced_tuning_enabled)
    self._manual_yield_torque_threshold.set_visible(advanced_tuning_enabled)
    self._manual_yield_filtered_detection.set_visible(advanced_tuning_enabled)
    self._manual_yield_resume_softness_enabled.set_visible(advanced_tuning_enabled)
    self._manual_yield_resume_softness.set_visible(advanced_tuning_enabled)
    self._manual_yield_release_guard_enabled.set_visible(advanced_tuning_enabled)
    self._manual_yield_release_guard_level.set_visible(advanced_tuning_enabled)
    self._subaru_mads_tighter_turns.set_visible(advanced_tuning_enabled)
    self._subaru_mads_steering_angle_cap.set_visible(advanced_tuning_enabled)
    self._subaru_soft_capture.set_visible(advanced_tuning_enabled)
    self._subaru_soft_capture_strength.set_visible(advanced_tuning_enabled)

  def _update_subaru_settings(self) -> None:
    advanced_tuning_enabled = self._get_bool_param("MCSubaruAdvancedTuning")
    torque_threshold_enabled = self._get_bool_param("MCSubaruManualYieldTorqueThresholdEnabled")
    filtered_detection_enabled = self._get_bool_param("MCSubaruManualYieldFilteredDetectionEnabled")
    resume_softness_enabled = self._get_bool_param("MCSubaruManualYieldResumeSoftnessEnabled")
    release_guard_enabled = self._get_bool_param("MCSubaruManualYieldReleaseGuardEnabled")
    mads_tighter_turns_enabled = self._get_bool_param("MCSubaruMadsTighterTurnsEnabled")
    self._subaru_match_vehicle_speedometer.action_item.set_state(
      self._get_bool_param("MCSubaruMatchVehicleSpeedometer", True)
    )
    self._subaru_advanced_tuning.action_item.set_state(advanced_tuning_enabled)
    self._manual_yield_torque_threshold_enabled.action_item.set_state(torque_threshold_enabled)
    self._manual_yield_filtered_detection.action_item.set_state(filtered_detection_enabled)
    self._manual_yield_resume_softness_enabled.action_item.set_state(resume_softness_enabled)
    self._manual_yield_release_guard_enabled.action_item.set_state(release_guard_enabled)
    self._subaru_mads_tighter_turns.action_item.set_state(mads_tighter_turns_enabled)
    self._manual_yield_torque_threshold.action_item.current_value = self._manual_yield_torque_threshold_index(
      self._get_int_param("MCSubaruManualYieldTorqueThreshold", 80)
    )
    self._manual_yield_resume_softness.action_item.current_value = max(0, min(self._get_int_param("MCSubaruManualYieldResumeSoftness", 4), 6))
    self._manual_yield_release_guard_level.action_item.current_value = max(1, min(self._get_int_param("MCSubaruManualYieldReleaseGuardLevel", 2), 3))
    self._subaru_mads_steering_angle_cap.action_item.current_value = self._mads_steering_angle_cap_index(
      self._get_int_param("MCSubaruMadsMaxSteeringAngle", 120)
    )
    soft_capture_enabled = self._get_bool_param("MCSubaruSoftCaptureEnabled")
    self._subaru_soft_capture.action_item.set_state(soft_capture_enabled)
    self._subaru_soft_capture_strength.action_item.current_value = max(1, min(self._get_int_param("MCSubaruSoftCaptureLevel", 3), 5))
    self._manual_yield_torque_threshold.action_item.set_enabled(torque_threshold_enabled)
    self._manual_yield_resume_softness.action_item.set_enabled(resume_softness_enabled)
    self._manual_yield_release_guard_level.action_item.set_enabled(release_guard_enabled)
    self._subaru_mads_steering_angle_cap.action_item.set_enabled(mads_tighter_turns_enabled)
    self._subaru_soft_capture_strength.action_item.set_enabled(soft_capture_enabled)
    self._set_subaru_section_visibility(advanced_tuning_enabled)

  def _update_state(self):
    super()._update_state()

    self._dynamic_path_color.action_item.set_state(self._get_bool_param("DynamicPathColor"))
    selected_color = max(0, min(self._get_int_param("CustomModelPathColor"), len(CUSTOM_MODEL_PATH_COLOR_LABELS) - 1))
    self._custom_model_path_color.action_item.set_selected_button(selected_color)
    self._show_vehicle_brake_status.action_item.set_state(self._get_bool_param("MCShowVehicleBrakeStatus"))
    self._update_subaru_settings()

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
