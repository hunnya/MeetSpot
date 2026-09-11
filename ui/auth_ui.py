"""Authentication UI views: Login, Registration, and User Profile."""
import streamlit as st
from auth.authentication import (
    register_user,
    authenticate_user,
    login_user,
    logout_user,
    is_authenticated,
    get_current_user,
)


def render_auth_section():
    """Renders the authentication block (Profile if logged in, or Login/Register tabs)."""
    if is_authenticated():
        user = get_current_user()
        st.markdown(
            f"""
            <div class="msp-card" style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 0.85rem; color: #64748B; text-transform: uppercase; font-weight: 600;">Active Account</span>
                    <h3 style="margin: 0.1rem 0; color: #0F172A;">👤 {user.get('name', 'User')}</h3>
                    <span style="color: #64748B; font-size: 0.9rem;">{user.get('email', '')}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Log Out", type="secondary"):
            logout_user()
            st.success("You have been logged out.")
            st.rerun()
        return

    st.markdown("### 🔐 Account & Profile")
    st.info("Log in or register to save your meetings, keep a history of group meetups, and favorite nearby venues.")

    tab_login, tab_register = st.tabs(["🔑 Log In", "📝 Create Account"])

    with tab_login:
        with st.form("login_form"):
            st.markdown("#### Welcome Back")
            email = st.text_input("Email Address", placeholder="name@example.com", key="auth_login_email")
            password = st.text_input("Password", type="password", key="auth_login_pw")
            submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

            if submitted:
                success, msg, user_data = authenticate_user(email, password)
                if success:
                    login_user(user_data)
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab_register:
        with st.form("register_form"):
            st.markdown("#### New to MeetSpot?")
            name = st.text_input("Full Name", placeholder="e.g. Hunnya Khan", key="auth_reg_name")
            reg_email = st.text_input("Email Address", placeholder="name@example.com", key="auth_reg_email")
            reg_pw = st.text_input("Password (min 6 characters)", type="password", key="auth_reg_pw")
            reg_pw_confirm = st.text_input("Confirm Password", type="password", key="auth_reg_pw_confirm")
            reg_submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)

            if reg_submitted:
                success, msg, user_data = register_user(name, reg_email, reg_pw, reg_pw_confirm)
                if success:
                    login_user(user_data)
                    st.success(f"{msg} Welcome, {name}!")
                    st.rerun()
                else:
                    st.error(msg)
