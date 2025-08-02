# 📄 spec.md – Gaming Events Social Scraper

## 🧩 Objective

Build a Jupyter notebook that:

1. Parses **social media sources** (Facebook and Discord to start) to find **upcoming gaming events**.
2. Extracts **structured schedule data** including:
   - Game system
   - Venue/store
   - Date
   - Start time
3. Saves each event in a local **JSON file** using a consistent schema.
4. Supports easy expansion to other platforms or storage types later.

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
  - Use regex/N
