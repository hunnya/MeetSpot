"""Meeting creation form and participant input UI."""
from datetime import date, timedelta
from typing import Dict, Any, Optional
import streamlit as st

from services.geocoding import geocode_address
from algorithms.fairness import calculate_fair_meeting_point
from services.places import get_nearby_places
from services.weather import get_weather_forecast
from services.ai import rank_places, generate_ai_explanation
from utils.validation import validate_participants
from utils.demo_data import get_demo_meeting_data


def render_create_meeting_form():
    """Renders the meeting configuration form and handles calculation."""
    st.markdown("### 📍 Plan Your Meetup")
    st.write("Enter your group's starting locations and preferences. MeetSpot will calculate the fairest point based on real travel times.")

    # State initialization for participant count and presets
    if "num_participants" not in st.session_state:
        st.session_state.num_participants = 3

    # Quick demo filler banner
    col_preset1, col_preset2 = st.columns([3, 1.2])
    with col_preset1:
        st.caption("Tip: You can manually enter any city addresses, or load our hackathon test case for Islamabad.")
    with col_preset2:
        if st.button("🚀 Load Islamabad Demo", use_container_width=True, help="Fills realistic Islamabad locations for rapid testing"):
            _load_islamabad_preset()
            st.rerun()

    # Participant Controls
    st.markdown("#### 1. Participants & Starting Locations")
    c_count1, c_count2, _ = st.columns([1.5, 1.5, 3])
    with c_count1:
        if st.button("➕ Add Person", disabled=st.session_state.num_participants >= 8, use_container_width=True):
            st.session_state.num_participants += 1
            st.rerun()
    with c_count2:
        if st.button("➖ Remove Person", disabled=st.session_state.num_participants <= 2, use_container_width=True):
            st.session_state.num_participants -= 1
            st.rerun()

    participants_input = []
    num_p = st.session_state.num_participants

    for i in range(num_p):
        default_name = st.session_state.get(f"preset_name_{i}", f"Person {i + 1}")
        default_addr = st.session_state.get(f"preset_addr_{i}", "")

        col_p_name, col_p_addr = st.columns([1.2, 3])
        with col_p_name:
            p_name = st.text_input(
                f"Name",
                value=default_name,
                key=f"p_name_{i}",
                placeholder="e.g. Sara",
            )
        with col_p_addr:
            p_addr = st.text_input(
                f"Starting Location / Landmark",
                value=default_addr,
                key=f"p_addr_{i}",
                placeholder="e.g. F-10 Markaz Islamabad",
            )
        participants_input.append({"name": p_name, "address": p_addr})

    # Preferences & Meeting Details
    st.markdown("#### 2. Group Preferences & Meeting Date")
    col_cui, col_atmo, col_bud = st.columns(3)

    with col_cui:
        cuisine = st.selectbox(
            "Cuisine Type",
            options=["Any", "Pakistani", "Cafe / Coffee", "Fast Food", "Italian / Continental", "Chinese / Asian", "Dessert / Bakery"],
            index=0,
            key="pref_cuisine",
        )
    with col_atmo:
        atmosphere = st.selectbox(
            "Atmosphere",
            options=["Any", "Casual & Cozy", "Quiet (Conversations/Work)", "Outdoor / Rooftop", "Family-friendly", "Premium / Fine Dining"],
            index=0,
            key="pref_atmosphere",
        )
    with col_bud:
        budget = st.selectbox(
            "Budget Level",
            options=["Any", "Budget ($)", "Moderate ($$)", "Premium ($$$)"],
            index=0,
            key="pref_budget",
        )

    col_date, col_free = st.columns([1.5, 2.5])
    with col_date:
        meet_date = st.date_input(
            "📅 Planned Meeting Date",
            value=date.today(),
            min_value=date.today(),
            max_value=date.today() + timedelta(days=60),
            key="pref_date",
        )
    with col_free:
        freetext = st.text_input(
            "Free-text requests (Optional)",
            placeholder="e.g. quiet cafe with outdoor seating and parking",
            key="pref_freetext",
        )

    # Optional Groq API Key
    with st.expander("🔑 Advanced AI Settings (Groq API Key)", expanded=False):
        st.write("Groq provides high-speed Llama LLM ranking and explanation. If omitted, MeetSpot uses deterministic rule-based ranking.")
        custom_groq_key = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_...",
            key="custom_groq_key",
            help="Free key from console.groq.com. Stored only in your current browser session.",
        )

    st.markdown("---")
    btn_calc = st.button("✨ Calculate Fair Meeting Point", type="primary", use_container_width=True)

    if btn_calc:
        _handle_calculation(
            participants_input=participants_input,
            preferences={
                "cuisine": cuisine,
                "atmosphere": atmosphere,
                "budget": budget,
                "freetext": freetext,
                "meeting_date": str(meet_date),
            },
            groq_key=custom_groq_key,
        )


def _load_islamabad_preset():
    """Fills session state with sample participants from Islamabad."""
    preset = [
        ("Hunnya", "Bahria University H-11, Islamabad"),
        ("Ali", "F-10 Markaz, Islamabad"),
        ("Sara", "I-8 Markaz, Islamabad"),
        ("Bilal", "Blue Area, Islamabad"),
    ]
    st.session_state.num_participants = len(preset)
    for idx, (name, addr) in enumerate(preset):
        st.session_state[f"preset_name_{idx}"] = name
        st.session_state[f"preset_addr_{idx}"] = addr
        st.session_state[f"p_name_{idx}"] = name
        st.session_state[f"p_addr_{idx}"] = addr


def _handle_calculation(
    participants_input: list,
    preferences: Dict[str, Any],
    groq_key: Optional[str] = None,
):
    """Orchestrates geocoding, fairness calculation, nearby places, weather, and AI ranking."""
    # Check if demo mode is requested
    import os
    if os.getenv("DEMO_MODE", "false").lower() == "true":
        st.session_state.result_data = get_demo_meeting_data()
        st.session_state.result_data["is_demo_mode"] = True
        st.success("Loaded fail-safe Islamabad demo data successfully!")
        st.rerun()
        return

    # 1. Validation
    is_valid, err_msg = validate_participants(participants_input)
    if not is_valid:
        st.error(f"⚠️ {err_msg}")
        return

    # 2. Geocoding
    geocoded_participants = []
    with st.spinner("📍 Geocoding participant addresses with OpenStreetMap Nominatim..."):
        for p in participants_input:
            geo_res = geocode_address(p["address"])
            if not geo_res:
                st.error(
                    f"❌ Could not locate address for '{p['name']}': **\"{p['address']}\"**.\n\n"
                    "Please try a more specific address, sector, or nearby landmark."
                )
                return
            geocoded_participants.append({
                "name": p["name"],
                "address": geo_res["display_name"],
                "lat": geo_res["lat"],
                "lon": geo_res["lon"],
            })

    # 3. Fairness Calculation
    with st.spinner("🧭 Balancing travel times across candidate nodes via OSRM..."):
        try:
            fair_calc_result = calculate_fair_meeting_point(geocoded_participants)
        except Exception as exc:
            st.error(f"Error calculating fair meeting point: {exc}")
            return

    fair_point = fair_calc_result["fair_point"]
    travel_data = fair_calc_result["travel_data"]
    fairness_metrics = fair_calc_result["fairness_metrics"]

    # 4. Nearby Places via Overpass
    with st.spinner("🍽️ Discovering nearby restaurants, cafes, and hotels with Overpass..."):
        nearby_raw = get_nearby_places(
            lat=fair_point["latitude"],
            lon=fair_point["longitude"],
            radius_meters=1500,
            limit=12,
            place_type_filter=preferences.get("cuisine"),
        )

    # 5. Weather via Open-Meteo
    with st.spinner("⛅ Retrieving weather forecast from Open-Meteo..."):
        weather_data = get_weather_forecast(
            lat=fair_point["latitude"],
            lon=fair_point["longitude"],
            meeting_date=preferences.get("meeting_date"),
        )

    # 6. AI Ranking & Explanation
    with st.spinner("🤖 Ranking venues according to group preferences..."):
        ranked_places, used_llm, ai_note = rank_places(
            places=nearby_raw,
            preferences=preferences,
            api_key=groq_key,
        )
        ai_explanation = generate_ai_explanation(
            fair_point=fair_point,
            travel_data=travel_data,
            fairness_metrics=fairness_metrics,
            api_key=groq_key,
        )

    # Save to session state
    st.session_state.result_data = {
        "participants": geocoded_participants,
        "fair_point": fair_point,
        "travel_data": travel_data,
        "fairness_metrics": fairness_metrics,
        "nearby_places": ranked_places,
        "weather": weather_data,
        "ai_explanation": ai_explanation,
        "ai_note": ai_note,
        "used_llm": used_llm,
        "preferences": preferences,
        "candidates": fair_calc_result.get("candidates", []),
    }
    st.success("✅ Fair meeting point calculated successfully!")
    st.rerun()
