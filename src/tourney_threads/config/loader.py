"""Configuration file loading and validation."""

from typing import Any

import yaml  # type: ignore[import-untyped]


def load_config(path: str) -> dict[str, Any]:
    """Load configuration from a YAML file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        Dictionary containing configuration data.

    Raises:
        FileNotFoundError: If the configuration file doesn't exist.
        yaml.YAMLError: If the YAML is malformed.
    """
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate_config(cfg: dict[str, Any]) -> None:
    """Validate that required configuration keys are present.

    Args:
        cfg: Configuration dictionary to validate.

    Raises:
        ValueError: If required configuration keys are missing.
    """
    # Validate OAuth2 configuration
    oauth_cfg = cfg.get("oauth2")
    if not oauth_cfg:
        raise ValueError("Missing required 'oauth2' section in config")

    required_oauth = ["client_id", "client_secret"]
    for key in required_oauth:
        if not oauth_cfg.get(key):
            raise ValueError(f"Missing required oauth2.{key} in config")

    # Validate Challonge configuration
    challonge_cfg = cfg.get("challonge")
    if not challonge_cfg:
        raise ValueError("Missing required 'challonge' section in config")

    if not challonge_cfg.get("tournament"):
        raise ValueError("Missing required challonge.tournament in config")

    # Validate Discord configuration (only if not in dry-run mode)
    # Note: This should be called conditionally based on dry_run flag
    discord_cfg = cfg.get("discord")
    if discord_cfg:
        required_discord = ["bot_token", "channel_id"]
        for key in required_discord:
            if not discord_cfg.get(key):
                raise ValueError(f"Missing required discord.{key} in config")


def validate_discord_config(cfg: dict[str, Any]) -> None:
    """Validate Discord-specific configuration.

    Call this only when actually creating threads (not in dry-run mode).

    Args:
        cfg: Configuration dictionary to validate.

    Raises:
        ValueError: If required Discord configuration is missing.
    """
    discord_cfg = cfg.get("discord")
    if not discord_cfg:
        raise ValueError("Missing required 'discord' section in config")

    required_discord = ["bot_token", "channel_id"]
    for key in required_discord:
        if not discord_cfg.get(key):
            raise ValueError(f"Missing required discord.{key} in config")
