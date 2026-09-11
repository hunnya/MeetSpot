"""SQLAlchemy models for MeetSpot."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def _utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=_utc_now, nullable=False)

    saved_meetings = relationship("SavedMeeting", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


class SavedMeeting(Base):
    __tablename__ = "saved_meetings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    meeting_name = Column(String(200), nullable=False)
    meeting_date = Column(String(50), nullable=True)
    fair_latitude = Column(Float, nullable=False)
    fair_longitude = Column(Float, nullable=False)
    fair_score = Column(Float, nullable=True)
    fair_address = Column(Text, nullable=True)
    fair_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utc_now, nullable=False)

    user = relationship("User", back_populates="saved_meetings")
    members = relationship("MeetingMember", back_populates="saved_meeting", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SavedMeeting(id={self.id}, name='{self.meeting_name}', user_id={self.user_id})>"


class MeetingMember(Base):
    __tablename__ = "meeting_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    saved_meeting_id = Column(Integer, ForeignKey("saved_meetings.id", ondelete="CASCADE"), nullable=False)
    member_name = Column(String(120), nullable=False)
    address = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    travel_time_min = Column(Float, nullable=True)

    saved_meeting = relationship("SavedMeeting", back_populates="members")

    def __repr__(self):
        return f"<MeetingMember(id={self.id}, name='{self.member_name}', meeting_id={self.saved_meeting_id})>"


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    place_name = Column(String(200), nullable=False)
    place_type = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text, nullable=True)
    rating_or_match = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utc_now, nullable=False)

    user = relationship("User", back_populates="favorites")

    def __repr__(self):
        return f"<Favorite(id={self.id}, name='{self.place_name}', user_id={self.user_id})>"
