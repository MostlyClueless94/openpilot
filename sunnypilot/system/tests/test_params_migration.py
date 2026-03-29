import unittest

from openpilot.common.params import Params
from openpilot.sunnypilot.system.params_migration import (
  LANEFULL_MODE_RESET_MIGRATION_VERSION,
  run_migration,
)


class TestParamsMigration(unittest.TestCase):
  def setUp(self):
    self.params = Params()
    for key in ("enable_lane_full_mode", "LanefullModeResetMigrated", "custom_profile"):
      self.params.remove(key)

  def tearDown(self):
    for key in ("enable_lane_full_mode", "LanefullModeResetMigrated", "custom_profile"):
      self.params.remove(key)

  def test_lanefull_mode_is_reset_once(self):
    self.params.put_bool("enable_lane_full_mode", True)
    self.params.put_bool("custom_profile", True)

    run_migration(self.params)

    self.assertFalse(self.params.get_bool("enable_lane_full_mode"))
    self.assertEqual(self.params.get("LanefullModeResetMigrated"), LANEFULL_MODE_RESET_MIGRATION_VERSION)
    self.assertTrue(self.params.get_bool("custom_profile"))

    self.params.put_bool("enable_lane_full_mode", True)
    run_migration(self.params)

    self.assertTrue(self.params.get_bool("enable_lane_full_mode"))
