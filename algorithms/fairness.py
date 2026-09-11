"""
MeetSpot Fairness Optimization Engine.

Calculates a fair meeting point by evaluating real-world driving travel times
from all participants to candidate points generated around their geographic centroid,
optimizing for minimal travel-time disparity (gap = max - min).
"""
import math
from typing import List, Dict, Any, Tuple
from services.routing import get_travel_times, haversine_distance_km
from services.geocoding import reverse_geocode


def compute_centroid(coords: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Computes the geographic centroid (mean latitude and longitude)."""
    if not coords:
        raise ValueError("Cannot calculate centroid of empty coordinates list.")
    mean_lat = sum(c[0] for c in coords) / len(coords)
    mean_lon = sum(c[1] for c in coords) / len(coords)
    return mean_lat, mean_lon


def generate_candidate_points(
    participants_latlon: List[Tuple[float, float]],
    rings: int = 2,
    points_per_ring: int = 8,
) -> List[Tuple[float, float]]:
    """
    Generates candidate meeting coordinates around the group's centroid.
    The search radius adapts dynamically to the spatial spread of the participants.
    """
    centroid_lat, centroid_lon = compute_centroid(participants_latlon)

    # Measure maximum distance between any two participants to scale search radius
    max_span_km = 0.5
    for i in range(len(participants_latlon)):
        for j in range(i + 1, len(participants_latlon)):
            d = haversine_distance_km(
                participants_latlon[i][0], participants_latlon[i][1],
                participants_latlon[j][0], participants_latlon[j][1],
            )
            if d > max_span_km:
                max_span_km = d

    # Search radii scale between 0.5 km and 8 km
    base_radius_km = max(0.6, min(max_span_km * 0.25, 4.0))

    candidates = [(centroid_lat, centroid_lon)]

    # Generate concentric rings
    # 1 degree latitude ~ 111 km; 1 degree longitude ~ 111 km * cos(lat)
    cos_lat = math.cos(math.radians(centroid_lat))
    lat_deg_per_km = 1.0 / 111.0
    lon_deg_per_km = 1.0 / (111.0 * max(0.2, abs(cos_lat)))

    for ring_idx in range(1, rings + 1):
        radius_km = base_radius_km * ring_idx
        for p in range(points_per_ring):
            angle = (2 * math.pi * p) / points_per_ring
            d_lat = radius_km * math.cos(angle) * lat_deg_per_km
            d_lon = radius_km * math.sin(angle) * lon_deg_per_km
            candidates.append((centroid_lat + d_lat, centroid_lon + d_lon))

    # Also add pairwise midpoints between all participants as strong natural candidate points
    for i in range(len(participants_latlon)):
        for j in range(i + 1, len(participants_latlon)):
            mid_lat = (participants_latlon[i][0] + participants_latlon[j][0]) / 2.0
            mid_lon = (participants_latlon[i][1] + participants_latlon[j][1]) / 2.0
            candidates.append((mid_lat, mid_lon))

    # Deduplicate candidates within 150 meters of each other
    deduped = []
    for cand in candidates:
        is_duplicate = False
        for existing in deduped:
            if haversine_distance_km(cand[0], cand[1], existing[0], existing[1]) < 0.15:
                is_duplicate = True
                break
        if not is_duplicate:
            deduped.append(cand)

    return deduped


def calculate_fair_meeting_point(
    participants: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Given a list of participant dicts containing 'name', 'lat', 'lon', 'address',
    calculates the fairest meeting point based on travel-time minimization.

    Returns:
        Structured result dict with fair_point, travel_data, metrics, candidate list.
    """
    if len(participants) < 2:
        raise ValueError("At least 2 participants required for fair meeting point calculation.")

    participant_coords = [(p["lat"], p["lon"]) for p in participants]
    candidates = generate_candidate_points(participant_coords)

    # Query OSRM travel times for all participants to all candidates in one batch
    durations_matrix, distances_matrix, is_fallback, routing_info = get_travel_times(
        origins=participant_coords,
        destinations=candidates,
    )

    best_idx = 0
    best_score = float("inf")
    best_gap = float("inf")
    best_avg = float("inf")

    num_participants = len(participants)
    num_candidates = len(candidates)

    for cand_idx in range(num_candidates):
        # Extract travel times from each participant to this candidate
        times = [durations_matrix[p_idx][cand_idx] for p_idx in range(num_participants)]
        max_t = max(times)
        min_t = min(times)
        gap = max_t - min_t
        avg_t = sum(times) / num_participants

        # Fairness objective function:
        # Primary: Minimize gap between members (2.0 weight)
        # Secondary: Keep average travel time reasonable (0.5 weight)
        score = (gap * 2.0) + (avg_t * 0.5)

        if score < best_score:
            best_score = score
            best_idx = cand_idx
            best_gap = gap
            best_avg = avg_t

    fair_lat, fair_lon = candidates[best_idx]
    fair_address = reverse_geocode(fair_lat, fair_lon)

    # Build individual travel details for the winning candidate
    winning_times = [durations_matrix[p_idx][best_idx] for p_idx in range(num_participants)]
    winning_distances = [distances_matrix[p_idx][best_idx] for p_idx in range(num_participants)]

    travel_data = []
    for idx, p in enumerate(participants):
        travel_data.append({
            "name": p["name"],
            "address": p["address"],
            "lat": p["lat"],
            "lon": p["lon"],
            "time_min": winning_times[idx],
            "distance_km": winning_distances[idx],
        })

    max_time = max(winning_times)
    min_time = min(winning_times)
    actual_gap = max_time - min_time
    avg_time = sum(winning_times) / len(winning_times)

    fair_point_info = {
        "name": fair_address.split(",")[0] if "," in fair_address else "Optimal Meeting Spot",
        "address": fair_address,
        "latitude": fair_lat,
        "longitude": fair_lon,
    }

    fairness_metrics = {
        "max_time_min": round(max_time, 1),
        "min_time_min": round(min_time, 1),
        "gap_min": round(actual_gap, 1),
        "avg_time_min": round(avg_time, 1),
        "fairness_score": round(best_score, 2),
        "is_fallback": is_fallback,
        "routing_engine": routing_info,
        "candidates_evaluated": len(candidates),
    }

    return {
        "fair_point": fair_point_info,
        "travel_data": travel_data,
        "fairness_metrics": fairness_metrics,
        "candidates": candidates,
    }
