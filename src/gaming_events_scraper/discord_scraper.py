"""Discord event scraper implementation."""

from typing import List, Optional

from .models import GamingEvent
from .extractors import EventExtractor

try:
    import discord

    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False


class DiscordEventScraper(EventExtractor):
    """Scrape gaming events from Discord servers."""

    def __init__(self, bot_token: Optional[str] = None):
        """Initialize Discord scraper.

        Args:
            bot_token: Optional Discord bot token
        """
        super().__init__()
        self.bot_token = bot_token
        self.events = []

    async def scrape_server_events(
        self, guild_id: int, channel_names: Optional[List[str]] = None
    ) -> List[GamingEvent]:
        """Scrape events from Discord server channels.

        Args:
            guild_id: Discord server (guild) ID
            channel_names: List of channel names to monitor

        Returns:
            List of GamingEvent objects
        """
        if not DISCORD_AVAILABLE:
            print("Discord.py not available. Cannot scrape Discord events.")
            return []

        if not self.bot_token:
            print("No Discord bot token provided.")
            return []

        if channel_names is None:
            channel_names = ["events", "schedule", "announcements", "general"]

        intents = discord.Intents.default()
        intents.message_content = True

        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            try:
                guild = client.get_guild(guild_id)
                if not guild:
                    print(f"Guild {guild_id} not found")
                    await client.close()
                    return

                for channel in guild.channels:
                    if isinstance(channel, discord.TextChannel) and any(
                        name.lower() in channel.name.lower() for name in channel_names
                    ):

                        print(f"Scanning channel: {channel.name}")

                        async for message in channel.history(limit=100):
                            event = self._parse_discord_message(message)
                            if event:
                                self.events.append(event)

                await client.close()

            except Exception as e:
                print(f"Error scraping Discord server: {e}")
                await client.close()

        await client.start(self.bot_token)
        return self.events

    def _parse_discord_message(self, message) -> Optional[GamingEvent]:
        """Parse Discord message for gaming events.

        Args:
            message: Discord message object

        Returns:
            GamingEvent object or None if not a gaming event
        """
        try:
            content = message.content

            # Check if this contains gaming keywords
            if not self.contains_gaming_keywords(content):
                return None

            game_system = self.extract_game_system(content)
            date = self.extract_date(content) or "Unknown"
            start_time = self.extract_time(content) or "Unknown"

            # Try to extract venue from message
            venue = "Unknown"
            if hasattr(message, "guild") and message.guild:
                venue = message.guild.name

            return GamingEvent(
                title=content[:100] if len(content) > 100 else content,
                game_system=game_system,
                venue=venue,
                date=date,
                start_time=start_time,
                source="discord",
                source_url=(
                    f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
                    if hasattr(message, "guild") and message.guild
                    else None
                ),
                description=content,
            )

        except Exception as e:
            print(f"Error parsing Discord message: {e}")
            return None

    def is_discord_available(self) -> bool:
        """Check if Discord.py is available.

        Returns:
            True if discord.py is installed, False otherwise
        """
        return DISCORD_AVAILABLE
