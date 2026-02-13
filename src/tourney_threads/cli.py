"""Command-line interface for tourney_threads.

This module provides CLI argument parsing and main orchestration logic.
"""

import argparse
import asyncio
from typing import Dict, Any

from .api import ChallongeAPIClient
from .discord_client import DiscordThreadManager, print_dry_run, print_debug_summary
from .config import load_config, validate_config, validate_discord_config


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Challonge v2: list matches via /matches and create/preview Discord threads."
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml (default: config.yaml)"
    )
    parser.add_argument(
        "--tournament",
        help="Override tournament slug/id from config (e.g., EBSSTEST)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print raw JSON and match summary"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print thread previews instead of creating them"
    )
    return parser.parse_args()


async def run_async(args: argparse.Namespace) -> None:
    """Main async execution logic.
    
    Args:
        args: Parsed command-line arguments.
    """
    # Load and validate configuration
    config = load_config(args.config)
    validate_config(config)
    
    # Validate Discord config only if not in dry-run mode
    if not args.dry_run:
        validate_discord_config(config)
    
    # Create API client
    api_client = ChallongeAPIClient(config, debug=args.debug)
    
    # Fetch matches and participants
    runner_map = config.get("runner_map", {}) or {}
    matches, _ = await api_client.fetch_matches(
        tournament_override=args.tournament,
        runner_map=runner_map,
    )
    
    # Probe tournament stage type
    stage_name = await api_client.probe_stage_type(tournament_override=args.tournament)
    
    # Debug summary
    if args.debug:
        print_debug_summary(matches, stage_name, config)
    
    # Dry-run or actual thread creation
    if args.dry_run:
        print_dry_run(matches, stage_name, config)
    else:
        thread_manager = DiscordThreadManager(config, stage_name)
        await thread_manager.create_threads(matches)


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()
    asyncio.run(run_async(args))


if __name__ == "__main__":
    main()
