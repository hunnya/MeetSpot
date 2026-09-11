"""Favorites UI: lists favorite venues saved by the authenticated user."""
import streamlit as st
from auth.authentication import is_authenticated, get_current_user
from database.database import get_db
from database.models import Favorite


def render_favorites_section():
    """Renders the saved favorite venues list for the current logged-in user."""
    st.markdown("### ⭐ My Favorite Places")

    if not is_authenticated():
        st.warning("🔒 Please sign in from the **Account** tab to view and manage your favorite places.")
        return

    user = get_current_user()

    with get_db() as db:
        favorites = (
            db.query(Favorite)
            .filter(Favorite.user_id == user["id"])
            .order_by(Favorite.created_at.desc())
            .all()
        )

        if not favorites:
            st.info("You have no favorite spots saved yet. When you calculate a meeting point, click '⭐ Favorite' next to any recommended venue!")
            return

        st.write(f"You have **{len(favorites)}** favorite place(s) saved:")

        for f in favorites:
            col_info, col_act = st.columns([3.5, 1])
            with col_info:
                st.markdown(
                    f"""
                    <div class="msp-card" style="margin-bottom: 0.8rem; padding: 1rem 1.2rem;">
                        <div style="display: flex; justify-content: space-between; align-items: baseline;">
                            <h4 style="margin: 0; color: #0F172A;">⭐ {f.place_name}</h4>
                            <span class="msp-pill-blue">{f.place_type.capitalize() if f.place_type else 'Venue'}</span>
                        </div>
                        <div style="font-size: 0.9rem; color: #475569; margin-top: 0.3rem;">
                            📍 {f.address or f"Coordinates: {f.latitude:.4f}, {f.longitude:.4f}"}
                        </div>
                        <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.3rem;">
                            Saved on {f.created_at.strftime('%B %d, %Y')} • {f.rating_or_match or ''}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_act:
                st.write("")
                if st.button("🗑️ Remove", key=f"del_fav_{f.id}", use_container_width=True):
                    _delete_favorite(f.id)
                    st.rerun()


def _delete_favorite(favorite_id: int):
    """Deletes a favorite place by id."""
    try:
        with get_db() as db:
            fav = db.query(Favorite).filter(Favorite.id == favorite_id).first()
            if fav:
                db.delete(fav)
        st.success("Removed from favorites.")
    except Exception as exc:
        st.error(f"Failed to remove favorite: {exc}")
