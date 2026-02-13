"""Tests for Discord thread manager."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestDiscordThreadManager:
    """Test Discord thread manager."""
    
    def test_init(self):
        """Test DiscordThreadManager initialization."""
        from tourney_threads.discord_client.thread_manager import DiscordThreadManager
        
        config = {
            "discord": {
                "bot_token": "test_token",
                "channel_id": 123456
            }
        }
        
        manager = DiscordThreadManager(config, "Swiss")
        assert manager.config == config
        assert manager.stage_name == "Swiss"
        assert manager.discord_cfg == config["discord"]
    
    @pytest.mark.asyncio
    async def test_create_threads_no_matches(self, capsys):
        """Test create_threads with empty match list."""
        from tourney_threads.discord_client.thread_manager import DiscordThreadManager
        
        config = {"discord": {}}
        manager = DiscordThreadManager(config)
        
        result = await manager.create_threads([])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "No matches to create threads for" in captured.out
    
    @pytest.mark.asyncio
    async def test_create_threads_missing_bot_token(self):
        """Test create_threads with missing bot_token."""
        from tourney_threads.discord_client.thread_manager import DiscordThreadManager
        from tourney_threads.api.models import Match, Participant
        
        config = {"discord": {}}  # No bot_token
        manager = DiscordThreadManager(config)
        
        p1 = Participant("1", "Alice", "Alice", "@Alice")
        p2 = Participant("2", "Bob", "Bob", "@Bob")
        match = Match("m1", "open", 1, p1, p2)
        
        with pytest.raises(ValueError, match="Missing required discord.bot_token"):
            await manager.create_threads([match])
    
    @pytest.mark.asyncio
    async def test_create_threads_missing_channel_id(self):
        """Test create_threads with missing channel_id."""
        from tourney_threads.discord_client.thread_manager import DiscordThreadManager
        from tourney_threads.api.models import Match, Participant
        
        config = {
            "discord": {
                "bot_token": "test_token"
                # No channel_id
            }
        }
        manager = DiscordThreadManager(config)
        
        p1 = Participant("1", "Alice", "Alice", "@Alice")
        p2 = Participant("2", "Bob", "Bob", "@Bob")
        match = Match("m1", "open", 1, p1, p2)
        
        with pytest.raises(ValueError, match="Missing required discord.channel_id"):
            await manager.create_threads([match])
    
    @pytest.mark.asyncio
    async def test_create_threads_success(self, capsys):
        """Test successful thread creation."""
        from tourney_threads.discord_client.thread_manager import DiscordThreadManager
        from tourney_threads.api.models import Match, Participant
        
        config = {
            "discord": {
                "bot_token": "test_token",
                "channel_id": 123456,
                "thread_archive_minutes": 1440,
                "role_ids_to_tag": [999]
            }
        }
        manager = DiscordThreadManager(config, "Elimination")
        
        p1 = Participant("1", "Alice", "Alice", "<@100>")
        p2 = Participant("2", "Bob", "Bob", "<@200>")
        match = Match("m1", "open", 1, p1, p2)
        
        # Mock Discord client
        mock_thread = MagicMock()
        mock_thread.send = AsyncMock()
        
        # Import actual ChannelType from discord
        from discord.enums import ChannelType
        
        mock_channel = MagicMock()
        mock_channel.type = ChannelType.text
        mock_channel.create_thread = AsyncMock(return_value=mock_thread)
        
        mock_client = MagicMock()
        mock_client.get_channel = MagicMock(return_value=mock_channel)
        mock_client.close = AsyncMock()
        
        # Mock the Client class
        with patch('discord.Client') as MockClient:
            MockClient.return_value = mock_client
            
            # Mock client.start to just call on_ready and return
            async def mock_start(token):
                # Find and call on_ready handler
                for call_args in mock_client.event.call_args_list:
                    handler = call_args[0][0]
                    if handler.__name__ == 'on_ready':
                        await handler()
                return
            
            mock_client.start = mock_start
            
            result = await manager.create_threads([match])
            
            assert result == 1
            captured = capsys.readouterr()
            assert "Created thread:" in captured.out
    
    @pytest.mark.asyncio
    async def test_create_threads_channel_not_found(self, capsys):
        """Test create_threads when channel is not found."""
        from tourney_threads.discord_client.thread_manager import DiscordThreadManager
        from tourney_threads.api.models import Match, Participant
        
        config = {
            "discord": {
                "bot_token": "test_token",
                "channel_id": 123456
            }
        }
        manager = DiscordThreadManager(config)
        
        p1 = Participant("1", "Alice", "Alice", "@Alice")
        p2 = Participant("2", "Bob", "Bob", "@Bob")
        match = Match("m1", "open", 1, p1, p2)
        
        mock_client = MagicMock()
        mock_client.get_channel = MagicMock(return_value=None)
        mock_client.fetch_channel = AsyncMock(return_value=None)
        mock_client.close = AsyncMock()
        
        with patch('discord.Client') as MockClient:
            MockClient.return_value = mock_client
            
            async def mock_start(token):
                for call_args in mock_client.event.call_args_list:
                    handler = call_args[0][0]
                    if handler.__name__ == 'on_ready':
                        await handler()
                return
            
            mock_client.start = mock_start
            
            result = await manager.create_threads([match])
            
            assert result == 0
            captured = capsys.readouterr()
            assert "ERROR: channel_id does not refer to a text channel" in captured.out
    
    @pytest.mark.asyncio
    async def test_create_threads_exception_handling(self, capsys):
        """Test create_threads handles exceptions gracefully."""
        from tourney_threads.discord_client.thread_manager import DiscordThreadManager
        from tourney_threads.api.models import Match, Participant
        
        config = {
            "discord": {
                "bot_token": "test_token",
                "channel_id": 123456
            }
        }
        manager = DiscordThreadManager(config)
        
        p1 = Participant("1", "Alice", "Alice", "@Alice")
        p2 = Participant("2", "Bob", "Bob", "@Bob")
        match = Match("m1", "open", 1, p1, p2)
        
        # Import actual ChannelType from discord
        from discord.enums import ChannelType
        
        mock_channel = MagicMock()
        mock_channel.type = ChannelType.text
        mock_channel.create_thread = AsyncMock(side_effect=Exception("Thread creation failed"))
        
        mock_client = MagicMock()
        mock_client.get_channel = MagicMock(return_value=mock_channel)
        mock_client.close = AsyncMock()
        
        with patch('discord.Client') as MockClient:
            MockClient.return_value = mock_client
            
            async def mock_start(token):
                for call_args in mock_client.event.call_args_list:
                    handler = call_args[0][0]
                    if handler.__name__ == 'on_ready':
                        await handler()
                return
            
            mock_client.start = mock_start
            
            result = await manager.create_threads([match])
            
            assert result == 0
            captured = capsys.readouterr()
            assert "Error creating thread for match" in captured.out
            assert "No threads created" in captured.out
