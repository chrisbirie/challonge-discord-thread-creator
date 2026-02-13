"""Tourney Threads - Discord thread creator for Challonge tournaments.

This module serves as the main entry point for the application.
It imports and delegates to the CLI module which contains the actual implementation.
"""

from .cli import main

if __name__ == "__main__":
    main()
