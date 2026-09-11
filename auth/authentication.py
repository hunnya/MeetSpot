"""Secure authentication routines and session management for MeetSpot."""
import re
from typing import Optional, Tuple
import bcrypt
import streamlit as st

from database.database import get_db
from database.models import User


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verifies a plaintext password against the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def is_valid_email(email: str) -> bool:
    """Basic RFC-like regex validation for email."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return bool(re.match(pattern, email.strip()))


def register_user(name: str, email: str, password: str, confirm_password: str) -> Tuple[bool, str, Optional[dict]]:
    """Registers a new user into the database."""
    name = name.strip()
    email = email.strip().lower()

    if not name:
        return False, "Please provide your full name.", None
    if not is_valid_email(email):
        return False, "Please enter a valid email address.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None
    if password != confirm_password:
        return False, "Passwords do not match.", None

    with get_db() as db:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return False, "An account with this email already exists.", None

        pw_hash = hash_password(password)
        new_user = User(name=name, email=email, password_hash=pw_hash)
        db.add(new_user)
        db.flush()
        user_data = {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
        }
        return True, "Account registered successfully!", user_data


def authenticate_user(email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
    """Authenticates a user by email and password."""
    email = email.strip().lower()
    if not email or not password:
        return False, "Email and password are required.", None

    with get_db() as db:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "Invalid email or password.", None

        if not verify_password(password, user.password_hash):
            return False, "Invalid email or password.", None

        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
        return True, "Login successful!", user_data


def init_session_auth():
    """Initializes authentication state in Streamlit session state."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None


def login_user(user_data: dict):
    """Stores user information in session state."""
    st.session_state.authenticated = True
    st.session_state.current_user = user_data


def logout_user():
    """Logs out the active user."""
    st.session_state.authenticated = False
    st.session_state.current_user = None


def is_authenticated() -> bool:
    """Checks whether a user is currently logged in."""
    return st.session_state.get("authenticated", False) and st.session_state.get("current_user") is not None


def get_current_user() -> Optional[dict]:
    """Retrieves the current logged in user dictionary."""
    return st.session_state.get("current_user")
