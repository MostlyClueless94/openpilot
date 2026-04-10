import unittest
from types import SimpleNamespace

from openpilot.common.params import Params
from opendbc.car.subaru.carstate import CarState
from opendbc.car.subaru.interface import CarInterface
from opendbc.car.subaru.values import CAR, SubaruFlags


class TestSubaruInterface(unittest.TestCase):
  def setUp(self):
    self.params = Params()
    self.params.remove("MCSubaruActuatorDelayTest")

  def tearDown(self):
    self.params.remove("MCSubaruActuatorDelayTest")

  @staticmethod
  def _make_carstate(*, preglobal: bool = False, enabled: bool = False, threshold: int = 80) -> CarState:
    carstate = CarState.__new__(CarState)
    carstate.CP = SimpleNamespace(flags=SubaruFlags.PREGLOBAL if preglobal else 0)
    carstate.steering_pressed_cnt = 0
    carstate.mc_subaru_manual_yield_torque_threshold_enabled = enabled
    carstate.mc_subaru_manual_yield_torque_threshold = threshold
    return carstate

  @staticmethod
  def _simulate_pressed(carstate: CarState, torque: int, samples: int) -> bool:
    pressed = False
    for _ in range(samples):
      pressed = carstate.update_steering_pressed(abs(torque) > carstate._get_active_manual_yield_torque_threshold(), 5)
    return pressed

  def test_subaru_delay_toggle_off_keeps_angle_delay_default(self):
    CP = CarInterface.get_non_essential_params(CAR.SUBARU_OUTBACK_2023)

    self.assertTrue(bool(CP.flags & SubaruFlags.LKAS_ANGLE))
    self.assertAlmostEqual(CP.steerActuatorDelay, 0.1)

  def test_subaru_delay_toggle_is_legacy_and_no_longer_changes_angle_delay(self):
    self.params.put_bool("MCSubaruActuatorDelayTest", True)

    CP = CarInterface.get_non_essential_params(CAR.SUBARU_OUTBACK_2023)

    self.assertTrue(bool(CP.flags & SubaruFlags.LKAS_ANGLE))
    self.assertAlmostEqual(CP.steerActuatorDelay, 0.1)

  def test_subaru_delay_toggle_does_not_change_torque_subaru(self):
    self.params.put_bool("MCSubaruActuatorDelayTest", True)

    CP = CarInterface.get_non_essential_params(CAR.SUBARU_FORESTER)

    self.assertFalse(bool(CP.flags & SubaruFlags.LKAS_ANGLE))
    self.assertNotAlmostEqual(CP.steerActuatorDelay, 0.08)

  def test_manual_yield_torque_threshold_toggle_off_uses_stock_platform_thresholds(self):
    modern = self._make_carstate()
    preglobal = self._make_carstate(preglobal=True)

    self.assertEqual(modern._get_active_manual_yield_torque_threshold(), 80)
    self.assertEqual(preglobal._get_active_manual_yield_torque_threshold(), 75)

  def test_manual_yield_torque_threshold_toggle_on_uses_selected_threshold(self):
    carstate = self._make_carstate(enabled=True, threshold=40)

    self.assertEqual(carstate._get_active_manual_yield_torque_threshold(), 40)

  def test_manual_yield_torque_threshold_is_clamped_to_supported_range(self):
    self.assertEqual(CarState._clamp_manual_yield_torque_threshold(9), 10)
    self.assertEqual(CarState._clamp_manual_yield_torque_threshold(18), 20)
    self.assertEqual(CarState._clamp_manual_yield_torque_threshold(81), 80)

  def test_manual_yield_torque_threshold_lower_values_trigger_pressed_sooner(self):
    stock_carstate = self._make_carstate()
    tuned_carstate = self._make_carstate(enabled=True, threshold=20)

    self.assertFalse(self._simulate_pressed(stock_carstate, torque=40, samples=6))
    self.assertTrue(self._simulate_pressed(tuned_carstate, torque=40, samples=6))

  def test_manual_yield_torque_threshold_keeps_existing_debounce_count(self):
    tuned_carstate = self._make_carstate(enabled=True, threshold=20)

    self.assertFalse(self._simulate_pressed(tuned_carstate, torque=40, samples=5))
    tuned_carstate = self._make_carstate(enabled=True, threshold=20)
    self.assertTrue(self._simulate_pressed(tuned_carstate, torque=40, samples=6))


if __name__ == "__main__":
  unittest.main()
