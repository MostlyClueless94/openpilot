import json
import os

from openpilot.common.basedir import BASEDIR
from openpilot.common.swaglog import cloudlog

CAR_LIST_JSON_OUT = os.path.join(BASEDIR, "sunnypilot", "selfdrive", "car", "car_list.json")


def get_runtime_car_list() -> dict:
  try:
    from opendbc.sunnypilot.car.platform_list import get_car_list
    return get_car_list()
  except Exception as e:
    cloudlog.warning(f"Falling back to static car list: {e}")
    with open(CAR_LIST_JSON_OUT) as f:
      return json.load(f)
