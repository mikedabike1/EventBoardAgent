"""Event storage and management functionality."""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Optional

from .models import GamingEvent


class EventStorage:
    """Manage storage of gaming events."""

    def __init__(self, storage_dir: str = "events_data"):
        """Initialize event storage.

        Args:
            storage_dir: Directory to store event files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def save_events(
        self, events: List[GamingEvent], filename: Optional[str] = None
    ) -> str:
        """Save events to JSON file.

        Args:
            events: List of GamingEvent objects to save
            filename: Optional filename, auto-generated if not provided

        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gaming_events_{timestamp}.json"

        filepath = self.storage_dir / filename

        events_data = {
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "total_events": len(events),
            "events": [event.to_dict() for event in events],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(events_data, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(events)} events to {filepath}")
        return str(filepath)

    def load_events(self, filename: str) -> List[GamingEvent]:
        """Load events from JSON file.

        Args:
            filename: Name of file to load

        Returns:
            List of GamingEvent objects
        """
        filepath = self.storage_dir / filename

        if not filepath.exists():
            print(f"File {filepath} does not exist")
            return []

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        events = []
        for event_data in data.get("events", []):
            event = GamingEvent.from_dict(event_data)
            events.append(event)

        return events

    def get_all_events(self) -> List[GamingEvent]:
        """Get all events from all files.

        Returns:
            List of all GamingEvent objects
        """
        all_events = []

        for json_file in self.storage_dir.glob("*.json"):
            events = self.load_events(json_file.name)
            all_events.extend(events)

        return all_events

    def get_events_by_game(self, game_system: str) -> List[GamingEvent]:
        """Get all events for a specific game system.

        Args:
            game_system: Game system to filter by (e.g., "MTG", "Warhammer")

        Returns:
            List of GamingEvent objects for the specified game
        """
        all_events = self.get_all_events()
        return [e for e in all_events if e.game_system.lower() == game_system.lower()]

    def get_upcoming_events(self, days_ahead: int = 30) -> List[GamingEvent]:
        """Get events happening in the next N days.

        Args:
            days_ahead: Number of days to look ahead

        Returns:
            List of upcoming GamingEvent objects, sorted by date
        """
        all_events = self.get_all_events()

        # Filter by date
        today = datetime.now().date()
        cutoff_date = today + timedelta(days=days_ahead)

        upcoming = []
        for event in all_events:
            try:
                event_date = datetime.fromisoformat(event.date).date()
                if today <= event_date <= cutoff_date:
                    upcoming.append(event)
            except (ValueError, TypeError):
                continue  # Skip events with invalid dates

        # Sort by date
        upcoming.sort(key=lambda x: x.date)
        return upcoming

    def get_events_by_venue(self, venue: str) -> List[GamingEvent]:
        """Get all events for a specific venue.

        Args:
            venue: Venue name to filter by

        Returns:
            List of GamingEvent objects for the specified venue
        """
        all_events = self.get_all_events()
        return [e for e in all_events if venue.lower() in e.venue.lower()]

    def get_events_by_source(self, source: str) -> List[GamingEvent]:
        """Get all events from a specific source.

        Args:
            source: Source to filter by ("facebook" or "discord")

        Returns:
            List of GamingEvent objects from the specified source
        """
        all_events = self.get_all_events()
        return [e for e in all_events if e.source.lower() == source.lower()]

    def list_files(self) -> List[str]:
        """List all event files in storage directory.

        Returns:
            List of filenames
        """
        return [f.name for f in self.storage_dir.glob("*.json")]

    def delete_file(self, filename: str) -> bool:
        """Delete an event file.

        Args:
            filename: Name of file to delete

        Returns:
            True if file was deleted, False if file didn't exist
        """
        filepath = self.storage_dir / filename
        if filepath.exists():
            filepath.unlink()
            return True
        return False
