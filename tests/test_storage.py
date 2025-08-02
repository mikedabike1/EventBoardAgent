"""Tests for event storage functionality."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from src.gaming_events_scraper.models import GamingEvent
from src.gaming_events_scraper.storage import EventStorage


class TestEventStorage:
    """Test cases for EventStorage class."""
    
    def setup_method(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = EventStorage(self.temp_dir)
        
        # Create sample events for testing
        self.sample_events = [
            GamingEvent(
                title="Friday Night Magic",
                game_system="MTG",
                venue="Card Kingdom",
                date="2024-07-18",
                start_time="19:00",
                source="facebook",
                extracted_at="2024-07-15T10:30:00Z"
            ),
            GamingEvent(
                title="Warhammer Tournament",
                game_system="Warhammer",
                venue="Games Workshop",
                date="2024-07-20",
                start_time="10:00",
                source="discord",
                extracted_at="2024-07-15T10:30:00Z"
            ),
            GamingEvent(
                title="D&D Adventure League",
                game_system="D&D",
                venue="Community Center",
                date="2024-07-22",
                start_time="18:30",
                source="facebook",
                extracted_at="2024-07-15T10:30:00Z"
            )
        ]
    
    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_save_events_with_filename(self):
        """Test saving events with specified filename."""
        filename = "test_events.json"
        filepath = self.storage.save_events(self.sample_events, filename)
        
        assert Path(filepath).exists()
        assert Path(filepath).name == filename
        
        # Verify file contents
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert data["total_events"] == 3
        assert len(data["events"]) == 3
        assert "scraped_at" in data
    
    def test_save_events_auto_filename(self):
        """Test saving events with auto-generated filename."""
        filepath = self.storage.save_events(self.sample_events)
        
        assert Path(filepath).exists()
        assert "gaming_events_" in Path(filepath).name
        assert Path(filepath).suffix == ".json"
    
    def test_save_empty_events(self):
        """Test saving empty events list."""
        filepath = self.storage.save_events([])
        
        assert Path(filepath).exists()
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert data["total_events"] == 0
        assert data["events"] == []
    
    def test_load_events(self):
        """Test loading events from file."""
        filename = "test_events.json"
        self.storage.save_events(self.sample_events, filename)
        
        loaded_events = self.storage.load_events(filename)
        
        assert len(loaded_events) == 3
        assert loaded_events[0].title == "Friday Night Magic"
        assert loaded_events[1].game_system == "Warhammer"
        assert loaded_events[2].venue == "Community Center"
    
    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file returns empty list."""
        loaded_events = self.storage.load_events("nonexistent.json")
        assert loaded_events == []
    
    def test_get_all_events(self):
        """Test getting all events from multiple files."""
        # Save events to multiple files
        self.storage.save_events(self.sample_events[:2], "file1.json")
        self.storage.save_events(self.sample_events[2:], "file2.json")
        
        all_events = self.storage.get_all_events()
        
        assert len(all_events) == 3
        titles = [event.title for event in all_events]
        assert "Friday Night Magic" in titles
        assert "Warhammer Tournament" in titles
        assert "D&D Adventure League" in titles
    
    def test_get_events_by_game(self):
        """Test filtering events by game system."""
        self.storage.save_events(self.sample_events, "test_events.json")
        
        mtg_events = self.storage.get_events_by_game("MTG")
        assert len(mtg_events) == 1
        assert mtg_events[0].title == "Friday Night Magic"
        
        warhammer_events = self.storage.get_events_by_game("Warhammer")
        assert len(warhammer_events) == 1
        assert warhammer_events[0].title == "Warhammer Tournament"
        
        # Test case insensitive matching
        dnd_events = self.storage.get_events_by_game("d&d")
        assert len(dnd_events) == 1
        assert dnd_events[0].title == "D&D Adventure League"
    
    def test_get_upcoming_events(self):
        """Test getting upcoming events within date range."""
        # Create events with dates relative to today
        today = datetime.now().date()
        future_events = [
            GamingEvent(
                title="Event Tomorrow",
                game_system="MTG",
                venue="Store",
                date=(today + timedelta(days=1)).isoformat(),
                start_time="19:00",
                source="test"
            ),
            GamingEvent(
                title="Event Next Week",
                game_system="MTG",
                venue="Store",
                date=(today + timedelta(days=7)).isoformat(),
                start_time="19:00",
                source="test"
            ),
            GamingEvent(
                title="Event Far Future",
                game_system="MTG",
                venue="Store",
                date=(today + timedelta(days=100)).isoformat(),
                start_time="19:00",
                source="test"
            ),
            GamingEvent(
                title="Event Yesterday",
                game_system="MTG",
                venue="Store",
                date=(today - timedelta(days=1)).isoformat(),
                start_time="19:00",
                source="test"
            )
        ]
        
        self.storage.save_events(future_events, "future_events.json")
        
        # Get events in next 30 days
        upcoming = self.storage.get_upcoming_events(30)
        
        # Should include tomorrow and next week, but not far future or yesterday
        assert len(upcoming) == 2
        titles = [event.title for event in upcoming]
        assert "Event Tomorrow" in titles
        assert "Event Next Week" in titles
        assert "Event Far Future" not in titles
        assert "Event Yesterday" not in titles
        
        # Test with smaller range
        upcoming_week = self.storage.get_upcoming_events(7)
        assert len(upcoming_week) == 2  # Tomorrow and next week (day 7)
    
    def test_get_events_by_venue(self):
        """Test filtering events by venue."""
        self.storage.save_events(self.sample_events, "test_events.json")
        
        card_kingdom_events = self.storage.get_events_by_venue("Card Kingdom")
        assert len(card_kingdom_events) == 1
        assert card_kingdom_events[0].title == "Friday Night Magic"
        
        # Test partial matching (case insensitive)
        workshop_events = self.storage.get_events_by_venue("workshop")
        assert len(workshop_events) == 1
        assert workshop_events[0].title == "Warhammer Tournament"
    
    def test_get_events_by_source(self):
        """Test filtering events by source."""
        self.storage.save_events(self.sample_events, "test_events.json")
        
        facebook_events = self.storage.get_events_by_source("facebook")
        assert len(facebook_events) == 2
        
        discord_events = self.storage.get_events_by_source("discord")
        assert len(discord_events) == 1
        assert discord_events[0].title == "Warhammer Tournament"
    
    def test_list_files(self):
        """Test listing all event files."""
        self.storage.save_events(self.sample_events[:1], "file1.json")
        self.storage.save_events(self.sample_events[1:2], "file2.json")
        
        files = self.storage.list_files()
        
        assert len(files) == 2
        assert "file1.json" in files
        assert "file2.json" in files
    
    def test_delete_file(self):
        """Test deleting event files."""
        filename = "test_events.json"
        self.storage.save_events(self.sample_events, filename)
        
        # Verify file exists
        assert filename in self.storage.list_files()
        
        # Delete file
        result = self.storage.delete_file(filename)
        assert result is True
        
        # Verify file is gone
        assert filename not in self.storage.list_files()
    
    def test_delete_nonexistent_file(self):
        """Test deleting nonexistent file returns False."""
        result = self.storage.delete_file("nonexistent.json")
        assert result is False
    
    def test_events_sorted_by_date(self):
        """Test that upcoming events are sorted by date."""
        today = datetime.now().date()
        events_unsorted = [
            GamingEvent(
                title="Event Day 5",
                game_system="MTG",
                venue="Store",
                date=(today + timedelta(days=5)).isoformat(),
                start_time="19:00",
                source="test"
            ),
            GamingEvent(
                title="Event Day 1",
                game_system="MTG",
                venue="Store",
                date=(today + timedelta(days=1)).isoformat(),
                start_time="19:00",
                source="test"
            ),
            GamingEvent(
                title="Event Day 3",
                game_system="MTG",
                venue="Store",
                date=(today + timedelta(days=3)).isoformat(),
                start_time="19:00",
                source="test"
            )
        ]
        
        self.storage.save_events(events_unsorted, "unsorted_events.json")
        upcoming = self.storage.get_upcoming_events(10)
        
        # Should be sorted by date
        assert upcoming[0].title == "Event Day 1"
        assert upcoming[1].title == "Event Day 3"
        assert upcoming[2].title == "Event Day 5"