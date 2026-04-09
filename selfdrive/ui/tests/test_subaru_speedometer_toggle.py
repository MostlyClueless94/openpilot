import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SPEED_DISPLAY = REPO_ROOT / "selfdrive/ui/sunnypilot/onroad/speed_display.py"
TICI_BP_HUD = REPO_ROOT / "selfdrive/ui/bp/onroad/hud_renderer_bp.py"
MICI_HUD = REPO_ROOT / "selfdrive/ui/mici/onroad/hud_renderer.py"
MICI_COMPLICATION = REPO_ROOT / "selfdrive/ui/bp/mici/onroad/complication.py"


def _read(path: Path) -> str:
  return path.read_text(encoding="utf-8")


def _load_module(path: Path):
  spec = importlib.util.spec_from_file_location(path.stem, path)
  module = importlib.util.module_from_spec(spec)
  assert spec.loader is not None
  spec.loader.exec_module(module)
  return module


def test_speed_display_helper_handles_subaru_override_and_default_passthrough():
  module = _load_module(SPEED_DISPLAY)

  class FakeCp:
    def __init__(self, car_name: str):
      self.carName = car_name

  assert module.is_subaru_platform(FakeCp("subaru")) is True
  assert module.is_subaru_platform(FakeCp("ford")) is False

  assert module.get_display_speed_ms(FakeCp("subaru"), True, 10.0, 12.0, True, 12.0) == 12.0
  assert module.get_display_speed_ms(FakeCp("subaru"), True, 10.0, 12.0, False, 12.0) == 10.0
  assert module.get_display_speed_ms(FakeCp("subaru"), False, 10.0, 12.0, True, 12.0) == 10.0
  assert module.get_display_speed_ms(FakeCp("ford"), False, 10.0, 12.0, True, 99.0) == 99.0


def test_tici_bp_hud_uses_subaru_speedometer_toggle_for_current_speed():
  source = _read(TICI_BP_HUD)

  assert "from openpilot.selfdrive.ui.sunnypilot.onroad.speed_display import get_display_speed_ms" in source
  assert 'ui_state.params.get_bool("MCSubaruMatchVehicleSpeedometer")' in source
  assert "display_speed_ms = get_display_speed_ms(" in source
  assert "self.speed = max(0.0, display_speed_ms * speed_conversion)" in source


def test_mici_hud_uses_subaru_speedometer_toggle_for_current_speed():
  source = _read(MICI_HUD)

  assert "from openpilot.selfdrive.ui.sunnypilot.onroad.speed_display import get_display_speed_ms" in source
  assert 'ui_state.params.get_bool("MCSubaruMatchVehicleSpeedometer")' in source
  assert "default_speed_ms = v_ego_cluster if self.v_ego_cluster_seen else car_state.vEgo" in source
  assert "v_ego = get_display_speed_ms(" in source


def test_mici_complication_only_applies_toggle_to_current_speed_mode():
  source = _read(MICI_COMPLICATION)

  assert "from openpilot.selfdrive.ui.sunnypilot.onroad.speed_display import get_display_speed_ms" in source
  assert "self.v_ego_cluster_seen: bool = False" in source
  assert "display_speed_ms = get_display_speed_ms(" in source
  assert 'self.params.get_bool("MCSubaruMatchVehicleSpeedometer")' in source
  assert "speed_text = str(round(max(0.0, display_speed_ms * speed_conversion)))" in source
  assert "self.speed = max(0.0, self._car_state.vEgoCluster * speed_conversion + speed_delta)" in source
