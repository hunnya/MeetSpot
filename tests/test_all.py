"""
Comprehensive test suite for MeetSpot.
Tests database, auth, algorithms, geocoding, routing, places, weather, and AI modules.
"""
import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Use an in-memory SQLite database for testing
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from database.database import init_db, get_db
from database.models import User, SavedMeeting, MeetingMember, Favorite
from auth.authentication import (
    hash_password,
    verify_password,
    register_user,
    authenticate_user,
)
from utils.validation import validate_participants, validate_coordinates
from utils.demo_data import get_demo_meeting_data
from services.geocoding import geocode_address, reverse_geocode
from services.routing import haversine_distance_km, get_travel_times
from services.places import get_nearby_places
from services.weather import get_weather_forecast
from services.ai import rank_places, generate_ai_explanation
from algorithms.fairness import compute_centroid, generate_candidate_points, calculate_fair_meeting_point


class TestMeetSpot(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    # --------------------------------------------------------------------------
    # 1. DATABASE & AUTHENTICATION TESTS
    # --------------------------------------------------------------------------
    def test_01_password_hashing(self):
        pwd = "SecretPassword123"
        hashed = hash_password(pwd)
        self.assertNotEqual(pwd, hashed)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_02_user_registration_and_login(self):
        # Register new user
        success, msg, user = register_user("Test User", "test@meetspot.app", "password123", "password123")
        self.assertTrue(success, msg)
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], "test@meetspot.app")

        # Duplicate registration should fail
        dup_success, dup_msg, _ = register_user("Test User 2", "test@meetspot.app", "password123", "password123")
        self.assertFalse(dup_success)
        self.assertIn("already exists", dup_msg)

        # Authenticate with correct password
        auth_success, auth_msg, auth_user = authenticate_user("test@meetspot.app", "password123")
        self.assertTrue(auth_success, auth_msg)
        self.assertEqual(auth_user["id"], user["id"])

        # Authenticate with wrong password
        fail_success, _, _ = authenticate_user("test@meetspot.app", "badpassword")
        self.assertFalse(fail_success)

    def test_03_saved_meetings_and_favorites(self):
        with get_db() as db:
            user = db.query(User).filter(User.email == "test@meetspot.app").first()
            self.assertIsNotNone(user)
            user_id = user.id

            # Create saved meeting
            saved = SavedMeeting(
                user_id=user_id,
                meeting_name="Hackathon Strategy Meeting",
                meeting_date="2026-09-15",
                fair_latitude=33.7077,
                fair_longitude=73.0498,
                fair_score=14.2,
                fair_address="Centaurus Islamabad",
            )
            db.add(saved)
            db.flush()

            # Add member
            m1 = MeetingMember(
                saved_meeting_id=saved.id,
                member_name="Hunnya",
                address="Bahria University",
                latitude=33.6628,
                longitude=72.9904,
                travel_time_min=16.0,
            )
            db.add(m1)

            # Add favorite
            fav = Favorite(
                user_id=user_id,
                place_name="Chaaye Khana",
                place_type="cafe",
                latitude=33.71,
                longitude=73.05,
                address="Blue Area",
            )
            db.add(fav)

        with get_db() as db:
            user_saved = db.query(SavedMeeting).filter(SavedMeeting.user_id == user_id).all()
            self.assertEqual(len(user_saved), 1)
            self.assertEqual(user_saved[0].members[0].member_name, "Hunnya")

            user_favs = db.query(Favorite).filter(Favorite.user_id == user_id).all()
            self.assertEqual(len(user_favs), 1)
            self.assertEqual(user_favs[0].place_name, "Chaaye Khana")

    # --------------------------------------------------------------------------
    # 2. VALIDATION & UTILS TESTS
    # --------------------------------------------------------------------------
    def test_04_validation(self):
        # Valid participants
        valid_input = [
            {"name": "Ali", "address": "F-10 Islamabad"},
            {"name": "Sara", "address": "I-8 Islamabad"},
        ]
        ok, msg = validate_participants(valid_input)
        self.assertTrue(ok)

        # Missing participant
        too_few = [{"name": "Ali", "address": "F-10 Islamabad"}]
        ok, msg = validate_participants(too_few)
        self.assertFalse(ok)

        # Empty address
        empty_addr = [
            {"name": "Ali", "address": "F-10 Islamabad"},
            {"name": "Sara", "address": "   "},
        ]
        ok, msg = validate_participants(empty_addr)
        self.assertFalse(ok)

        # Coordinate validation
        self.assertTrue(validate_coordinates(33.6844, 73.0479))
        self.assertFalse(validate_coordinates(95.0, 73.0))

    def test_05_demo_data(self):
        demo = get_demo_meeting_data()
        self.assertIn("participants", demo)
        self.assertIn("fair_point", demo)
        self.assertIn("travel_data", demo)
        self.assertIn("fairness_metrics", demo)
        self.assertEqual(len(demo["participants"]), 4)
        self.assertEqual(demo["fairness_metrics"]["gap_min"], 4.0)

    # --------------------------------------------------------------------------
    # 3. ROUTING & FAIRNESS ALGORITHM TESTS
    # --------------------------------------------------------------------------
    def test_06_haversine_distance(self):
        # Distance between F-10 (33.6934, 73.0135) and I-8 (33.6687, 73.0768)
        dist = haversine_distance_km(33.6934, 73.0135, 33.6687, 73.0768)
        self.assertGreater(dist, 5.0)
        self.assertLess(dist, 10.0)

    def test_07_centroid_and_candidates(self):
        coords = [(33.66, 72.99), (33.69, 73.01), (33.67, 73.07)]
        c_lat, c_lon = compute_centroid(coords)
        self.assertAlmostEqual(c_lat, 33.6733, places=2)
        self.assertAlmostEqual(c_lon, 73.0233, places=2)

        candidates = generate_candidate_points(coords, rings=2, points_per_ring=8)
        self.assertGreater(len(candidates), 5)
        # Check that centroid is included in candidates
        self.assertEqual(candidates[0], (c_lat, c_lon))

    def test_08_fairness_calculation(self):
        participants = [
            {"name": "Hunnya", "address": "H-11", "lat": 33.6628, "lon": 72.9904},
            {"name": "Ali", "address": "F-10", "lat": 33.6934, "lon": 73.0135},
            {"name": "Sara", "address": "I-8", "lat": 33.6687, "lon": 73.0768},
        ]
        res = calculate_fair_meeting_point(participants)
        self.assertIn("fair_point", res)
        self.assertIn("travel_data", res)
        self.assertIn("fairness_metrics", res)

        metrics = res["fairness_metrics"]
        self.assertIn("max_time_min", metrics)
        self.assertIn("min_time_min", metrics)
        self.assertIn("gap_min", metrics)
        self.assertGreater(metrics["max_time_min"], 0)
        self.assertGreaterEqual(metrics["max_time_min"], metrics["min_time_min"])
        self.assertEqual(len(res["travel_data"]), 3)

    # --------------------------------------------------------------------------
    # 4. WEATHER & PLACES & AI TESTS
    # --------------------------------------------------------------------------
    def test_09_weather_service(self):
        forecast = get_weather_forecast(33.6844, 73.0479)
        self.assertIn("temp_max", forecast)
        self.assertIn("condition", forecast)
        self.assertIn("outdoor_advice", forecast)

    def test_10_places_service(self):
        places = get_nearby_places(33.6844, 73.0479, radius_meters=1500, limit=5)
        self.assertIsInstance(places, list)
        self.assertGreater(len(places), 0)
        first = places[0]
        self.assertIn("name", first)
        self.assertIn("category", first)
        self.assertIn("distance_meters", first)

    def test_11_ai_ranking_and_explanation(self):
        places = [
            {"name": "Cafe Cozy", "category": "cafe", "cuisine": "coffee;bakery", "outdoor_seating": "yes", "distance_meters": 300},
            {"name": "Steakhouse Prime", "category": "restaurant", "cuisine": "steak", "outdoor_seating": "no", "distance_meters": 700},
        ]
        prefs = {"cuisine": "Cafe / Coffee", "atmosphere": "Outdoor", "freetext": "nice outdoor cafe with coffee"}

        ranked, used_llm, note = rank_places(places, prefs)
        self.assertEqual(len(ranked), 2)
        # Cafe Cozy should rank higher for cafe/outdoor preferences
        self.assertEqual(ranked[0]["name"], "Cafe Cozy")
        self.assertGreater(ranked[0]["match_score"], ranked[1]["match_score"])

        explanation = generate_ai_explanation(
            fair_point={"name": "Centaurus", "address": "Islamabad"},
            travel_data=[{"name": "Ali", "time_min": 14.0}, {"name": "Sara", "time_min": 16.0}],
            fairness_metrics={"max_time_min": 16.0, "min_time_min": 14.0, "gap_min": 2.0, "avg_time_min": 15.0},
        )
        self.assertIn("MeetSpot", explanation)
        self.assertIn("16", explanation)
        self.assertIn("14", explanation)


if __name__ == "__main__":
    unittest.main()
