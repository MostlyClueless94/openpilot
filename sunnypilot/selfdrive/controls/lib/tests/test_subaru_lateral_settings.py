from types import SimpleNamespace

from openpilot.sunnypilot.selfdrive.controls.lib.subaru_lateral_settings import SubaruLateralSettings
from openpilot.selfdrive.modeld.constants import ModelConstants


class FakeParams:
  def __init__(self, values):
    self.values = values

  def get_bool(self, key):
    return bool(self.values.get(key, False))

  def get(self, key, return_default=False):
    return self.values.get(key)


def build_car_state(v_ego=15.0, steering_pressed=False, steering_angle_deg=0.0):
  return SimpleNamespace(
    vEgoRaw=v_ego,
    steeringPressed=steering_pressed,
    steeringAngleDeg=steering_angle_deg,
  )


def build_model(path_position=0.0, predicted_curvature=0.0, lane_center=0.0, lane_change_state=0, lane_change_direction=0,
                left_prob=0.95, right_prob=0.95):
  model_len = len(ModelConstants.T_IDXS)
  v_ego = 15.0
  orientation_rate = [predicted_curvature * v_ego] * model_len
  left_lane = lane_center - 1.7
  right_lane = lane_center + 1.7

  return SimpleNamespace(
    orientation=SimpleNamespace(x=[0.0] * model_len),
    orientationRate=SimpleNamespace(z=orientation_rate),
    position=SimpleNamespace(y=[path_position] * model_len),
    laneLines=[
      SimpleNamespace(y=[0.0]),
      SimpleNamespace(y=[left_lane]),
      SimpleNamespace(y=[right_lane]),
      SimpleNamespace(y=[0.0]),
    ],
    laneLineProbs=[0.0, left_prob, right_prob, 0.0],
    meta=SimpleNamespace(laneChangeState=lane_change_state, laneChangeDirection=lane_change_direction),
  )


class TestSubaruLateralSettings:
  def setup_method(self):
    CP = SimpleNamespace(brand="subaru")
    self.CP = CP

  def test_custom_profile_blends_predicted_curvature(self):
    helper = SubaruLateralSettings(self.CP, FakeParams({
      "custom_profile": 1,
      "pc_blend_ratio_high_C_UI": 1.0,
      "pc_blend_ratio_low_C_UI": 1.0,
    }))
    cs = build_car_state()
    model = build_model(predicted_curvature=0.0012)

    adjusted_curvature = helper.update(True, cs, model, 0.0003)

    assert adjusted_curvature == 0.0012

  def test_lane_positioning_blends_lane_center_when_lanefull_enabled(self):
    helper = SubaruLateralSettings(self.CP, FakeParams({
      "enable_lane_positioning": True,
      "enable_lane_full_mode": True,
      "LC_PID_gain_UI": 3.0,
    }))
    cs = build_car_state()
    model = build_model(path_position=0.0, lane_center=0.2)

    adjusted_curvature = helper.update(True, cs, model, 0.0)

    assert adjusted_curvature > 0.0

  def test_lane_positioning_ignores_lane_center_when_lanefull_disabled(self):
    helper = SubaruLateralSettings(self.CP, FakeParams({
      "enable_lane_positioning": True,
      "enable_lane_full_mode": False,
      "LC_PID_gain_UI": 3.0,
    }))
    cs = build_car_state()
    model = build_model(path_position=0.0, lane_center=0.2)

    adjusted_curvature = helper.update(True, cs, model, 0.0)

    assert adjusted_curvature == 0.0

  def test_custom_path_offset_shifts_subaru_target(self):
    helper = SubaruLateralSettings(self.CP, FakeParams({
      "enable_lane_positioning": True,
      "custom_path_offset": 0.2,
      "LC_PID_gain_UI": 3.0,
    }))
    cs = build_car_state()
    model = build_model(path_position=0.0)

    adjusted_curvature = helper.update(True, cs, model, 0.0)

    assert adjusted_curvature > 0.0

  def test_disable_bp_lat_ui_restores_stock_curvature_path(self):
    helper = SubaruLateralSettings(self.CP, FakeParams({
      "disable_BP_lat_UI": True,
      "enable_lane_positioning": True,
      "custom_path_offset": 0.2,
      "custom_profile": 1,
      "pc_blend_ratio_high_C_UI": 1.0,
      "pc_blend_ratio_low_C_UI": 1.0,
    }))
    cs = build_car_state()
    model = build_model(path_position=0.2, predicted_curvature=0.0012, lane_center=0.2)

    adjusted_curvature = helper.update(True, cs, model, 0.0003)

    assert adjusted_curvature == 0.0003

  def test_lane_change_factor_high_scales_subaru_lane_change_curvature(self):
    helper = SubaruLateralSettings(self.CP, FakeParams({
      "lane_change_factor_high": 0.5,
    }))
    cs = build_car_state(v_ego=40.23)
    model = build_model(lane_change_state=2, lane_change_direction=2)

    adjusted_curvature = helper.update(True, cs, model, 0.001)

    assert adjusted_curvature == 0.0005
