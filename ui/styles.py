"""Modern executive Map-Blue styling and custom CSS for MeetSpot."""

MODERN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--msp-slate-900);
}
.stApp {
    background-color: var(--msp-slate-50);
}
html, body, [class*="css"], .stMarkdown, p, span, label, h1, h2, h3, h4, h5, h6, .stCaption {
    color: #0F172A !important;  /* Dark slate text */
}
/* Base page background */
.stApp {
    background-color: #F8FAFC !important;
}
/* Card backgrounds and text */
.msp-card, .msp-venue-card, div[data-testid="stForm"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
}
:root {
    --msp-blue-600: #2563EB;
    --msp-blue-700: #1D4ED8;
    --msp-blue-900: #1E3A8A;
    --msp-blue-50: #EFF6FF;
    --msp-emerald-500: #10B981;
    --msp-emerald-50: #ECFDF5;
    --msp-amber-500: #F59E0B;
    --msp-slate-50: #F8FAFC;
    --msp-slate-100: #F1F5F9;
    --msp-slate-200: #E2E8F0;
    --msp-slate-600: #475569;
    --msp-slate-700: #334155;
    --msp-slate-900: #0F172A;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--msp-slate-900);
}

.stApp {
    background-color: var(--msp-slate-50);
}

/* Hero Header */
.msp-hero {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
    border-radius: 16px;
    padding: 2.2rem 2.4rem;
    color: #FFFFFF;
    margin-bottom: 2rem;
    box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.msp-badge {
    display: inline-flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(8px);
    color: #FFFFFF;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 0.3rem 0.85rem;
    border-radius: 9999px;
    margin-bottom: 0.8rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.msp-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.15;
    margin: 0 0 0.4rem 0;
    color: #FFFFFF;
}

.msp-tagline {
    font-size: 1.25rem;
    font-weight: 600;
    color: #93C5FD;
    margin-bottom: 0.6rem;
}

.msp-description {
    font-size: 1.0rem;
    line-height: 1.5;
    color: #E0E7FF;
    max-width: 680px;
    margin: 0;
}

/* Polished Card */
.msp-card {
    background: #FFFFFF;
    border: 1px solid var(--msp-slate-200);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.msp-card:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
}

/* Highlight Card */
.msp-highlight-card {
    background: #FFFFFF;
    border: 1px solid #BFDBFE;
    border-left: 5px solid var(--msp-blue-600);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.4rem;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.06);
}

/* Fairness Winner Card */
.msp-winner-card {
    background: linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%);
    border: 1.5px solid #86EFAC;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.4rem;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.08);
}

/* Stat Box */
.msp-stat {
    background: var(--msp-slate-50);
    border: 1px solid var(--msp-slate-200);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
}

.msp-stat-val {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--msp-blue-700);
    line-height: 1.2;
}

.msp-stat-lbl {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--msp-slate-600);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-top: 0.2rem;
}

/* Badges & Pills */
.msp-pill-blue {
    display: inline-block;
    background: var(--msp-blue-50);
    color: var(--msp-blue-700);
    font-weight: 600;
    font-size: 0.8rem;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    border: 1px solid #DBEAFE;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}

.msp-pill-green {
    display: inline-block;
    background: var(--msp-emerald-50);
    color: #047857;
    font-weight: 600;
    font-size: 0.8rem;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    border: 1px solid #A7F3D0;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}

.msp-demo-tag {
    background: #FEF3C7;
    border: 1px solid #FCD34D;
    color: #92400E;
    font-weight: 700;
    font-size: 0.82rem;
    padding: 0.35rem 0.85rem;
    border-radius: 8px;
    display: inline-block;
    margin-bottom: 1rem;
}

/* Streamlit Widget Polish */
div[data-testid="stForm"] {
    background: #FFFFFF;
    border: 1px solid var(--msp-slate-200);
    border-radius: 16px;
    padding: 1.8rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.stButton button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.25rem !important;
    transition: all 0.15s ease !important;
}

.stButton button[kind="primary"] {
    background: var(--msp-blue-600) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25) !important;
}

.stButton button[kind="primary"]:hover {
    background: var(--msp-blue-700) !important;
    box-shadow: 0 6px 14px rgba(37, 99, 235, 0.35) !important;
}

/* Custom Venue Card */
.msp-venue-card {
    background: #FFFFFF;
    border: 1px solid var(--msp-slate-200);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.msp-venue-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--msp-slate-900);
    margin-bottom: 0.3rem;
}

.msp-venue-meta {
    font-size: 0.9rem;
    color: var(--msp-slate-600);
    margin-bottom: 0.6rem;
}

.msp-venue-reason {
    font-size: 0.92rem;
    color: var(--msp-slate-700);
    background: var(--msp-slate-50);
    border-left: 3px solid var(--msp-blue-600);
    padding: 0.5rem 0.75rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.8rem;
}
</style>
"""


def render_hero():
    """Renders the top branding hero banner."""
    import streamlit as st
    st.markdown(
        """
        <div class="msp-hero">
            <div class="msp-badge">📍 Location-Based Fairness Engine</div>
            <div class="msp-title">MeetSpot</div>
            <div class="msp-tagline">"Stop arguing about where to meet."</div>
            <p class="msp-description">
                MeetSpot finds the fairest meeting point based on how long everyone actually has to travel — 
                balancing real road travel times, recommending top-rated nearby spots with AI, and checking the weather for your day.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
