"""Utility functions for handling names and mentions.

This module provides utilities for cleaning participant names and building Discord mentions.
"""

import re

# Regex to remove "(invitation pending)" suffix from participant names
_INVITE_SUFFIX_RE = re.compile(r"\s*\(invitation pending\)\s*$", re.IGNORECASE)


def clean_runner_name(name: str) -> str:
    """Clean a participant name by removing invitation pending suffix.

    Args:
        name: Raw participant name from Challonge.

    Returns:
        Cleaned name with invitation suffix removed.
    """
    if not isinstance(name, str):
        return "UNKNOWN"
    return _INVITE_SUFFIX_RE.sub("", name).strip()


def participant_username(participant_item: dict) -> str:
    """Extract username from a participant resource.

    Tries multiple fields in order: username, name, display_name.

    Args:
        participant_item: Participant resource dict from Challonge API.

    Returns:
        Participant username or 'UNKNOWN' if not found.
    """
    if not participant_item:
        return "UNKNOWN"
    attrs = participant_item.get("attributes") or {}
    return attrs.get("username") or attrs.get("name") or attrs.get("display_name") or "UNKNOWN"


def mention_for_name(name: str, runner_map: dict[str, int]) -> str:
    """Build Discord mention string for a participant name.

    Args:
        name: Participant username.
        runner_map: Mapping of usernames to Discord user IDs.

    Returns:
        Discord mention string (<@user_id>) or username if no mapping exists.
    """
    user_id = runner_map.get(name)
    return f"<@{user_id}>" if user_id else name


def build_role_mentions(role_ids: list[int] | None = None) -> str:
    """Build Discord role mention strings from role IDs.

    Args:
        role_ids: List of Discord role IDs to mention.

    Returns:
        Space-separated role mention strings (<@&role_id>).
    """
    role_ids = role_ids or []
    return " ".join(f"<@&{rid}>" for rid in role_ids)
