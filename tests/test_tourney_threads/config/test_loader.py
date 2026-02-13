"""Tests for configuration loading and validation."""

import os
import tempfile

import pytest

from tourney_threads.config.loader import load_config, validate_config, validate_discord_config


class TestConfigLoader:
    """Tests for configuration loading and validation."""

    def test_validate_config_success(self):
        """Test validation with complete config."""
        config = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": {"tournament": "test-tournament"},
        }
        # Should not raise
        validate_config(config)

    def test_validate_config_missing_oauth(self):
        """Test validation with missing oauth2 section."""
        config = {"challonge": {"tournament": "test-tournament"}}
        with pytest.raises(ValueError, match="Missing required 'oauth2' section"):
            validate_config(config)

    def test_validate_config_missing_client_id(self):
        """Test validation with missing client_id."""
        config = {
            "oauth2": {"client_secret": "test_secret"},
            "challonge": {"tournament": "test-tournament"},
        }
        with pytest.raises(ValueError, match="Missing required oauth2.client_id"):
            validate_config(config)

    def test_validate_config_missing_tournament(self):
        """Test validation with missing tournament."""
        config = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": {"tournament": ""},  # Empty string
        }
        with pytest.raises(ValueError, match="Missing required challonge.tournament"):
            validate_config(config)

    def test_validate_discord_config_success(self):
        """Test Discord config validation with complete config."""
        config = {"discord": {"bot_token": "test_token", "channel_id": "123456"}}
        # Should not raise
        validate_discord_config(config)

    def test_validate_discord_config_missing_section(self):
        """Test Discord config validation with missing section."""
        config = {}
        with pytest.raises(ValueError, match="Missing required 'discord' section"):
            validate_discord_config(config)

    def test_validate_discord_config_missing_bot_token(self):
        """Test Discord config validation with missing bot_token."""
        config = {"discord": {"channel_id": "123456"}}
        with pytest.raises(ValueError, match="Missing required discord.bot_token"):
            validate_discord_config(config)

    def test_load_config_file_not_found(self):
        """Test loading config from non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_config.yaml")

    def test_validate_config_empty_challonge_section(self):
        """Test validation with empty challonge section."""
        config = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": None,  # Falsy value
        }
        with pytest.raises(ValueError, match="Missing required 'challonge' section"):
            validate_config(config)

    def test_validate_discord_with_empty_values(self):
        """Test Discord validation with empty string values."""
        config = {"discord": {"bot_token": "", "channel_id": "123"}}  # Empty string
        with pytest.raises(ValueError, match="Missing required discord.bot_token"):
            validate_discord_config(config)

    def test_validate_config_with_discord_section(self):
        """Test validate_config with Discord section included."""
        # Valid config with Discord section should pass
        config = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": {"tournament": "test-tourney"},
            "discord": {"bot_token": "test_token", "channel_id": 123456},
        }
        validate_config(config)  # Should not raise

        # Config with Discord section but missing bot_token
        config_bad_discord = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": {"tournament": "test-tourney"},
            "discord": {
                "channel_id": 123456
                # Missing bot_token
            },
        }
        with pytest.raises(ValueError, match="discord.bot_token"):
            validate_config(config_bad_discord)

    def test_load_config_empty_file(self):
        """Test load_config with empty YAML file."""
        # Create a temporary file with empty content
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write("")
            temp_path = f.name

        try:
            # Empty YAML should return empty dict
            result = load_config(temp_path)
            assert result == {}
        finally:
            os.unlink(temp_path)

    def test_validate_discord_config_comprehensive(self):
        """Test validate_discord_config with various scenarios."""
        # Valid config
        valid_config = {"discord": {"bot_token": "abc123", "channel_id": 999}}
        validate_discord_config(valid_config)  # Should not raise

        # Missing bot_token
        with pytest.raises(ValueError, match="discord.bot_token"):
            validate_discord_config({"discord": {"channel_id": 999}})

        # Missing channel_id
        with pytest.raises(ValueError, match="discord.channel_id"):
            validate_discord_config({"discord": {"bot_token": "abc"}})

        # Empty bot_token
        with pytest.raises(ValueError, match="discord.bot_token"):
            validate_discord_config({"discord": {"bot_token": "", "channel_id": 999}})
