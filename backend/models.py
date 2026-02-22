from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from .database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    city = Column(String)
    state = Column(String)
    website = Column(String)
    discord_url = Column(String)
    facebook_url = Column(String)
    created_at = Column(DateTime, default=func.now())

    events = relationship("Event", back_populates="store")


class GameSystem(Base):
    __tablename__ = "game_systems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    publisher = Column(String)
    created_at = Column(DateTime, default=func.now())

    events = relationship("Event", back_populates="game_system")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    game_system_id = Column(Integer, ForeignKey("game_systems.id"), nullable=False)
    title = Column(String, nullable=False)
    date = Column(Date, nullable=False, index=True)
    start_time = Column(String)
    description = Column(Text)
    source_url = Column(String)
    source_type = Column(String)
    last_seen_at = Column(DateTime)
    is_expired = Column(Boolean, default=False, nullable=False)
    dedup_hash = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    store = relationship("Store", back_populates="events")
    game_system = relationship("GameSystem", back_populates="events")


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    store_ids = Column(Text, default="[]")
    game_system_ids = Column(Text, default="[]")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
