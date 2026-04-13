"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.swaglog import cloudlog

ONROAD_BRIGHTNESS_MIGRATION_VERSION: str = "1.0"
SUBARU_11_BLUEPILOT_TUNING_MIGRATION_VERSION: str = "subi-1.0-bluepilot-tuning-preserve"
SUBARU_MANUAL_YIELD_TORQUE_FLOOR_MIGRATION_VERSION: str = "subi-1.0-torque-floor-40"


def run_migration(_params):
  # migrate OnroadScreenOffBrightness
  if _params.get("OnroadScreenOffBrightnessMigrated") != ONROAD_BRIGHTNESS_MIGRATION_VERSION:
    try:
      val = _params.get("OnroadScreenOffBrightness")
      if val >= 2:  # old: 5%, new: Screen Off
        new_val = val + 1
        _params.put("OnroadScreenOffBrightness", new_val)
        log_str = f"Successfully migrated OnroadScreenOffBrightness from {val} to {new_val}."
      else:
        log_str = "Migration not required for OnroadScreenOffBrightness."

      _params.put("OnroadScreenOffBrightnessMigrated", ONROAD_BRIGHTNESS_MIGRATION_VERSION)
      cloudlog.info(log_str + f" Setting OnroadScreenOffBrightnessMigrated to {ONROAD_BRIGHTNESS_MIGRATION_VERSION}")
    except Exception as e:
      cloudlog.exception(f"Error migrating OnroadScreenOffBrightness: {e}")

  # Seed the current personal-build Subaru tuning defaults without overwriting saved test choices.
  if _params.get("Subaru11BluePilotTuningMigrated") != SUBARU_11_BLUEPILOT_TUNING_MIGRATION_VERSION:
    try:
      seeded_keys = []
      bool_defaults = {
        "MCSubaruManualYieldTorqueThresholdEnabled": False,
        "MCSubaruManualYieldResumeSoftnessEnabled": False,
        "MCSubaruManualYieldReleaseGuardEnabled": False,
        "MCSubaruSoftCaptureEnabled": False,
      }
      value_defaults = {
        "MCSubaruManualYieldTorqueThreshold": "80",
        "MCSubaruManualYieldResumeSoftness": "4",
        "MCSubaruManualYieldReleaseGuardLevel": "2",
        "MCSubaruSoftCaptureLevel": "3",
      }

      for key, default in bool_defaults.items():
        if _params.get(key) is None:
          _params.put_bool(key, default)
          seeded_keys.append(key)

      for key, default in value_defaults.items():
        if _params.get(key) is None:
          _params.put(key, default)
          seeded_keys.append(key)

      _params.put("Subaru11BluePilotTuningMigrated", SUBARU_11_BLUEPILOT_TUNING_MIGRATION_VERSION)
      cloudlog.info(
        "Successfully preserved existing Subaru tuning and seeded missing BluePilot defaults "
        + f"for {seeded_keys}. "
        + f"Setting Subaru11BluePilotTuningMigrated to {SUBARU_11_BLUEPILOT_TUNING_MIGRATION_VERSION}"
      )
    except Exception as e:
      cloudlog.exception(f"Error migrating Subaru BluePilot tuning defaults: {e}")

  # Clamp old test values below the current safe manual-yield torque floor without touching other settings.
  if _params.get("SubaruManualYieldTorqueFloorMigrated") != SUBARU_MANUAL_YIELD_TORQUE_FLOOR_MIGRATION_VERSION:
    try:
      val = _params.get("MCSubaruManualYieldTorqueThreshold", return_default=True)
      try:
        threshold = int(val)
      except (TypeError, ValueError):
        threshold = 80

      if threshold < 40:
        _params.put("MCSubaruManualYieldTorqueThreshold", "40")
        log_str = f"Successfully clamped MCSubaruManualYieldTorqueThreshold from {threshold} to 40."
      else:
        log_str = "Migration not required for MCSubaruManualYieldTorqueThreshold floor."

      _params.put("SubaruManualYieldTorqueFloorMigrated", SUBARU_MANUAL_YIELD_TORQUE_FLOOR_MIGRATION_VERSION)
      cloudlog.info(log_str + f" Setting SubaruManualYieldTorqueFloorMigrated to {SUBARU_MANUAL_YIELD_TORQUE_FLOOR_MIGRATION_VERSION}")
    except Exception as e:
      cloudlog.exception(f"Error migrating Subaru manual-yield torque floor: {e}")
