"""Discord thread management.

This module provides functionality for creating Discord threads for tournament matches.
"""

import discord
from discord.enums import ChannelType
from discord import AllowedMentions
from typing import Dict, Any, List, Optional

from ..api.models import Match
from ..config.constants import DEFAULT_THREAD_ARCHIVE_MINUTES, MAX_THREAD_NAME_LENGTH
from ..utils.names import build_role_mentions
from .formatters import format_thread_name, format_thread_message


class DiscordThreadManager:
    """Manager for creating Discord threads for tournament matches.
    
    Attributes:
        config: Configuration dictionary containing discord settings.
        stage_name: Tournament stage type.
    """
    
    def __init__(self, config: Dict[str, Any], stage_name: Optional[str] = None):
        """Initialize Discord thread manager.
        
        Args:
            config: Configuration dictionary with discord section.
            stage_name: Tournament stage type ('Swiss', 'Groups', 'Elimination').
        """
        self.config = config
        self.stage_name = stage_name
        self.discord_cfg = config.get("discord", {}) or {}
    
    async def create_threads(self, matches: List[Match]) -> int:
        """Create Discord threads for a list of matches.
        
        Args:
            matches: List of Match objects to create threads for.
            
        Returns:
            Number of threads successfully created.
            
        Raises:
            ValueError: If required Discord configuration is missing.
        """
        if not matches:
            print("[info] No matches to create threads for.")
            return 0
        
        bot_token = self.discord_cfg.get("bot_token")
        if not bot_token:
            raise ValueError("Missing required discord.bot_token in config")
        
        channel_id = self.discord_cfg.get("channel_id")
        if not channel_id:
            raise ValueError("Missing required discord.channel_id in config")
        
        channel_id = int(channel_id)
        archive_minutes = int(
            self.discord_cfg.get("thread_archive_minutes", DEFAULT_THREAD_ARCHIVE_MINUTES)
        )
        role_mentions = build_role_mentions(self.discord_cfg.get("role_ids_to_tag"))
        
        intents = discord.Intents.default()
        intents.guilds = True
        allowed = AllowedMentions(everyone=False, users=True, roles=True, replied_user=False)
        client = discord.Client(intents=intents, allowed_mentions=allowed)
        
        created_count = 0
        
        @client.event
        async def on_ready():
            nonlocal created_count
            try:
                # Fetch the channel
                channel = client.get_channel(channel_id)
                if channel is None:
                    channel = await client.fetch_channel(channel_id)
                
                if channel is None or channel.type != ChannelType.text:
                    print("ERROR: channel_id does not refer to a text channel.")
                    await client.close()
                    return
                
                # Create threads for each match
                for match in matches:
                    try:
                        thread_name = format_thread_name(
                            match, self.stage_name, self.config, role_mentions
                        )
                        message_body = format_thread_message(
                            match, self.stage_name, self.config, role_mentions
                        )
                        
                        # Truncate thread name to Discord's limit
                        thread_name = thread_name[:MAX_THREAD_NAME_LENGTH]
                        
                        # Create the thread
                        thread = await channel.create_thread(
                            name=thread_name,
                            auto_archive_duration=archive_minutes,
                            type=ChannelType.public_thread
                        )
                        
                        # Send the initial message
                        await thread.send(message_body, allowed_mentions=allowed)
                        print(f"Created thread: {thread_name}")
                        created_count += 1
                        
                    except Exception as e:
                        print(f"Error creating thread for match {match.match_id}: {e}")
                        # Continue with other matches even if one fails
                
                if created_count == 0:
                    print("[info] No threads created.")
                    
            finally:
                await client.close()
        
        await client.start(bot_token)
        return created_count
