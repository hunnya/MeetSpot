"""UI package for MeetSpot."""
from ui.styles import MODERN_CSS, render_hero
from ui.auth_ui import render_auth_section
from ui.meeting_ui import render_create_meeting_form
from ui.results_ui import render_results_section
from ui.history_ui import render_history_section
from ui.favorites_ui import render_favorites_section

__all__ = [
    "MODERN_CSS",
    "render_hero",
    "render_auth_section",
    "render_create_meeting_form",
    "render_results_section",
    "render_history_section",
    "render_favorites_section",
]
