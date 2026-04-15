"""Vehicle-specific profile storage and restore for BluePilot."""

from __future__ import annotations

import base64
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from openpilot.common.params import Params, ParamKeyFlag, ParamKeyType, UnknownKeyName
from openpilot.common.swaglog import cloudlog
from openpilot.system.hardware.hw import Paths
from openpilot.sunnypilot.models.helpers import is_bundle_version_compatible


PROFILE_SCHEMA_VERSION = 1

STORE_PARAM = "BPVehicleProfiles"
ACTIVE_PARAM = "BPVehicleProfileActive"
STATUS_PARAM = "BPVehicleProfileStatus"
READY_PARAM = "BPVehicleProfileReady"

MODEL_BUNDLE_PARAM = "ModelManager_ActiveBundle"
MODEL_RUNNER_CACHE_PARAM = "ModelRunnerTypeCache"
ALPHA_LONG_PARAM = "AlphaLongitudinalEnabled"

_PROFILE_INTERNAL_KEYS = {
  STORE_PARAM,
  ACTIVE_PARAM,
  STATUS_PARAM,
  READY_PARAM,
}

_EXPLICIT_PROFILE_KEYS = {
  MODEL_BUNDLE_PARAM,
  "LagdValueCache",
  "LiveDelay",
  "LiveTorqueParameters",
}

_ALLOWED_PROFILE_TYPES = {
  ParamKeyType.STRING,
  ParamKeyType.BOOL,
  ParamKeyType.INT,
  ParamKeyType.FLOAT,
  ParamKeyType.JSON,
}

_EXCLUDED_EXACT_KEYS = {
  "AccessToken",
  "AssistNowToken",
  "AthenadUploadQueue",
  "AthenadRecentlyViewedRoutes",
  "CalibrationParams",
  "CarPlatformBundle",
  "CompletedSunnylinkConsentVersion",
  "ControlsReady",
  "CurrentRoute",
  "DisableLogging",
  "DongleId",
  "EnableCopyparty",
  "EnableGithubRunner",
  "EnableWebRoutesServer",
  "EnableSunnylinkUploader",
  "FirmwareQueryDone",
  "GithubSshKeys",
  "GithubUsername",
  "GsmApn",
  "GsmMetered",
  "GsmRoaming",
  "HardwareSerial",
  "LastGPSPosition",
  "LastGPSPositionLLK",
  "LiveParameters",
  "LiveParametersV2",
  "LocationFilterInitialState",
  "ModelManager_ClearCache",
  "ModelManager_DownloadIndex",
  "ModelManager_LastSyncTime",
  "ModelManager_ModelsCache",
  MODEL_RUNNER_CACHE_PARAM,
  "NetworkMetered",
  "RecordFrontLock",
  "SecOCKey",
  "SunnylinkDongleId",
  "WifiFavoriteSSID",
}

_EXCLUDED_PREFIXES = (
  "ApiCache_",
  "Athenad",
  "BackupManager_",
  "BPPortal",
  "BPVehicleProfile",
  "CarParams",
  "Current",
  "Git",
  "Github",
  "Gsm",
  "Last",
  "Offroad_",
  "OSMDownload",
  "OsmDownloaded",
  "OsmDb",
  "OsmLocation",
  "OsmState",
  "Route",
  "Sunnylink",
  "Update",
  "Updater",
  "Wifi",
)

_EXCLUDED_SUBSTRINGS = (
  "Cache",
  "Dongle",
  "Pid",
  "Token",
)


def _decode_key(key: str | bytes) -> str:
  return key.decode("utf-8") if isinstance(key, bytes) else key


def _get_store(params: Params) -> dict[str, Any]:
  try:
    store = params.get(STORE_PARAM)
  except UnknownKeyName:
    return {"version": PROFILE_SCHEMA_VERSION, "profiles": {}}

  if not isinstance(store, dict):
    return {"version": PROFILE_SCHEMA_VERSION, "profiles": {}}

  store.setdefault("version", PROFILE_SCHEMA_VERSION)
  profiles = store.setdefault("profiles", {})
  if not isinstance(profiles, dict):
    store["profiles"] = {}
  return store


def _put_store(params: Params, store: dict[str, Any]) -> None:
  store["version"] = PROFILE_SCHEMA_VERSION
  store.setdefault("profiles", {})
  params.put(STORE_PARAM, store)


def _put_status(params: Params, **status: Any) -> dict[str, Any]:
  status.setdefault("updatedAt", int(time.time()))
  try:
    params.put(STATUS_PARAM, status)
  except UnknownKeyName:
    pass
  return status


def _set_ready(params: Params, ready: bool) -> None:
  try:
    params.put_bool(READY_PARAM, ready)
  except UnknownKeyName:
    pass


def _normalize_fingerprint(fingerprint: Any) -> str:
  if fingerprint is None:
    return ""
  if isinstance(fingerprint, bytes):
    fingerprint = fingerprint.decode("utf-8", errors="replace")
  return str(fingerprint).strip()


def _valid_fingerprint(fingerprint: Any) -> bool:
  fingerprint = _normalize_fingerprint(fingerprint)
  return bool(fingerprint and fingerprint.lower() not in ("mock", "unknown", "notcar"))


def _profile_key_allowed(params: Params, key: str) -> bool:
  if key in _PROFILE_INTERNAL_KEYS or key in _EXCLUDED_EXACT_KEYS:
    return False

  try:
    key_type = params.get_type(key)
  except UnknownKeyName:
    return False

  if key in _EXPLICIT_PROFILE_KEYS:
    return True
  if key.startswith(_EXCLUDED_PREFIXES):
    return False
  if any(part in key for part in _EXCLUDED_SUBSTRINGS):
    return False
  return key_type in _ALLOWED_PROFILE_TYPES


def profile_keys(params: Params) -> list[str]:
  """Return the current list of params that should be stored per vehicle."""
  keys = {_decode_key(k) for k in params.all_keys(ParamKeyFlag.BACKUP)}
  keys.update(_EXPLICIT_PROFILE_KEYS)
  return sorted(key for key in keys if _profile_key_allowed(params, key))


def _encode_value(value: Any) -> dict[str, Any]:
  if value is None:
    return {"kind": "missing"}
  if isinstance(value, bytes):
    return {"kind": "bytes", "value": base64.b64encode(value).decode("ascii")}
  return {"kind": "value", "value": value}


def _decode_value(record: dict[str, Any]) -> Any:
  if not isinstance(record, dict) or record.get("kind") == "missing":
    return None
  if record.get("kind") == "bytes":
    return base64.b64decode(record.get("value", ""))
  return record.get("value")


def _snapshot_settings(params: Params) -> dict[str, dict[str, Any]]:
  settings: dict[str, dict[str, Any]] = {}
  for key in profile_keys(params):
    try:
      settings[key] = _encode_value(params.get(key))
    except UnknownKeyName:
      continue
  return settings


def _bundle_model_files(bundle: dict[str, Any]) -> list[str]:
  files: list[str] = []
  for model in bundle.get("models", []) or []:
    for artifact_key in ("artifact", "metadata"):
      artifact = model.get(artifact_key, {}) if isinstance(model, dict) else {}
      filename = artifact.get("fileName")
      if filename:
        files.append(filename)
  return files


def _bundle_is_available(bundle: Any) -> tuple[bool, str]:
  if not isinstance(bundle, dict):
    return False, "invalid_bundle"
  if not bundle:
    return False, "missing_bundle"
  if not is_bundle_version_compatible(bundle):
    return False, "incompatible_bundle"

  model_root = Path(Paths.model_root())
  missing_files = [filename for filename in _bundle_model_files(bundle) if not (model_root / filename).exists()]
  if missing_files:
    return False, "missing_model_files"
  return True, "ok"


def _current_value(params: Params, key: str) -> Any:
  try:
    return params.get(key)
  except UnknownKeyName:
    return None


def _write_value(params: Params, key: str, value: Any) -> None:
  if value is None:
    params.remove(key)
  else:
    params.put(key, value)


def _restore_settings(params: Params, settings: dict[str, dict[str, Any]]) -> dict[str, Any]:
  changed = 0
  model_changed = False
  model_fallback = False
  model_fallback_reason = ""
  restart_required = False

  for key, record in settings.items():
    if not _profile_key_allowed(params, key):
      continue

    target_value = _decode_value(record)
    current_value = _current_value(params, key)

    if key == MODEL_BUNDLE_PARAM and target_value is not None:
      valid_bundle, reason = _bundle_is_available(target_value)
      if not valid_bundle:
        target_value = None
        model_fallback = True
        model_fallback_reason = reason

    if current_value == target_value:
      continue

    _write_value(params, key, target_value)
    changed += 1

    if key == MODEL_BUNDLE_PARAM:
      model_changed = True
    elif key == ALPHA_LONG_PARAM:
      restart_required = True

  if model_changed or model_fallback:
    params.remove(MODEL_RUNNER_CACHE_PARAM)

  if restart_required:
    params.put_bool("OnroadCycleRequested", True)

  return {
    "changed": changed,
    "modelChanged": model_changed,
    "modelFallback": model_fallback,
    "modelFallbackReason": model_fallback_reason,
    "restartRequired": restart_required,
  }


def snapshot_active_profile(params: Params) -> dict[str, Any]:
  """Persist current settings into the currently active vehicle profile."""
  active_fingerprint = _normalize_fingerprint(params.get(ACTIVE_PARAM))
  if not _valid_fingerprint(active_fingerprint):
    return _put_status(params, action="skipped", ready=True, message="No active vehicle profile")

  store = _get_store(params)
  profiles = store.setdefault("profiles", {})
  profiles[active_fingerprint] = {
    "fingerprint": active_fingerprint,
    "updatedAt": int(time.time()),
    "settings": _snapshot_settings(params),
  }
  _put_store(params, store)

  status = _put_status(
    params,
    active=active_fingerprint,
    action="saved",
    ready=True,
    message=f"Saved profile for {active_fingerprint}",
  )
  _set_ready(params, True)
  return status


def reset_active_profile(params: Params) -> dict[str, Any]:
  """Remove the currently active vehicle profile so it will be re-seeded."""
  active_fingerprint = _normalize_fingerprint(params.get(ACTIVE_PARAM))
  if not _valid_fingerprint(active_fingerprint):
    return _put_status(params, action="skipped", ready=True, message="No active vehicle profile")

  store = _get_store(params)
  profiles = store.setdefault("profiles", {})
  profiles.pop(active_fingerprint, None)
  _put_store(params, store)

  status = _put_status(
    params,
    active=active_fingerprint,
    action="reset",
    ready=True,
    message=f"Reset profile for {active_fingerprint}",
  )
  _set_ready(params, True)
  return status


def apply_vehicle_profile(CP: SimpleNamespace, params: Params) -> dict[str, Any]:
  """Apply or seed the vehicle profile for the detected car fingerprint."""
  fingerprint = _normalize_fingerprint(getattr(CP, "carFingerprint", None))
  if not _valid_fingerprint(fingerprint):
    status = _put_status(params, action="skipped", ready=True, message="No valid car fingerprint")
    _set_ready(params, True)
    return status

  active_fingerprint = _normalize_fingerprint(params.get(ACTIVE_PARAM))
  store = _get_store(params)
  profiles = store.setdefault("profiles", {})

  if _valid_fingerprint(active_fingerprint) and active_fingerprint != fingerprint:
    snapshot_active_profile(params)
    store = _get_store(params)
    profiles = store.setdefault("profiles", {})

  if fingerprint not in profiles:
    params.put(ACTIVE_PARAM, fingerprint)
    profiles[fingerprint] = {
      "fingerprint": fingerprint,
      "updatedAt": int(time.time()),
      "settings": _snapshot_settings(params),
    }
    _put_store(params, store)
    status = _put_status(
      params,
      active=fingerprint,
      action="seeded",
      ready=True,
      message=f"Created profile for {fingerprint}",
    )
    _set_ready(params, True)
    cloudlog.info("BluePilot: seeded vehicle profile for %s", fingerprint)
    return status

  if active_fingerprint == fingerprint:
    params.put(ACTIVE_PARAM, fingerprint)
    return snapshot_active_profile(params)

  restore_result = _restore_settings(params, profiles[fingerprint].get("settings", {}))
  params.put(ACTIVE_PARAM, fingerprint)

  ready = not restore_result["restartRequired"]
  status = _put_status(
    params,
    active=fingerprint,
    action="restored",
    ready=ready,
    changed=restore_result["changed"],
    modelChanged=restore_result["modelChanged"],
    modelFallback=restore_result["modelFallback"],
    modelFallbackReason=restore_result["modelFallbackReason"],
    restartRequired=restore_result["restartRequired"],
    message=f"Restored profile for {fingerprint}",
  )
  _set_ready(params, ready)
  cloudlog.info("BluePilot: restored vehicle profile for %s: %s", fingerprint, status)
  return status
