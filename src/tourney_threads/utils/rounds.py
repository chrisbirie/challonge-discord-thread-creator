"""Utility functions for round labeling and formatting.

This module provides utilities for generating human-readable round labels.
"""

from typing import Any


def make_round_label(round_value: int, stage_name: str | None, config: dict[str, Any]) -> str:
    """Generate a human-readable round label.

    If config contains 'round_label_template', formats it with:
      - stage: 'Swiss'|'Groups'|'Elimination'|None
      - bracket: 'Winners'|'Losers'|'Round'
      - round: signed int (as given by Challonge)
      - abs_round: positive int

    Otherwise uses default labeling:
      - Swiss/Groups: "Swiss R{round}" or "Groups R{round}"
      - Elimination: "Winners R{round}" or "Losers R{abs_round}" based on sign

    Args:
        round_value: Round number from Challonge (positive=winners, negative=losers).
        stage_name: Tournament stage type ('Swiss', 'Groups', 'Elimination', or None).
        config: Configuration dictionary that may contain 'round_label_template'.

    Returns:
        Formatted round label string.
    """
    try:
        round_int = int(round_value)
    except (ValueError, TypeError):
        round_int = 0

    # Determine bracket type
    bracket = "Round"
    if round_int > 0:
        bracket = "Winners"
    elif round_int < 0:
        bracket = "Losers"

    # Try custom template from config
    template = config.get("round_label_template")
    if isinstance(template, str) and template.strip():
        try:
            return template.format(
                stage=stage_name,
                bracket=bracket,
                round=round_int,
                abs_round=abs(round_int),
            )
        except (KeyError, ValueError):
            # Fall through to default if template formatting fails
            pass

    # Default labeling logic
    if stage_name in ("Swiss", "Groups"):
        return f"{stage_name} R{round_int if round_int != 0 else 1}"

    if round_int > 0:
        return f"Winners R{round_int}"
    elif round_int < 0:
        return f"Losers R{abs(round_int)}"

    return f"Round {round_int}"
