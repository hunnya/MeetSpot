"""Results display view: Fair meeting point, Folium map, travel chart, places, and weather."""
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

from auth.authentication import is_authenticated, get_current_user
from database.database import get_db
from database.models import SavedMeeting, MeetingMember, Favorite


def render_results_section():
    """Renders the comprehensive results view from st.session_state.result_data."""
    res = st.session_state.get("result_data")
    if not res:
        st.info("Enter your group's details above and click 'Calculate Fair Meeting Point' to view results.")
        return

    fair_point = res["fair_point"]
    metrics = res["fairness_metrics"]
    travel_data = res["travel_data"]
    places = res.get("nearby_places", [])
    weather = res.get("weather", {})
    ai_explanation = res.get("ai_explanation", "")
    ai_note = res.get("ai_note", "")

    st.markdown("---")
    st.markdown("## Your Fairest Meeting Point")

    # Fallback / Demo indicator banner if applicable
    if res.get("is_demo_mode"):
        st.markdown(
            '<div class="msp-demo-tag">🛡️ DEMO MODE ACTIVE — Displaying realistic Islamabad test case</div>',
            unsafe_allow_html=True,
        )
    elif metrics.get("is_fallback"):
        st.warning(f"ℹ️ {metrics.get('routing_engine')}")

    # Top Hero Winner Card
    col_win1, col_win2 = st.columns([2.5, 1.5])
    with col_win1:
        st.markdown(
            f"""
            <div class="msp-winner-card">
                <div style="font-size: 0.85rem; font-weight: 700; color: #B5678A; text-transform: uppercase; margin-bottom: 0.3rem;">
                    🏆 Optimal Meeting Location
                </div>
                <h2 style="margin: 0 0 0.4rem 0; color: #2C3531; font-family: 'Plus Jakarta Sans', sans-serif;">
                    {fair_point.get('name', 'Meeting Point')}
                </h2>
                <p style="color: #55645A; font-size: 0.95rem; margin-bottom: 0.8rem;">
                    📍 {fair_point.get('address', '')}
                </p>
                <div>
                    <span class="msp-pill-green">⚖️ Fairness Gap: {metrics.get('gap_min', 0):.0f} min</span>
                    <span class="msp-pill-blue">⏱️ Avg Journey: {metrics.get('avg_time_min', 0):.0f} min</span>
                    <span class="msp-pill-blue">🛣️ {metrics.get('routing_engine', 'OSRM')}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_win2:
        _render_save_meeting_box(res)

    # 4 Quick Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="msp-stat"><div class="msp-stat-val">{metrics.get("max_time_min", 0):.0f} min</div><div class="msp-stat-lbl">Longest Drive</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="msp-stat"><div class="msp-stat-val">{metrics.get("min_time_min", 0):.0f} min</div><div class="msp-stat-lbl">Shortest Drive</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="msp-stat"><div class="msp-stat-val">{metrics.get("gap_min", 0):.0f} min</div><div class="msp-stat-lbl">Travel Disparity</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="msp-stat"><div class="msp-stat-val">{metrics.get("avg_time_min", 0):.1f} min</div><div class="msp-stat-lbl">Group Average</div></div>', unsafe_allow_html=True)

    st.write("")

    # AI Explanation
    if ai_explanation:
        st.markdown(
            f"""
            <div class="msp-highlight-card">
                <div style="font-weight: 700; color: #2C3531; margin-bottom: 0.3rem;">
                    🤖 AI Fairness Justification
                </div>
                <div style="color: #2C3531; line-height: 1.55; font-size: 0.98rem;">
                    {ai_explanation}
                </div>
                <div style="font-size: 0.78rem; color: #55645A; margin-top: 0.5rem;">
                    {ai_note}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Row with Travel Time Comparison Chart + Weather Forecast
    col_chart, col_weather = st.columns([1.6, 1.2])

    with col_chart:
        st.markdown("#### Travel Time Balancing")
        chart_df = pd.DataFrame([
            {
                "Participant": p["name"],
                "Drive Time (min)": p["time_min"],
                "Distance (km)": p.get("distance_km", 0),
            }
            for p in travel_data
        ])
        st.bar_chart(
            chart_df,
            x="Participant",
            y="Drive Time (min)",
            color="#7C8B65",
            use_container_width=True,
        )
        st.caption("Lower disparity = higher fairness. Everyone spends comparable time on the road.")

    with col_weather:
        st.markdown("#### Meetup Weather")
        _render_weather_card(weather)

    # Interactive Map
    st.markdown("#### Interactive Map")
    st.caption("Visualizing group starting points, the balanced meeting spot, and nearby venue options.")
    _render_folium_map(fair_point, travel_data, places)

    # Nearby Places
    st.markdown("---")
    st.markdown("#### Recommended Nearby Places")
    st.write("Ranked by group preferences and distance from the optimal meeting spot.")
    _render_places_list(places)


def _render_save_meeting_box(res: dict):
    """Renders the 'Save this meeting' action box."""
    st.markdown(
        """
        <div class="msp-card" style="padding: 1.1rem;">
            <div style="font-weight: 700; font-size: 0.95rem; color: #2C3531; margin-bottom: 0.4rem;">
                Save Meeting
            </div>
            <div style="font-size: 0.85rem; color: #55645A; margin-bottom: 0.8rem;">
                Store this calculation in your account for future reference.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not is_authenticated():
        st.caption("🔒 *Log in to save this meeting to your account.*")
    else:
        user = get_current_user()
        meeting_name = st.text_input("Meeting Name", value=f"Meetup at {res['fair_point']['name']}", key="save_meeting_title")
        if st.button("Save to My Meetings", type="primary", use_container_width=True):
            _save_meeting_to_db(user["id"], meeting_name, res)


def _save_meeting_to_db(user_id: int, meeting_name: str, res: dict):
    """Persists meeting and its participants to SQLite."""
    try:
        with get_db() as db:
            fp = res["fair_point"]
            metrics = res["fairness_metrics"]
            saved = SavedMeeting(
                user_id=user_id,
                meeting_name=meeting_name.strip() or "Group Meetup",
                meeting_date=str(res.get("preferences", {}).get("meeting_date", "")),
                fair_latitude=fp["latitude"],
                fair_longitude=fp["longitude"],
                fair_score=metrics.get("fairness_score", 0.0),
                fair_address=fp.get("address", ""),
                fair_summary=res.get("ai_explanation", ""),
            )
            db.add(saved)
            db.flush()

            for p in res.get("travel_data", []):
                member = MeetingMember(
                    saved_meeting_id=saved.id,
                    member_name=p["name"],
                    address=p.get("address", ""),
                    latitude=p.get("lat", 0.0),
                    longitude=p.get("lon", 0.0),
                    travel_time_min=p.get("time_min", 0.0),
                )
                db.add(member)

        st.success(f"🎉 Saved '{meeting_name}' to My Meetings!")
    except Exception as exc:
        st.error(f"Failed to save meeting: {exc}")


def _render_weather_card(weather: dict):
    """Renders the weather widget card."""
    if not weather:
        st.info("Weather data unavailable.")
        return

    icon = weather.get("icon", "🌤️")
    cond = weather.get("condition", "Fair")
    t_max = weather.get("temp_max", 25)
    t_min = weather.get("temp_min", 15)
    p_prob = weather.get("precipitation_probability", 0)
    advice = weather.get("outdoor_advice", "Suitable for outdoor or indoor meetups.")
    notice = weather.get("range_notice")

    st.markdown(
        f"""
        <div class="msp-card" style="background: linear-gradient(180deg, #EDF0E3 0%, #FFFFFF 100%);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                <div>
                    <span style="font-size: 1.8rem;">{icon}</span>
                    <span style="font-size: 1.1rem; font-weight: 700; color: #2C3531; margin-left: 0.4rem;">{cond}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 1.4rem; font-weight: 800; color: #7C8B65;">{t_max:.0f}°C</span>
                    <span style="font-size: 0.85rem; color: #55645A;">/ {t_min:.0f}°C</span>
                </div>
            </div>
            <div style="font-size: 0.88rem; color: #55645A; margin-bottom: 0.6rem;">
                🌧️ <b>Rain Probability:</b> {p_prob}%
            </div>
            <div style="font-size: 0.85rem; color: #8B4E68; background: #FBEEF2; border-radius: 8px; padding: 0.5rem 0.7rem; border: 1px solid #F0C9DA;">
                💡 {advice}
            </div>
            {"<div style='font-size: 0.75rem; color: #8A9A8C; margin-top: 0.5rem;'>" + notice + "</div>" if notice else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_folium_map(fair_point: dict, travel_data: list, places: list):
    """Renders interactive Folium map centered on the fair meeting point."""
    center_lat = fair_point["latitude"]
    center_lon = fair_point["longitude"]

    fmap = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles="CartoDB positron",
    )

    # 1. Add participant markers
    for idx, p in enumerate(travel_data):
        folium.Marker(
            [p["lat"], p["lon"]],
            tooltip=f"{p['name']} ({p['time_min']:.0f} min drive)",
            popup=folium.Popup(
                f"<b>{p['name']}</b><br>{p['address']}<br>Travel time: <b>{p['time_min']:.0f} mins</b> ({p.get('distance_km', 0):.1f} km)",
                max_width=250,
            ),
            icon=folium.Icon(color="blue", icon="user", prefix="fa"),
        ).add_to(fmap)

        # Draw light dashed line from participant to fair point
        folium.PolyLine(
            locations=[[p["lat"], p["lon"]], [center_lat, center_lon]],
            color="#3B82F6",
            weight=2,
            opacity=0.5,
            dash_array="5, 8",
        ).add_to(fmap)

    # 2. Add Fair Meeting Point Marker (Special green star)
    folium.Marker(
        [center_lat, center_lon],
        tooltip="🌟 Fairest Meeting Point",
        popup=folium.Popup(
            f"<div style='font-family:sans-serif;'><b>⭐ Fairest Meeting Point</b><br>{fair_point.get('name')}<br>{fair_point.get('address')}</div>",
            max_width=300,
        ),
        icon=folium.Icon(color="green", icon="star", prefix="fa"),
    ).add_to(fmap)

    # 3. Add Recommended Places Markers
    category_colors = {
        "cafe": "orange",
        "restaurant": "red",
        "fast_food": "darkred",
        "hotel": "purple",
    }
    category_icons = {
        "cafe": "coffee",
        "restaurant": "cutlery",
        "fast_food": "cutlery",
        "hotel": "bed",
    }

    for p in places[:8]:
        cat = p.get("category", "restaurant")
        color = category_colors.get(cat, "cadetblue")
        icon_name = category_icons.get(cat, "info-circle")

        folium.Marker(
            [p["latitude"], p["longitude"]],
            tooltip=f"{p['name']} ({cat.capitalize()})",
            popup=folium.Popup(
                f"<b>{p['name']}</b> ({cat.capitalize()})<br>{p.get('address', '')}<br>Distance: {p.get('distance_meters', 0)}m",
                max_width=240,
            ),
            icon=folium.Icon(color=color, icon=icon_name, prefix="fa"),
        ).add_to(fmap)

    st_folium(fmap, width="100%", height=460)


def _render_places_list(places: list):
    """Renders ranked place recommendation cards."""
    if not places:
        st.info("No nearby places found within walking distance.")
        return

    for idx, p in enumerate(places[:8]):
        cat_emojis = {"cafe": "☕ Cafe", "restaurant": "🍽️ Restaurant", "fast_food": "🍔 Fast Food", "hotel": "🏨 Hotel"}
        cat_badge = cat_emojis.get(p.get("category"), "📍 Venue")
        score = p.get("match_score", 85)

        col_card, col_fav = st.columns([4, 1])
        with col_card:
            st.markdown(
                f"""
                <div class="msp-venue-card">
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <div class="msp-venue-title">#{idx + 1}. {p.get('name')}</div>
                        <span class="msp-pill-blue">🎯 {score}% Match</span>
                    </div>
                    <div class="msp-venue-meta">
                        <b>{cat_badge}</b> • 🚶 {p.get('distance_meters', 0)} meters away • 📍 {p.get('address', 'Near meeting spot')}
                    </div>
                    <div class="msp-venue-reason">
                        💡 {p.get('reason', 'Great choice for a group hangout.')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_fav:
            st.write("")
            st.write("")
            if is_authenticated():
                fav_btn = st.button("⭐ Favorite", key=f"fav_{idx}_{p.get('id', idx)}", use_container_width=True)
                if fav_btn:
                    _add_favorite_place(p)
            else:
                st.caption("Log in to save")


def _add_favorite_place(place: dict):
    """Saves a place to user's favorites in SQLite."""
    user = get_current_user()
    try:
        with get_db() as db:
            existing = db.query(Favorite).filter(
                Favorite.user_id == user["id"],
                Favorite.place_name == place["name"],
            ).first()
            if existing:
                st.info(f"'{place['name']}' is already in your favorites.")
                return

            fav = Favorite(
                user_id=user["id"],
                place_name=place["name"],
                place_type=place.get("category", "place"),
                latitude=place["latitude"],
                longitude=place["longitude"],
                address=place.get("address", ""),
                rating_or_match=f"{place.get('match_score', 85)}% Match",
            )
            db.add(fav)
        st.success(f"Added '{place['name']}' to favorites!")
    except Exception as exc:
        st.error(f"Could not save favorite: {exc}")