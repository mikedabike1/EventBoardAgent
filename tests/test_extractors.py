"""Tests for event extractors."""

from src.gaming_events_scraper.extractors import EventExtractor


class TestEventExtractor:
    """Test cases for EventExtractor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = EventExtractor()

    def test_extract_game_system_mtg(self):
        """Test extracting MTG game system."""
        test_cases = [
            "Friday Night Magic at Card Kingdom",
            "MTG Modern tournament this Saturday",
            "Commander night every Wednesday",
            "Draft event - Bloomburrow set",
            "EDH pod looking for players",
            "Prerelease weekend for new set",
            "FNM starts at 7 PM",
        ]

        for text in test_cases:
            result = self.extractor.extract_game_system(text)
            assert result == "MTG", f"Failed for text: {text}"

    def test_extract_game_system_warhammer(self):
        """Test extracting Warhammer game system."""
        test_cases = [
            "Warhammer 40K tournament this weekend",
            "Age of Sigmar campaign starting",
            "40k hobby night at the store",
        ]

        for text in test_cases:
            result = self.extractor.extract_game_system(text)
            assert result == "Warhammer", f"Failed for text: {text}"

    def test_extract_game_system_dnd(self):
        """Test extracting D&D game system."""
        test_cases = [
            "D&D adventure league tonight",
            "Dungeons and Dragons one-shot",
            "DnD campaign looking for players",
        ]

        for text in test_cases:
            result = self.extractor.extract_game_system(text)
            assert result == "D&D", f"Failed for text: {text}"

    def test_extract_game_system_pokemon(self):
        """Test extracting Pokemon game system."""
        text = "Pokemon league challenge this Saturday"
        result = self.extractor.extract_game_system(text)
        assert result == "Pokemon"

    def test_extract_game_system_yugioh(self):
        """Test extracting Yu-Gi-Oh game system."""
        text = "YuGiOh tournament with prizes"
        result = self.extractor.extract_game_system(text)
        assert result == "Yu-Gi-Oh"

    def test_extract_game_system_unknown(self):
        """Test extracting unknown game system."""
        text = "Board game night at the library"
        result = self.extractor.extract_game_system(text)
        assert result == "Unknown"

    def test_extract_time_12_hour_format(self):
        """Test extracting time in 12-hour format."""
        test_cases = [
            ("Event starts at 7:00 PM", "7:00 PM"),
            ("Meeting at 10:30 AM tomorrow", "10:30 AM"),
            ("Join us at 6 PM for games", "6:00 PM"),
            ("Tournament begins 9am sharp", "9:00 AM"),
        ]

        for text, expected in test_cases:
            result = self.extractor.extract_time(text)
            assert result == expected, f"Failed for text: {text}"

    def test_extract_time_24_hour_format(self):
        """Test extracting time in 24-hour format."""
        test_cases = [
            ("Event starts at 19:00", "19:00"),
            ("Meeting at 10:30 tomorrow", "10:30"),
            ("Join us at 18:45 for games", "18:45"),
        ]

        for text, expected in test_cases:
            result = self.extractor.extract_time(text)
            assert result == expected, f"Failed for text: {text}"

    def test_extract_time_no_match(self):
        """Test extracting time when no time is present."""
        text = "Gaming event happening soon"
        result = self.extractor.extract_time(text)
        assert result is None

    def test_extract_date_slash_format(self):
        """Test extracting date in MM/DD/YYYY format."""
        test_cases = [
            ("Event on 7/18/2024", "2024-07-18"),
            ("Tournament 12/25/2024", "2024-12-25"),
            ("Meeting on 1/5/2024", "2024-01-05"),
        ]

        for text, expected in test_cases:
            result = self.extractor.extract_date(text)
            assert result == expected, f"Failed for text: {text}"

    def test_extract_date_dash_format(self):
        """Test extracting date in MM-DD-YYYY format."""
        test_cases = [
            ("Event on 7-18-2024", "2024-07-18"),
            ("Tournament 12-25-2024", "2024-12-25"),
        ]

        for text, expected in test_cases:
            result = self.extractor.extract_date(text)
            assert result == expected, f"Failed for text: {text}"

    def test_extract_date_month_name(self):
        """Test extracting date with month names."""
        from datetime import datetime

        current_year = datetime.now().year

        test_cases = [
            ("Event on July 18", f"{current_year}-07-18"),  # Uses current year
            ("Tournament December 25", f"{current_year}-12-25"),
            ("Meeting on Jan 5", f"{current_year}-01-05"),
            ("Game night Feb 14", f"{current_year}-02-14"),
        ]

        for text, expected in test_cases:
            result = self.extractor.extract_date(text)
            assert result == expected, f"Failed for text: {text}"

    def test_extract_date_no_match(self):
        """Test extracting date when no date is present."""
        text = "Gaming event happening soon"
        result = self.extractor.extract_date(text)
        assert result is None

    def test_contains_gaming_keywords_true(self):
        """Test detecting gaming keywords in text."""
        test_cases = [
            "Friday Night Magic tournament",
            "Warhammer 40K painting session",
            "D&D adventure tonight",
            "Pokemon card trading",
            "YuGiOh duel monsters",
        ]

        for text in test_cases:
            result = self.extractor.contains_gaming_keywords(text)
            assert result is True, f"Failed for text: {text}"

    def test_contains_gaming_keywords_false(self):
        """Test not detecting gaming keywords in non-gaming text."""
        test_cases = [
            "Board meeting at 7 PM",
            "Chess club gathering",
            "Book club discussion",
            "Cooking class tonight",
        ]

        for text in test_cases:
            result = self.extractor.contains_gaming_keywords(text)
            assert result is False, f"Failed for text: {text}"

    def test_case_insensitive_matching(self):
        """Test that keyword matching is case insensitive."""
        test_cases = [
            "FRIDAY NIGHT MAGIC",
            "friday night magic",
            "Friday Night Magic",
            "fRiDaY nIgHt MaGiC",
        ]

        for text in test_cases:
            assert self.extractor.contains_gaming_keywords(text) is True
            assert self.extractor.extract_game_system(text) == "MTG"
