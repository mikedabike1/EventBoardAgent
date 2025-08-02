# 📄 spec.md – Gaming Events Social Scraper

## 🧩 Objective

Build a modular gaming events scraper that:

1. Parses **social media sources** (Facebook and Discord to start) to find **upcoming gaming events**.
2. Extracts **structured schedule data** including:
   - Game system
   - Venue/store
   - Date
   - Start time
3. Saves each event in a local **JSON file** using a consistent schema.
4. Supports easy expansion to other platforms or storage types later.
5. **NEW**: Implements a **modular Python package** with proper separation of concerns.
6. **NEW**: Includes **comprehensive unit tests** for all functionality.
7. **NEW**: Uses **UV for dependency management** and modern Python tooling.

---

## 🏗️ Architecture Requirements

### Code Organization
- **MUST** extract all functionality from Jupyter notebook into separate Python modules
- **MUST** implement proper package structure with `src/gaming_events_scraper/`
- **MUST** follow separation of concerns with dedicated modules for:
  - Data models (`models.py`)
  - Base extraction logic (`extractors.py`) 
  - Facebook scraping (`facebook_scraper.py`)
  - Discord scraping (`discord_scraper.py`)
  - Event storage (`storage.py`)
  - Main orchestrator (`scraper.py`)

### Testing Requirements
- **MUST** implement comprehensive unit tests for all modules
- **MUST** achieve good test coverage for core functionality
- **MUST** include tests for:
  - Event data models and serialization
  - Text extraction patterns (dates, times, game systems)
  - Storage operations (save, load, filter)
  - Facebook event parsing
  - Discord message parsing
  - Main scraper orchestration
  - Error handling and edge cases

### Dependency Management
- **MUST** use UV for modern Python dependency management
- **MUST** configure `pyproject.toml` with proper metadata
- **MUST** include development dependencies (pytest, black, ruff, mypy)
- **MUST** set up proper tooling configuration

### Jupyter Integration
- **MUST** update Jupyter notebook to import and use the modular code
- **MUST** provide clear examples and demonstrations
- **MUST** maintain ease of use for end users

---

## 🎯 Target Social Sources

### 1. Facebook

- **Scope**: Public posts and events from gaming stores, clubs, or groups.
- **Access**: Use Facebook Graph API or fallback to scraping with `requests`/`BeautifulSoup`.
- **Targets**:
  - Page events (e.g., "Modern FNM – July 18")
  - Posts announcing event schedules
- **Extraction Goals**:
  - Event title
  - Date & start time
  - Game system (e.g., MTG, Warhammer, D&D)
  - Store name (inferred from context or page)

### 2. Discord

- **Scope**: Gaming community servers where schedules are posted.
- **Access**: Use `discord.py` with bot credentials.
- **Targets**:
  - Channels like `#events`, `#schedule`, `#announcements`
- **Extraction Goals**:
  - Use regex/NLP to extract event details from messages
  - Event title, date/time, game system, venue information
