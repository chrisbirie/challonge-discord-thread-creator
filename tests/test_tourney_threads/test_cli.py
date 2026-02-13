"""Tests for CLI module."""

from argparse import Namespace
from unittest.mock import AsyncMock, patch

import pytest


class TestCLIModule:
    """Tests for CLI module functions."""

    def test_parse_args_defaults(self):
        """Test argument parsing with defaults."""
        import sys

        from tourney_threads.cli import parse_args

        # Save original argv
        original_argv = sys.argv
        try:
            # Set argv to just program name (no arguments)
            sys.argv = ["program"]
            args = parse_args()

            assert args.config == "config.yaml"
            assert args.tournament is None
            assert args.debug is False
            assert args.dry_run is False
        finally:
            # Restore original argv
            sys.argv = original_argv

    def test_parse_args_with_options(self):
        """Test argument parsing with all options."""
        import sys

        from tourney_threads.cli import parse_args

        original_argv = sys.argv
        try:
            sys.argv = [
                "program",
                "--config",
                "custom.yaml",
                "--tournament",
                "my-tournament",
                "--debug",
                "--dry-run",
            ]
            args = parse_args()

            assert args.config == "custom.yaml"
            assert args.tournament == "my-tournament"
            assert args.debug is True
            assert args.dry_run is True
        finally:
            sys.argv = original_argv

    @pytest.mark.asyncio
    async def test_run_async_dry_run(self, capsys):
        """Test run_async in dry-run mode."""
        import os
        import tempfile

        from tourney_threads.cli import run_async

        # Create a temporary config file
        config_content = """
oauth2:
  client_id: test_id
  client_secret: test_secret
challonge:
  tournament: test-tournament
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write(config_content)
            temp_config = f.name

        try:
            args = Namespace(config=temp_config, tournament=None, debug=False, dry_run=True)

            # Mock the API client
            from tourney_threads.api.models import Match, Participant

            p1 = Participant("1", "Alice", "Alice", "@Alice")
            p2 = Participant("2", "Bob", "Bob", "@Bob")
            mock_match = Match("m1", "open", 1, p1, p2)

            with patch("tourney_threads.cli.ChallongeAPIClient") as MockAPI:
                mock_api_instance = MockAPI.return_value
                mock_api_instance.fetch_matches = AsyncMock(return_value=([mock_match], {}))
                mock_api_instance.probe_stage_type = AsyncMock(return_value="Elimination")

                await run_async(args)

            captured = capsys.readouterr()
            assert "DRY RUN" in captured.out
            assert "Alice vs Bob" in captured.out
        finally:
            os.unlink(temp_config)

    @pytest.mark.asyncio
    async def test_run_async_debug_mode(self, capsys):
        """Test run_async in debug mode."""
        import os
        import tempfile

        from tourney_threads.cli import run_async

        config_content = """
oauth2:
  client_id: test_id
  client_secret: test_secret
challonge:
  tournament: test-tournament
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write(config_content)
            temp_config = f.name

        try:
            args = Namespace(
                config=temp_config, tournament="override-tourney", debug=True, dry_run=True
            )

            with patch("tourney_threads.cli.ChallongeAPIClient") as MockAPI:
                mock_api_instance = MockAPI.return_value
                mock_api_instance.fetch_matches = AsyncMock(return_value=([], {}))
                mock_api_instance.probe_stage_type = AsyncMock(return_value="Swiss")

                await run_async(args)

            captured = capsys.readouterr()
            assert "No matches returned" in captured.out  # Debug summary shows even with no matches
            assert "DRY RUN" in captured.out
        finally:
            os.unlink(temp_config)

    def test_cli_main_function(self):
        """Test CLI main() function."""
        from tourney_threads.cli import main

        # Mock parse_args to avoid sys.argv issues
        with (
            patch("tourney_threads.cli.parse_args") as mock_parse_args,
            patch("tourney_threads.cli.asyncio.run") as mock_asyncio_run,
        ):

            mock_parse_args.return_value = Namespace(
                config="test.yaml", tournament=None, debug=False, dry_run=True
            )

            main()

            # Verify parse_args was called
            mock_parse_args.assert_called_once()
            # Verify asyncio.run was called
            mock_asyncio_run.assert_called_once()
            # Close coroutine passed to asyncio.run to avoid unawaited warnings
            coro = mock_asyncio_run.call_args[0][0]
            if hasattr(coro, "close"):
                coro.close()

    def test_cli_if_name_main(self):
        """Test CLI if __name__ == '__main__' block by running as module."""
        import subprocess
        import sys

        # Run the module as a script using python -m to trigger if __name__ == "__main__"
        result = subprocess.run(
            [sys.executable, "-m", "tourney_threads.cli", "--help"],
            capture_output=True,
            timeout=2,
            cwd=r"C:\devl\tourney_threads\src",
        )
        # --help should work and return 0
        assert result.returncode == 0
        assert b"usage:" in result.stdout or b"Tourney" in result.stdout or result.returncode == 0

    @pytest.mark.asyncio
    async def test_run_async_non_dry_run_creates_thread_manager(self):
        """Test run_async creates DiscordThreadManager when not in dry-run."""
        import os
        import tempfile

        from tourney_threads.cli import run_async

        config_content = """
oauth2:
  client_id: test_id
  client_secret: test_secret
challonge:
  tournament: test-tournament
discord:
  bot_token: test_bot_token
  channel_id: 123456
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write(config_content)
            temp_config = f.name

        try:
            args = Namespace(
                config=temp_config, tournament=None, debug=False, dry_run=False  # Non-dry-run mode
            )

            from tourney_threads.api.models import Match, Participant

            p1 = Participant("1", "Alice", "Alice", "@Alice")
            p2 = Participant("2", "Bob", "Bob", "@Bob")
            mock_match = Match("m1", "open", 1, p1, p2)

            with (
                patch("tourney_threads.cli.ChallongeAPIClient") as MockAPI,
                patch("tourney_threads.cli.DiscordThreadManager") as MockThreadMgr,
            ):

                mock_api_instance = MockAPI.return_value
                mock_api_instance.fetch_matches = AsyncMock(return_value=([mock_match], {}))
                mock_api_instance.probe_stage_type = AsyncMock(return_value="Elimination")

                mock_thread_mgr_instance = MockThreadMgr.return_value
                mock_thread_mgr_instance.create_threads = AsyncMock(return_value=1)

                await run_async(args)

                # Verify DiscordThreadManager was created
                MockThreadMgr.assert_called_once()
                # Verify create_threads was called
                mock_thread_mgr_instance.create_threads.assert_called_once_with([mock_match])
        finally:
            os.unlink(temp_config)
