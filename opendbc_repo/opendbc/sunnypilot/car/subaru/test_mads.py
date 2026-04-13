from opendbc.car import structs
from opendbc.sunnypilot.car.subaru.mads import (
  MadsCarState,
  SUBARU_LKAS_OFF_STATE,
  SUBARU_MADS_LKAS_BUTTON_STATE,
  SUBARU_STOCK_LKAS_ACTIVE_STATES,
)


ButtonType = structs.CarState.ButtonEvent.Type


def _lkas_events(cur_btn: int, prev_btn: int) -> list[structs.CarState.ButtonEvent]:
  return MadsCarState.create_lkas_button_events(cur_btn, prev_btn, {SUBARU_MADS_LKAS_BUTTON_STATE: ButtonType.lkas})


def _assert_lkas_event(events: list[structs.CarState.ButtonEvent]) -> None:
  assert len(events) == 1
  assert events[0].pressed
  assert events[0].type == ButtonType.lkas


def test_lkas_ready_toggle_creates_mads_button_event():
  for cur_btn, prev_btn in (
    (SUBARU_MADS_LKAS_BUTTON_STATE, SUBARU_LKAS_OFF_STATE),
    (SUBARU_LKAS_OFF_STATE, SUBARU_MADS_LKAS_BUTTON_STATE),
  ):
    _assert_lkas_event(_lkas_events(cur_btn, prev_btn))


def test_stock_lkas_active_states_do_not_create_mads_button_events():
  for state in SUBARU_STOCK_LKAS_ACTIVE_STATES:
    assert _lkas_events(state, SUBARU_LKAS_OFF_STATE) == []
    assert _lkas_events(state, SUBARU_MADS_LKAS_BUTTON_STATE) == []


def test_stock_lkas_active_clear_creates_mads_button_event():
  for prev_btn in SUBARU_STOCK_LKAS_ACTIVE_STATES:
    _assert_lkas_event(_lkas_events(SUBARU_LKAS_OFF_STATE, prev_btn))
    _assert_lkas_event(_lkas_events(SUBARU_MADS_LKAS_BUTTON_STATE, prev_btn))


def test_repeated_lkas_dash_states_do_not_create_mads_button_events():
  for state in (
    SUBARU_LKAS_OFF_STATE,
    SUBARU_MADS_LKAS_BUTTON_STATE,
    *SUBARU_STOCK_LKAS_ACTIVE_STATES,
  ):
    assert _lkas_events(state, state) == []


def test_lkas_state_transitions_that_are_not_physical_button_pulses_do_not_create_events():
  assert _lkas_events(3, 2) == []
  assert _lkas_events(2, 3) == []
