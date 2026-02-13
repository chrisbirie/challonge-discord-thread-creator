"""Data models for tournament matches and participants.

This module defines dataclasses representing Challonge API resources.
"""

from dataclasses import dataclass


@dataclass
class Participant:
    """Represents a tournament participant from the Challonge API.

    Attributes:
        id: Participant ID from Challonge.
        username: Username of the participant (cleaned).
        raw_name: Raw name from the API (may include invitation pending suffix).
        mention: Discord mention string (<@user_id>) or username if no Discord mapping.
    """

    id: str
    username: str
    raw_name: str
    mention: str


@dataclass
class Match:
    """Represents a tournament match with participants.

    Attributes:
        match_id: Match ID from Challonge.
        state: Match state (e.g., 'open', 'pending', 'complete').
        round: Round number (positive for winners bracket, negative for losers).
        player1: First participant (None if TBD).
        player2: Second participant (None if TBD).
    """

    match_id: str
    state: str
    round: int
    player1: Participant | None
    player2: Participant | None

    @property
    def p1_name(self) -> str:
        """Get player1's username, or 'TBD' if not set."""
        return self.player1.username if self.player1 else "TBD"

    @property
    def p2_name(self) -> str:
        """Get player2's username, or 'TBD' if not set."""
        return self.player2.username if self.player2 else "TBD"

    @property
    def p1_mention(self) -> str:
        """Get player1's mention string, or 'TBD' if not set."""
        return self.player1.mention if self.player1 else "TBD"

    @property
    def p2_mention(self) -> str:
        """Get player2's mention string, or 'TBD' if not set."""
        return self.player2.mention if self.player2 else "TBD"


@dataclass
class MatchSummary:
    """Legacy dictionary-based match representation for backward compatibility.

    This is used internally for template formatting and will be phased out.
    """

    match_id: str
    state: str
    round: int
    p1_id: str | None
    p1_name: str
    p1_mention: str
    p2_id: str | None
    p2_name: str
    p2_mention: str

    @classmethod
    def from_match(cls, match: Match) -> "MatchSummary":
        """Create a MatchSummary from a Match dataclass.

        Args:
            match: Match instance to convert.

        Returns:
            MatchSummary instance with equivalent data.
        """
        return cls(
            match_id=match.match_id,
            state=match.state,
            round=match.round,
            p1_id=match.player1.id if match.player1 else None,
            p1_name=match.p1_name,
            p1_mention=match.p1_mention,
            p2_id=match.player2.id if match.player2 else None,
            p2_name=match.p2_name,
            p2_mention=match.p2_mention,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for template formatting.

        Returns:
            Dictionary with all fields.
        """
        return {
            "match_id": self.match_id,
            "state": self.state,
            "round": self.round,
            "p1_id": self.p1_id,
            "p1_name": self.p1_name,
            "p1_mention": self.p1_mention,
            "p2_id": self.p2_id,
            "p2_name": self.p2_name,
            "p2_mention": self.p2_mention,
        }
