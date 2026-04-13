from types import SimpleNamespace

from cereal import custom
from opendbc.car import structs
from openpilot.selfdrive.selfdrived.events import Events
from openpilot.sunnypilot.mads.helpers import MadsSteeringModeOnBrake
from openpilot.sunnypilot.mads.mads import ModularAssistiveDrivingSystem
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP


ButtonType = structs.CarState.ButtonEvent.Type
EventNameSP = custom.OnroadEventSP.EventName
GearShifter = structs.CarState.GearShifter
State = custom.ModularAssistiveDrivingSystem.ModularAssistiveDrivingSystemState


def _mads_for_lkas_button(*, enabled=True, selfdrive_enabled=True):
  mads = ModularAssistiveDrivingSystem.__new__(ModularAssistiveDrivingSystem)
  mads.enabled = enabled
  mads.allow_always = False
  mads.no_main_cruise = False
  mads.main_enabled_toggle = False
  mads.steering_mode_on_brake = MadsSteeringModeOnBrake.PAUSE
  mads.state_machine = SimpleNamespace(state=State.enabled)
  mads.events = Events()
  mads.events_sp = EventsSP()
  mads.selfdrive = SimpleNamespace(
    enabled=selfdrive_enabled,
    enabled_prev=selfdrive_enabled,
    CS_prev=SimpleNamespace(
      gasPressed=False,
      cruiseState=SimpleNamespace(available=True),
    ),
  )
  return mads


def _car_state_with_lkas_button():
  return SimpleNamespace(
    standstill=False,
    gasPressed=False,
    vEgo=10.0,
    gearShifter=GearShifter.drive,
    cruiseState=SimpleNamespace(available=True),
    buttonEvents=[structs.CarState.ButtonEvent(pressed=True, type=ButtonType.lkas)],
  )


def test_lkas_button_disables_mads_even_when_selfdrive_is_enabled():
  mads = _mads_for_lkas_button(enabled=True, selfdrive_enabled=True)

  mads.update_events(_car_state_with_lkas_button())

  assert mads.events_sp.has(EventNameSP.lkasDisable)
  assert not mads.events_sp.has(EventNameSP.manualSteeringRequired)


def test_lkas_button_still_enables_mads_when_mads_is_disabled():
  mads = _mads_for_lkas_button(enabled=False, selfdrive_enabled=True)

  mads.update_events(_car_state_with_lkas_button())

  assert mads.events_sp.has(EventNameSP.lkasEnable)
  assert not mads.events_sp.has(EventNameSP.manualSteeringRequired)
