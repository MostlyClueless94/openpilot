from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
TICI_SUBARU = REPO_ROOT / "selfdrive/ui/sunnypilot/layouts/settings/vehicle/brands/subaru.py"
TICI_MC_CUSTOM = REPO_ROOT / "selfdrive/ui/sunnypilot/layouts/settings/mc_custom.py"
TICI_FORD = REPO_ROOT / "selfdrive/ui/sunnypilot/layouts/settings/vehicle/brands/ford.py"
MICI_VEHICLE = REPO_ROOT / "selfdrive/ui/bp/mici/layouts/settings/vehicle_mici.py"
MICI_SUBARU = REPO_ROOT / "selfdrive/ui/sunnypilot/mici/layouts/subaru.py"
PARAMS_KEYS = REPO_ROOT / "common/params_keys.h"
PARAMS_METADATA = REPO_ROOT / "sunnypilot/sunnylink/params_metadata.json"

REMOVED_SUBARU_TUNING_PARAMS = (
  "MCSubaruSmoothingTune",
  "MCSubaruSmoothingStrength",
  "MCSubaruCenterDampingStrength",
  "MCSubaruManualYieldResumeSpeedEnabled",
  "MCSubaruManualYieldResumeSpeed",
)


def _read(path: Path) -> str:
  return path.read_text(encoding="utf-8")


def test_tici_subaru_brand_page_only_hosts_stop_and_go_controls():
  source = _read(TICI_SUBARU)
  assert "class SubaruSettings(BrandSettings):" in source
  assert "def __init__(self):" in source
  assert "def update_settings(self):" in source
  assert 'param="SubaruStopAndGo"' in source
  assert 'param="SubaruStopAndGoManualParkingBrake"' in source
  assert "self.items = [" in source
  assert "self.stop_and_go_toggle," in source
  assert "self.stop_and_go_manual_parking_brake_toggle," in source
  assert "MCSubaruMatchVehicleSpeedometer" not in source
  assert 'param="MCSubaruAdvancedTuning"' not in source
  assert 'SectionHeader(tr("Lateral Tuning"))' not in source
  assert "Manual Yield Resume" not in source


def test_tici_subaru_brand_page_restores_stop_and_go_platform_logic():
  source = _read(TICI_SUBARU)
  assert "from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.base import BrandSettings" in source
  assert "from openpilot.selfdrive.ui.ui_state import ui_state" in source
  assert "from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp" in source
  assert "from opendbc.car.subaru.values import CAR, SubaruFlags" in source
  assert "self.has_stop_and_go = False" in source
  assert "platform = bundle.get(\"platform\")" in source
  assert "config = CAR[platform].config" in source
  assert "self.has_stop_and_go = not (config.flags & (SubaruFlags.GLOBAL_GEN2 | SubaruFlags.HYBRID))" in source
  assert "toggle.action_item.set_enabled(self.has_stop_and_go and ui_state.is_offroad())" in source
  assert 'Enable "Always Offroad" in Device panel, or turn vehicle off to toggle.' in source
  assert "strict=True" in source
  assert 'action_item.set_state(ui_state.params.get_bool("SubaruStopAndGo"))' not in source
  assert 'action_item.set_state(' not in source


def test_tici_mc_custom_subaru_section_hosts_speedometer_toggle():
  source = _read(TICI_MC_CUSTOM)
  assert 'MATCH_VEHICLE_SPEEDOMETER_DESC = (' in source
  assert '"Match Vehicle Speedometer"' in source
  assert 'param="MCSubaruMatchVehicleSpeedometer"' in source
  assert 'initial_state=self._get_bool_param("MCSubaruMatchVehicleSpeedometer", True)' in source
  assert "self._subaru_match_vehicle_speedometer," in source
  assert "self._subaru_match_vehicle_speedometer.set_visible(True)" in source
  assert 'self._get_bool_param("MCSubaruMatchVehicleSpeedometer", True)' in source
  assert 'matches the vehicle dash or cluster speed when supported' in source
  assert 'self._subaru_advanced_tuning.set_visible(True)' in source
  assert 'param="MCSubaruAdvancedTuning"' in source
  assert 'param="MCSubaruManualYieldTorqueThresholdEnabled"' in source
  assert 'param="MCSubaruManualYieldTorqueThreshold"' in source
  assert 'param="MCSubaruManualYieldReleaseGuardEnabled"' in source
  assert 'param="MCSubaruManualYieldReleaseGuardLevel"' in source
  assert 'param="MCSubaruMadsTighterTurnsEnabled"' in source
  assert 'param="MCSubaruMadsMaxSteeringAngle"' in source
  assert '"Custom Yield Torque"' in source
  assert '"Manual Yield Torque Threshold"' in source
  assert '"Manual Yield Release Guard"' in source
  assert '"Release Guard Strength"' in source
  assert '"Tighter MADS Turns"' in source
  assert '"MADS Steering Angle Cap"' in source


def test_ford_brand_page_does_not_gain_subaru_controls():
  source = _read(TICI_FORD)
  assert "MCSubaru" not in source
  assert "SubaruStopAndGo" not in source
  assert "Manual Yield Resume" not in source
  assert "Advanced Tuning" not in source


def test_mici_vehicle_menu_adds_subaru_entry_only_for_subaru_brand():
  source = _read(MICI_VEHICLE)
  assert "from openpilot.selfdrive.ui.sunnypilot.mici.layouts.subaru import SubaruLayoutMici" in source
  assert "def get_vehicle_brand() -> str:" in source
  assert 'self._btn_subaru = BigButtonBP(tr("subaru settings")' in source
  assert 'self._btn_subaru.set_click_callback(self._on_subaru_settings)' in source
  assert 'is_subaru = get_vehicle_brand() == "subaru"' in source
  assert "self._btn_subaru.set_visible(is_subaru)" in source
  assert "self._btn_subaru.set_enabled(is_subaru)" in source
  assert "gui_app.push_widget(SubaruLayoutMici(back_callback=gui_app.pop_widget))" in source


def test_mici_subaru_layout_contains_driving_only_subaru_controls():
  source = _read(MICI_SUBARU)
  assert 'GreyBigButton("stop and\\ngo")' in source
  assert 'GreyBigButton("lateral\\ntuning")' in source
  assert 'BigParamControl("stop and go\\n(beta)", "SubaruStopAndGo")' in source
  assert '"SubaruStopAndGoManualParkingBrake"' in source
  assert '"match vehicle\\nspeedometer"' in source
  assert '"MCSubaruMatchVehicleSpeedometer"' in source
  assert 'BigParamControl("advanced\\ntuning", "MCSubaruAdvancedTuning")' in source
  assert 'BigParamControl("custom yield\\ntorque", "MCSubaruManualYieldTorqueThresholdEnabled")' in source
  assert 'BigButton("manual yield\\ntorque")' in source
  assert 'BigParamControl("custom resume\\nsoftness", "MCSubaruManualYieldResumeSoftnessEnabled")' in source
  assert 'BigButton("manual yield\\nresume softness")' in source
  assert 'BigParamControl("manual yield\\nrelease guard", "MCSubaruManualYieldReleaseGuardEnabled")' in source
  assert 'BigButton("release guard\\nstrength")' in source
  assert 'BigParamControl("tighter MADS\\nturns", "MCSubaruMadsTighterTurnsEnabled")' in source
  assert 'BigButton("MADS steering\\nangle cap")' in source
  assert 'BigParamControl("soft-capture\\nengage blend", "MCSubaruSoftCaptureEnabled")' in source
  assert 'BigButton("soft-capture\\nstrength")' in source
  assert 'list(range(MANUAL_YIELD_TORQUE_THRESHOLD_MIN, MANUAL_YIELD_TORQUE_THRESHOLD_MAX + MANUAL_YIELD_TORQUE_THRESHOLD_STEP, MANUAL_YIELD_TORQUE_THRESHOLD_STEP))' in source
  assert 'list(range(7))' in source
  assert 'list(range(1, 4))' in source
  assert 'list(MADS_STEERING_ANGLE_CAP_VALUES)' in source
  assert 'list(range(1, 6))' in source
  assert 'BigParamControl("subaru steering\\nsmoothing", "MCSubaruSmoothingTune")' not in source
  assert 'BigButton("smoothing\\nstrength")' not in source
  assert 'BigButton("center\\ndamping")' not in source
  assert 'BigParamControl("custom resume\\nspeed", "MCSubaruManualYieldResumeSpeedEnabled")' not in source
  assert 'BigButton("manual yield\\nresume speed")' not in source
  assert 'list(range(-3, 5))' not in source
  for param in REMOVED_SUBARU_TUNING_PARAMS:
    assert param not in source
  assert 'ShowBrakeStatus' not in source
  assert 'DynamicPathColor' not in source
  assert 'BPShowConfidenceBall' not in source
  assert 'HideVEgoUI' not in source


def test_mici_subaru_layout_has_safe_grey_header_fallback_for_bp_branch():
  source = _read(MICI_SUBARU)
  assert "try:" in source
  assert "from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigParamControl, GreyBigButton" in source
  assert "except ImportError:" in source
  assert "from openpilot.selfdrive.ui.bp.mici.widgets.button_bp import BigButtonBP as BigButton, BigParamControlBP as BigParamControl" in source
  assert "class GreyBigButton(BigButton):" in source
  assert "tint=rl.Color(0x66, 0x66, 0x66, 0xFF)" in source
  assert "self.set_touch_valid_callback(lambda: False)" in source


def test_mici_subaru_layout_preserves_scroll_restore_selector_stack():
  source = _read(MICI_SUBARU)
  assert "def _show_selection_view(self, items, back_callback: Callable):" in source
  assert "def _show_value_selector(self, focused_widget: BigButton, param: str, values: list[int], label_callback: Callable[[int], str]):" in source
  assert "def _select_value(self, param: str, value: int):" in source
  assert "def _reset_main_view(self):" in source
  assert "self.focused_widget = focused_widget" in source
  assert "self._show_selection_view(buttons, self._reset_main_view)" in source
  assert "self._scroller.scroll_to(x)" in source


def test_mici_subaru_layout_uses_safe_bool_reads_and_advanced_tuning_visibility():
  source = _read(MICI_SUBARU)
  assert "value = ui_state.params.get(key, return_default=True)" in source
  assert "self._set_advanced_tuning_visibility(advanced_tuning_enabled)" in source
  assert '("MCSubaruMatchVehicleSpeedometer", self._match_vehicle_speedometer_toggle, True)' in source
  assert '("MCSubaruManualYieldTorqueThresholdEnabled", self._manual_yield_torque_threshold_toggle, False)' in source
  assert '("MCSubaruManualYieldResumeSoftnessEnabled", self._manual_yield_resume_softness_toggle, False)' in source
  assert '("MCSubaruManualYieldReleaseGuardEnabled", self._manual_yield_release_guard_toggle, False)' in source
  assert '("MCSubaruMadsTighterTurnsEnabled", self._subaru_mads_tighter_turns_toggle, False)' in source
  assert '("MCSubaruSoftCaptureEnabled", self._subaru_soft_capture_toggle, False)' in source
  assert 'self._manual_yield_torque_threshold_btn.set_enabled(torque_threshold_enabled)' in source
  assert 'self._manual_yield_resume_softness_btn.set_enabled(resume_softness_enabled)' in source
  assert 'self._manual_yield_release_guard_btn.set_enabled(release_guard_enabled)' in source
  assert 'self._subaru_mads_steering_angle_cap_btn.set_enabled(mads_tighter_turns_enabled)' in source
  assert 'self._subaru_soft_capture_strength_btn.set_enabled(soft_capture_enabled)' in source
  assert 'self._manual_yield_torque_threshold_toggle.set_visible(enabled)' in source
  assert 'self._manual_yield_torque_threshold_btn.set_visible(enabled)' in source
  assert 'self._manual_yield_resume_softness_toggle.set_visible(enabled)' in source
  assert 'self._manual_yield_resume_softness_btn.set_visible(enabled)' in source
  assert 'self._manual_yield_release_guard_toggle.set_visible(enabled)' in source
  assert 'self._manual_yield_release_guard_btn.set_visible(enabled)' in source
  assert 'self._subaru_mads_tighter_turns_toggle.set_visible(enabled)' in source
  assert 'self._subaru_mads_steering_angle_cap_btn.set_visible(enabled)' in source
  assert 'self._subaru_soft_capture_toggle.set_visible(enabled)' in source
  assert 'self._subaru_soft_capture_strength_btn.set_visible(enabled)' in source
  assert 'self._format_manual_yield_torque_threshold_label(' in source
  assert 'self._format_resume_softness_label(max(0, min(self._get_int_param("MCSubaruManualYieldResumeSoftness", 4), 6)))' in source
  assert 'self._format_release_guard_label(max(1, min(self._get_int_param("MCSubaruManualYieldReleaseGuardLevel", 2), 3)))' in source
  assert 'self._format_mads_steering_angle_cap_label(' in source
  assert 'self._format_soft_capture_label(max(1, min(self._get_int_param("MCSubaruSoftCaptureLevel", 3), 5)))' in source
  assert "smoothing_enabled" not in source
  assert "resume_speed_enabled" not in source
  assert "self._manual_yield_resume_speed_btn" not in source


def test_subaru_params_and_metadata_match_brand_scoped_defaults():
  params_source = _read(PARAMS_KEYS)
  metadata_source = _read(PARAMS_METADATA)
  assert '{"MCSubaruAdvancedTuning", {PERSISTENT | BACKUP, BOOL, "0"}}' in params_source
  assert '{"MCSubaruMatchVehicleSpeedometer", {PERSISTENT | BACKUP, BOOL, "1"}}' in params_source
  assert '{"MCSubaruManualYieldTorqueThresholdEnabled", {PERSISTENT | BACKUP, BOOL, "0"}}' in params_source
  assert '{"MCSubaruManualYieldTorqueThreshold", {PERSISTENT | BACKUP, INT, "80"}}' in params_source
  assert '{"MCSubaruManualYieldResumeSoftnessEnabled", {PERSISTENT | BACKUP, BOOL, "0"}}' in params_source
  assert '{"MCSubaruManualYieldResumeSoftness", {PERSISTENT | BACKUP, INT, "4"}}' in params_source
  assert '{"MCSubaruManualYieldReleaseGuardEnabled", {PERSISTENT | BACKUP, BOOL, "0"}}' in params_source
  assert '{"MCSubaruManualYieldReleaseGuardLevel", {PERSISTENT | BACKUP, INT, "2"}}' in params_source
  assert '{"MCSubaruMadsTighterTurnsEnabled", {PERSISTENT | BACKUP, BOOL, "0"}}' in params_source
  assert '{"MCSubaruMadsMaxSteeringAngle", {PERSISTENT | BACKUP, INT, "120"}}' in params_source
  assert '{"MCSubaruSoftCaptureEnabled", {PERSISTENT | BACKUP, BOOL, "0"}}' in params_source
  assert '{"MCSubaruSoftCaptureLevel", {PERSISTENT | BACKUP, INT, "3"}}' in params_source
  assert '{"Subaru11BluePilotTuningMigrated", {PERSISTENT | BACKUP, STRING, "0.0"}}' in params_source
  assert '{"SubaruManualYieldTorqueFloorMigrated", {PERSISTENT | BACKUP, STRING, "0.0"}}' in params_source
  assert '"MCSubaruAdvancedTuning"' in metadata_source
  assert '"MCSubaruMatchVehicleSpeedometer"' in metadata_source
  assert '"MCSubaruManualYieldTorqueThresholdEnabled"' in metadata_source
  assert '"MCSubaruManualYieldTorqueThreshold"' in metadata_source
  assert '"MCSubaruManualYieldResumeSoftnessEnabled"' in metadata_source
  assert '"MCSubaruManualYieldResumeSoftness"' in metadata_source
  assert '"MCSubaruManualYieldReleaseGuardEnabled"' in metadata_source
  assert '"MCSubaruManualYieldReleaseGuardLevel"' in metadata_source
  assert '"MCSubaruMadsTighterTurnsEnabled"' in metadata_source
  assert '"MCSubaruMadsMaxSteeringAngle"' in metadata_source
  assert '"MCSubaruSoftCaptureEnabled"' in metadata_source
  assert '"MCSubaruSoftCaptureLevel"' in metadata_source
  assert '"label": "40 - Caution"' in metadata_source
  assert '"label": "80 - Stock"' in metadata_source
  assert '"label": "150"' in metadata_source
  assert '"label": "Standard"' in metadata_source
  assert '"label": "Max Soft"' in metadata_source
  assert '"label": "Light"' in metadata_source
  assert '"label": "Strong"' in metadata_source
  assert '"label": "120 - Stock"' in metadata_source
  assert '"label": "545 - Max Safe"' in metadata_source
  for param in REMOVED_SUBARU_TUNING_PARAMS:
    assert param not in params_source
    assert param not in metadata_source
  assert '"label": "Fastest"' not in metadata_source
  assert '"label": "Slowest"' not in metadata_source
