"""Weather forecasting service using Open-Meteo API."""
from datetime import date, datetime
from typing import Optional, Dict, Any
import requests
from utils.caching import weather_cache

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

WMO_CODE_MAP = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    61: ("Slight rain", "🌧️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "❄️"),
    75: ("Heavy snow", "❄️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with slight hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}


def get_weather_forecast(lat: float, lon: float, meeting_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches daily weather forecast for (lat, lon) on meeting_date using Open-Meteo.
    Gracefully handles dates beyond the available forecast range.
    """
    if meeting_date is None:
        meeting_date = date.today().isoformat()
    elif isinstance(meeting_date, (datetime, date)):
        meeting_date = meeting_date.isoformat()

    cache_key = f"weather:{lat:.3f},{lon:.3f}:{meeting_date}"
    cached = weather_cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max,windspeed_10m_max",
            "timezone": "auto",
        }
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            daily = data.get("daily", {})
            times = daily.get("time", [])

            if times:
                target_idx = 0
                is_out_of_range = False
                if meeting_date in times:
                    target_idx = times.index(meeting_date)
                else:
                    # Compare date string to forecast range
                    if meeting_date > times[-1]:
                        is_out_of_range = True
                        target_idx = len(times) - 1
                    elif meeting_date < times[0]:
                        target_idx = 0

                w_code = daily.get("weathercode", [0])[target_idx]
                t_max = daily.get("temperature_2m_max", [25.0])[target_idx]
                t_min = daily.get("temperature_2m_min", [15.0])[target_idx]
                precip_prob = daily.get("precipitation_probability_max", [0])[target_idx] or 0
                wind_speed = daily.get("windspeed_10m_max", [10.0])[target_idx] or 0

                condition, icon = WMO_CODE_MAP.get(w_code, ("Fair", "🌤️"))

                # Generate actionable recommendation
                if precip_prob >= 40:
                    outdoor_advice = f"Rain is likely ({precip_prob}% chance). An indoor venue with covered seating or parking is strongly recommended."
                elif t_max >= 34:
                    outdoor_advice = f"High temperature expected ({t_max}°C). An air-conditioned indoor cafe or evening meetup is suggested."
                elif t_min <= 10:
                    outdoor_advice = f"Chilly weather ({t_min}°C low). Warm indoor seating or cozy cafe recommended."
                else:
                    outdoor_advice = "Great weather conditions! Outdoor dining, rooftop lounges, or garden seating are highly suitable."

                range_notice = None
                if is_out_of_range:
                    range_notice = f"Note: Selected date ({meeting_date}) is beyond Open-Meteo's 14-day live forecast window. Showing forecast for {times[target_idx]} as an indicator."

                result = {
                    "available": True,
                    "date": meeting_date,
                    "forecast_date_used": times[target_idx],
                    "temp_max": t_max,
                    "temp_min": t_min,
                    "precipitation_probability": precip_prob,
                    "wind_speed_kmh": wind_speed,
                    "condition": condition,
                    "icon": icon,
                    "outdoor_advice": outdoor_advice,
                    "range_notice": range_notice,
                }
                weather_cache.set(cache_key, result)
                return result

    except Exception as exc:
        print(f"[Weather Service] Failed to retrieve forecast: {exc}")

    # Graceful fallback response
    return {
        "available": False,
        "date": meeting_date,
        "temp_max": 26.0,
        "temp_min": 18.0,
        "precipitation_probability": 15,
        "wind_speed_kmh": 12.0,
        "condition": "Seasonal Weather",
        "icon": "🌤️",
        "outdoor_advice": "Live forecast service is temporarily unreachable. Standard seasonal indoor/outdoor dining is generally fine.",
        "range_notice": "Live forecast data unavailable at this moment.",
    }
