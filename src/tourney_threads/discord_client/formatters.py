"""Template formatting utilities for Discord messages.

This module provides functions for formatting thread names and messages from templates.
"""

from typing import Any

from ..api.models import Match
from ..config.constants import DEFAULT_MESSAGE_TEMPLATE, DEFAULT_THREAD_NAME_TEMPLATE
from ..utils.names import build_role_mentions
from ..utils.rounds import make_round_label


def format_thread_name(
    match: Match,
    stage_name: str | None,
    config: dict[str, Any],
    role_mentions: str = "",
) -> str:
    """Format a thread name from a template.

    Args:
        match: Match object with participant data.
        stage_name: Tournament stage type.
        config: Configuration dictionary.
        role_mentions: Role mention string (for template compatibility).

    Returns:
        Formatted thread name string.
    """
    template = str(config.get("thread_name_template", DEFAULT_THREAD_NAME_TEMPLATE))
    round_label = make_round_label(match.round, stage_name, config)

    # Get tournament name from config
    challonge_cfg = config.get("challonge", {}) or {}
    tournament_name = challonge_cfg.get("tournament", "")
    subdomain = challonge_cfg.get("subdomain", "")

    # Construct match URL
    if subdomain:
        match_url = f"https://{subdomain}.challonge.com/{tournament_name}/matches/{match.match_id}"
    else:
        match_url = f"https://challonge.com/{tournament_name}/matches/{match.match_id}"

    return template.format(
        round_label=round_label,
        p1_name=match.p1_name,
        p2_name=match.p2_name,
        p1_mention=match.p1_mention,
        p2_mention=match.p2_mention,
        role_mentions=role_mentions,
        match_id=match.match_id,
        match_state=match.state,
        tournament_name=tournament_name,
        match_url=match_url,
        stage=stage_name or "",
        bracket="Winners" if match.round > 0 else ("Losers" if match.round < 0 else "Round"),
        round=match.round,
        abs_round=abs(match.round),
    )


def format_thread_message(
    match: Match,
    stage_name: str | None,
    config: dict[str, Any],
    role_mentions: str = "",
) -> str:
    """Format a thread message from a template.

    Args:
        match: Match object with participant data.
        stage_name: Tournament stage type.
        config: Configuration dictionary.
        role_mentions: Role mention string.

    Returns:
        Formatted message string.
    """
    template = str(config.get("message_template", DEFAULT_MESSAGE_TEMPLATE))
    round_label = make_round_label(match.round, stage_name, config)

    # Get tournament name from config
    challonge_cfg = config.get("challonge", {}) or {}
    tournament_name = challonge_cfg.get("tournament", "")
    subdomain = challonge_cfg.get("subdomain", "")

    # Construct match URL
    if subdomain:
        match_url = f"https://{subdomain}.challonge.com/{tournament_name}/matches/{match.match_id}"
    else:
        match_url = f"https://challonge.com/{tournament_name}/matches/{match.match_id}"

    return template.format(
        round_label=round_label,
        p1_name=match.p1_name,
        p2_name=match.p2_name,
        p1_mention=match.p1_mention,
        p2_mention=match.p2_mention,
        role_mentions=role_mentions,
        match_id=match.match_id,
        match_state=match.state,
        tournament_name=tournament_name,
        match_url=match_url,
        stage=stage_name or "",
        bracket="Winners" if match.round > 0 else ("Losers" if match.round < 0 else "Round"),
        round=match.round,
        abs_round=abs(match.round),
    )


def print_dry_run(matches: list, stage_name: str | None, config: dict[str, Any]) -> None:
    """Print a dry-run preview of threads that would be created.

    Args:
        matches: List of Match objects to preview.
        stage_name: Tournament stage type.
        config: Configuration dictionary.
    """
    discord_cfg = config.get("discord", {}) or {}
    role_ids = discord_cfg.get("role_ids_to_tag")
    if not isinstance(role_ids, list):
        role_ids = []
    role_mentions = build_role_mentions(role_ids)

    if not matches:
        print("=== DRY RUN ===\n(No matches to show)\n=== END DRY RUN ===")
        return

    print("=== DRY RUN: Discord threads preview ===")
    for match in matches:
        thread_name = format_thread_name(match, stage_name, config, role_mentions)
        message_body = format_thread_message(match, stage_name, config, role_mentions)

        print(f"\nTHREAD: {thread_name}\nMESSAGE:\n{message_body}\n")

    print("=== END DRY RUN ===")


def print_debug_summary(matches: list, stage_name: str | None, config: dict[str, Any]) -> None:
    """Print a debug summary of matches.

    Args:
        matches: List of Match objects to summarize.
        stage_name: Tournament stage type.
        config: Configuration dictionary.
    """
    if not matches:
        print("\n(No matches returned)")
        return

    print("\n=== Matches Summary ===")
    for match in matches:
        round_label = make_round_label(match.round, stage_name, config)
        p1_id = match.player1.id if match.player1 else None
        p2_id = match.player2.id if match.player2 else None

        print(
            f"- match_id={match.match_id}  state={match.state}  "
            f"round={match.round} ({round_label})  "
            f"p1_id={p1_id} username='{match.p1_name}' mention={match.p1_mention}  "
            f"p2_id={p2_id} username='{match.p2_name}' mention={match.p2_mention}"
        )
