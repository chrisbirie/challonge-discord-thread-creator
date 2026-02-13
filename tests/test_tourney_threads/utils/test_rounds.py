"""Tests for round labeling utilities."""


from tourney_threads.utils.rounds import make_round_label


class TestRoundLabeling:
    """Tests for round label generation."""

    def test_round_label_elimination_winners(self):
        """Test winners bracket labeling."""
        config = {}
        assert make_round_label(1, "Elimination", config) == "Winners R1"
        assert make_round_label(3, "Elimination", config) == "Winners R3"

    def test_round_label_elimination_losers(self):
        """Test losers bracket labeling."""
        config = {}
        assert make_round_label(-2, "Elimination", config) == "Losers R2"
        assert make_round_label(-5, "Elimination", config) == "Losers R5"

    def test_round_label_swiss(self):
        """Test Swiss stage labeling."""
        config = {}
        assert make_round_label(1, "Swiss", config) == "Swiss R1"
        assert make_round_label(3, "Swiss", config) == "Swiss R3"
        assert make_round_label(0, "Swiss", config) == "Swiss R1"

    def test_round_label_groups(self):
        """Test groups stage labeling."""
        config = {}
        assert make_round_label(1, "Groups", config) == "Groups R1"
        assert make_round_label(2, "Groups", config) == "Groups R2"

    def test_round_label_custom_template(self):
        """Test custom template formatting."""
        config = {"round_label_template": "{stage} - {bracket} Round {abs_round}"}
        assert make_round_label(3, "Elimination", config) == "Elimination - Winners Round 3"
        assert make_round_label(-2, "Elimination", config) == "Elimination - Losers Round 2"

    def test_round_label_no_stage(self):
        """Test labeling when stage is unknown."""
        config = {}
        assert make_round_label(1, None, config) == "Winners R1"
        assert make_round_label(-2, None, config) == "Losers R2"
        assert make_round_label(0, None, config) == "Round 0"


class TestRoundLabelEdgeCases:
    """Additional edge case tests for round labeling."""

    def test_make_round_label_invalid_template(self):
        """Test round label with invalid template that raises exception."""
        # Template with missing key should fall back to default
        config = {"round_label_template": "{invalid_key}"}
        result = make_round_label(1, "Elimination", config)
        assert result == "Winners R1"

    def test_make_round_label_empty_template(self):
        """Test round label with empty template."""
        config = {"round_label_template": ""}
        result = make_round_label(2, "Elimination", config)
        assert result == "Winners R2"

    def test_make_round_label_whitespace_template(self):
        """Test round label with whitespace-only template."""
        config = {"round_label_template": "   "}
        result = make_round_label(3, "Swiss", config)
        assert result == "Swiss R3"

    def test_make_round_label_invalid_round_value(self):
        """Test round label with invalid round value."""
        # Non-numeric value should default to 0
        config = {}
        result = make_round_label("invalid", "Elimination", config)
        assert result == "Round 0"

        # None should also default to 0
        result = make_round_label(None, "Elimination", config)
        assert result == "Round 0"
