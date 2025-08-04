# Gaming Events Scraper

A social media scraper for gaming events from Facebook and Discord, built with Python and Jupyter notebooks.

## Features

- 🎮 Extract gaming events from Facebook pages and posts
- 💬 Monitor Discord servers for event announcements
- 📅 Parse dates, times, and game systems automatically
- 💾 Save structured event data in JSON format
- 🔧 Extensible for additional platforms and data sources

## Quick Start

### Prerequisites

- Python 3.9 or higher
- UV package manager (installed automatically if needed)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd EventBoardAgent
```

2. Install dependencies with UV:
```bash
uv sync
```

3. Activate the virtual environment:
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. Start Jupyter:
```bash
uv run jupyter lab
```

5. Open `gaming_events_scraper.ipynb` and follow the notebook instructions.

## Starting Coding Agents

Run a VSCode task called "Start Claude Agents" (cmd + shift + P -> Tasks:Run Task)

## Configuration

### API Tokens (Optional)

For enhanced functionality, you can provide API tokens:

- **Facebook**: Get an access token from [Facebook Developers](https://developers.facebook.com/)
- **Discord**: Create a bot and get a token from [Discord Developer Portal](https://discord.com/developers/applications)

Add your tokens to the configuration section in the notebook.

### Scraping Targets

Configure your scraping targets in the notebook:

```python
FACEBOOK_PAGES = [
    "yourlocalcardshop",
    "magicthegathering"
]

DISCORD_SERVERS = [
    {"guild_id": 123456789, "channels": ["events", "announcements"]}
]
```

## Usage

The scraper can extract events for various gaming systems:

- Magic: The Gathering (MTG)
- Warhammer 40K
- Dungeons & Dragons (D&D)
- Pokemon
- Yu-Gi-Oh
- And more...

### Running the Scraper

```python
# Initialize scraper
scraper = GamingEventsScraper(
    facebook_token=FACEBOOK_ACCESS_TOKEN,
    discord_token=DISCORD_BOT_TOKEN
)

# Scrape and save events
output_file = scraper.scrape_and_save(
    facebook_pages=FACEBOOK_PAGES,
    discord_servers=DISCORD_SERVERS
)
```

### Working with Saved Events

```python
# Load saved events
storage = EventStorage("gaming_events_data")

# Get upcoming events
upcoming = storage.get_upcoming_events(days_ahead=14)

# Get events by game system
mtg_events = storage.get_events_by_game("MTG")
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
uv sync --group dev

# Install pre-commit hooks
uv run pre-commit install
```

### Code Quality

```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Type checking
uv run mypy src/

# Run tests
uv run pytest
```

## Project Structure

```
EventBoardAgent/
├── gaming_events_scraper.ipynb  # Main Jupyter notebook
├── pyproject.toml               # Project configuration
├── uv.lock                      # Dependency lock file
├── .python-version              # Python version specification
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Event Data Schema

Events are stored with the following structure:

```json
{
  "title": "Friday Night Magic - Modern",
  "game_system": "MTG",
  "venue": "Local Card Shop",
  "date": "2024-07-18",
  "start_time": "19:00",
  "source": "facebook",
  "source_url": "https://facebook.com/event/123",
  "description": "Join us for Modern format FNM...",
  "extracted_at": "2024-07-15T10:30:00Z"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
