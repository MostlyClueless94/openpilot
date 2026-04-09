from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
BLUEPILOT_SETTINGS = REPO_ROOT / "selfdrive/ui/bp/layouts/settings/bluepilot.py"
BP_CHEVRON_RENDERER = REPO_ROOT / "selfdrive/ui/bp/onroad/chevron_metrics_bp.py"
PARAMS_KEYS = REPO_ROOT / "common/params_keys.h"
PARAMS_METADATA = REPO_ROOT / "sunnypilot/sunnylink/params_metadata.json"


def _read(path: Path) -> str:
  return path.read_text(encoding="utf-8")


def test_bluepilot_settings_add_radar_overlay_info_selector():
  source = _read(BLUEPILOT_SETTINGS)

  visuals_order = [
    "self._show_ford_radar_overlay,",
    "self._radar_overlay_size_btn,",
    "self._radar_overlay_info_btn,",
  ]
  order_indexes = [source.index(token) for token in visuals_order]

  assert order_indexes == sorted(order_indexes)
  assert 'lambda: tr("Radar Overlay Info")' in source
  assert 'buttons=[lambda: tr("Distance"), lambda: tr("Speed"), lambda: tr("Time"), lambda: tr("All")]' in source
  assert "callback=self._set_overlay_info" in source
  assert "selected_index=overlay_info_value - 1" in source
  assert 'overlay_enabled = fresh.get("FordPrefShowRadarLeadOverlay") if "FordPrefShowRadarLeadOverlay" in fresh else self._safe_get_bool(ui_state.params, "FordPrefShowRadarLeadOverlay")' in source
  assert "self._radar_overlay_size_btn.action_item.set_enabled(overlay_enabled)" in source
  assert "self._radar_overlay_info_btn.action_item.set_enabled(overlay_enabled)" in source
  assert "self._radar_overlay_info_btn.action_item.set_selected_button(overlay_info_value - 1)" in source
  assert "def _set_overlay_info(self, button_index: int):" in source
  assert 'self._params.put("FordPrefRadarOverlayInfo", button_index + 1)' in source


def test_bluepilot_radar_overlay_param_is_registered_and_documented():
  params_source = _read(PARAMS_KEYS)
  metadata_source = _read(PARAMS_METADATA)

  assert '{"FordPrefRadarOverlayInfo", {PERSISTENT | BACKUP, INT, "4"}}' in params_source
  assert '"FordPrefRadarOverlayInfo"' in metadata_source
  assert '"title": "BluePilot: Radar Overlay Info (C3X)"' in metadata_source
  assert '{ "value": 1, "label": "Distance" }' in metadata_source
  assert '{ "value": 2, "label": "Speed" }' in metadata_source
  assert '{ "value": 3, "label": "Time" }' in metadata_source
  assert '{ "value": 4, "label": "All" }' in metadata_source


def test_bp_renderer_keeps_boxed_overlay_for_single_metric_modes():
  source = _read(BP_CHEVRON_RENDERER)

  assert "FORD_RADAR_OVERLAY_INFO_DEFAULT = ChevronOptions.ALL" in source
  assert "def _build_ford_overlay_text_lines" in source
  assert "return self._build_ford_overlay_text_lines(d_rel, v_rel, v_ego, self._get_ford_overlay_info(), ui_state.is_metric)" in source
  assert "if self.ford_overlay_enabled and text_lines:" in source
  assert "if self.ford_overlay_enabled and len(text_lines) == 3:" not in source
  assert "box = box_rects[len(box_rects) // 2] if box_rects else None" in source


def test_bp_overlay_info_modes_build_expected_metric_sets():
  chevron_module = pytest.importorskip("openpilot.selfdrive.ui.bp.onroad.chevron_metrics_bp")

  distance = chevron_module.ChevronMetricsBP._build_ford_overlay_text_lines(
    30.0, 0.0, 10.0, chevron_module.ChevronOptions.DISTANCE_ONLY, True
  )
  speed = chevron_module.ChevronMetricsBP._build_ford_overlay_text_lines(
    30.0, 0.0, 10.0, chevron_module.ChevronOptions.SPEED_ONLY, True
  )
  time = chevron_module.ChevronMetricsBP._build_ford_overlay_text_lines(
    30.0, 0.0, 10.0, chevron_module.ChevronOptions.TTC_ONLY, True
  )
  all_metrics = chevron_module.ChevronMetricsBP._build_ford_overlay_text_lines(
    30.0, 0.0, 10.0, chevron_module.ChevronOptions.ALL, True
  )

  assert distance == ["30 m"]
  assert speed == ["36 km/h"]
  assert time == ["3.0 s"]
  assert all_metrics == ["30 m", "36 km/h", "3.0 s"]
