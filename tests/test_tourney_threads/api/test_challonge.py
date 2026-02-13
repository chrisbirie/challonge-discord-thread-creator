"""Tests for Challonge API client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tourney_threads.api.challonge import ChallongeAPIClient


class TestChallongeAPIClient:
    """Tests for Challonge API client."""

    def test_build_tournament_slug_no_subdomain(self):
        """Test tournament slug building without subdomain."""
        config = {"challonge": {"tournament": "my-tournament"}}
        client = ChallongeAPIClient(config, debug=False)
        slug = client._build_tournament_slug()
        assert slug == "my-tournament"

    def test_build_tournament_slug_with_subdomain(self):
        """Test tournament slug building with subdomain."""
        config = {"challonge": {"tournament": "my-tournament", "subdomain": "myorg"}}
        client = ChallongeAPIClient(config, debug=False)
        slug = client._build_tournament_slug()
        assert slug == "myorg-my-tournament"

    def test_build_tournament_slug_override(self):
        """Test tournament slug override."""
        config = {"challonge": {"tournament": "default-tournament", "subdomain": "myorg"}}
        client = ChallongeAPIClient(config, debug=False)
        slug = client._build_tournament_slug(tournament_override="override-tournament")
        assert slug == "myorg-override-tournament"

    def test_build_api_headers(self):
        """Test API headers construction."""
        config = {
            "oauth2": {"client_id": "test", "client_secret": "test"},
            "challonge": {"tournament": "test"},
        }
        client = ChallongeAPIClient(config, debug=False)
        headers = client._build_api_headers("test_token")

        assert headers["Authorization"] == "Bearer test_token"
        assert headers["Authorization-Type"] == "v2"
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/vnd.api+json"

    def test_parse_participant_none_id(self):
        """Test parsing participant with None ID."""
        config = {
            "oauth2": {"client_id": "test", "client_secret": "test"},
            "challonge": {"tournament": "test"},
        }
        client = ChallongeAPIClient(config, debug=False)

        result = client._parse_participant(None, {}, {})
        assert result is None

    def test_parse_participant_missing_from_index(self):
        """Test parsing participant not in index."""
        config = {
            "oauth2": {"client_id": "test", "client_secret": "test"},
            "challonge": {"tournament": "test"},
        }
        client = ChallongeAPIClient(config, debug=False)

        result = client._parse_participant("123", {}, {})
        assert result is None

    def test_parse_participant_valid(self):
        """Test parsing valid participant."""
        config = {
            "oauth2": {"client_id": "test", "client_secret": "test"},
            "challonge": {"tournament": "test"},
        }
        client = ChallongeAPIClient(config, debug=False)

        participant_index = {"123": {"attributes": {"username": "TestPlayer"}}}
        runner_map = {"TestPlayer": 999}

        result = client._parse_participant("123", participant_index, runner_map)

        assert result is not None
        assert result.id == "123"
        assert result.username == "TestPlayer"
        assert result.mention == "<@999>"

    @pytest.mark.asyncio
    async def test_fetch_matches_integration(self):
        """Test fetch_matches with mocked API response."""
        config = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": {"tournament": "test-tournament", "page": 1, "per_page": 25},
        }
        client = ChallongeAPIClient(config, debug=False)

        # Mock the OAuth client
        mock_oauth = MagicMock()
        mock_oauth.get_token = AsyncMock(return_value="test_token")
        client._oauth_client = mock_oauth

        # Mock API response
        api_response = {
            "data": [
                {
                    "id": "1",
                    "attributes": {"state": "open", "round": 1},
                    "relationships": {
                        "player1": {"data": {"id": "p1"}},
                        "player2": {"data": {"id": "p2"}},
                    },
                }
            ],
            "included": [
                {"type": "participant", "id": "p1", "attributes": {"username": "Alice"}},
                {"type": "participant", "id": "p2", "attributes": {"username": "Bob"}},
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
        mock_session_instance = MagicMock()
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            matches, _ = await client.fetch_matches(runner_map={})

        assert len(matches) == 1
        assert matches[0].match_id == "1"
        assert matches[0].state == "open"
        assert matches[0].round == 1
        assert matches[0].player1.username == "Alice"
        assert matches[0].player2.username == "Bob"

    @pytest.mark.asyncio
    async def test_probe_stage_type_swiss(self):
        """Test probing stage type for Swiss tournament."""
        config = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": {"tournament": "test-tournament"},
        }
        client = ChallongeAPIClient(config, debug=False)

        mock_oauth = MagicMock()
        mock_oauth.get_token = AsyncMock(return_value="test_token")
        client._oauth_client = mock_oauth

        tournament_response = {
            "data": {
                "attributes": {
                    "state": "group_stages_underway",
                    "group_stage_enabled": True,
                    "group_stage_options": {"stage_type": "swiss"},
                }
            }
        }

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value="{}")
        mock_resp.json = AsyncMock(return_value=tournament_response)

        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            stage_type = await client.probe_stage_type()

        assert stage_type == "Swiss"

    @pytest.mark.asyncio
    async def test_probe_stage_type_failure(self):
        """Test probing stage type when API request fails."""
        config = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": {"tournament": "test-tournament"},
        }
        client = ChallongeAPIClient(config, debug=False)

        mock_oauth = MagicMock()
        mock_oauth.get_token = AsyncMock(return_value="test_token")
        client._oauth_client = mock_oauth

        mock_resp = MagicMock()
        mock_resp.status = 404
        mock_resp.text = AsyncMock(return_value='{"error": "not found"}')

        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            stage_type = await client.probe_stage_type()

        assert stage_type is None

    @pytest.mark.asyncio
    async def test_probe_stage_type_with_debug(self, capsys):
        """Test probing stage type with debug mode enabled."""
        config = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": {"tournament": "test-tournament"},
        }
        client = ChallongeAPIClient(config, debug=True)

        mock_oauth = MagicMock()
        mock_oauth.get_token = AsyncMock(return_value="test_token")
        client._oauth_client = mock_oauth

        tournament_response = {
            "data": {"attributes": {"state": "underway", "group_stage_enabled": False}}
        }

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value="{}")
        mock_resp.json = AsyncMock(return_value=tournament_response)

        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            stage_type = await client.probe_stage_type()

        assert stage_type == "Elimination"
        captured = capsys.readouterr()
        assert "[debug]" in captured.out

    @pytest.mark.asyncio
    async def test_fetch_matches_with_debug(self, capsys):
        """Test fetching matches with debug mode enabled."""
        config = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": {"tournament": "test-tournament"},
        }
        client = ChallongeAPIClient(config, debug=True)

        mock_oauth = MagicMock()
        mock_oauth.get_token = AsyncMock(return_value="test_token")
        client._oauth_client = mock_oauth

        api_response = {"data": [], "included": []}

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value="{}")
        mock_resp.json = AsyncMock(return_value=api_response)

        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            matches, participants = await client.fetch_matches()

        assert matches == []
        assert participants == {}
        captured = capsys.readouterr()
        assert "[debug]" in captured.out
        # Verify JSON debug output is printed (line 122 in challonge.py)
        assert "data" in captured.out or "{" in captured.out  # JSON output

    @pytest.mark.asyncio
    async def test_fetch_matches_api_error(self):
        """Test fetching matches when API returns error."""
        config = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": {"tournament": "test-tournament"},
        }
        client = ChallongeAPIClient(config, debug=False)

        mock_oauth = MagicMock()
        mock_oauth.get_token = AsyncMock(return_value="test_token")
        client._oauth_client = mock_oauth

        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_resp.text = AsyncMock(return_value='{"error": "server error"}')

        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("aiohttp.ClientSession", return_value=mock_session_cm),
            pytest.raises(RuntimeError, match="failed"),
        ):
            await client.fetch_matches()

    @pytest.mark.asyncio
    async def test_probe_stage_type_exception_handling(self, capsys):
        """Test probe_stage_type exception handling with debug."""
        config = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": {"tournament": "test-tournament"},
        }
        client = ChallongeAPIClient(config, debug=True)

        mock_oauth = MagicMock()
        mock_oauth.get_token = AsyncMock(side_effect=Exception("Connection error"))
        client._oauth_client = mock_oauth

        result = await client.probe_stage_type()

        assert result is None
        captured = capsys.readouterr()
        assert "[debug]" in captured.out
        assert "exception" in captured.out

    def test_get_oauth_client_lazy_initialization(self):
        """Test that OAuth client is lazily initialized."""
        config = {
            "oauth2": {
                "client_id": "test_id",
                "client_secret": "test_secret",
                "scope": "custom_scope",
            },
            "challonge": {"tournament": "test-tournament"},
        }
        client = ChallongeAPIClient(config, debug=False)

        # OAuth client should be None initially
        assert client._oauth_client is None

        # Call _get_oauth_client
        oauth = client._get_oauth_client()

        # Should be created now
        assert oauth is not None
        assert client._oauth_client is oauth

        # Second call should return same instance
        oauth2 = client._get_oauth_client()
        assert oauth2 is oauth

    @pytest.mark.asyncio
    async def test_fetch_matches_long_error_text(self):
        """Test fetch_matches with error response >500 chars."""
        config = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": {"tournament": "test-tournament"},
        }
        client = ChallongeAPIClient(config, debug=False)

        mock_oauth = MagicMock()
        mock_oauth.get_token = AsyncMock(return_value="test_token")
        client._oauth_client = mock_oauth

        # Create error text >500 chars
        long_error = "ERROR: " + ("x" * 600)

        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_resp.text = AsyncMock(return_value=long_error)

        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            with pytest.raises(RuntimeError) as exc_info:
                await client.fetch_matches()
            # Verify error was raised and text contains truncated portion
            error_msg = str(exc_info.value)
            assert "failed (500)" in error_msg
            assert "ERROR:" in error_msg
            # The [:500] slice truncates the text
            assert len(error_msg) < 700  # Significantly less than full error

    @pytest.mark.asyncio
    async def test_probe_stage_type_long_error_debug(self, capsys):
        """Test probe_stage_type with error response >300 chars in debug mode."""
        config = {
            "oauth2": {"client_id": "test_id", "client_secret": "test_secret"},
            "challonge": {"tournament": "test-tournament"},
        }
        client = ChallongeAPIClient(config, debug=True)

        mock_oauth = MagicMock()
        mock_oauth.get_token = AsyncMock(return_value="test_token")
        client._oauth_client = mock_oauth

        # Create error text >300 chars
        long_error = "ERROR: " + ("y" * 400)

        mock_resp = MagicMock()
        mock_resp.status = 404
        mock_resp.text = AsyncMock(return_value=long_error)

        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=mock_session_cm):
            result = await client.probe_stage_type()

        assert result is None
        captured = capsys.readouterr()
        # Verify debug output contains truncated text
        assert "[debug]" in captured.out
        assert "tournament stage probe failed" in captured.out
