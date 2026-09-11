"""My Saved Meetings view: displays previously calculated and saved meetups."""
import streamlit as st
from auth.authentication import is_authenticated, get_current_user
from database.database import get_db
from database.models import SavedMeeting, MeetingMember


def render_history_section():
    """Renders the saved meetings list for the current logged-in user."""
    st.markdown("### 📋 My Saved Meetings")

    if not is_authenticated():
        st.warning("🔒 Please sign in from the **Account** tab to view your saved meetings.")
        return

    user = get_current_user()

    with get_db() as db:
        meetings = (
            db.query(SavedMeeting)
            .filter(SavedMeeting.user_id == user["id"])
            .order_by(SavedMeeting.created_at.desc())
            .all()
        )

        if not meetings:
            st.info("You haven't saved any meetings yet. Plan a meetup on the **Find Fair Spot** tab and click 'Save to My Meetings'!")
            return

        st.write(f"You have **{len(meetings)}** saved meeting(s):")

        for m in meetings:
            with st.expander(f"📍 {m.meeting_name} — {m.meeting_date or 'No date set'}", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Fair Meeting Point:** {m.fair_address or 'Coordinates'}")
                    st.write(f"**Coordinates:** `{m.fair_latitude:.4f}, {m.fair_longitude:.4f}`")
                    if m.fair_summary:
                        st.info(f"💡 {m.fair_summary}")

                    st.markdown("**Participants:**")
                    for member in m.members:
                        time_str = f" (~{member.travel_time_min:.0f} min)" if member.travel_time_min else ""
                        st.write(f"- **{member.member_name}**: {member.address}{time_str}")

                with col2:
                    st.caption(f"Saved: {m.created_at.strftime('%b %d, %Y')}")
                    if st.button("🗑️ Delete Meeting", key=f"del_meet_{m.id}", use_container_width=True):
                        _delete_meeting(m.id)
                        st.rerun()


def _delete_meeting(meeting_id: int):
    """Deletes a saved meeting by id."""
    try:
        with get_db() as db:
            meeting = db.query(SavedMeeting).filter(SavedMeeting.id == meeting_id).first()
            if meeting:
                db.delete(meeting)
        st.success("Meeting deleted successfully.")
    except Exception as exc:
        st.error(f"Failed to delete meeting: {exc}")
