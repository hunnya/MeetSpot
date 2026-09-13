"""
MeetSpot — The Fair Meeting Point Finder
Main Streamlit Application Controller.
"""
import base64

def img_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Convert your local image
logo_base64 = img_to_base64("logo1.png")  # Replace with your file path
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="MeetSpot — The Fair Meeting Point Finder",
    page_icon="logo1.png", ######
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
# init_db()
@st.cache_resource
def setup_database():
    init_db()

# Call the cached function instead of init_db() directly
setup_database()

# Initialize Streamlit session state
init_session_auth()
if "result_data" not in st.session_state:
    st.session_state.result_data = None

# Apply modern executive Map-Blue styling
st.markdown(MODERN_CSS, unsafe_allow_html=True)


# ==============================================================================
# SIDEBAR
# ==============================================================================
# with st.sidebar: ####### in span,, logo   # <span style="font-size: 1.8rem; margin-right: 0.5rem;"></span> 
#     st.markdown(
#         """
#         <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
#            <img src="data:logo/jpe;base64,{logo_base64}" style="width: 35px; height: 35px; margin-right: 0.5rem; object-fit: contain;" alt="MeetSpot Logo">
#             <div>
#                 <h2 style="margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.5rem; color: #2C3531;">MeetSpot</h2>
#                 <div style="font-size: 0.8rem; color: #55645A; font-weight: 600;">The Fair Meeting Point Finder</div>
#             </div>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )
with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
            <img src="data:image/png;base64,{logo_base64}" style="width: 35px; height: 35px; margin-right: 0.5rem; object-fit: contain;" alt="MeetSpot Logo">  
            <div>
                <h2 style="margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.5rem; color: #2C3531;">MeetSpot</h2>
                <div style="font-size: 0.8rem; color: #55645A; font-weight: 600;">The Fair Meeting Point Finder</div>
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
            <div style="background: #E7EBDD; border: 1px solid #F3D9E3; border-radius: 10px; padding: 0.7rem; margin-bottom: 1rem;">
                <div style="font-size: 0.75rem; color: #7C8B65; text-transform: uppercase; font-weight: 700;">Signed In</div>
                <div style="font-weight: 700; color: #2C3531; font-size: 0.95rem;">👤 {u.get('name')}</div>
                <div style="font-size: 0.8rem; color: #55645A;">{u.get('email')}</div>
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
            <div style="background: #F3EDE0; border: 1px solid #F3D9E3; border-radius: 10px; padding: 0.6rem; margin-bottom: 1rem;">
                <div style="font-size: 0.8rem; color: #55645A;">Guest Session • Sign in on the Account tab to save meetings & favorites.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Hackathon Demo Mode Controller
    st.markdown("#### 🕒 Demo Mode")
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
        <div style="font-size: 0.85rem; color: #55645A; line-height: 1.8;">
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
    st.caption("MeetSpot v1.0 • Hackathon Edition\n")


# ==============================================================================
# MAIN PAGE AREA
# ==============================================================================
render_hero()

tab_find, tab_history, tab_favorites, tab_guide, tab_account = st.tabs([
    "Find Fair Spot",
    "My Saved Meetings",
    "Saved Favorites",
    "How It Works",
    "Account",
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

# Tab 4: How It Works
with tab_guide:
    st.markdown("### How MeetSpot Works")
    st.markdown(
        """
        <div class="msp-card">
            <p style="font-size: 0.95rem; color: #2C3531; line-height: 1.6; margin: 0;">
                Planning a meetup with a group usually means someone ends up traveling much further than
                everyone else. MeetSpot looks at where each person is starting from and works out a spot
                that keeps everyone's travel time as fair and balanced as possible — instead of just
                picking the midpoint on a map.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Getting Your Fair Meeting Point")
    st.markdown(
        """
        <div class="msp-card">
            <ol style="font-size: 0.92rem; color: #2C3531; line-height: 1.7; padding-left: 1.2rem; margin: 0;">
                <li><b>Add each person</b> in your group along with their starting location or a nearby landmark, on the <b>Find Fair Spot</b> tab.</li>
                <li><b>Set your preferences</b> — cuisine, atmosphere, and budget — plus the date you're planning to meet.</li>
                <li><b>Click "Calculate Fair Meeting Point"</b> and MeetSpot will balance everyone's travel time and pick the fairest spot to meet.</li>
                <li><b>Browse the results</b> — you'll see the recommended location, a map of everyone's routes, nearby places to eat or hang out, and the weather forecast for your meeting day.</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Saving Your Meetings & Favorites")
    st.markdown(
        """
        <div class="msp-card">
            <p style="font-size: 0.92rem; color: #2C3531; line-height: 1.6; margin: 0;">
                Want to keep track of your meetups? Sign in or create an account from the <b>Account</b> tab.
                Once you're logged in, you can save any meeting you calculate to <b>My Saved Meetings</b>, and
                mark venues you like as <b>Saved Favorites</b> so they're easy to find again later.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Tab 5: Account
with tab_account:
    render_auth_section()
