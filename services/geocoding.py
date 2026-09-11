"""Geocoding and reverse geocoding service using OpenStreetMap Nominatim."""
import time
from typing import Optional, Dict, Any
import requests
from utils.caching import geo_cache

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
HEADERS = {
    "User-Agent": "MeetSpot-FairMeetingFinder/1.0 (contact: support@meetspot.app)",
    "Accept-Language": "en",
}

_last_request_time = 0.0


def _throttle(delay_seconds: float = 1.0):
    """Enforce Nominatim's usage policy of at most 1 request per second."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < delay_seconds:
        time.sleep(delay_seconds - elapsed)
    _last_request_time = time.time()


def geocode_address(address: str) -> Optional[Dict[str, Any]]:
    """
    Converts a user-entered address into latitude, longitude, and display name.
    Utilizes in-memory caching and request throttling.
    """
    cleaned_address = address.strip()
    if not cleaned_address:
        return None

    cache_key = f"geocode:{cleaned_address.lower()}"
    cached = geo_cache.get(cache_key)
    if cached:
        return cached

    _throttle(1.0)
    try:
        params = {
            "q": cleaned_address,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }
        resp = requests.get(NOMINATIM_SEARCH_URL, params=params, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                top = data[0]
                result = {
                    "lat": float(top["lat"]),
                    "lon": float(top["lon"]),
                    "display_name": top.get("display_name", cleaned_address),
                    "type": top.get("type", "address"),
                }
                geo_cache.set(cache_key, result)
                return result
    except Exception as exc:
        print(f"[Geocoding Error] Failed to geocode '{cleaned_address}': {exc}")

    return None


def reverse_geocode(lat: float, lon: float) -> str:
    """Converts coordinates back into a human-readable place name or landmark."""
    cache_key = f"reverse:{lat:.4f},{lon:.4f}"
    cached = geo_cache.get(cache_key)
    if cached:
        return cached

    _throttle(1.0)
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 16,
            "addressdetails": 1,
        }
        resp = requests.get(NOMINATIM_REVERSE_URL, params=params, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            name = data.get("display_name")
            if name:
                geo_cache.set(cache_key, name)
                return name
    except Exception as exc:
        print(f"[Geocoding Error] Failed to reverse geocode ({lat}, {lon}): {exc}")

    fallback_name = f"Coordinates ({lat:.4f}, {lon:.4f})"
    return fallback_name
