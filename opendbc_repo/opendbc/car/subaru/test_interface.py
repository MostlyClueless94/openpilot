import unittest
from types import SimpleNamespace

from openpilot.common.params import Params
from opendbc.car.subaru.carstate import CarState, MANUAL_YIELD_FILTERED_DETECTION_FRAMES
from opendbc.car.subaru.interface import CarInterface
from opendbc.car.subaru.values import CAR, SubaruFlags


class TestSubaruInterface(unittest.TestCase):
  def setUp(self):
    self.params = Params()
    self.params.remove("MCSubaruActuatorDelayTest")

  def tearDown(self):
    self.params.remove("MCSubaruActuatorDelayTest")

  @staticmethod
  def _make_carstate(*, preglobal: bool = False, enabled: bool = False,
                     filtered: bool = False, threshold: int = 80) -> CarState:
    carstate = CarState.__new__(CarState)
    carstate.CP = SimpleNamespace(flags=SubaruFlags.PREGLOBAL if preglobal else 0)
    carstate.steering_pressed_cnt = 0
    carstate.mc_subaru_manual_yield_torque_threshold_enabled = enabled
    carstate.mc_subaru_manual_yield_torque_threshold = threshold
    carstate.mc_subaru_manual_yield_filtered_detection_enabled = filtered
    return carstate

  @staticmethod
  def _simulate_pressed(carstate: CarState, torque: int, samples: int) -> bool:
    pressed = False
    for _ in range(samples):
      pressed = carstate._get_manual_yield_steering_pressed(torque)
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
    self.assertEqual(CarState._clamp_manual_yield_torque_threshold(9), 40)
    self.assertEqual(CarState._clamp_manual_yield_torque_threshold(38), 40)
    self.assertEqual(CarState._clamp_manual_yield_torque_threshold(81), 80)
    self.assertEqual(CarState._clamp_manual_yield_torque_threshold(175), 150)
    self.assertEqual(CarState._clamp_manual_yield_torque_threshold(501), 500)

  def test_manual_yield_direct_detection_toggle_off_uses_single_sample_behavior(self):
    carstate = self._make_carstate(enabled=True, threshold=40)

    self.assertFalse(carstate._get_manual_yield_steering_pressed(40))
    self.assertTrue(carstate._get_manual_yield_steering_pressed(41))
    self.assertFalse(carstate._get_manual_yield_steering_pressed(39))

  def test_manual_yield_torque_threshold_lower_values_trigger_pressed_sooner_when_direct(self):
    stock_carstate = self._make_carstate()
    tuned_carstate = self._make_carstate(enabled=True, threshold=40)

    self.assertFalse(stock_carstate._get_manual_yield_steering_pressed(40))
    self.assertTrue(tuned_carstate._get_manual_yield_steering_pressed(41))

  def test_filtered_manual_yield_detection_does_not_latch_from_single_sample(self):
    carstate = self._make_carstate(enabled=True, filtered=True, threshold=40)

    self.assertFalse(carstate._get_manual_yield_steering_pressed(41))

  def test_filtered_manual_yield_detection_latches_after_sustained_samples(self):
    carstate = self._make_carstate(enabled=True, filtered=True, threshold=40)

    self.assertFalse(self._simulate_pressed(carstate, torque=41, samples=MANUAL_YIELD_FILTERED_DETECTION_FRAMES))
    carstate = self._make_carstate(enabled=True, filtered=True, threshold=40)
    self.assertTrue(self._simulate_pressed(carstate, torque=41, samples=MANUAL_YIELD_FILTERED_DETECTION_FRAMES + 1))

  def test_filtered_manual_yield_detection_survives_brief_dropout_after_latch(self):
    carstate = self._make_carstate(enabled=True, filtered=True, threshold=40)

    self.assertTrue(self._simulate_pressed(carstate, torque=41, samples=MANUAL_YIELD_FILTERED_DETECTION_FRAMES * 2 + 1))
    self.assertTrue(carstate._get_manual_yield_steering_pressed(0))

  def test_filtered_manual_yield_detection_still_uses_selected_threshold(self):
    high_threshold = self._make_carstate(enabled=True, filtered=True, threshold=100)
    low_threshold = self._make_carstate(enabled=True, filtered=True, threshold=40)

    self.assertFalse(self._simulate_pressed(high_threshold, torque=80, samples=MANUAL_YIELD_FILTERED_DETECTION_FRAMES + 1))
    self.assertTrue(self._simulate_pressed(low_threshold, torque=80, samples=MANUAL_YIELD_FILTERED_DETECTION_FRAMES + 1))

  def test_filtered_manual_yield_detection_still_uses_stock_threshold_when_custom_off(self):
    modern = self._make_carstate(filtered=True)
    preglobal = self._make_carstate(preglobal=True, filtered=True)

    self.assertTrue(self._simulate_pressed(modern, torque=81, samples=MANUAL_YIELD_FILTERED_DETECTION_FRAMES + 1))
    self.assertFalse(self._simulate_pressed(preglobal, torque=75, samples=MANUAL_YIELD_FILTERED_DETECTION_FRAMES + 1))


if __name__ == "__main__":
  unittest.main()
