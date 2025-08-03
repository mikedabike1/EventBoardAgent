"""Data models for gaming events."""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any, Optional


@dataclass
class GamingEvent:
    """Structured data for a gaming event."""

    title: str
    game_system: str  # e.g., "MTG", "Warhammer 40K", "D&D"
    venue: str  # Store/location name
    date: str  # ISO format date
    start_time: str  # Time in HH:MM format
    source: str  # "facebook" or "discord"
    source_url: Optional[str] = None
    description: Optional[str] = None
    extracted_at: Optional[str] = None

    def __post_init__(self):
        """Set extracted_at timestamp if not provided."""
        if self.extracted_at is None:
            self.extracted_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GamingEvent":
        """Create event from dictionary."""
        return cls(**data)
