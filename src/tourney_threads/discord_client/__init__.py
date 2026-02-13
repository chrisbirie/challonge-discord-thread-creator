"""Discord client module for thread creation.

This package provides Discord thread creation and formatting functionality.
"""

from .thread_manager import DiscordThreadManager
from .formatters import (
    format_thread_name,
    format_thread_message,
    print_dry_run,
    print_debug_summary,
)

__all__ = [
    "DiscordThreadManager",
    "format_thread_name",
    "format_thread_message",
    "print_dry_run",
    "print_debug_summary",
]
