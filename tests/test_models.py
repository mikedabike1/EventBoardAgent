"""Tests for gaming event models."""

import pytest
from datetime import datetime, timezone

from src.gaming_events_scraper.models import GamingEvent


class TestGamingEvent:
    """Test cases for GamingEvent model."""
    
    def test_create_event(self):
        """Test creating a basic gaming event."""
        event = GamingEvent(
            title="Friday Night Magic",
            game_system="MTG",
            venue="Local Card Shop",
            date="2024-07-18",
            start_time="19:00",
            source="facebook"
        )
        
        assert event.title == "Friday Night Magic"
        assert event.game_system == "MTG"
        assert event.venue == "Local Card Shop"
        assert event.date == "2024-07-18"
        assert event.start_time == "19:00"
        assert event.source == "facebook"
        assert event.extracted_at is not None
    
    def test_create_event_with_optional_fields(self):
        """Test creating event with all optional fields."""
        event = GamingEvent(
            title="Warhammer Tournament",
            game_system="Warhammer",
            venue="Games Workshop",
            date="2024-08-15",
            start_time="10:00",
            source="discord",
            source_url="https://discord.com/channels/123/456/789",
            description="Annual Warhammer 40K tournament",
            extracted_at="2024-07-15T10:30:00Z"
        )
        
        assert event.source_url == "https://discord.com/channels/123/456/789"
        assert event.description == "Annual Warhammer 40K tournament"
        assert event.extracted_at == "2024-07-15T10:30:00Z"
    
    def test_auto_extracted_at(self):
        """Test that extracted_at is automatically set."""
        before = datetime.now(timezone.utc)
        
        event = GamingEvent(
            title="Test Event",
            game_system="MTG",
            venue="Test Venue",
            date="2024-07-18",
            start_time="19:00",
            source="test"
        )
        
        after = datetime.now(timezone.utc)
        extracted_time = datetime.fromisoformat(event.extracted_at.replace('Z', '+00:00'))
        
        assert before <= extracted_time <= after
    
    def test_to_dict(self):
        """Test converting event to dictionary."""
        event = GamingEvent(
            title="D&D Session",
            game_system="D&D",
            venue="Community Center",
            date="2024-07-20",
            start_time="18:30",
            source="facebook",
            description="Weekly D&D adventure"
        )
        
        event_dict = event.to_dict()
        
        assert isinstance(event_dict, dict)
        assert event_dict["title"] == "D&D Session"
        assert event_dict["game_system"] == "D&D"
        assert event_dict["venue"] == "Community Center"
        assert event_dict["description"] == "Weekly D&D adventure"
        assert "extracted_at" in event_dict
    
    def test_from_dict(self):
        """Test creating event from dictionary."""
        event_data = {
            "title": "Pokemon League",
            "game_system": "Pokemon",
            "venue": "Trading Card Store",
            "date": "2024-07-25",
            "start_time": "17:00",
            "source": "facebook",
            "source_url": "https://facebook.com/event/123",
            "description": "Weekly Pokemon league battles",
            "extracted_at": "2024-07-15T10:30:00Z"
        }
        
        event = GamingEvent.from_dict(event_data)
        
        assert event.title == "Pokemon League"
        assert event.game_system == "Pokemon"
        assert event.venue == "Trading Card Store"
        assert event.source_url == "https://facebook.com/event/123"
        assert event.description == "Weekly Pokemon league battles"
        assert event.extracted_at == "2024-07-15T10:30:00Z"
    
    def test_round_trip_conversion(self):
        """Test converting to dict and back maintains data integrity."""
        original_event = GamingEvent(
            title="Yu-Gi-Oh Tournament",
            game_system="Yu-Gi-Oh",
            venue="Hobby Shop",
            date="2024-08-01",
            start_time="14:00",
            source="discord",
            source_url="https://discord.com/channels/111/222/333",
            description="Monthly Yu-Gi-Oh tournament"
        )
        
        event_dict = original_event.to_dict()
        restored_event = GamingEvent.from_dict(event_dict)
        
        assert restored_event.title == original_event.title
        assert restored_event.game_system == original_event.game_system
        assert restored_event.venue == original_event.venue
        assert restored_event.date == original_event.date
        assert restored_event.start_time == original_event.start_time
        assert restored_event.source == original_event.source
        assert restored_event.source_url == original_event.source_url
        assert restored_event.description == original_event.description
        assert restored_event.extracted_at == original_event.extracted_at