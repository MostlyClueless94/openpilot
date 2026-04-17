from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SLIDER = REPO_ROOT / "system/ui/widgets/slider.py"


def _read(path: Path) -> str:
  return path.read_text(encoding="utf-8")


def test_confirmation_slider_hitbox_matches_centered_visual_knob():
  source = _read(SLIDER)

  assert "def _circle_button_rect(self) -> rl.Rectangle:" in source
  assert "bg_txt_x = self._rect.x + (self._rect.width - self._bg_txt.width) / 2" in source
  assert "bg_txt_y = self._rect.y + (self._rect.height - self._circle_bg_txt.height) / 2" in source
  assert "circle_button_rect = self._circle_button_rect()" in source
  assert "self._rect.x + (self._rect.width - self._circle_bg_txt.width)" not in source
