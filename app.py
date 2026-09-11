"""
MeetSpot — The Fair Meeting Point Finder
Main Streamlit Application Controller.
"""
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="MeetSpot — The Fair Meeting Point Finder",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Imports after page_config
from database.database import init_db
from auth.authentication import init_session_auth, is_authenticated, get_current_user, logout_user
from ui.styles import MODERN_CSS, render_hero
from ui.auth_ui import render_auth_section
from ui.meeting_ui import render_create_meeting_form
from ui.results_ui import render_results_section
from ui.history_ui import render_history_section
from ui.favorites_ui import render_favorites_section
from utils.demo_data import get_demo_meeting_data

# Initialize SQLite database tables
init_db()

# Initialize Streamlit session state
init_session_auth()
if "result_data" not in st.session_state:
    st.session_state.result_data = None

# Apply modern executive Map-Blue styling
st.markdown(MODERN_CSS, unsafe_allow_html=True)


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
            <span style="font-size: 1.8rem; margin-right: 0.5rem;">📍</span>
            <div>
                <h2 style="margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.5rem; color: #1E3A8A;">MeetSpot</h2>
                <div style="font-size: 0.8rem; color: #64748B; font-weight: 600;">The Fair Meeting Point Finder</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # User state badge
    if is_authenticated():
        u = get_current_user()
        st.markdown(
            f"""
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 10px; padding: 0.7rem; margin-bottom: 1rem;">
                <div style="font-size: 0.75rem; color: #1E40AF; text-transform: uppercase; font-weight: 700;">Signed In</div>
                <div style="font-weight: 700; color: #0F172A; font-size: 0.95rem;">👤 {u.get('name')}</div>
                <div style="font-size: 0.8rem; color: #64748B;">{u.get('email')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Sign Out", key="sidebar_logout", use_container_width=True):
            logout_user()
            st.rerun()
    else:
        st.markdown(
            """
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 0.6rem; margin-bottom: 1rem;">
                <div style="font-size: 0.8rem; color: #64748B;">Guest Session • Sign in on the Account tab to save meetings & favorites.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Hackathon Demo Mode Controller
    st.markdown("#### 🛡️ Hackathon Controls")
    demo_env = os.getenv("DEMO_MODE", "false").lower() == "true"
    is_demo_active = st.toggle("Enable Offline Demo Mode", value=demo_env, help="Activates precomputed realistic Islamabad data, protecting the demo from network/API drops.")
    if is_demo_active != demo_env:
        os.environ["DEMO_MODE"] = "true" if is_demo_active else "false"

    if is_demo_active:
        st.info("Demo mode is ON: Any calculation loads instant fail-safe Islamabad data.")
        if st.button("Load Islamabad Sample Now", type="secondary", use_container_width=True):
            st.session_state.result_data = get_demo_meeting_data()
            st.session_state.result_data["is_demo_mode"] = True
            st.rerun()

    st.markdown("---")

    # Service Health Status
    st.markdown("#### 🌐 Service Integrations")
    groq_available = bool(os.getenv("GROQ_API_KEY") and os.getenv("GROQ_API_KEY") != "your_groq_api_key_here")
    st.markdown(
        f"""
        <div style="font-size: 0.85rem; color: #475569; line-height: 1.8;">
            <div>🟢 <b>OSRM:</b> Live (Road routing)</div>
            <div>🟢 <b>Nominatim:</b> Live (OSM Geocoding)</div>
            <div>🟢 <b>Overpass:</b> Live (OSM Places)</div>
            <div>🟢 <b>Open-Meteo:</b> Live (Weather)</div>
            <div>{'🟢 <b>Groq AI:</b> Connected' if groq_available else '🟡 <b>Groq AI:</b> Rule-based fallback'}</div>
            <div>🟢 <b>Database:</b> SQLite (Persistent)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("MeetSpot v1.0 • Hackathon Edition\nBuilt with Streamlit & OpenStreetMap")


# ==============================================================================
# MAIN PAGE AREA
# ==============================================================================
render_hero()

tab_find, tab_history, tab_favorites, tab_guide, tab_account = st.tabs([
    "📍 Find Fair Spot",
    "📋 My Saved Meetings",
    "⭐ Saved Favorites",
    "💡 How It Works",
    "🔐 Account",
])

# Tab 1: Find Fair Spot
with tab_find:
    render_create_meeting_form()
    render_results_section()

# Tab 2: Saved Meetings
with tab_history:
    render_history_section()

# Tab 3: Favorites
with tab_favorites:
    render_favorites_section()

# Tab 4: How It Works / Algorithm Guide
with tab_guide:
    st.markdown("### 💡 Why MeetSpot? (The Science of Fairness)")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown(
            """
            <div class="msp-card">
                <h4 style="color: #DC2626; margin-top: 0;">❌ The Geographic Midpoint Fallacy</h4>
                <p style="font-size: 0.92rem; color: #475569; line-height: 1.5;">
                    Most apps simply calculate the mathematical average of latitude and longitude (the centroid).
                    This completely ignores:
                </p>
                <ul style="font-size: 0.9rem; color: #334155;">
                    <li>One-way streets, highways, and bridges.</li>
                    <li>Terrain obstacles (mountains, rivers, railway tracks).</li>
                    <li>Congested urban zones vs expressways.</li>
                </ul>
                <p style="font-size: 0.9rem; color: #64748B;">
                    Result: One person drives 40 minutes while someone else walks 5 minutes.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_g2:
        st.markdown(
            """
            <div class="msp-card">
                <h4 style="color: #059669; margin-top: 0;">✅ The MeetSpot Travel-Time Balancer</h4>
                <p style="font-size: 0.92rem; color: #475569; line-height: 1.5;">
                    MeetSpot evaluates real-world driving travel times using OSRM Table routing:
                </p>
                <ul style="font-size: 0.9rem; color: #334155;">
                    <li>Generates multi-ring candidate road coordinates around the centroid.</li>
                    <li>Calculates driving duration from <b>every participant</b> to each candidate.</li>
                    <li>Minimizes the <b>travel time gap (Max - Min)</b> across all group members.</li>
                </ul>
                <p style="font-size: 0.9rem; color: #047857; font-weight: 600;">
                    Result: Travel disparity is minimized, making the meetup genuinely fair.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### 📐 Mathematical Objective Function")
    st.markdown(
        """
        For each candidate meeting point $k$ and participants $i = 1, \\dots, N$:
        
        $$T_{i, k} = \\text{TravelTime}(\\text{Participant}_i \\to \\text{Candidate}_k)$$
        $$\\text{Disparity Gap}_k = \\max_i(T_{i, k}) - \\min_i(T_{i, k})$$
        $$\\text{Average Time}_k = \\frac{1}{N} \\sum_{i=1}^{N} T_{i, k}$$
        $$\\text{Fairness Score}_k = 2.0 \\times \\text{Disparity Gap}_k + 0.5 \\times \\text{Average Time}_k$$
        
        The candidate that minimizes the **Fairness Score** is selected as the winning meeting spot.
        """
    )

    st.markdown("#### 🏗️ Architecture & Open-Source Stack")
    st.markdown(
        """
        | Layer | Technology | Cost / Key Requirement |
        |---|---|---|
        | **Frontend / UI** | Streamlit 1.58 + Folium | Open-source, no key |
        | **Geocoding** | OpenStreetMap Nominatim | Free, rate-throttled User-Agent |
        | **Distance & Routing** | OSRM Table API | Free, real road networks |
        | **Nearby Places** | OSM Overpass API | Free, queries cafes, restaurants, hotels |
        | **Weather Forecast** | Open-Meteo API | Free, no credit card required |
        | **AI Preference Engine** | Groq API (`llama-3.3-70b`) | Free tier / Seamless deterministic fallback |
        | **Persistence** | SQLite + SQLAlchemy 2.0 | Local, encrypted passwords via bcrypt |
        """
    )

# Tab 5: Account
with tab_account:
    render_auth_section()
