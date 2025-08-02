"""Facebook event scraper implementation."""

import requests
from datetime import datetime
from typing import List, Optional, Dict
from bs4 import BeautifulSoup

from .models import GamingEvent
from .extractors import EventExtractor


class FacebookEventScraper(EventExtractor):
    """Scrape gaming events from Facebook."""
    
    def __init__(self, access_token: Optional[str] = None):
        """Initialize Facebook scraper.
        
        Args:
            access_token: Optional Facebook Graph API access token
        """
        super().__init__()
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        
    def scrape_page_events(self, page_id: str) -> List[GamingEvent]:
        """Scrape events from a Facebook page.
        
        Args:
            page_id: Facebook page ID or username
            
        Returns:
            List of GamingEvent objects
        """
        events = []
        
        if not self.access_token:
            print("Warning: No Facebook access token provided. Using public scraping fallback.")
            return self._scrape_public_page(page_id)
        
        try:
            # Get page events via Graph API
            url = f"{self.base_url}/{page_id}/events"
            params = {
                'access_token': self.access_token,
                'fields': 'name,description,start_time,place'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            for event_data in data.get('data', []):
                event = self._parse_facebook_event(event_data, 'facebook_api')
                if event:
                    events.append(event)
                    
        except Exception as e:
            print(f"Error scraping Facebook page {page_id}: {e}")
            
        return events
    
    def _scrape_public_page(self, page_id: str) -> List[GamingEvent]:
        """Fallback method to scrape public Facebook page.
        
        Args:
            page_id: Facebook page ID or username
            
        Returns:
            List of GamingEvent objects
        """
        events = []
        
        try:
            # Note: This is a simplified example - Facebook's public pages
            # are heavily JavaScript-rendered and may require selenium
            url = f"https://www.facebook.com/{page_id}/events"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for event-like content in the page
            # This is a simplified approach - real implementation would need
            # more sophisticated parsing
            text_content = soup.get_text()
            
            # Look for gaming-related events in the text
            lines = text_content.split('\\n')
            for line in lines:
                if self.contains_gaming_keywords(line):
                    event = self._parse_text_event(line, f"https://facebook.com/{page_id}")
                    if event:
                        events.append(event)
                        
        except Exception as e:
            print(f"Error scraping public Facebook page {page_id}: {e}")
            
        return events
    
    def _parse_facebook_event(self, event_data: Dict, source_url: str) -> Optional[GamingEvent]:
        """Parse Facebook event data into GamingEvent.
        
        Args:
            event_data: Facebook event data dictionary
            source_url: URL of the source
            
        Returns:
            GamingEvent object or None if not a gaming event
        """
        try:
            title = event_data.get('name', '')
            description = event_data.get('description', '')
            
            # Check if this is a gaming event
            combined_text = f"{title} {description}".lower()
            if not self.contains_gaming_keywords(combined_text):
                return None
            
            game_system = self.extract_game_system(combined_text)
            
            # Extract venue
            venue = "Unknown"
            place = event_data.get('place', {})
            if isinstance(place, dict):
                venue = place.get('name', 'Unknown')
            
            # Parse date/time
            start_time_str = event_data.get('start_time', '')
            if start_time_str:
                try:
                    dt = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    date = dt.date().isoformat()
                    start_time = dt.time().strftime('%H:%M')
                except Exception:
                    date = self.extract_date(combined_text) or "Unknown"
                    start_time = self.extract_time(combined_text) or "Unknown"
            else:
                date = self.extract_date(combined_text) or "Unknown"
                start_time = self.extract_time(combined_text) or "Unknown"
            
            return GamingEvent(
                title=title,
                game_system=game_system,
                venue=venue,
                date=date,
                start_time=start_time,
                source="facebook",
                source_url=source_url,
                description=description
            )
            
        except Exception as e:
            print(f"Error parsing Facebook event: {e}")
            return None
    
    def _parse_text_event(self, text: str, source_url: str) -> Optional[GamingEvent]:
        """Parse event from text content.
        
        Args:
            text: Text content to parse
            source_url: URL of the source
            
        Returns:
            GamingEvent object or None if not a gaming event
        """
        game_system = self.extract_game_system(text)
        if game_system == "Unknown":
            return None
        
        date = self.extract_date(text) or "Unknown"
        start_time = self.extract_time(text) or "Unknown"
        
        return GamingEvent(
            title=text.strip()[:100],  # Limit title length
            game_system=game_system,
            venue="Unknown",
            date=date,
            start_time=start_time,
            source="facebook",
            source_url=source_url,
            description=text.strip()
        )