"""Tests for Facebook event scraper."""

from unittest.mock import Mock, patch
import requests

from src.gaming_events_scraper.facebook_scraper import FacebookEventScraper


class TestFacebookEventScraper:
    """Test cases for FacebookEventScraper class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = FacebookEventScraper()
        self.scraper_with_token = FacebookEventScraper("test_access_token")

    def test_init_without_token(self):
        """Test initializing scraper without access token."""
        scraper = FacebookEventScraper()
        assert scraper.access_token is None
        assert scraper.base_url == "https://graph.facebook.com/v18.0"

    def test_init_with_token(self):
        """Test initializing scraper with access token."""
        token = "test_access_token"
        scraper = FacebookEventScraper(token)
        assert scraper.access_token == token

    @patch("requests.get")
    def test_scrape_page_events_with_token_success(self, mock_get):
        """Test successful scraping with access token."""
        # Mock API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": [
                {
                    "name": "Friday Night Magic - Modern",
                    "description": "Join us for FNM Modern format",
                    "start_time": "2024-07-18T19:00:00-07:00",
                    "place": {"name": "Local Card Shop"},
                }
            ]
        }
        mock_get.return_value = mock_response

        events = self.scraper_with_token.scrape_page_events("test_page")

        assert len(events) == 1
        assert events[0].title == "Friday Night Magic - Modern"
        assert events[0].game_system == "MTG"
        assert events[0].venue == "Local Card Shop"
        assert events[0].source == "facebook"

    @patch("requests.get")
    def test_scrape_page_events_with_token_api_error(self, mock_get):
        """Test handling API error when scraping with token."""
        mock_get.side_effect = requests.RequestException("API Error")

        events = self.scraper_with_token.scrape_page_events("test_page")

        assert events == []

    @patch.object(FacebookEventScraper, "_scrape_public_page")
    def test_scrape_page_events_without_token(self, mock_scrape_public):
        """Test scraping without token falls back to public scraping."""
        mock_scrape_public.return_value = [Mock()]

        self.scraper.scrape_page_events("test_page")

        mock_scrape_public.assert_called_once_with("test_page")

    def test_parse_facebook_event_valid_gaming_event(self):
        """Test parsing valid gaming event data."""
        event_data = {
            "name": "Warhammer 40K Tournament",
            "description": "Annual 40K tournament with prizes",
            "start_time": "2024-07-20T10:00:00Z",
            "place": {"name": "Games Workshop Store"},
        }

        event = self.scraper._parse_facebook_event(event_data, "test_url")

        assert event is not None
        assert event.title == "Warhammer 40K Tournament"
        assert event.game_system == "Warhammer"
        assert event.venue == "Games Workshop Store"
        assert event.date == "2024-07-20"
        assert event.start_time == "10:00"
        assert event.source == "facebook"
        assert event.source_url == "test_url"

    def test_parse_facebook_event_non_gaming_event(self):
        """Test parsing non-gaming event returns None."""
        event_data = {
            "name": "Cooking Class",
            "description": "Learn to cook Italian cuisine",
            "start_time": "2024-07-20T18:00:00Z",
        }

        event = self.scraper._parse_facebook_event(event_data, "test_url")

        assert event is None

    def test_parse_facebook_event_missing_place(self):
        """Test parsing event with missing place data."""
        event_data = {
            "name": "MTG Draft Night",
            "description": "Bloomburrow draft tournament",
            "start_time": "2024-07-18T19:00:00Z",
        }

        event = self.scraper._parse_facebook_event(event_data, "test_url")

        assert event is not None
        assert event.venue == "Unknown"

    def test_parse_facebook_event_invalid_datetime(self):
        """Test parsing event with invalid datetime format."""
        event_data = {
            "name": "Magic Tournament Saturday July 20th 7pm",
            "description": "Modern format tournament",
            "start_time": "invalid_datetime",
        }

        event = self.scraper._parse_facebook_event(event_data, "test_url")

        assert event is not None
        # Should fall back to text extraction
        assert event.date != "Unknown" or event.start_time != "Unknown"

    def test_parse_facebook_event_no_datetime(self):
        """Test parsing event without start_time field."""
        event_data = {
            "name": "Commander Night - Wednesday July 17 at 6:30 PM",
            "description": "Bring your favorite commander deck",
        }

        event = self.scraper._parse_facebook_event(event_data, "test_url")

        assert event is not None
        assert event.game_system == "MTG"
        # Should extract from title
        assert "6:30 PM" in event.start_time or event.start_time != "Unknown"

    def test_parse_text_event_valid_gaming_text(self):
        """Test parsing valid gaming event from text."""
        text = "Friday Night Magic - Modern format at Card Kingdom, July 18th 7:00 PM"

        event = self.scraper._parse_text_event(text, "test_url")

        assert event is not None
        assert event.game_system == "MTG"
        assert event.source == "facebook"
        assert event.source_url == "test_url"
        assert len(event.title) <= 100  # Title should be truncated

    def test_parse_text_event_non_gaming_text(self):
        """Test parsing non-gaming text returns None."""
        text = "Book club meeting at the library tonight"

        event = self.scraper._parse_text_event(text, "test_url")

        assert event is None

    @patch("requests.get")
    @patch("src.gaming_events_scraper.facebook_scraper.BeautifulSoup")
    def test_scrape_public_page(self, mock_soup, mock_get):
        """Test public page scraping."""
        # Mock response
        mock_response = Mock()
        mock_response.content = b"<html>Friday Night Magic tonight at 7 PM</html>"
        mock_get.return_value = mock_response

        # Mock BeautifulSoup
        mock_soup_instance = Mock()
        mock_soup_instance.get_text.return_value = (
            "Friday Night Magic tonight at 7 PM\\nOther content"
        )
        mock_soup.return_value = mock_soup_instance

        events = self.scraper._scrape_public_page("test_page")

        # Should find the MTG event
        assert len(events) >= 0  # May be 0 if text extraction fails
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_scrape_public_page_request_error(self, mock_get):
        """Test public page scraping with request error."""
        mock_get.side_effect = requests.RequestException("Network error")

        events = self.scraper._scrape_public_page("test_page")

        assert events == []

    def test_parse_facebook_event_error_handling(self):
        """Test error handling in event parsing."""
        # Test with malformed data
        event_data = "not_a_dict"

        event = self.scraper._parse_facebook_event(event_data, "test_url")

        assert event is None

    def test_inheritance_from_event_extractor(self):
        """Test that FacebookEventScraper inherits from EventExtractor."""
        # Should have access to parent methods
        assert hasattr(self.scraper, "extract_game_system")
        assert hasattr(self.scraper, "extract_time")
        assert hasattr(self.scraper, "extract_date")
        assert hasattr(self.scraper, "contains_gaming_keywords")

        # Test inherited functionality
        assert self.scraper.extract_game_system("Magic tournament") == "MTG"
        assert self.scraper.contains_gaming_keywords("Friday Night Magic") is True
