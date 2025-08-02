"""Base extractor classes for event data extraction."""

import re
from datetime import datetime
from typing import List, Optional


class EventExtractor:
    """Base class for event extraction with common functionality."""
    
    def __init__(self):
        """Initialize extractor with common patterns and keywords."""
        self.game_keywords = [
            "mtg", "magic", "magic the gathering",
            "warhammer", "40k", "age of sigmar",
            "d&d", "dungeons and dragons", "dnd",
            "pokemon", "yugioh", "digimon",
            "fnm", "friday night magic",
            "commander", "edh",
            "draft", "sealed", "prerelease"
        ]
        
        self.time_patterns = [
            r'(\d{1,2}):?(\d{2})\s*(am|pm)',
            r'(\d{1,2})\s*(am|pm)',
            r'(\d{1,2}):?(\d{2})'
        ]
        
        self.date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{1,2})-(\d{1,2})-(\d{4})',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})',
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})'
        ]
    
    def extract_game_system(self, text: str) -> str:
        """Extract game system from text."""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ["mtg", "magic", "fnm", "commander", "edh", "draft", "sealed", "prerelease"]):
            return "MTG"
        elif any(keyword in text_lower for keyword in ["warhammer", "40k", "age of sigmar"]):
            return "Warhammer"
        elif any(keyword in text_lower for keyword in ["d&d", "dungeons", "dnd"]):
            return "D&D"
        elif "pokemon" in text_lower:
            return "Pokemon"
        elif "yugioh" in text_lower:
            return "Yu-Gi-Oh"
        
        return "Unknown"
    
    def extract_time(self, text: str) -> Optional[str]:
        """Extract time from text."""
        for pattern in self.time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 3:  # HH:MM AM/PM
                    hour, minute, period = groups
                    return f"{hour}:{minute} {period.upper()}"
                elif len(groups) == 2 and groups[1].lower() in ['am', 'pm']:  # HH AM/PM
                    hour, period = groups
                    return f"{hour}:00 {period.upper()}"
                elif len(groups) == 2:  # HH:MM (24hr)
                    hour, minute = groups
                    return f"{hour}:{minute}"
        return None
    
    def extract_date(self, text: str) -> Optional[str]:
        """Extract date from text and convert to ISO format."""
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                # Handle different date formats
                if len(groups) == 3 and groups[2].isdigit():  # MM/DD/YYYY
                    month, day, year = groups
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                elif len(groups) == 2:  # Month DD
                    month_name, day = groups
                    month_map = {
                        'january': '01', 'jan': '01',
                        'february': '02', 'feb': '02',
                        'march': '03', 'mar': '03',
                        'april': '04', 'apr': '04',
                        'may': '05',
                        'june': '06', 'jun': '06',
                        'july': '07', 'jul': '07',
                        'august': '08', 'aug': '08',
                        'september': '09', 'sep': '09',
                        'october': '10', 'oct': '10',
                        'november': '11', 'nov': '11',
                        'december': '12', 'dec': '12'
                    }
                    month = month_map.get(month_name.lower())
                    if month:
                        current_year = datetime.now().year
                        return f"{current_year}-{month}-{day.zfill(2)}"
        return None
    
    def contains_gaming_keywords(self, text: str) -> bool:
        """Check if text contains gaming keywords."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.game_keywords)