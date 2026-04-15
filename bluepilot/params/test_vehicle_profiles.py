import base64
from types import SimpleNamespace

from openpilot.common.params import Params

from bluepilot.params.vehicle_profiles import (
  ACTIVE_PARAM,
  READY_PARAM,
  STATUS_PARAM,
  STORE_PARAM,
  apply_vehicle_profile,
)


def make_params(tmp_path):
  params = Params(str(tmp_path / "params"))
  params.clear_all()
  return params


def car(fingerprint: str):
  return SimpleNamespace(carFingerprint=fingerprint)


def bundle(ref: str):
  return {
    "index": 1,
    "internalName": ref,
    "displayName": ref,
    "models": [],
    "status": 2,
    "generation": 10,
    "environment": "",
    "runner": 1,
    "is20hz": False,
    "ref": ref,
    "minimumSelectorVersion": 14,
    "overrides": [],
  }


def missing_file_bundle(ref: str):
  data = bundle(ref)
  data["models"] = [{
    "type": 0,
    "artifact": {"fileName": "does-not-exist.onnx", "downloadUri": {}, "downloadProgress": {}},
    "metadata": {"fileName": "does-not-exist.pkl", "downloadUri": {}, "downloadProgress": {}},
  }]
  return data


def get_profile_settings(params: Params, fingerprint: str):
  return params.get(STORE_PARAM)["profiles"][fingerprint]["settings"]


def test_first_fingerprint_seeds_profile_without_changing_params(tmp_path):
  params = make_params(tmp_path)
  params.put_bool("IsMetric", True)

  status = apply_vehicle_profile(car("FORD_A"), params)

  assert status["action"] == "seeded"
  assert params.get(ACTIVE_PARAM) == "FORD_A"
  assert params.get_bool(READY_PARAM)
  assert params.get_bool("IsMetric")
  assert get_profile_settings(params, "FORD_A")["IsMetric"] == {"kind": "value", "value": True}


def test_same_fingerprint_snapshots_current_settings(tmp_path):
  params = make_params(tmp_path)
  apply_vehicle_profile(car("FORD_A"), params)

  params.put_bool("IsMetric", True)
  status = apply_vehicle_profile(car("FORD_A"), params)

  assert status["action"] == "saved"
  assert get_profile_settings(params, "FORD_A")["IsMetric"] == {"kind": "value", "value": True}


def test_switching_profiles_restores_settings_and_clears_model_runner_cache(tmp_path):
  params = make_params(tmp_path)
  params.put_bool("IsMetric", True)
  apply_vehicle_profile(car("FORD_A"), params)

  store = params.get(STORE_PARAM)
  store["profiles"]["FORD_B"] = {
    "fingerprint": "FORD_B",
    "updatedAt": 0,
    "settings": {
      "IsMetric": {"kind": "value", "value": False},
      "ModelManager_ActiveBundle": {"kind": "value", "value": bundle("model-b")},
    },
  }
  params.put(STORE_PARAM, store)
  params.put("ModelRunnerTypeCache", 1)

  status = apply_vehicle_profile(car("FORD_B"), params)

  assert status["action"] == "restored"
  assert status["modelChanged"]
  assert not params.get_bool("IsMetric")
  assert params.get("ModelManager_ActiveBundle")["ref"] == "model-b"
  assert params.get("ModelRunnerTypeCache") is None


def test_missing_model_bundle_falls_back_to_default_model(tmp_path):
  params = make_params(tmp_path)
  params.put("ModelManager_ActiveBundle", bundle("model-a"))
  apply_vehicle_profile(car("FORD_A"), params)

  store = params.get(STORE_PARAM)
  store["profiles"]["FORD_B"] = {
    "fingerprint": "FORD_B",
    "updatedAt": 0,
    "settings": {
      "ModelManager_ActiveBundle": {"kind": "value", "value": missing_file_bundle("model-b")},
    },
  }
  params.put(STORE_PARAM, store)
  params.put("ModelRunnerTypeCache", 1)

  status = apply_vehicle_profile(car("FORD_B"), params)

  assert status["modelFallback"]
  assert status["modelFallbackReason"] == "missing_model_files"
  assert params.get("ModelManager_ActiveBundle") is None
  assert params.get("ModelRunnerTypeCache") is None


def test_excluded_keys_are_not_stored(tmp_path):
  params = make_params(tmp_path)
  params.put("WifiFavoriteSSID", "garage")
  params.put("SecOCKey", "00" * 16)
  params.put("CarPlatformBundle", {"platform": "FORD_A"})
  params.put("ModelManager_ModelsCache", {"cached": True})

  apply_vehicle_profile(car("FORD_A"), params)

  settings = get_profile_settings(params, "FORD_A")
  assert "WifiFavoriteSSID" not in settings
  assert "SecOCKey" not in settings
  assert "CarPlatformBundle" not in settings
  assert "ModelManager_ModelsCache" not in settings


def test_bytes_values_round_trip(tmp_path):
  params = make_params(tmp_path)
  params.put("LiveTorqueParameters", b"torque-a")
  apply_vehicle_profile(car("FORD_A"), params)

  store = params.get(STORE_PARAM)
  store["profiles"]["FORD_B"] = {
    "fingerprint": "FORD_B",
    "updatedAt": 0,
    "settings": {
      "LiveTorqueParameters": {
        "kind": "bytes",
        "value": base64.b64encode(b"torque-b").decode("ascii"),
      },
    },
  }
  params.put(STORE_PARAM, store)

  apply_vehicle_profile(car("FORD_B"), params)

  assert params.get("LiveTorqueParameters") == b"torque-b"


def test_alpha_long_change_requests_onroad_cycle_and_defers_ready(tmp_path):
  params = make_params(tmp_path)
  params.put_bool("AlphaLongitudinalEnabled", False)
  apply_vehicle_profile(car("FORD_A"), params)

  store = params.get(STORE_PARAM)
  store["profiles"]["FORD_B"] = {
    "fingerprint": "FORD_B",
    "updatedAt": 0,
    "settings": {
      "AlphaLongitudinalEnabled": {"kind": "value", "value": True},
    },
  }
  params.put(STORE_PARAM, store)

  status = apply_vehicle_profile(car("FORD_B"), params)

  assert status["restartRequired"]
  assert not params.get_bool(READY_PARAM)
  assert params.get_bool("OnroadCycleRequested")
  assert params.get_bool("AlphaLongitudinalEnabled")
  assert params.get(STATUS_PARAM)["restartRequired"]
