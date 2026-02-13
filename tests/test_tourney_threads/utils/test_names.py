"""Tests for name cleaning and mention utilities."""

import pytest
from tourney_threads.utils.names import (
    clean_runner_name,
    participant_username,
    mention_for_name,
    build_role_mentions,
)


class TestNameCleaning:
    """Tests for name cleaning utilities."""
    
    def test_clean_runner_name_with_invitation(self):
        """Test removing invitation pending suffix."""
        assert clean_runner_name("Player1 (invitation pending)") == "Player1"
        assert clean_runner_name("Test User (Invitation Pending)") == "Test User"
    
    def test_clean_runner_name_normal(self):
        """Test cleaning normal names."""
        assert clean_runner_name("NormalPlayer") == "NormalPlayer"
        assert clean_runner_name("Player With Spaces") == "Player With Spaces"
    
    def test_clean_runner_name_invalid_input(self):
        """Test handling invalid input."""
        assert clean_runner_name(None) == "UNKNOWN"
        assert clean_runner_name(123) == "UNKNOWN"
    
    def test_participant_username_extraction(self):
        """Test extracting username from participant data."""
        participant = {
            "attributes": {
                "username": "test_user",
                "name": "Test Name",
                "display_name": "Display"
            }
        }
        assert participant_username(participant) == "test_user"
    
    def test_participant_username_fallback(self):
        """Test username fallback to name or display_name."""
        participant1 = {"attributes": {"name": "NameOnly"}}
        assert participant_username(participant1) == "NameOnly"
        
        participant2 = {"attributes": {"display_name": "DisplayOnly"}}
        assert participant_username(participant2) == "DisplayOnly"
    
    def test_participant_username_missing(self):
        """Test handling missing participant data."""
        assert participant_username(None) == "UNKNOWN"
        assert participant_username({}) == "UNKNOWN"
        assert participant_username({"attributes": {}}) == "UNKNOWN"


class TestMentions:
    """Tests for Discord mention generation."""
    
    def test_mention_for_name_with_mapping(self):
        """Test creating mention when Discord ID exists."""
        runner_map = {"Player1": 123456789}
        assert mention_for_name("Player1", runner_map) == "<@123456789>"
    
    def test_mention_for_name_without_mapping(self):
        """Test using plain name when no Discord ID exists."""
        runner_map = {"Player1": 123456789}
        assert mention_for_name("Player2", runner_map) == "Player2"
    
    def test_mention_for_name_empty_map(self):
        """Test with empty runner map."""
        assert mention_for_name("Player1", {}) == "Player1"
    
    def test_build_role_mentions(self):
        """Test building role mentions."""
        assert build_role_mentions([111, 222, 333]) == "<@&111> <@&222> <@&333>"
        assert build_role_mentions([]) == ""
        assert build_role_mentions(None) == ""
