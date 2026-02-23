import json
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class StoreOut(BaseModel):
    id: int
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    website: Optional[str] = None
    discord_url: Optional[str] = None
    facebook_url: Optional[str] = None

    model_config = {"from_attributes": True}


class GameSystemOut(BaseModel):
    id: int
    name: str
    slug: str
    publisher: Optional[str] = None

    model_config = {"from_attributes": True}


class EventOut(BaseModel):
    id: int
    title: str
    date: date
    start_time: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    last_seen_at: Optional[datetime] = None
    store: StoreOut
    game_system: GameSystemOut

    model_config = {"from_attributes": True}


class EventIn(BaseModel):
    store_name: str
    game_system: str
    title: str
    date: date
    time: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    last_seen_at: Optional[datetime] = None


class SubscribeIn(BaseModel):
    email: EmailStr
    store_ids: list[int] = []
    game_system_ids: list[int] = []


class SubscribeOut(BaseModel):
    id: int
    email: str
    store_ids: list[int]
    game_system_ids: list[int]
    is_active: bool

    @field_validator("store_ids", "game_system_ids", mode="before")
    @classmethod
    def parse_json_list(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    model_config = {"from_attributes": True}
