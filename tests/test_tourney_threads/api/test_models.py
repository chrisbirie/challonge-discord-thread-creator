"""Tests for data models."""

from tourney_threads.api.models import Match, Participant


class TestDataModels:
    """Tests for Match and Participant dataclasses."""

    def test_participant_creation(self):
        """Test creating a Participant."""
        p = Participant(
            id="123",
            username="TestPlayer",
            raw_name="TestPlayer (invitation pending)",
            mention="<@999>",
        )
        assert p.id == "123"
        assert p.username == "TestPlayer"
        assert p.mention == "<@999>"

    def test_match_properties(self):
        """Test Match property accessors."""
        p1 = Participant("1", "Player1", "Player1", "<@100>")
        p2 = Participant("2", "Player2", "Player2", "Player2")

        match = Match(match_id="m1", state="open", round=2, player1=p1, player2=p2)

        assert match.p1_name == "Player1"
        assert match.p2_name == "Player2"
        assert match.p1_mention == "<@100>"
        assert match.p2_mention == "Player2"

    def test_match_tbd_players(self):
        """Test Match with TBD players."""
        match = Match(match_id="m1", state="pending", round=1, player1=None, player2=None)

        assert match.p1_name == "TBD"
        assert match.p2_name == "TBD"
        assert match.p1_mention == "TBD"
        assert match.p2_mention == "TBD"


class TestMatchSummaryModel:
    """Test MatchSummary data model methods."""

    def test_match_summary_to_dict(self):
        """Test MatchSummary.to_dict() conversion."""
        from tourney_threads.api.models import MatchSummary

        summary = MatchSummary(
            match_id=123,
            state="open",
            round=1,
            p1_id=456,
            p1_name="Player1",
            p1_mention="@Player1",
            p2_id=789,
            p2_name="Player2",
            p2_mention="@Player2",
        )

        result = summary.to_dict()
        assert result["match_id"] == 123
        assert result["state"] == "open"
        assert result["round"] == 1
        assert result["p1_name"] == "Player1"
        assert result["p2_name"] == "Player2"

    def test_match_summary_from_match(self):
        """Test MatchSummary.from_match() factory method."""
        from tourney_threads.api.models import Match, MatchSummary, Participant

        p1 = Participant(id="100", username="Alice", raw_name="Alice", mention="@Alice")
        p2 = Participant(id="200", username="Bob", raw_name="Bob", mention="@Bob")

        match = Match(match_id=999, state="complete", round=3, player1=p1, player2=p2)

        summary = MatchSummary.from_match(match)
        assert summary.match_id == 999
        assert summary.state == "complete"
        assert summary.round == 3
        assert summary.p1_id == "100"
        assert summary.p1_name == "Alice"
        assert summary.p2_id == "200"
        assert summary.p2_name == "Bob"

    def test_match_summary_from_match_with_none_players(self):
        """Test MatchSummary.from_match() with None players."""
        from tourney_threads.api.models import Match, MatchSummary

        match = Match(match_id=888, state="pending", round=1, player1=None, player2=None)

        summary = MatchSummary.from_match(match)
        assert summary.match_id == 888
        assert summary.state == "pending"
        assert summary.round == 1
        assert summary.p1_id is None
        assert summary.p1_name == "TBD"
        assert summary.p2_id is None
        assert summary.p2_name == "TBD"
