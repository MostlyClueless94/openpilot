from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
CARSTATE = REPO_ROOT / "opendbc_repo/opendbc/car/subaru/carstate.py"
CARCONTROLLER = REPO_ROOT / "opendbc_repo/opendbc/car/subaru/carcontroller.py"
FORD_CARSTATE = REPO_ROOT / "opendbc_repo/opendbc/car/ford/carstate.py"
FORD_CARCONTROLLER = REPO_ROOT / "opendbc_repo/opendbc/car/ford/carcontroller.py"


def _read(path: Path) -> str:
  return path.read_text(encoding="utf-8")


def test_carstate_fault_logs_include_steering_and_cruise_context():
  source = _read(CARSTATE)
  assert 'steerFaultTemporary={ret.steerFaultTemporary} angle={ret.steeringAngleDeg:.2f}' in source
  assert 'steerFaultPermanent={ret.steerFaultPermanent} angle={ret.steeringAngleDeg:.2f}' in source
  assert 'rate={ret.steeringRateDeg:.2f}' in source
  assert 'torque={ret.steeringTorque:.2f}' in source
  assert 'yieldThreshold={steer_threshold}' in source
  assert 'torqueEps={ret.steeringTorqueEps:.2f}' in source
  assert 'cruiseEnabled={ret.cruiseState.enabled}' in source
  assert 'cruiseAvailable={ret.cruiseState.available}' in source


def test_carstate_logs_active_manual_yield_torque_threshold():
  source = _read(CARSTATE)
  assert 'MCSubaruManualYieldTorqueThresholdEnabled' in source
  assert 'MCSubaruManualYieldTorqueThreshold' in source
  assert 'MCSubaruManualYieldFilteredDetectionEnabled' in source
  assert 'manual yield torque threshold active={steer_threshold}' in source
  assert 'customEnabled={self.mc_subaru_manual_yield_torque_threshold_enabled}' in source
  assert 'filteredEnabled={self.mc_subaru_manual_yield_filtered_detection_enabled}' in source


def test_carcontroller_request_logs_include_target_and_handoff_context():
  source = _read(CARCONTROLLER)
  assert 'angle LKAS request={lkas_request} inhibit={inhibit_reason} rawTarget={raw_steer_target:.2f}' in source
  assert 'target={steer_target:.2f}' in source
  assert 'lastApplied={self.apply_angle_last:.2f}' in source
  assert 'measuredAngle={CS.out.steeringAngleDeg:.2f}' in source
  assert 'madsOnly={mads_only} madsSelectedCap={mads_only_selected_steer_angle:.2f}' in source
  assert 'madsActiveCap={mads_only_active_steer_angle:.2f}' in source
  assert 'madsFaultGuardActive={mads_fault_guard_active}' in source
  assert 'madsFaultGuardReason={mads_fault_guard_reason}' in source
  assert 'measuredRate={CS.out.steeringRateDeg:.2f}' in source
  assert 'handoffActive={handoff_active}' in source
  assert 'rampActive={manual_override_ramp_active}' in source


def test_carcontroller_logs_neutral_angle_driver_override_state():
  source = _read(CARCONTROLLER)
  assert 'angle driver override hold active={self.angle_driver_override_hold_frames > 0}' in source
  assert 'angle driver override ramp active={manual_override_ramp_active}' in source
  assert 'MCSubaruManualYieldResumeSoftness' in source
  assert 'MCSubaruManualYieldReleaseGuardEnabled' in source
  assert 'MCSubaruManualYieldReleaseGuardLevel' in source
  assert 'angle driver override release guard active={self.angle_driver_override_release_guard_pending}' in source
  assert 'angle manual yield full release active={self.subaru_manual_yield_full_release_active}' in source
  assert 'fullReleaseActive={self.subaru_manual_yield_full_release_active}' in source
  assert 'effectiveLkasState={self.subaru_effective_lkas_active}' in source
  assert 'steeringPressed={CS.out.steeringPressed}' in source
  assert 'mads LKAS fault guard active={mads_fault_guard_active}' in source
  assert 'subaru_lkas_state_active = self.subaru_effective_lkas_active' in source
  assert 'totalFrames={self.angle_driver_override_ramp_total_frames}' in source
  assert 'softnessExponent={self.angle_driver_override_ramp_softness_exponent:.2f}' in source
  assert 'MADS manual override hold active=' not in source
  assert 'MADS manual override ramp active=' not in source


def test_carcontroller_no_longer_reads_chatter_toggle_param():
  source = _read(CARCONTROLLER)
  assert "MCSubaruChatterFix" not in source
  assert "mc_subaru_chatter_fix" not in source


def test_carcontroller_no_longer_reads_retired_subaru_tuning_params():
  source = _read(CARCONTROLLER)
  assert "MCSubaruSmoothingTune" not in source
  assert "MCSubaruSmoothingStrength" not in source
  assert "MCSubaruCenterDampingStrength" not in source
  assert "MCSubaruManualYieldResumeSpeed" not in source
  assert "_get_resume_speed_frames" not in source
  assert "angle_lkas_delta_deadzone" not in source
  assert "angle_lkas_center_damping" not in source
  assert "angle_lkas_center_sign_flip_clamp" not in source
  assert "self.angle_driver_override_ramp_frames = ANGLE_DRIVER_OVERRIDE_RAMP_FRAMES" in source


def test_ford_files_remain_free_of_subaru_release_guard_references():
  ford_controller_source = _read(FORD_CARCONTROLLER)
  ford_carstate_source = _read(FORD_CARSTATE)
  assert "MCSubaruManualYieldReleaseGuard" not in ford_controller_source
  assert "MCSubaruManualYieldReleaseGuard" not in ford_carstate_source
  assert "MCSubaruManualYieldTorqueThreshold" not in ford_controller_source
  assert "MCSubaruManualYieldTorqueThreshold" not in ford_carstate_source
  assert "MCSubaruManualYieldFilteredDetection" not in ford_controller_source
  assert "MCSubaruManualYieldFilteredDetection" not in ford_carstate_source
  assert "MCSubaruManualYieldFullRelease" not in ford_controller_source
  assert "MCSubaruManualYieldFullRelease" not in ford_carstate_source
  assert "MCSubaruMatchVehicleSpeedometer" not in ford_controller_source
  assert "MCSubaruMatchVehicleSpeedometer" not in ford_carstate_source
  assert "MCSubaruSoftCapture" not in ford_controller_source
  assert "MCSubaruSoftCapture" not in ford_carstate_source
  assert "MCSubaruMadsTighterTurns" not in ford_controller_source
  assert "MCSubaruMadsTighterTurns" not in ford_carstate_source
  assert "MCSubaruMadsMaxSteeringAngle" not in ford_controller_source
  assert "MCSubaruMadsMaxSteeringAngle" not in ford_carstate_source
  assert "MCSubaruSmoothingTune" not in ford_controller_source
  assert "MCSubaruSmoothingTune" not in ford_carstate_source
  assert "MCSubaruManualYieldResumeSpeed" not in ford_controller_source
  assert "MCSubaruManualYieldResumeSpeed" not in ford_carstate_source
  assert "angle_driver_override_release_guard" not in ford_controller_source
  assert "angle_driver_override_release_guard" not in ford_carstate_source
