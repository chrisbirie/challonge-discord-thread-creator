"""Tests for print/display functions and formatters."""

import pytest
from tourney_threads.discord_client.formatters import (
    print_dry_run,
    print_debug_summary,
    format_thread_name,
    format_thread_message,
)
from tourney_threads.api.models import Participant, Match


class TestFormatting:
    """Tests for thread name and message formatting."""
    
    def test_format_thread_name_default(self):
        """Test thread name formatting with default template."""
        p1 = Participant("1", "Alice", "Alice", "<@100>")
        p2 = Participant("2", "Bob", "Bob", "<@200>")
        match = Match("m1", "open", 2, p1, p2)
        
        config = {}
        name = format_thread_name(match, "Elimination", config)
        assert name == "Winners R2: Alice vs Bob"
    
    def test_format_thread_name_custom(self):
        """Test thread name with custom template."""
        p1 = Participant("1", "Alice", "Alice", "<@100>")
        p2 = Participant("2", "Bob", "Bob", "<@200>")
        match = Match("m1", "open", 2, p1, p2)
        
        config = {"thread_name_template": "{p1_name} vs {p2_name} ({round_label})"}
        name = format_thread_name(match, "Elimination", config)
        assert name == "Alice vs Bob (Winners R2)"
    
    def test_format_thread_message_default(self):
        """Test message formatting with default template."""
        p1 = Participant("1", "Alice", "Alice", "<@100>")
        p2 = Participant("2", "Bob", "Bob", "<@200>")
        match = Match("m1", "open", 1, p1, p2)
        
        config = {}
        message = format_thread_message(match, "Swiss", config, role_mentions="<@&500>")
        assert "Hi <@100> vs <@200>!" in message
        assert "<@&500>" in message
        assert "Swiss R1" in message
    
    def test_format_with_tbd_players(self):
        """Test formatting with TBD players."""
        match = Match("m1", "pending", 3, None, None)
        
        config = {}
        name = format_thread_name(match, "Elimination", config)
        assert name == "Winners R3: TBD vs TBD"
    
    def test_format_with_match_url_no_subdomain(self):
        """Test that match_url is generated correctly without subdomain."""
        p1 = Participant("1", "Alice", "Alice", "<@100>")
        p2 = Participant("2", "Bob", "Bob", "<@200>")
        match = Match("m123", "open", 1, p1, p2)
        
        config = {
            "challonge": {
                "tournament": "test-tourney"
            },
            "message_template": "{match_url}"
        }
        
        message = format_thread_message(match, "Swiss", config)
        assert message == "https://challonge.com/test-tourney/matches/m123"
    
    def test_format_with_match_url_with_subdomain(self):
        """Test that match_url is generated correctly with subdomain."""
        p1 = Participant("1", "Alice", "Alice", "<@100>")
        p2 = Participant("2", "Bob", "Bob", "<@200>")
        match = Match("m456", "open", 1, p1, p2)
        
        config = {
            "challonge": {
                "tournament": "test-tourney",
                "subdomain": "myorg"
            },
            "message_template": "{match_url}"
        }
        
        message = format_thread_message(match, "Swiss", config)
        assert message == "https://myorg.challonge.com/test-tourney/matches/m456"
    
    def test_format_with_new_template_variables(self):
        """Test all new template variables (match_id, match_state, match_url, tournament_name)."""
        p1 = Participant("1", "Alice", "Alice", "<@100>")
        p2 = Participant("2", "Bob", "Bob", "<@200>")
        match = Match("match789", "complete", 2, p1, p2)
        
        config = {
            "challonge": {
                "tournament": "my-event"
            },
            "message_template": "ID:{match_id} State:{match_state} Tournament:{tournament_name} URL:{match_url}"
        }
        
        message = format_thread_message(match, "Elimination", config)
        assert "ID:match789" in message
        assert "State:complete" in message
        assert "Tournament:my-event" in message
        assert "URL:https://challonge.com/my-event/matches/match789" in message
    
    def test_format_thread_name_with_all_variables(self):
        """Test thread name template with all available variables."""
        p1 = Participant("1", "Player1", "Player1", "<@100>")
        p2 = Participant("2", "Player2", "Player2", "<@200>")
        match = Match("m999", "open", -2, p1, p2)  # Losers bracket
        
        config = {
            "challonge": {
                "tournament": "big-tourney"
            },
            "thread_name_template": "{stage} {bracket} R{abs_round}: {p1_name} vs {p2_name} [{match_id}]"
        }
        
        name = format_thread_name(match, "Elimination", config)
        assert name == "Elimination Losers R2: Player1 vs Player2 [m999]"


class TestPrintFunctions:
    """Tests for print/display functions."""
    
    def test_print_dry_run_empty_matches(self, capsys):
        """Test dry-run with no matches."""
        config = {}
        matches = []
        
        print_dry_run(matches, "Elimination", config)
        captured = capsys.readouterr()
        
        assert "No matches to show" in captured.out
    
    def test_print_debug_summary_empty_matches(self, capsys):
        """Test debug summary with no matches."""
        config = {}
        matches = []
        
        print_debug_summary(matches, "Elimination", config)
        captured = capsys.readouterr()
        
        assert "No matches returned" in captured.out
    
    def test_print_dry_run_with_matches(self, capsys):
        """Test dry-run with actual matches."""
        from tourney_threads.api.models import Match, Participant
        
        p1 = Participant("1", "Alice", "Alice", "<@100>")
        p2 = Participant("2", "Bob", "Bob", "<@200>")
        match = Match("m1", "open", 1, p1, p2)
        
        config = {
            "discord": {
                "role_ids_to_tag": [999]
            }
        }
        
        print_dry_run([match], "Elimination", config)
        captured = capsys.readouterr()
        
        assert "DRY RUN" in captured.out
        assert "Winners R1" in captured.out
        assert "Alice vs Bob" in captured.out
        assert "END DRY RUN" in captured.out
    
    def test_print_debug_summary_with_matches(self, capsys):
        """Test debug summary with actual matches."""
        from tourney_threads.api.models import Match, Participant
        
        p1 = Participant("1", "Alice", "Alice", "<@100>")
        p2 = Participant("2", "Bob", "Bob", "Bob")
        match = Match("m1", "open", 2, p1, p2)
        
        config = {}
        
        print_debug_summary([match], "Swiss", config)
        captured = capsys.readouterr()
        
        assert "Matches Summary" in captured.out
        assert "match_id=m1" in captured.out
        assert "state=open" in captured.out
        assert "round=2" in captured.out
        assert "Swiss R2" in captured.out
        assert "Alice" in captured.out
        assert "Bob" in captured.out
