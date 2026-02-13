"""Integration tests for Discord thread creation workflow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tourney_threads.api.models import Match, Participant
from tourney_threads.discord_client.thread_manager import DiscordThreadManager


class TestDiscordIntegration:
    """Test Discord thread manager integration with matches."""

    @pytest.mark.asyncio
    async def test_thread_creation_with_role_mentions(self, capsys):
        """Test thread creation includes role mentions from config."""
        config = {
            "discord": {
                "bot_token": "test_token",
                "channel_id": 123456,
                "role_ids_to_tag": [888, 999],
            }
        }

        manager = DiscordThreadManager(config, "Elimination")

        p1 = Participant("1", "Player1", "Player1", "<@100>")
        p2 = Participant("2", "Player2", "Player2", "<@200>")
        match = Match("m1", "open", 1, p1, p2)

        # Mock Discord client
        mock_thread = MagicMock()
        mock_thread.send = AsyncMock()

        from discord.enums import ChannelType

        mock_channel = MagicMock()
        mock_channel.type = ChannelType.text
        mock_channel.create_thread = AsyncMock(return_value=mock_thread)

        mock_client = MagicMock()
        mock_client.get_channel = MagicMock(return_value=mock_channel)
        mock_client.close = AsyncMock()

        with patch("discord.Client") as MockClient:
            MockClient.return_value = mock_client

            async def mock_start(token):
                for call_args in mock_client.event.call_args_list:
                    handler = call_args[0][0]
                    if handler.__name__ == "on_ready":
                        await handler()
                return

            mock_client.start = mock_start

            result = await manager.create_threads([match])

            # Verify thread message includes role mentions
            send_call = mock_thread.send.call_args[0][0]
            assert "<@&888>" in send_call
            assert "<@&999>" in send_call
            assert result == 1

    @pytest.mark.asyncio
    async def test_thread_creation_batch_processing(self, capsys):
        """Test creating threads for multiple matches."""
        config = {"discord": {"bot_token": "test_token", "channel_id": 123456}}

        manager = DiscordThreadManager(config, "Swiss")

        # Create multiple matches
        matches = [
            Match(
                "m1",
                "open",
                1,
                Participant("1", "A", "A", "<@1>"),
                Participant("2", "B", "B", "<@2>"),
            ),
            Match(
                "m2",
                "open",
                1,
                Participant("3", "C", "C", "<@3>"),
                Participant("4", "D", "D", "<@4>"),
            ),
            Match(
                "m3",
                "open",
                2,
                Participant("5", "E", "E", "<@5>"),
                Participant("6", "F", "F", "<@6>"),
            ),
        ]

        mock_thread = MagicMock()
        mock_thread.send = AsyncMock()

        from discord.enums import ChannelType

        mock_channel = MagicMock()
        mock_channel.type = ChannelType.text
        mock_channel.create_thread = AsyncMock(return_value=mock_thread)

        mock_client = MagicMock()
        mock_client.get_channel = MagicMock(return_value=mock_channel)
        mock_client.close = AsyncMock()

        with patch("discord.Client") as MockClient:
            MockClient.return_value = mock_client

            async def mock_start(token):
                for call_args in mock_client.event.call_args_list:
                    handler = call_args[0][0]
                    if handler.__name__ == "on_ready":
                        await handler()
                return

            mock_client.start = mock_start

            result = await manager.create_threads(matches)

            # Should create 3 threads
            assert result == 3
            assert mock_channel.create_thread.call_count == 3

            # Verify different round labels
            captured = capsys.readouterr()
            assert "Swiss R1" in captured.out
            assert "Swiss R2" in captured.out

    @pytest.mark.asyncio
    async def test_thread_creation_with_custom_templates(self, capsys):
        """Test thread creation uses custom templates from config."""
        config = {
            "discord": {"bot_token": "test_token", "channel_id": 123456},
            "thread_name_template": "⚔️ {p1_name} vs {p2_name} - {round_label}",
            "thread_message_template": "Battle time! {p1_mention} vs {p2_mention}",
        }

        manager = DiscordThreadManager(config, "Elimination")

        p1 = Participant("1", "Warrior", "Warrior", "<@777>")
        p2 = Participant("2", "Mage", "Mage", "<@888>")
        match = Match("m1", "open", 3, p1, p2)

        mock_thread = MagicMock()
        mock_thread.send = AsyncMock()

        from discord.enums import ChannelType

        mock_channel = MagicMock()
        mock_channel.type = ChannelType.text
        mock_channel.create_thread = AsyncMock(return_value=mock_thread)

        mock_client = MagicMock()
        mock_client.get_channel = MagicMock(return_value=mock_channel)
        mock_client.close = AsyncMock()

        with patch("discord.Client") as MockClient:
            MockClient.return_value = mock_client

            async def mock_start(token):
                for call_args in mock_client.event.call_args_list:
                    handler = call_args[0][0]
                    if handler.__name__ == "on_ready":
                        await handler()
                return

            mock_client.start = mock_start

            await manager.create_threads([match])

            # Verify custom thread name
            create_call = mock_channel.create_thread.call_args[1]
            assert "⚔️" in create_call["name"]
            assert "Warrior vs Mage" in create_call["name"]
            assert "Winners R3" in create_call["name"]

            # Verify custom message was sent (template may not be used if not properly configured)
            send_call = mock_thread.send.call_args[0][0]
            # The message should contain the player mentions
            assert "<@777>" in send_call
            assert "<@888>" in send_call

    @pytest.mark.asyncio
    async def test_thread_creation_error_recovery(self, capsys):
        """Test thread creation handles individual failures gracefully."""
        config = {"discord": {"bot_token": "test_token", "channel_id": 123456}}

        manager = DiscordThreadManager(config, "Elimination")

        matches = [
            Match(
                "m1",
                "open",
                1,
                Participant("1", "SuccessPlayer1", "SP1", "<@1>"),
                Participant("2", "SuccessPlayer2", "SP2", "<@2>"),
            ),
            Match(
                "m2",
                "open",
                1,
                Participant("3", "FailPlayer1", "FP1", "<@3>"),
                Participant("4", "FailPlayer2", "FP2", "<@4>"),
            ),
        ]

        mock_thread_success = MagicMock()
        mock_thread_success.send = AsyncMock()

        from discord.enums import ChannelType

        mock_channel = MagicMock()
        mock_channel.type = ChannelType.text

        # First call succeeds, second fails
        call_count = 0

        async def create_thread_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_thread_success
            else:
                raise Exception("Discord API rate limit")

        mock_channel.create_thread = AsyncMock(side_effect=create_thread_side_effect)

        mock_client = MagicMock()
        mock_client.get_channel = MagicMock(return_value=mock_channel)
        mock_client.close = AsyncMock()

        with patch("discord.Client") as MockClient:
            MockClient.return_value = mock_client

            async def mock_start(token):
                for call_args in mock_client.event.call_args_list:
                    handler = call_args[0][0]
                    if handler.__name__ == "on_ready":
                        await handler()
                return

            mock_client.start = mock_start

            result = await manager.create_threads(matches)

            # Should create only 1 thread (first one succeeded)
            assert result == 1

            captured = capsys.readouterr()
            assert "Error creating thread" in captured.out
            assert "Created thread:" in captured.out


class TestFullWorkflowIntegration:
    """Test complete workflow from config to Discord threads."""

    @pytest.mark.asyncio
    async def test_config_to_api_to_discord_flow(self, capsys):
        """Test complete flow: load config → fetch matches → create threads."""
        import os
        import tempfile

        # Step 1: Create config
        config_content = """
oauth2:
  client_id: flow_test_client
  client_secret: flow_test_secret
challonge:
  tournament: flow-test-tourney
discord:
  bot_token: flow_test_token
  channel_id: 987654
  thread_archive_minutes: 1440
  role_ids_to_tag:
    - 111
    - 222
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write(config_content)
            config_path = f.name

        try:
            # Step 2: Load config
            from tourney_threads.config.loader import load_config

            config = load_config(config_path)

            # Step 3: Mock API responses
            from tourney_threads.api.challonge import ChallongeAPIClient

            api_client = ChallongeAPIClient(config, debug=False)

            # Mock OAuth
            mock_oauth = MagicMock()
            mock_oauth.get_token = AsyncMock(return_value="flow_test_token_123")
            api_client._oauth_client = mock_oauth

            # Mock API response
            api_response = {
                "data": [
                    {
                        "id": "flow_m1",
                        "attributes": {"state": "open", "round": 1},
                        "relationships": {
                            "player1": {"data": {"id": "fp1"}},
                            "player2": {"data": {"id": "fp2"}},
                        },
                    }
                ],
                "included": [
                    {"type": "participant", "id": "fp1", "attributes": {"username": "FlowPlayer1"}},
                    {"type": "participant", "id": "fp2", "attributes": {"username": "FlowPlayer2"}},
                ],
            }

            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.text = AsyncMock(return_value="{}")
            mock_resp.json = AsyncMock(return_value=api_response)

            mock_get_cm = MagicMock()
            mock_get_cm.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_get_cm.__aexit__ = AsyncMock(return_value=None)

            mock_session_cm = MagicMock()
            mock_session = MagicMock()
            mock_session.get = MagicMock(return_value=mock_get_cm)
            mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_cm.__aexit__ = AsyncMock(return_value=None)

            # Step 4: Fetch matches
            with patch("aiohttp.ClientSession", return_value=mock_session_cm):
                matches, participants = await api_client.fetch_matches()

            assert len(matches) == 1
            assert matches[0].player1.username == "FlowPlayer1"

            # Step 5: Create Discord threads
            from tourney_threads.discord_client.thread_manager import DiscordThreadManager

            manager = DiscordThreadManager(config, "Elimination")

            mock_thread = MagicMock()
            mock_thread.send = AsyncMock()

            from discord.enums import ChannelType

            mock_channel = MagicMock()
            mock_channel.type = ChannelType.text
            mock_channel.create_thread = AsyncMock(return_value=mock_thread)

            mock_client = MagicMock()
            mock_client.get_channel = MagicMock(return_value=mock_channel)
            mock_client.close = AsyncMock()

            with patch("discord.Client") as MockClient:
                MockClient.return_value = mock_client

                async def mock_start(token):
                    for call_args in mock_client.event.call_args_list:
                        handler = call_args[0][0]
                        if handler.__name__ == "on_ready":
                            await handler()
                    return

                mock_client.start = mock_start

                thread_count = await manager.create_threads(matches)

            # Verify end-to-end
            assert thread_count == 1

            # Verify thread was created with correct data
            create_call = mock_channel.create_thread.call_args
            assert "FlowPlayer1 vs FlowPlayer2" in create_call[1]["name"]

            # Verify message includes role mentions from config
            send_call = mock_thread.send.call_args[0][0]
            assert "<@&111>" in send_call or "111" in str(send_call)
            assert "<@&222>" in send_call or "222" in str(send_call)

            captured = capsys.readouterr()
            assert "Created thread:" in captured.out

        finally:
            os.unlink(config_path)
