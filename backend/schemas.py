import json
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, field_validator


class StoreOut(BaseModel):
    id: int
    name: str
    city: str | None = None
    state: str | None = None
    website: str | None = None
    discord_url: str | None = None
    facebook_url: str | None = None

    model_config = {"from_attributes": True}


class GameSystemOut(BaseModel):
    id: int
    name: str
    slug: str
    publisher: str | None = None

    model_config = {"from_attributes": True}


class EventOut(BaseModel):
    id: int
    title: str
    date: date
    start_time: str | None = None
    description: str | None = None
    source_url: str | None = None
    source_type: str | None = None
    last_seen_at: datetime | None = None
    store: StoreOut
    game_system: GameSystemOut

    model_config = {"from_attributes": True}


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
