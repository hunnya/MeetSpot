"""Realistic sample/demo data for Islamabad/Rawalpindi meetups."""
from datetime import date, timedelta


def get_demo_meeting_data():
    """Returns a fully populated, realistic meeting calculation result for Islamabad."""
    today = date.today()
    meeting_date = today + timedelta(days=2)

    participants = [
        {"name": "Hunnya", "address": "H-11, Islamabad", "lat": 33.6628, "lon": 72.9904},
        {"name": "Ali", "address": "F-10 Markaz, Islamabad", "lat": 33.6934, "lon": 73.0135},
        {"name": "Sara", "address": "I-8 Markaz, Islamabad", "lat": 33.6687, "lon": 73.0768},
        {"name": "Bilal", "address": "Blue Area, Islamabad", "lat": 33.7121, "lon": 73.0652},
    ]

    # Selected fair meeting spot: Centaurus / Blue Area Sector F-8 junction
    fair_point = {
        "name": "Centaurus / Jinnah Avenue Junction, Islamabad",
        "latitude": 33.7077,
        "longitude": 73.0498,
        "address": "Jinnah Avenue, Sector F-8/G-8, Islamabad, 44000, Pakistan",
    }

    # Travel times computed for realistic driving in minutes and km
    travel_data = [
        {"name": "Hunnya", "time_min": 16.0, "distance_km": 10.2},
        {"name": "Ali", "name": "Ali", "time_min": 14.0, "distance_km": 7.8},
        {"name": "Sara", "time_min": 15.0, "distance_km": 8.5},
        {"name": "Bilal", "time_min": 12.0, "distance_km": 3.2},
    ]
    # Ensure correct name matching
    travel_data[1]["name"] = "Ali"

    fairness_metrics = {
        "max_time_min": 16.0,
        "min_time_min": 12.0,
        "gap_min": 4.0,
        "avg_time_min": 14.25,
        "fairness_score": 15.1,
        "is_fallback": False,
        "routing_engine": "OSRM (Driving / Real-road routing)",
    }

    nearby_places = [
        {
            "name": "Chaaye Khana",
            "category": "cafe",
            "distance_meters": 450,
            "address": "Shop 11, Block B, Blue Area, Islamabad",
            "tags": {"amenity": "cafe", "cuisine": "tea;pakistani;breakfast", "outdoor_seating": "yes"},
            "rating": 4.6,
            "match_score": 96,
            "reason": "Top-tier ambiance with artisan teas, comfortable indoor & outdoor seating, ideal for groups.",
        },
        {
            "name": "The Monal Downtown",
            "category": "restaurant",
            "distance_meters": 350,
            "address": "Centaurus Mall 4th Floor, Sector F-8, Islamabad",
            "tags": {"amenity": "restaurant", "cuisine": "pakistani;continental", "wheelchair": "yes"},
            "rating": 4.5,
            "match_score": 92,
            "reason": "Extensive buffet and à la carte menu, expansive seating, and convenient covered mall parking.",
        },
        {
            "name": "Burning Brown Sugar",
            "category": "cafe",
            "distance_meters": 680,
            "address": "Beverly Centre, Blue Area, Islamabad",
            "tags": {"amenity": "cafe", "cuisine": "coffee_shop;bakery", "wifi": "yes"},
            "rating": 4.5,
            "match_score": 88,
            "reason": "Quiet, cozy cafe famous for freshly roasted specialty coffee and signature pastries.",
        },
        {
            "name": "Howdy Islamabad",
            "category": "restaurant",
            "distance_meters": 520,
            "address": "Food Court, Centaurus Mall, Islamabad",
            "tags": {"amenity": "fast_food", "cuisine": "burger;bbq"},
            "rating": 4.3,
            "match_score": 82,
            "reason": "Energetic, casual spot with gourmet burgers and steaks, very budget-friendly.",
        },
        {
            "name": "Islamabad Serena Hotel",
            "category": "hotel",
            "distance_meters": 2400,
            "address": "Khayaban-e-Suhrawardy, Sector G-5, Islamabad",
            "tags": {"tourism": "hotel", "luxury": "yes", "dining": "multiple"},
            "rating": 4.8,
            "match_score": 80,
            "reason": "Premium luxury venue with lush Mughal gardens, quiet lounges, and world-class fine dining.",
        },
    ]

    weather = {
        "date": str(meeting_date),
        "temp_max": 28.5,
        "temp_min": 18.2,
        "precipitation_probability": 10,
        "condition": "Mainly clear and pleasant",
        "icon": "☀️",
        "outdoor_advice": "Excellent conditions for outdoor or terrace dining. Mild temperatures expected.",
    }

    ai_explanation = (
        "MeetSpot evaluated 25 candidate road nodes around the group's geographic centroid. "
        "The selected meeting point near Jinnah Avenue / F-8 balances travel times remarkably well: "
        "the longest drive (Hunnya, 16 min) and shortest drive (Bilal, 12 min) are within just 4 minutes of each other, "
        "delivering high fairness across all 4 participants."
    )

    return {
        "participants": participants,
        "fair_point": fair_point,
        "travel_data": travel_data,
        "fairness_metrics": fairness_metrics,
        "nearby_places": nearby_places,
        "weather": weather,
        "ai_explanation": ai_explanation,
        "preferences": {
            "cuisine": "Any",
            "atmosphere": "Casual & Outdoor",
            "budget": "Moderate",
            "freetext": "nice cafe or restaurant with comfortable seating",
            "meeting_date": str(meeting_date),
        },
    }
