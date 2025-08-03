"""Main orchestrator for gaming events scraping."""

import asyncio
from typing import List, Optional, Dict

from .models import GamingEvent
from .facebook_scraper import FacebookEventScraper
from .discord_scraper import DiscordEventScraper, DISCORD_AVAILABLE
from .storage import EventStorage


class GamingEventsScraper:
    """Main orchestrator for gaming events scraping."""

    def __init__(
        self,
        facebook_token: Optional[str] = None,
        discord_token: Optional[str] = None,
        storage_dir: str = "events_data",
    ):
        """Initialize the main scraper.

        Args:
            facebook_token: Optional Facebook Graph API access token
            discord_token: Optional Discord bot token
            storage_dir: Directory to store event files
        """
        self.facebook_scraper = FacebookEventScraper(facebook_token)
        self.discord_scraper = DiscordEventScraper(discord_token)
        self.storage = EventStorage(storage_dir)

    def scrape_all_sources(
        self,
        facebook_pages: Optional[List[str]] = None,
        discord_servers: Optional[List[Dict]] = None,
    ) -> List[GamingEvent]:
        """Scrape events from all configured sources.

        Args:
            facebook_pages: List of Facebook page IDs to scrape
            discord_servers: List of Discord server configurations

        Returns:
            List of all scraped GamingEvent objects
        """
        all_events = []

        # Scrape Facebook
        if facebook_pages:
            print("Scraping Facebook pages...")
            for page_id in facebook_pages:
                try:
                    events = self.facebook_scraper.scrape_page_events(page_id)
                    all_events.extend(events)
                    print(f"Found {len(events)} events from Facebook page {page_id}")
                except Exception as e:
                    print(f"Error scraping Facebook page {page_id}: {e}")

        # Scrape Discord (requires async)
        if discord_servers and DISCORD_AVAILABLE:
            print("Scraping Discord servers...")

            async def scrape_discord():
                discord_events = []
                for server_config in discord_servers:
                    try:
                        guild_id = server_config["guild_id"]
                        channels = server_config.get("channels", None)
                        events = await self.discord_scraper.scrape_server_events(
                            guild_id, channels
                        )
                        discord_events.extend(events)
                        print(
                            f"Found {len(events)} events from Discord server {guild_id}"
                        )
                    except Exception as e:
                        print(f"Error scraping Discord server: {e}")
                return discord_events

            # Run async Discord scraping
            try:
                discord_events = asyncio.run(scrape_discord())
                all_events.extend(discord_events)
            except Exception as e:
                print(f"Error running Discord scraping: {e}")

        return all_events

    def scrape_and_save(
        self,
        facebook_pages: Optional[List[str]] = None,
        discord_servers: Optional[List[Dict]] = None,
        filename: Optional[str] = None,
    ) -> str:
        """Scrape events and save to file.

        Args:
            facebook_pages: List of Facebook page IDs to scrape
            discord_servers: List of Discord server configurations
            filename: Optional filename for saved events

        Returns:
            Path to saved file
        """
        events = self.scrape_all_sources(facebook_pages, discord_servers)

        if not events:
            print("No events found")
            return ""

        # Remove duplicates based on title and date
        unique_events = self._remove_duplicates(events)

        print(f"Found {len(events)} total events, {len(unique_events)} unique")

        # Save to file
        filepath = self.storage.save_events(unique_events, filename)

        # Print summary
        self._print_summary(unique_events)

        return filepath

    def _remove_duplicates(self, events: List[GamingEvent]) -> List[GamingEvent]:
        """Remove duplicate events based on title, date, and time.

        Args:
            events: List of events to deduplicate

        Returns:
            List of unique events
        """
        unique_events = []
        seen = set()

        for event in events:
            key = (event.title.lower().strip(), event.date, event.start_time)
            if key not in seen:
                unique_events.append(event)
                seen.add(key)

        return unique_events

    def _print_summary(self, events: List[GamingEvent]):
        """Print summary of scraped events.

        Args:
            events: List of events to summarize
        """
        if not events:
            return

        print("\\n=== EVENTS SUMMARY ===")

        # Group by game system
        by_game = {}
        for event in events:
            game = event.game_system
            if game not in by_game:
                by_game[game] = []
            by_game[game].append(event)

        for game, game_events in by_game.items():
            print(f"\\n{game}: {len(game_events)} events")
            for event in sorted(game_events, key=lambda x: x.date)[:3]:  # Show first 3
                print(
                    f"  - {event.title} | {event.date} {event.start_time} | {event.venue}"
                )
            if len(game_events) > 3:
                print(f"  ... and {len(game_events) - 3} more")

    def get_storage(self) -> EventStorage:
        """Get the storage instance for direct access.

        Returns:
            EventStorage instance
        """
        return self.storage
