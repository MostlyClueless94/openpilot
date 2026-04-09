def is_subaru_platform(cp) -> bool:
  car_name = getattr(cp, "carName", "") or ""
  if isinstance(car_name, bytes):
    car_name = car_name.decode("utf-8", errors="ignore")
  return str(car_name).lower() == "subaru"


def get_display_speed_ms(cp, match_vehicle_speedometer: bool, v_ego: float, v_ego_cluster: float,
                         v_ego_cluster_seen: bool, default_speed_ms: float) -> float:
  if not is_subaru_platform(cp):
    return default_speed_ms

  if match_vehicle_speedometer:
    return v_ego_cluster if v_ego_cluster_seen else v_ego

  return v_ego
