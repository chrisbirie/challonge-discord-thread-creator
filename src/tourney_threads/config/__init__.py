"""Configuration handling for tourney_threads.

This module provides configuration loading, validation, and constants.
"""

from .loader import load_config, validate_config, validate_discord_config
from .constants import (
    DEFAULT_API_BASE_URL,
    DEFAULT_TOKEN_URL,
    DEFAULT_PATH_SUFFIX,
    DEFAULT_THREAD_NAME_TEMPLATE,
    DEFAULT_MESSAGE_TEMPLATE,
    DEFAULT_THREAD_ARCHIVE_MINUTES,
    MAX_THREAD_NAME_LENGTH,
)

__all__ = [
    "load_config",
    "validate_config",
    "validate_discord_config",
    "DEFAULT_API_BASE_URL",
    "DEFAULT_TOKEN_URL",
    "DEFAULT_PATH_SUFFIX",
    "DEFAULT_THREAD_NAME_TEMPLATE",
    "DEFAULT_MESSAGE_TEMPLATE",
    "DEFAULT_THREAD_ARCHIVE_MINUTES",
    "MAX_THREAD_NAME_LENGTH",
]
