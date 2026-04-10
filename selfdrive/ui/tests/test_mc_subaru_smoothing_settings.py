from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MC_CUSTOM = REPO_ROOT / "selfdrive/ui/sunnypilot/layouts/settings/mc_custom.py"
PARAMS_KEYS = REPO_ROOT / "common/params_keys.h"
PARAMS_METADATA = REPO_ROOT / "sunnypilot/sunnylink/params_metadata.json"


def _read(path: Path) -> str:
  return path.read_text(encoding="utf-8")


def test_mc_custom_hosts_subaru_controls_at_the_end_of_the_page():
  source = _read(MC_CUSTOM)
  assert 'param="DynamicPathColor"' in source
  assert 'param="DynamicPathColorPalette"' not in source
  assert 'param="CustomModelPathColor"' in source
  assert 'param="MCShowVehicleBrakeStatus"' in source
  assert 'SectionHeader(tr("Subaru"))' in source
  assert source.index("self._show_vehicle_brake_status,") < source.index("self._subaru_header,")
  assert 'param="SubaruStopAndGo"' not in source
  assert 'param="SubaruStopAndGoManualParkingBrake"' not in source
  assert 'param="MCSubaruAdvancedTuning"' in source
  assert 'param="MCSubaruSmoothingTune"' in source
  assert 'param="MCSubaruSmoothingStrength"' in source
  assert 'param="MCSubaruCenterDampingStrength"' in source
  assert 'param="MCSubaruManualYieldResumeSpeedEnabled"' in source
  assert 'param="MCSubaruManualYieldResumeSpeed"' in source
  assert 'param="MCSubaruManualYieldResumeSoftnessEnabled"' in source
  assert 'param="MCSubaruManualYieldResumeSoftness"' in source
  assert 'param="MCSubaruManualYieldReleaseGuardEnabled"' in source
  assert 'param="MCSubaruManualYieldReleaseGuardLevel"' in source
  assert 'param="MCSubaruSoftCaptureEnabled"' in source
  assert 'param="MCSubaruSoftCaptureLevel"' in source
  assert 'Subaru Delay Tweak (Test)' not in source
  assert "Dynamic Path Color Palette" not in source


def test_mc_custom_always_shows_subaru_section_and_preserves_tuning_logic():
  source = _read(MC_CUSTOM)
  assert 'def _get_current_brand(self) -> str:' not in source
  assert 'CarPlatformBundle' not in source
  assert 'def _is_subaru_active(self) -> bool:' not in source
  assert 'def _get_subaru_stop_and_go_available(self) -> bool:' not in source
  assert 'def _set_subaru_section_visibility(self, advanced_tuning_enabled: bool) -> None:' in source
  assert 'self._subaru_header.set_visible(True)' in source
  assert 'self._subaru_advanced_tuning.set_visible(True)' in source
  assert 'self._subaru_smoothing_tune.set_visible(advanced_tuning_enabled)' in source
  assert 'self._manual_yield_resume_softness.set_visible(advanced_tuning_enabled)' in source
  assert 'self._manual_yield_resume_speed_enabled.set_visible(advanced_tuning_enabled)' in source
  assert 'self._manual_yield_resume_softness_enabled.set_visible(advanced_tuning_enabled)' in source
  assert 'self._manual_yield_release_guard_enabled.set_visible(advanced_tuning_enabled)' in source
  assert 'self._manual_yield_release_guard_level.set_visible(advanced_tuning_enabled)' in source
  assert 'self._subaru_soft_capture.set_visible(advanced_tuning_enabled)' in source
  assert 'self._subaru_soft_capture_strength.set_visible(advanced_tuning_enabled)' in source
  assert 'self._subaru_smoothing_strength.action_item.set_enabled(smoothing_enabled)' in source
  assert 'self._subaru_center_damping.action_item.set_enabled(smoothing_enabled)' in source
  assert 'self._manual_yield_resume_speed.action_item.set_enabled(resume_speed_enabled)' in source
  assert 'self._manual_yield_resume_softness.action_item.set_enabled(resume_softness_enabled)' in source
  assert 'self._manual_yield_release_guard_level.action_item.set_enabled(release_guard_enabled)' in source
  assert 'self._subaru_soft_capture_strength.action_item.set_enabled(soft_capture_enabled)' in source
  assert 'self._set_subaru_section_visibility(advanced_tuning_enabled)' in source
  assert 'callback=self._on_subaru_toggle_changed' not in source
  assert 'def _on_subaru_toggle_changed(self, _):' not in source
  assert 'self._subaru_advanced_tuning.action_item.set_state(advanced_tuning_enabled)' in source
  assert 'self._subaru_smoothing_tune.action_item.set_state(smoothing_enabled)' in source
  assert 'self._manual_yield_resume_speed_enabled.action_item.set_state(resume_speed_enabled)' in source
  assert 'self._manual_yield_resume_softness_enabled.action_item.set_state(resume_softness_enabled)' in source
  assert 'self._manual_yield_release_guard_enabled.action_item.set_state(release_guard_enabled)' in source
  assert 'self._subaru_soft_capture.action_item.set_state(soft_capture_enabled)' in source
  assert 'self._manual_yield_release_guard_level.action_item.current_value = max(1, min(self._get_int_param("MCSubaruManualYieldReleaseGuardLevel", 2), 3))' in source
  assert 'self._subaru_soft_capture_strength.action_item.current_value = max(1, min(self._get_int_param("MCSubaruSoftCaptureLevel", 3), 5))' in source
  assert 'value = self._params.get(key, return_default=True)' in source


def test_params_keys_register_subaru_tuning_defaults_for_mc_custom_menu():
  source = _read(PARAMS_KEYS)
  assert '{"MCSubaruAdvancedTuning", {PERSISTENT | BACKUP, BOOL, "0"}}' in source
  assert '{"MCSubaruSmoothingTune", {PERSISTENT | BACKUP, BOOL, "1"}}' in source
  assert '{"MCSubaruSmoothingStrength", {PERSISTENT | BACKUP, INT, "2"}}' in source
  assert '{"MCSubaruCenterDampingStrength", {PERSISTENT | BACKUP, INT, "2"}}' in source
  assert '{"MCSubaruManualYieldResumeSpeedEnabled", {PERSISTENT | BACKUP, BOOL, "1"}}' in source
  assert '{"MCSubaruManualYieldResumeSpeed", {PERSISTENT | BACKUP, INT, "4"}}' in source
  assert '{"MCSubaruManualYieldResumeSoftnessEnabled", {PERSISTENT | BACKUP, BOOL, "1"}}' in source
  assert '{"MCSubaruManualYieldResumeSoftness", {PERSISTENT | BACKUP, INT, "4"}}' in source
  assert '{"MCSubaruManualYieldReleaseGuardEnabled", {PERSISTENT | BACKUP, BOOL, "0"}}' in source
  assert '{"MCSubaruManualYieldReleaseGuardLevel", {PERSISTENT | BACKUP, INT, "2"}}' in source
  assert '{"MCSubaruSoftCaptureEnabled", {PERSISTENT | BACKUP, BOOL, "0"}}' in source
  assert '{"MCSubaruSoftCaptureLevel", {PERSISTENT | BACKUP, INT, "3"}}' in source
  assert '{"SubaruStopAndGo", {PERSISTENT | BACKUP, BOOL, "0"}}' in source
  assert '{"SubaruStopAndGoManualParkingBrake", {PERSISTENT | BACKUP, BOOL, "0"}}' in source


def test_params_metadata_describes_subaru_brand_menu_ranges_and_labels():
  source = _read(PARAMS_METADATA)
  assert '"MCSubaruAdvancedTuning"' in source
  assert '"title": "Advanced Tuning"' in source
  assert 'Show Subaru lateral tuning controls. Hidden controls keep their saved values active.' in source
  assert '"MCSubaruSmoothingTune"' in source
  assert '"title": "Subaru Steering Smoothing"' in source
  assert '"MCSubaruSmoothingStrength"' in source
  assert '"min": -3' in source
  assert '"max": 4' in source
  assert '"label": "-3"' in source
  assert '"label": "+4"' in source
  assert '"label": "+5"' not in source
  assert '"label": "-4"' not in source
  assert '"MCSubaruCenterDampingStrength"' in source
  assert '"title": "Center Damping"' in source
  assert '"MCSubaruManualYieldResumeSpeedEnabled"' in source
  assert '"title": "Custom Resume Speed"' in source
  assert 'falls back to the current validated default while keeping your saved speed selection' in source
  assert '"MCSubaruManualYieldResumeSpeed"' in source
  assert '"title": "Manual Yield Resume Speed"' in source
  assert '"label": "Fastest"' in source
  assert '"label": "Slow"' in source
  assert '"label": "Slowest"' in source
  assert '"MCSubaruManualYieldResumeSoftnessEnabled"' in source
  assert '"title": "Custom Resume Softness"' in source
  assert 'falls back to the current validated default while keeping your saved softness selection' in source
  assert '"MCSubaruManualYieldResumeSoftness"' in source
  assert '"title": "Manual Yield Resume Softness"' in source
  assert '"label": "Standard"' in source
  assert '"label": "Extra Soft"' in source
  assert '"label": "Max Soft"' in source
  assert '"MCSubaruManualYieldReleaseGuardEnabled"' in source
  assert '"title": "Manual Yield Release Guard"' in source
  assert 'reduce false reclaim jerks when you are still holding the wheel at a steady angle' in source
  assert '"MCSubaruManualYieldReleaseGuardLevel"' in source
  assert '"title": "Release Guard Strength"' in source
  assert '"label": "Light"' in source
  assert '"label": "Medium"' in source
  assert '"label": "Strong"' in source
  assert '"MCSubaruSoftCaptureEnabled"' in source
  assert '"title": "Soft-Capture Engage Blend"' in source
  assert 'Experiment — MostlyClueless only.' in source
  assert '"MCSubaruSoftCaptureLevel"' in source
  assert '"title": "Soft-Capture Strength"' in source
  assert '"label": "1 - Light"' in source
  assert '"label": "5 - Max"' in source
