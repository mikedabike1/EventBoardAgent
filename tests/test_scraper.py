"""Tests for main scraper orchestrator."""

from unittest.mock import Mock, patch

from src.gaming_events_scraper.scraper import GamingEventsScraper
from src.gaming_events_scraper.models import GamingEvent


class TestGamingEventsScraper:
    """Test cases for GamingEventsScraper class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = GamingEventsScraper(
            facebook_token="test_fb_token",
            discord_token="test_discord_token",
            storage_dir="test_storage",
        )

        # Create sample events for testing
        self.sample_events = [
            GamingEvent(
                title="Friday Night Magic",
                game_system="MTG",
                venue="Card Shop",
                date="2024-07-18",
                start_time="19:00",
                source="facebook",
            ),
            GamingEvent(
                title="Warhammer Tournament",
                game_system="Warhammer",
                venue="Games Workshop",
                date="2024-07-20",
                start_time="10:00",
                source="discord",
            ),
        ]

    def test_init(self):
        """Test scraper initialization."""
        assert self.scraper.facebook_scraper is not None
        assert self.scraper.discord_scraper is not None
        assert self.scraper.storage is not None

        # Test with no tokens
        scraper = GamingEventsScraper()
        assert scraper.facebook_scraper.access_token is None
        assert scraper.discord_scraper.bot_token is None

    @patch.object(GamingEventsScraper, "_print_summary")
    def test_scrape_all_sources_facebook_only(self, mock_print):
        """Test scraping only Facebook sources."""
        # Mock Facebook scraper
        self.scraper.facebook_scraper.scrape_page_events = Mock(
            return_value=[self.sample_events[0]]
        )

        facebook_pages = ["test_page"]
        events = self.scraper.scrape_all_sources(facebook_pages=facebook_pages)

        assert len(events) == 1
        assert events[0].title == "Friday Night Magic"
        self.scraper.facebook_scraper.scrape_page_events.assert_called_once_with(
            "test_page"
        )

    def test_scrape_all_sources_facebook_error(self):
        """Test handling Facebook scraping errors."""
        # Mock Facebook scraper to raise exception
        self.scraper.facebook_scraper.scrape_page_events = Mock(
            side_effect=Exception("Facebook API error")
        )

        facebook_pages = ["test_page"]
        events = self.scraper.scrape_all_sources(facebook_pages=facebook_pages)

        assert events == []

    @patch("src.gaming_events_scraper.scraper.DISCORD_AVAILABLE", True)
    @patch("asyncio.run")
    def test_scrape_all_sources_discord_only(self, mock_asyncio_run):
        """Test scraping only Discord sources."""
        # Mock Discord scraping
        mock_asyncio_run.return_value = [self.sample_events[1]]

        discord_servers = [{"guild_id": 12345, "channels": ["events"]}]
        events = self.scraper.scrape_all_sources(discord_servers=discord_servers)

        assert len(events) == 1
        assert events[0].title == "Warhammer Tournament"
        mock_asyncio_run.assert_called_once()

    @patch("src.gaming_events_scraper.scraper.DISCORD_AVAILABLE", False)
    def test_scrape_all_sources_discord_unavailable(self):
        """Test Discord scraping when discord.py is unavailable."""
        discord_servers = [{"guild_id": 12345}]
        events = self.scraper.scrape_all_sources(discord_servers=discord_servers)

        assert events == []

    @patch("asyncio.run")
    def test_scrape_all_sources_discord_error(self, mock_asyncio_run):
        """Test handling Discord scraping errors."""
        mock_asyncio_run.side_effect = Exception("Discord connection error")

        discord_servers = [{"guild_id": 12345}]
        events = self.scraper.scrape_all_sources(discord_servers=discord_servers)

        assert events == []

    def test_scrape_all_sources_both_platforms(self):
        """Test scraping from both Facebook and Discord."""
        # Mock both scrapers
        self.scraper.facebook_scraper.scrape_page_events = Mock(
            return_value=[self.sample_events[0]]
        )

        with (
            patch("src.gaming_events_scraper.scraper.DISCORD_AVAILABLE", True),
            patch("asyncio.run", return_value=[self.sample_events[1]]),
        ):

            facebook_pages = ["test_page"]
            discord_servers = [{"guild_id": 12345}]

            events = self.scraper.scrape_all_sources(
                facebook_pages=facebook_pages, discord_servers=discord_servers
            )

            assert len(events) == 2
            titles = [event.title for event in events]
            assert "Friday Night Magic" in titles
            assert "Warhammer Tournament" in titles

    def test_scrape_all_sources_no_sources(self):
        """Test scraping with no sources specified."""
        events = self.scraper.scrape_all_sources()
        assert events == []

    def test_remove_duplicates(self):
        """Test removing duplicate events."""
        # Create duplicate events
        duplicate_event = GamingEvent(
            title="Friday Night Magic",  # Same title
            game_system="MTG",
            venue="Different Venue",  # Different venue
            date="2024-07-18",  # Same date
            start_time="19:00",  # Same time
            source="discord",  # Different source
        )

        events_with_duplicates = self.sample_events + [duplicate_event]
        unique_events = self.scraper._remove_duplicates(events_with_duplicates)

        # Should remove the duplicate
        assert len(unique_events) == 2
        titles = [event.title for event in unique_events]
        assert titles.count("Friday Night Magic") == 1

    def test_remove_duplicates_no_duplicates(self):
        """Test removing duplicates when none exist."""
        unique_events = self.scraper._remove_duplicates(self.sample_events)
        assert len(unique_events) == len(self.sample_events)

    def test_remove_duplicates_case_sensitivity(self):
        """Test that duplicate removal is case insensitive."""
        duplicate_event = GamingEvent(
            title="friday night magic",  # Different case
            game_system="MTG",
            venue="Card Shop",
            date="2024-07-18",
            start_time="19:00",
            source="facebook",
        )

        events_with_duplicates = self.sample_events + [duplicate_event]
        unique_events = self.scraper._remove_duplicates(events_with_duplicates)

        assert len(unique_events) == 2  # Should remove case-insensitive duplicate

    @patch.object(GamingEventsScraper, "scrape_all_sources")
    @patch.object(GamingEventsScraper, "_print_summary")
    def test_scrape_and_save_success(self, mock_print, mock_scrape):
        """Test successful scrape and save operation."""
        mock_scrape.return_value = self.sample_events

        # Mock storage
        self.scraper.storage.save_events = Mock(return_value="test_file.json")

        facebook_pages = ["test_page"]
        result = self.scraper.scrape_and_save(facebook_pages=facebook_pages)

        assert result == "test_file.json"
        self.scraper.storage.save_events.assert_called_once()
        mock_print.assert_called_once()

    @patch.object(GamingEventsScraper, "scrape_all_sources")
    def test_scrape_and_save_no_events(self, mock_scrape):
        """Test scrape and save when no events found."""
        mock_scrape.return_value = []

        result = self.scraper.scrape_and_save()

        assert result == ""

    def test_print_summary_empty(self):
        """Test printing summary with no events."""
        # Should not raise exception
        self.scraper._print_summary([])

    def test_print_summary_with_events(self):
        """Test printing summary with events."""
        # Should not raise exception
        self.scraper._print_summary(self.sample_events)

    def test_print_summary_many_events(self):
        """Test printing summary with many events of same type."""
        # Create multiple MTG events
        mtg_events = []
        for i in range(5):
            event = GamingEvent(
                title=f"MTG Event {i}",
                game_system="MTG",
                venue="Card Shop",
                date=f"2024-07-{18+i}",
                start_time="19:00",
                source="test",
            )
            mtg_events.append(event)

        # Should not raise exception, should show "... and X more"
        self.scraper._print_summary(mtg_events)

    def test_get_storage(self):
        """Test getting storage instance."""
        storage = self.scraper.get_storage()
        assert storage is self.scraper.storage

    @patch("builtins.print")
    def test_print_output_capture(self, mock_print):
        """Test that print statements are called during scraping."""
        self.scraper.facebook_scraper.scrape_page_events = Mock(
            return_value=[self.sample_events[0]]
        )

        facebook_pages = ["test_page"]
        self.scraper.scrape_all_sources(facebook_pages=facebook_pages)

        # Should print scraping progress
        mock_print.assert_called()

        # Check for expected print messages
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Scraping Facebook pages" in call for call in print_calls)
        assert any(
            "Found" in call and "events from Facebook page" in call
            for call in print_calls
        )
