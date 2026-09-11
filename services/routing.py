"""Routing and travel time calculation service using OSRM with Haversine fallback."""
import math
from typing import List, Tuple, Dict, Any
import requests
from utils.caching import routing_cache

OSRM_TABLE_URL = "http://router.project-osrm.org/table/v1/driving"
AVG_CITY_SPEED_KMH = 30.0  # Used for fallback travel-time approximation


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two geographic coordinates in kilometers."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    )
    return 2.0 * r * math.asin(math.sqrt(max(0.0, min(1.0, a))))


def get_travel_times(
    origins: List[Tuple[float, float]],
    destinations: List[Tuple[float, float]],
    timeout_sec: float = 8.0,
) -> Tuple[List[List[float]], List[List[float]], bool, str]:
    """
    Computes travel times (in minutes) and distances (in km) from each origin to each destination.
    Uses OSRM Table API. If OSRM fails or times out, falls back to Haversine approximation.

    Returns:
        (durations_matrix_minutes, distances_matrix_km, is_fallback, routing_info)
    """
    n_orig = len(origins)
    n_dest = len(destinations)

    # Check cache first
    cache_key = f"osrm_matrix:{origins}_{destinations}"
    cached = routing_cache.get(cache_key)
    if cached:
        return cached

    # Attempt live OSRM Table request
    try:
        all_coords = []
        # Origins come first (indices 0 .. n_orig-1)
        for lat, lon in origins:
            all_coords.append(f"{lon:.6f},{lat:.6f}")
        # Destinations come second (indices n_orig .. n_orig+n_dest-1)
        for lat, lon in destinations:
            all_coords.append(f"{lon:.6f},{lat:.6f}")

        coords_str = ";".join(all_coords)
        sources_str = ";".join(str(i) for i in range(n_orig))
        destinations_str = ";".join(str(n_orig + j) for j in range(n_dest))

        url = f"{OSRM_TABLE_URL}/{coords_str}?sources={sources_str}&destinations={destinations_str}&annotations=duration,distance"
        resp = requests.get(url, timeout=timeout_sec)

        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == "Ok" and "durations" in data:
                raw_durations = data["durations"]
                raw_distances = data.get("distances", [])

                durations_min = []
                distances_km = []

                for i in range(n_orig):
                    row_dur = []
                    row_dist = []
                    for j in range(n_dest):
                        sec = raw_durations[i][j]
                        dist_m = raw_distances[i][j] if raw_distances else 0.0

                        if sec is None or sec < 0:
                            # Local fallback for unreachable node
                            orig_lat, orig_lon = origins[i]
                            dest_lat, dest_lon = destinations[j]
                            km = haversine_distance_km(orig_lat, orig_lon, dest_lat, dest_lon)
                            minutes = (km / AVG_CITY_SPEED_KMH) * 60.0
                        else:
                            minutes = sec / 60.0

                        if dist_m is None or dist_m < 0:
                            orig_lat, orig_lon = origins[i]
                            dest_lat, dest_lon = destinations[j]
                            km = haversine_distance_km(orig_lat, orig_lon, dest_lat, dest_lon)
                        else:
                            km = dist_m / 1000.0

                        row_dur.append(round(minutes, 2))
                        row_dist.append(round(km, 2))

                    durations_min.append(row_dur)
                    distances_km.append(row_dist)

                result = (durations_min, distances_km, False, "OSRM Live Routing (Driving)")
                routing_cache.set(cache_key, result)
                return result

    except Exception as exc:
        print(f"[Routing Service] OSRM call failed, switching to Haversine fallback: {exc}")

    # Fallback to Haversine
    durations_min = []
    distances_km = []
    for orig_lat, orig_lon in origins:
        row_dur = []
        row_dist = []
        for dest_lat, dest_lon in destinations:
            km = haversine_distance_km(orig_lat, orig_lon, dest_lat, dest_lon)
            # City drive time approximation: 30 km/h average with slight urban winding factor (1.25x)
            effective_km = km * 1.25
            minutes = (effective_km / AVG_CITY_SPEED_KMH) * 60.0
            row_dur.append(round(minutes, 2))
            row_dist.append(round(km, 2))
        durations_min.append(row_dur)
        distances_km.append(row_dist)

    result = (
        durations_min,
        distances_km,
        True,
        "Haversine Geometric Fallback (OSRM service temporarily unavailable)",
    )
    routing_cache.set(cache_key, result, ttl=300)
    return result
