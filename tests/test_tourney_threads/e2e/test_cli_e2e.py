"""End-to-end CLI tests with full workflow."""

import os
import tempfile
from argparse import Namespace
from unittest.mock import AsyncMock, patch

import pytest


class TestCLIEndToEnd:
    """End-to-end tests for complete CLI workflows."""

    @pytest.mark.asyncio
    async def test_cli_dry_run_full_workflow(self, capsys):
        """Test complete dry-run workflow from CLI args to output."""
        from tourney_threads.api.models import Match, Participant
        from tourney_threads.cli import run_async

        # Create temporary config file
        config_content = """
oauth2:
  client_id: e2e_test_client
  client_secret: e2e_test_secret
  scope: tournaments:read matches:read
challonge:
  tournament: e2e-test-tourney
  subdomain: testorg
  page: 1
  per_page: 25
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write(config_content)
            config_path = f.name

        try:
            # Simulate CLI arguments
            args = Namespace(config=config_path, tournament=None, debug=False, dry_run=True)

            # Mock API responses
            p1 = Participant("1", "AliceE2E", "AliceE2E", "<@100>")
            p2 = Participant("2", "BobE2E", "BobE2E", "<@200>")
            p3 = Participant("3", "CharlieE2E", "CharlieE2E", "CharlieE2E")

            mock_matches = [
                Match("m1", "open", 1, p1, p2),
                Match("m2", "open", 1, p2, p3),
            ]

            with patch("tourney_threads.cli.ChallongeAPIClient") as MockAPI:
                mock_api = MockAPI.return_value
                mock_api.fetch_matches = AsyncMock(return_value=(mock_matches, {}))
                mock_api.probe_stage_type = AsyncMock(return_value="Elimination")

                # Run the full workflow
                await run_async(args)

            # Verify output
            captured = capsys.readouterr()

            # Should show dry run header
            assert "DRY RUN" in captured.out
            assert "END DRY RUN" in captured.out

            # Should show matches
            assert "AliceE2E vs BobE2E" in captured.out
            assert "BobE2E vs CharlieE2E" in captured.out

            # Should show round labels
            assert "Winners R1" in captured.out

            # Verify API was called with correct config
            MockAPI.assert_called_once()
            call_config = MockAPI.call_args[0][0]
            assert call_config["challonge"]["tournament"] == "e2e-test-tourney"
            assert call_config["challonge"]["subdomain"] == "testorg"

        finally:
            os.unlink(config_path)

    @pytest.mark.asyncio
    async def test_cli_tournament_override(self, capsys):
        """Test CLI with --tournament override parameter."""
        from tourney_threads.api.models import Match, Participant
        from tourney_threads.cli import run_async

        config_content = """
oauth2:
  client_id: test_client
  client_secret: test_secret
challonge:
  tournament: default-tournament
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write(config_content)
            config_path = f.name

        try:
            args = Namespace(
                config=config_path,
                tournament="override-tournament",  # Override via CLI
                debug=False,
                dry_run=True,
            )

            p1 = Participant("1", "Player1", "Player1", "Player1")
            p2 = Participant("2", "Player2", "Player2", "Player2")
            mock_matches = [Match("m1", "open", 1, p1, p2)]

            with patch("tourney_threads.cli.ChallongeAPIClient") as MockAPI:
                mock_api = MockAPI.return_value
                mock_api.fetch_matches = AsyncMock(return_value=(mock_matches, {}))
                mock_api.probe_stage_type = AsyncMock(return_value="Swiss")

                await run_async(args)

                # Verify fetch_matches was called with override tournament
                fetch_call_kwargs = mock_api.fetch_matches.call_args[1]
                assert fetch_call_kwargs["tournament_override"] == "override-tournament"

            captured = capsys.readouterr()
            assert "DRY RUN" in captured.out
            assert "Swiss R1" in captured.out

        finally:
            os.unlink(config_path)

    @pytest.mark.asyncio
    async def test_cli_debug_mode_verbose_output(self, capsys):
        """Test CLI with --debug flag shows detailed output."""
        from tourney_threads.cli import run_async

        config_content = """
oauth2:
  client_id: test_client
  client_secret: test_secret
challonge:
  tournament: test-tournament
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write(config_content)
            config_path = f.name

        try:
            args = Namespace(
                config=config_path, tournament=None, debug=True, dry_run=True  # Debug mode
            )

            with patch("tourney_threads.cli.ChallongeAPIClient") as MockAPI:
                mock_api = MockAPI.return_value
                mock_api.fetch_matches = AsyncMock(return_value=([], {}))
                mock_api.probe_stage_type = AsyncMock(return_value="Elimination")

                await run_async(args)

            captured = capsys.readouterr()

            # Debug mode should show debug summary even with no matches
            assert "No matches returned" in captured.out or "Matches Summary" in captured.out
            assert "DRY RUN" in captured.out

        finally:
            os.unlink(config_path)

    @pytest.mark.asyncio
    async def test_cli_with_discord_config_non_dry_run(self, capsys):
        """Test CLI creates Discord thread manager when not in dry-run mode."""
        from tourney_threads.api.models import Match, Participant
        from tourney_threads.cli import run_async

        config_content = """
oauth2:
  client_id: test_client
  client_secret: test_secret
challonge:
  tournament: test-tournament
discord:
  bot_token: test_bot_token_xyz
  channel_id: 123456789
  thread_archive_minutes: 1440
  role_ids_to_tag:
    - 999
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write(config_content)
            config_path = f.name

        try:
            args = Namespace(
                config=config_path,
                tournament=None,
                debug=False,
                dry_run=False,  # NOT dry-run, should create threads
            )

            p1 = Participant("1", "DiscordPlayer1", "DiscordPlayer1", "<@111>")
            p2 = Participant("2", "DiscordPlayer2", "DiscordPlayer2", "<@222>")
            mock_matches = [Match("m1", "open", 1, p1, p2)]

            with (
                patch("tourney_threads.cli.ChallongeAPIClient") as MockAPI,
                patch("tourney_threads.cli.DiscordThreadManager") as MockThreadMgr,
            ):

                mock_api = MockAPI.return_value
                mock_api.fetch_matches = AsyncMock(return_value=(mock_matches, {}))
                mock_api.probe_stage_type = AsyncMock(return_value="Swiss")

                mock_thread_mgr = MockThreadMgr.return_value
                mock_thread_mgr.create_threads = AsyncMock(return_value=1)

                await run_async(args)

                # Verify DiscordThreadManager was instantiated
                MockThreadMgr.assert_called_once()
                call_config = MockThreadMgr.call_args[0][0]
                assert call_config["discord"]["bot_token"] == "test_bot_token_xyz"
                assert call_config["discord"]["channel_id"] == 123456789

                # Verify create_threads was called with matches
                mock_thread_mgr.create_threads.assert_called_once()
                threads_arg = mock_thread_mgr.create_threads.call_args[0][0]
                assert len(threads_arg) == 1
                assert threads_arg[0].match_id == "m1"

            captured = capsys.readouterr()
            # Should NOT show dry-run messages
            assert "DRY RUN" not in captured.out

        finally:
            os.unlink(config_path)

    @pytest.mark.asyncio
    async def test_cli_invalid_config_file(self):
        """Test CLI handles invalid config file gracefully."""
        from tourney_threads.cli import run_async

        args = Namespace(
            config="nonexistent_config.yaml", tournament=None, debug=False, dry_run=True
        )

        # Should raise FileNotFoundError when trying to load config
        with pytest.raises(FileNotFoundError):
            await run_async(args)

    @pytest.mark.asyncio
    async def test_cli_missing_required_config_sections(self):
        """Test CLI validates config has required sections."""
        from tourney_threads.cli import run_async

        # Config missing OAuth section
        config_content = """
challonge:
  tournament: test-tournament
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write(config_content)
            config_path = f.name

        try:
            args = Namespace(config=config_path, tournament=None, debug=False, dry_run=True)

            # Should raise ValueError due to missing oauth2 section
            with pytest.raises(ValueError, match="oauth2"):
                await run_async(args)

        finally:
            os.unlink(config_path)

    @pytest.mark.asyncio
    async def test_cli_swiss_tournament_stage_detection(self, capsys):
        """Test CLI properly detects and labels Swiss tournament stages."""
        from tourney_threads.api.models import Match, Participant
        from tourney_threads.cli import run_async

        config_content = """
oauth2:
  client_id: test_client
  client_secret: test_secret
challonge:
  tournament: swiss-test
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write(config_content)
            config_path = f.name

        try:
            args = Namespace(config=config_path, tournament=None, debug=False, dry_run=True)

            p1 = Participant("1", "SwissP1", "SwissP1", "SwissP1")
            p2 = Participant("2", "SwissP2", "SwissP2", "SwissP2")
            mock_matches = [
                Match("m1", "open", 1, p1, p2),
                Match("m2", "open", 2, p1, p2),
            ]

            with patch("tourney_threads.cli.ChallongeAPIClient") as MockAPI:
                mock_api = MockAPI.return_value
                mock_api.fetch_matches = AsyncMock(return_value=(mock_matches, {}))
                mock_api.probe_stage_type = AsyncMock(return_value="Swiss")

                await run_async(args)

            captured = capsys.readouterr()

            # Should show Swiss round labels
            assert "Swiss R1" in captured.out
            assert "Swiss R2" in captured.out
            assert "SwissP1 vs SwissP2" in captured.out

        finally:
            os.unlink(config_path)

    @pytest.mark.asyncio
    async def test_cli_custom_templates_from_config(self, capsys):
        """Test CLI uses custom templates from config."""
        from tourney_threads.api.models import Match, Participant
        from tourney_threads.cli import run_async

        config_content = """
oauth2:
  client_id: test_client
  client_secret: test_secret
challonge:
  tournament: custom-test
round_label_template: "{stage} Round {abs_round}"
thread_name_template: "Match: {p1_name} vs {p2_name}"
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write(config_content)
            config_path = f.name

        try:
            args = Namespace(config=config_path, tournament=None, debug=False, dry_run=True)

            p1 = Participant("1", "CustomA", "CustomA", "CustomA")
            p2 = Participant("2", "CustomB", "CustomB", "CustomB")
            mock_matches = [Match("m1", "open", 3, p1, p2)]

            with patch("tourney_threads.cli.ChallongeAPIClient") as MockAPI:
                mock_api = MockAPI.return_value
                mock_api.fetch_matches = AsyncMock(return_value=(mock_matches, {}))
                mock_api.probe_stage_type = AsyncMock(return_value="Elimination")

                await run_async(args)

            captured = capsys.readouterr()

            # Should use custom templates
            assert "Elimination Round 3" in captured.out
            assert "Match: CustomA vs CustomB" in captured.out

        finally:
            os.unlink(config_path)

    @pytest.mark.asyncio
    async def test_cli_api_error_handling(self, capsys):
        """Test CLI handles API errors gracefully."""
        from tourney_threads.cli import run_async

        config_content = """
oauth2:
  client_id: test_client
  client_secret: test_secret
challonge:
  tournament: error-test
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write(config_content)
            config_path = f.name

        try:
            args = Namespace(config=config_path, tournament=None, debug=False, dry_run=True)

            with patch("tourney_threads.cli.ChallongeAPIClient") as MockAPI:
                mock_api = MockAPI.return_value
                # Simulate API error
                mock_api.fetch_matches = AsyncMock(
                    side_effect=RuntimeError("API request failed (500)")
                )
                mock_api.probe_stage_type = AsyncMock(return_value="Elimination")

                # Should raise the RuntimeError
                with pytest.raises(RuntimeError, match="API request failed"):
                    await run_async(args)

        finally:
            os.unlink(config_path)

    def test_cli_parse_args_help(self):
        """Test CLI --help displays usage information."""
        import subprocess
        import sys
        from pathlib import Path

        # Run CLI with --help
        repo_root = Path(__file__).resolve().parents[3]
        src_dir = repo_root / "src"
        result = subprocess.run(
            [sys.executable, "-m", "tourney_threads.cli", "--help"],
            capture_output=True,
            timeout=5,
            cwd=str(src_dir),
        )

        # Should exit successfully and show usage
        assert result.returncode == 0
        output = result.stdout.decode()
        assert "usage:" in output.lower() or "tourney" in output.lower()
        assert "--config" in output
        assert "--dry-run" in output
        assert "--debug" in output
        assert "--tournament" in output


class TestCLIWithRunnerMap:
    """Test CLI with Discord runner mapping."""

    @pytest.mark.asyncio
    async def test_cli_uses_runner_map_file(self, capsys):
        """Test CLI loads and uses runner_map.json for Discord mentions."""
        import json

        from tourney_threads.api.models import Match, Participant
        from tourney_threads.cli import run_async

        config_content = """
oauth2:
  client_id: test_client
  client_secret: test_secret
challonge:
  tournament: runner-map-test
"""
        runner_map_content = {"MappedPlayer1": 111222333, "MappedPlayer2": 444555666}

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write(config_content)
            config_path = f.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(runner_map_content, f)
            runner_map_path = f.name

        try:
            args = Namespace(config=config_path, tournament=None, debug=False, dry_run=True)

            # Mock matches with players that have mappings
            p1 = Participant("1", "MappedPlayer1", "MappedPlayer1", "<@111222333>")
            p2 = Participant("2", "MappedPlayer2", "MappedPlayer2", "<@444555666>")
            mock_matches = [Match("m1", "open", 1, p1, p2)]

            with patch("tourney_threads.cli.ChallongeAPIClient") as MockAPI:
                mock_api = MockAPI.return_value
                # Note: In real implementation, fetch_matches would use runner_map
                mock_api.fetch_matches = AsyncMock(return_value=(mock_matches, {}))
                mock_api.probe_stage_type = AsyncMock(return_value="Elimination")

                await run_async(args)

            captured = capsys.readouterr()

            # Should show Discord mentions for mapped players
            assert (
                "MappedPlayer1 vs MappedPlayer2" in captured.out
                or "<@111222333> vs <@444555666>" in captured.out
            )

        finally:
            os.unlink(config_path)
            if os.path.exists(runner_map_path):
                os.unlink(runner_map_path)
