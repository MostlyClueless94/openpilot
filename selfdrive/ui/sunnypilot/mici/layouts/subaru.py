"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

import pyray as rl

try:
  from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigParamControl, GreyBigButton
except ImportError:
  from openpilot.selfdrive.ui.bp.mici.widgets.button_bp import BigButtonBP as BigButton, BigParamControlBP as BigParamControl

  class GreyBigButton(BigButton):
    def __init__(self, text: str, value: str = ""):
      super().__init__(text, value, tint=rl.Color(0x66, 0x66, 0x66, 0xFF))
      self.set_touch_valid_callback(lambda: False)

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.widgets.scroller import NavScroller

RESUME_SOFTNESS_LABELS = ["Standard", "Soft", "Softer", "Very Soft", "Extra Soft", "Softest", "Max Soft"]
RELEASE_GUARD_LEVEL_LABELS = ["Light", "Medium", "Strong"]
SOFT_CAPTURE_STRENGTH_LABELS = ["1 - Light", "2 - Mild", "3 - Medium", "4 - Strong", "5 - Max"]
SUBARU_UNWIND_RATE_LEVEL_VALUES = (
  0.8, 1.0, 1.2, 1.5, 1.8, 2.1, 2.4, 2.8, 3.2, 3.6, 4.0,
  4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 9.0, 10.0,
)
SUBARU_UNWIND_RATE_COMMAND_HZ = 50
SUBARU_UNWIND_RATE_LEVEL_LABELS = (
  "L0 Stock",
  "L1 50 deg/s",
  "L2 60 deg/s",
  "L3 75 deg/s",
  "L4 90 deg/s",
  "L5 105 deg/s",
  "L6 120 deg/s",
  "L7 140 deg/s",
  "L8 160 deg/s",
  "L9 180 deg/s",
  "L10 200 deg/s",
  "L11 225 deg/s",
  "L12 250 deg/s",
  "L13 275 deg/s",
  "L14 300 deg/s",
  "L15 325 deg/s",
  "L16 350 deg/s",
  "L17 375 deg/s",
  "L18 400 deg/s",
  "L19 450 deg/s",
  "L20 500 deg/s",
)
SUBARU_TURN_IN_RATE_LEVEL_VALUES = SUBARU_UNWIND_RATE_LEVEL_VALUES
SUBARU_TURN_IN_RATE_LEVEL_LABELS = SUBARU_UNWIND_RATE_LEVEL_LABELS
MANUAL_YIELD_TORQUE_THRESHOLD_MIN = 40
MANUAL_YIELD_TORQUE_THRESHOLD_STEP = 5
MANUAL_YIELD_TORQUE_THRESHOLD_FINE_MAX = 150
MANUAL_YIELD_TORQUE_THRESHOLD_MAX = 500
MANUAL_YIELD_TORQUE_THRESHOLD_VALUES = (
  *range(MANUAL_YIELD_TORQUE_THRESHOLD_MIN, MANUAL_YIELD_TORQUE_THRESHOLD_FINE_MAX + MANUAL_YIELD_TORQUE_THRESHOLD_STEP, MANUAL_YIELD_TORQUE_THRESHOLD_STEP),
  *range(200, MANUAL_YIELD_TORQUE_THRESHOLD_MAX + 50, 50),
)
MADS_STEERING_ANGLE_CAP_VALUES = (120, 180, 190, 199, 200, 240, 360, 545)


class SubaruLayoutMici(NavScroller):
  def __init__(self, back_callback: Callable):
    super().__init__()
    self.set_back_callback(back_callback)
    self.original_back_callback = back_callback
    self.focused_widget = None

    self._stop_and_go_header = GreyBigButton("stop and\ngo")
    self._lateral_header = GreyBigButton("lateral\ntuning")

    self._stop_and_go_toggle = BigParamControl("stop and go\n(beta)", "SubaruStopAndGo")
    self._stop_and_go_manual_parking_brake_toggle = BigParamControl(
      "manual parking\nbrake stop and go",
      "SubaruStopAndGoManualParkingBrake",
    )
    # BluePilot: Subaru-specific dash-match speedometer toggle lives on the main Subaru page, outside advanced tuning.
    self._match_vehicle_speedometer_toggle = BigParamControl(
      "match vehicle\nspeedometer",
      "MCSubaruMatchVehicleSpeedometer",
    )
    self._subaru_advanced_tuning_toggle = BigParamControl("advanced\ntuning", "MCSubaruAdvancedTuning")
    self._manual_yield_torque_threshold_toggle = BigParamControl("custom yield\ntorque", "MCSubaruManualYieldTorqueThresholdEnabled")
    self._manual_yield_filtered_detection_toggle = BigParamControl("filtered yield\ndetection", "MCSubaruManualYieldFilteredDetectionEnabled")
    self._manual_yield_resume_softness_toggle = BigParamControl("custom resume\nsoftness", "MCSubaruManualYieldResumeSoftnessEnabled")
    self._manual_yield_release_guard_toggle = BigParamControl("manual yield\nrelease guard", "MCSubaruManualYieldReleaseGuardEnabled")
    self._subaru_mads_tighter_turns_toggle = BigParamControl("tighter MADS\nturns", "MCSubaruMadsTighterTurnsEnabled")
    self._subaru_soft_capture_toggle = BigParamControl("soft-capture\nengage blend", "MCSubaruSoftCaptureEnabled")

    self._manual_yield_torque_threshold_btn = BigButton("manual yield\ntorque")
    self._manual_yield_torque_threshold_btn.set_click_callback(
      lambda: self._show_value_selector(
        self._manual_yield_torque_threshold_btn,
        "MCSubaruManualYieldTorqueThreshold",
        list(MANUAL_YIELD_TORQUE_THRESHOLD_VALUES),
        self._format_manual_yield_torque_threshold_label,
      )
    )

    self._manual_yield_resume_softness_btn = BigButton("manual yield\nresume softness")
    self._manual_yield_resume_softness_btn.set_click_callback(
      lambda: self._show_value_selector(
        self._manual_yield_resume_softness_btn,
        "MCSubaruManualYieldResumeSoftness",
        list(range(7)),
        self._format_resume_softness_label,
      )
    )

    self._manual_yield_release_guard_btn = BigButton("release guard\nstrength")
    self._manual_yield_release_guard_btn.set_click_callback(
      lambda: self._show_value_selector(
        self._manual_yield_release_guard_btn,
        "MCSubaruManualYieldReleaseGuardLevel",
        list(range(1, 4)),
        self._format_release_guard_label,
      )
    )
    self._subaru_mads_steering_angle_cap_btn = BigButton("MADS steering\nangle cap")
    self._subaru_mads_steering_angle_cap_btn.set_click_callback(
      lambda: self._show_value_selector(
        self._subaru_mads_steering_angle_cap_btn,
        "MCSubaruMadsMaxSteeringAngle",
        list(MADS_STEERING_ANGLE_CAP_VALUES),
        self._format_mads_steering_angle_cap_label,
      )
    )
    self._subaru_unwind_rate_level_btn = BigButton("unwind rate\nlevel")
    self._subaru_unwind_rate_level_btn.set_click_callback(
      lambda: self._show_value_selector(
        self._subaru_unwind_rate_level_btn,
        "MCSubaruUnwindRateLevel",
        list(range(len(SUBARU_UNWIND_RATE_LEVEL_VALUES))),
        self._format_subaru_unwind_rate_label,
      )
    )
    self._subaru_turn_in_rate_level_btn = BigButton("turn-in rate\nlevel")
    self._subaru_turn_in_rate_level_btn.set_click_callback(
      lambda: self._show_value_selector(
        self._subaru_turn_in_rate_level_btn,
        "MCSubaruTurnInRateLevel",
        list(range(len(SUBARU_TURN_IN_RATE_LEVEL_VALUES))),
        self._format_subaru_turn_in_rate_label,
      )
    )
    self._subaru_soft_capture_strength_btn = BigButton("soft-capture\nstrength")
    self._subaru_soft_capture_strength_btn.set_click_callback(
      lambda: self._show_value_selector(
        self._subaru_soft_capture_strength_btn,
        "MCSubaruSoftCaptureLevel",
        list(range(1, 6)),
        self._format_soft_capture_label,
      )
    )

    self.main_items = [
      self._stop_and_go_header,
      self._stop_and_go_toggle,
      self._stop_and_go_manual_parking_brake_toggle,
      self._match_vehicle_speedometer_toggle,
      self._lateral_header,
      self._subaru_advanced_tuning_toggle,
      self._manual_yield_torque_threshold_toggle,
      self._manual_yield_torque_threshold_btn,
      self._manual_yield_filtered_detection_toggle,
      self._manual_yield_resume_softness_toggle,
      self._manual_yield_resume_softness_btn,
      self._manual_yield_release_guard_toggle,
      self._manual_yield_release_guard_btn,
      self._subaru_mads_tighter_turns_toggle,
      self._subaru_mads_steering_angle_cap_btn,
      self._subaru_turn_in_rate_level_btn,
      self._subaru_unwind_rate_level_btn,
      self._subaru_soft_capture_toggle,
      self._subaru_soft_capture_strength_btn,
    ]
    self._scroller.add_widgets(self.main_items)

    self._refresh_toggles = (
      ("SubaruStopAndGo", self._stop_and_go_toggle, False),
      ("SubaruStopAndGoManualParkingBrake", self._stop_and_go_manual_parking_brake_toggle, False),
      ("MCSubaruMatchVehicleSpeedometer", self._match_vehicle_speedometer_toggle, True),
      ("MCSubaruAdvancedTuning", self._subaru_advanced_tuning_toggle, False),
      ("MCSubaruManualYieldTorqueThresholdEnabled", self._manual_yield_torque_threshold_toggle, False),
      ("MCSubaruManualYieldFilteredDetectionEnabled", self._manual_yield_filtered_detection_toggle, False),
      ("MCSubaruManualYieldResumeSoftnessEnabled", self._manual_yield_resume_softness_toggle, False),
      ("MCSubaruManualYieldReleaseGuardEnabled", self._manual_yield_release_guard_toggle, False),
      ("MCSubaruMadsTighterTurnsEnabled", self._subaru_mads_tighter_turns_toggle, False),
      ("MCSubaruSoftCaptureEnabled", self._subaru_soft_capture_toggle, False),
    )

  @staticmethod
  def _get_int_param(key: str, default: int = 0) -> int:
    value = ui_state.params.get(key, return_default=True)
    try:
      return int(value)
    except (TypeError, ValueError):
      return default

  @staticmethod
  def _get_bool_param(key: str, default: bool = False) -> bool:
    value = ui_state.params.get(key, return_default=True)
    if value is None:
      return default
    if isinstance(value, bool):
      return value
    if isinstance(value, bytes):
      return value not in (b"", b"0")
    if isinstance(value, str):
      return value not in ("", "0", "false", "False")
    return bool(value)

  @staticmethod
  def _format_resume_softness_label(value: int) -> str:
    return RESUME_SOFTNESS_LABELS[max(0, min(value, len(RESUME_SOFTNESS_LABELS) - 1))]

  @staticmethod
  def _format_release_guard_label(value: int) -> str:
    return RELEASE_GUARD_LEVEL_LABELS[max(0, min(value - 1, len(RELEASE_GUARD_LEVEL_LABELS) - 1))]

  @staticmethod
  def _clamp_manual_yield_torque_threshold(value: int) -> int:
    return min(
      MANUAL_YIELD_TORQUE_THRESHOLD_VALUES,
      key=lambda threshold: (abs(threshold - value), threshold),
    )

  @staticmethod
  def _format_manual_yield_torque_threshold_label(value: int) -> str:
    clamped = SubaruLayoutMici._clamp_manual_yield_torque_threshold(value)
    if clamped <= 55:
      return f"{clamped} - Caution"
    if clamped == 80:
      return "80 - Stock"
    if clamped >= 200:
      return f"{clamped} - High"
    return str(clamped)

  @staticmethod
  def _format_soft_capture_label(value: int) -> str:
    return SOFT_CAPTURE_STRENGTH_LABELS[max(0, min(value - 1, len(SOFT_CAPTURE_STRENGTH_LABELS) - 1))]

  @staticmethod
  def _format_mads_steering_angle_cap_label(value: int) -> str:
    if value == 120:
      return "120 - Stock"
    if value == 545:
      return "545 - Max Safe"
    return str(value)

  @staticmethod
  def _format_subaru_unwind_rate_label(value: int) -> str:
    idx = max(0, min(value, len(SUBARU_UNWIND_RATE_LEVEL_LABELS) - 1))
    return SUBARU_UNWIND_RATE_LEVEL_LABELS[idx]

  @staticmethod
  def _format_subaru_turn_in_rate_label(value: int) -> str:
    idx = max(0, min(value, len(SUBARU_TURN_IN_RATE_LEVEL_LABELS) - 1))
    return SUBARU_TURN_IN_RATE_LEVEL_LABELS[idx]

  @staticmethod
  def _clamp_mads_steering_angle_cap(value: int) -> int:
    return max(MADS_STEERING_ANGLE_CAP_VALUES[0], min(value, MADS_STEERING_ANGLE_CAP_VALUES[-1]))

  def _set_advanced_tuning_visibility(self, enabled: bool) -> None:
    self._manual_yield_torque_threshold_toggle.set_visible(enabled)
    self._manual_yield_torque_threshold_btn.set_visible(enabled)
    self._manual_yield_filtered_detection_toggle.set_visible(enabled)
    self._manual_yield_resume_softness_toggle.set_visible(enabled)
    self._manual_yield_resume_softness_btn.set_visible(enabled)
    self._manual_yield_release_guard_toggle.set_visible(enabled)
    self._manual_yield_release_guard_btn.set_visible(enabled)
    self._subaru_mads_tighter_turns_toggle.set_visible(enabled)
    self._subaru_mads_steering_angle_cap_btn.set_visible(enabled)
    self._subaru_turn_in_rate_level_btn.set_visible(enabled)
    self._subaru_unwind_rate_level_btn.set_visible(enabled)
    self._subaru_soft_capture_toggle.set_visible(enabled)
    self._subaru_soft_capture_strength_btn.set_visible(enabled)

  def _show_selection_view(self, items, back_callback: Callable):
    self._scroller._items = items
    for item in items:
      item.set_touch_valid_callback(lambda: self._scroller.scroll_panel.is_touch_valid() and self._scroller.enabled)
    self._scroller.scroll_panel.set_offset(0)
    self.set_back_callback(back_callback)

  def _show_value_selector(self, focused_widget: BigButton, param: str, values: list[int], label_callback: Callable[[int], str]):
    self.focused_widget = focused_widget
    current_value = self._get_int_param(param)
    header = GreyBigButton("", "tap a value to select")
    buttons = [header]
    for value in values:
      label = label_callback(value)
      btn = BigButton(label)
      if value == current_value:
        btn.set_value("selected")
      btn.set_click_callback(lambda value=value, param=param: self._select_value(param, value))
      buttons.append(btn)
    self._show_selection_view(buttons, self._reset_main_view)

  def _select_value(self, param: str, value: int):
    ui_state.params.put(param, value)
    self._reset_main_view()

  def _reset_main_view(self):
    self._scroller._items = self.main_items
    self.set_back_callback(self.original_back_callback)
    if self.focused_widget and self.focused_widget in self.main_items:
      x = self._scroller._pad
      for item in self.main_items:
        if not item.is_visible:
          continue
        if item == self.focused_widget:
          break
        x += item.rect.width + self._scroller._spacing
      self._scroller.scroll_panel.set_offset(0)
      self._scroller.scroll_to(x)
      self.focused_widget = None
    else:
      self._scroller.scroll_panel.set_offset(0)

  def _update_state(self):
    super()._update_state()

    for key, item, default in self._refresh_toggles:
      item.set_checked(self._get_bool_param(key, default))

    advanced_tuning_enabled = self._get_bool_param("MCSubaruAdvancedTuning")
    torque_threshold_enabled = self._get_bool_param("MCSubaruManualYieldTorqueThresholdEnabled")
    resume_softness_enabled = self._get_bool_param("MCSubaruManualYieldResumeSoftnessEnabled")
    release_guard_enabled = self._get_bool_param("MCSubaruManualYieldReleaseGuardEnabled")
    mads_tighter_turns_enabled = self._get_bool_param("MCSubaruMadsTighterTurnsEnabled")
    soft_capture_enabled = self._get_bool_param("MCSubaruSoftCaptureEnabled")
    self._set_advanced_tuning_visibility(advanced_tuning_enabled)
    self._manual_yield_torque_threshold_btn.set_enabled(torque_threshold_enabled)
    self._manual_yield_resume_softness_btn.set_enabled(resume_softness_enabled)
    self._manual_yield_release_guard_btn.set_enabled(release_guard_enabled)
    self._subaru_mads_steering_angle_cap_btn.set_enabled(mads_tighter_turns_enabled)
    self._subaru_soft_capture_strength_btn.set_enabled(soft_capture_enabled)
    self._manual_yield_torque_threshold_btn.set_value(
      self._format_manual_yield_torque_threshold_label(
        self._clamp_manual_yield_torque_threshold(self._get_int_param("MCSubaruManualYieldTorqueThreshold", 80))
      )
    )
    self._manual_yield_resume_softness_btn.set_value(
      self._format_resume_softness_label(max(0, min(self._get_int_param("MCSubaruManualYieldResumeSoftness", 4), 6)))
    )
    self._manual_yield_release_guard_btn.set_value(
      self._format_release_guard_label(max(1, min(self._get_int_param("MCSubaruManualYieldReleaseGuardLevel", 2), 3)))
    )
    self._subaru_mads_steering_angle_cap_btn.set_value(
      self._format_mads_steering_angle_cap_label(
        self._clamp_mads_steering_angle_cap(self._get_int_param("MCSubaruMadsMaxSteeringAngle", 120))
      )
    )
    self._subaru_turn_in_rate_level_btn.set_value(
      self._format_subaru_turn_in_rate_label(
        max(0, min(self._get_int_param("MCSubaruTurnInRateLevel"), len(SUBARU_TURN_IN_RATE_LEVEL_VALUES) - 1))
      )
    )
    self._subaru_unwind_rate_level_btn.set_value(
      self._format_subaru_unwind_rate_label(
        max(0, min(self._get_int_param("MCSubaruUnwindRateLevel"), len(SUBARU_UNWIND_RATE_LEVEL_VALUES) - 1))
      )
    )
    self._subaru_soft_capture_strength_btn.set_value(
      self._format_soft_capture_label(max(1, min(self._get_int_param("MCSubaruSoftCaptureLevel", 3), 5)))
    )

  def show_event(self):
    super().show_event()
    self._set_advanced_tuning_visibility(self._get_bool_param("MCSubaruAdvancedTuning"))
    self._reset_main_view()
