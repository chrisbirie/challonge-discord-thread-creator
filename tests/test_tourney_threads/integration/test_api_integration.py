"""Integration tests for OAuth + API client interaction."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from tourney_threads.api.oauth import OAuthClient
from tourney_threads.api.challonge import ChallongeAPIClient


class TestOAuthAPIIntegration:
    """Test OAuth client integration with API client."""
    
    @pytest.mark.asyncio
    async def test_api_client_uses_oauth_token(self):
        """Test that API client properly uses OAuth token from OAuth client."""
        config = {
            "oauth2": {
                "client_id": "test_client",
                "client_secret": "test_secret",
                "scope": "tournaments:read matches:read"
            },
            "challonge": {
                "tournament": "test-tournament"
            }
        }
        
        api_client = ChallongeAPIClient(config, debug=False)
        
        # Mock OAuth token response
        mock_token_resp = MagicMock()
        mock_token_resp.status = 200
        mock_token_resp.json = AsyncMock(return_value={"access_token": "test_oauth_token"})
        mock_token_resp.text = AsyncMock(return_value='{}')
        
        mock_token_post_cm = MagicMock()
        mock_token_post_cm.__aenter__ = AsyncMock(return_value=mock_token_resp)
        mock_token_post_cm.__aexit__ = AsyncMock(return_value=None)
        
        # Mock matches API response
        matches_response = {
            "data": [
                {
                    "id": "match1",
                    "attributes": {"state": "open", "round": 1},
                    "relationships": {
                        "player1": {"data": {"id": "p1"}},
                        "player2": {"data": {"id": "p2"}}
                    }
                }
            ],
            "included": [
                {"type": "participant", "id": "p1", "attributes": {"username": "Player1"}},
                {"type": "participant", "id": "p2", "attributes": {"username": "Player2"}}
            ]
        }
        
        mock_matches_resp = MagicMock()
        mock_matches_resp.status = 200
        mock_matches_resp.json = AsyncMock(return_value=matches_response)
        mock_matches_resp.text = AsyncMock(return_value='{}')
        
        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_matches_resp)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)
        
        # Mock session that handles both POST (OAuth) and GET (API)
        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.post = MagicMock(return_value=mock_token_post_cm)
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session_cm):
            matches, participants = await api_client.fetch_matches()
        
        # Verify OAuth was called
        assert mock_session_instance.post.called
        
        # Verify API was called with OAuth token in headers
        assert mock_session_instance.get.called
        call_kwargs = mock_session_instance.get.call_args[1]
        assert call_kwargs['headers']['Authorization'] == 'Bearer test_oauth_token'
        
        # Verify matches were returned
        assert len(matches) == 1
        assert matches[0].match_id == "match1"
        assert matches[0].player1.username == "Player1"
    
    @pytest.mark.asyncio
    async def test_oauth_token_caching_across_api_calls(self):
        """Test that OAuth token is cached and reused across multiple API calls."""
        config = {
            "oauth2": {
                "client_id": "test_client",
                "client_secret": "test_secret"
            },
            "challonge": {
                "tournament": "test-tournament"
            }
        }
        
        api_client = ChallongeAPIClient(config, debug=False)
        
        # Mock OAuth response
        mock_token_resp = MagicMock()
        mock_token_resp.status = 200
        mock_token_resp.text = AsyncMock(return_value='{}')
        mock_token_resp.json = AsyncMock(return_value={"access_token": "cached_token"})
        
        mock_post_cm = MagicMock()
        mock_post_cm.__aenter__ = AsyncMock(return_value=mock_token_resp)
        mock_post_cm.__aexit__ = AsyncMock(return_value=None)
        
        # Mock API responses
        empty_response = {"data": [], "included": []}
        mock_api_resp = MagicMock()
        mock_api_resp.status = 200
        mock_api_resp.json = AsyncMock(return_value=empty_response)
        mock_api_resp.text = AsyncMock(return_value='{}')
        
        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_api_resp)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.post = MagicMock(return_value=mock_post_cm)
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session_cm):
            # First API call
            await api_client.fetch_matches()
            # Second API call (should reuse cached token)
            await api_client.probe_stage_type()
        
        # OAuth should only be called once due to caching
        assert mock_session_instance.post.call_count == 1
        # API should be called twice
        assert mock_session_instance.get.call_count == 2
    
    @pytest.mark.asyncio
    async def test_oauth_failure_propagates_to_api(self):
        """Test that OAuth failures are properly handled by API client."""
        config = {
            "oauth2": {
                "client_id": "bad_client",
                "client_secret": "bad_secret"
            },
            "challonge": {
                "tournament": "test-tournament"
            }
        }
        
        api_client = ChallongeAPIClient(config, debug=False)
        
        # Mock OAuth failure
        mock_token_resp = MagicMock()
        mock_token_resp.status = 401
        mock_token_resp.json = AsyncMock(return_value={"error": "invalid_client"})
        
        mock_post_cm = MagicMock()
        mock_token_resp.text = AsyncMock(return_value='{"error": "invalid_client"}')
        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.post = MagicMock(return_value=mock_post_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session_cm):
            with pytest.raises(RuntimeError, match="OAuth token request failed"):
                await api_client.fetch_matches()


class TestConfigAPIIntegration:
    """Test configuration loading integration with API client."""
    
    @pytest.mark.asyncio
    async def test_api_client_with_subdomain_config(self):
        """Test API client properly handles subdomain from config."""
        config = {
            "oauth2": {
                "client_id": "test_client",
                "client_secret": "test_secret"
            },
            "challonge": {
                "tournament": "my-tournament",
                "subdomain": "myorg"
            }
        }
        
        api_client = ChallongeAPIClient(config, debug=False)
        slug = api_client._build_tournament_slug()
        
        assert slug == "myorg-my-tournament"
        
        # Verify the slug is used in API calls
        mock_oauth = MagicMock()
        mock_oauth.get_token = AsyncMock(return_value="token")
        api_client._oauth_client = mock_oauth
        
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"data": []})
        mock_resp.text = AsyncMock(return_value='{}')
        
        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session_cm):
            await api_client.fetch_matches()
        
        # Verify URL contains the subdomain-prefixed tournament slug
        call_args = mock_session_instance.get.call_args[0]
        assert "myorg-my-tournament" in call_args[0]
    
    @pytest.mark.asyncio
    async def test_api_client_with_pagination_config(self):
        """Test API client uses pagination settings from config."""
        config = {
            "oauth2": {
                "client_id": "test_client",
                "client_secret": "test_secret"
            },
            "challonge": {
                "tournament": "test-tournament",
                "page": 2,
                "per_page": 50
            }
        }
        
        api_client = ChallongeAPIClient(config, debug=False)
        
        mock_oauth = MagicMock()
        mock_oauth.get_token = AsyncMock(return_value="token")
        api_client._oauth_client = mock_oauth
        
        mock_resp = MagicMock()
        mock_resp.text = AsyncMock(return_value='{}')
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"data": [], "included": []})
        
        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session_cm):
            await api_client.fetch_matches()
        
        # Verify pagination params are in the request
        call_kwargs = mock_session_instance.get.call_args[1]
        assert call_kwargs['params']['page'] == 2
        assert call_kwargs['params']['per_page'] == 50


class TestMatchDataFlow:
    """Test data flow from API to models to formatters."""
    
    @pytest.mark.asyncio
    async def test_match_data_transformation_pipeline(self):
        """Test complete data transformation from API response to Match models."""
        from tourney_threads.api.models import Match
        
        config = {
            "oauth2": {"client_id": "test", "client_secret": "test"},
            "challonge": {"tournament": "test"}
        }
        
        api_client = ChallongeAPIClient(config, debug=False)
        
        # Mock full API response with realistic data
        api_response = {
            "data": [
                {
                    "id": "12345",
                    "attributes": {
                        "state": "open",
                        "round": 2
                    },
                    "relationships": {
                        "player1": {"data": {"id": "100"}},
                        "player2": {"data": {"id": "200"}}
                    }
                },
                {
                    "id": "67890",
                    "attributes": {
                        "state": "complete",
                        "round": -1
                    },
                    "relationships": {
                        "player1": {"data": {"id": "300"}},
                        "player2": {"data": {"id": "400"}}
                    }
                }
            ],
            "included": [
                {"type": "participant", "id": "100", "attributes": {"username": "Alice"}},
                {"type": "participant", "id": "200", "attributes": {"username": "Bob"}},
                {"type": "participant", "id": "300", "attributes": {"username": "Charlie"}},
                {"type": "participant", "id": "400", "attributes": {"username": "Diana"}}
            ]
        }
        
        mock_oauth = MagicMock()
        mock_oauth.get_token = AsyncMock(return_value="token")
        api_client._oauth_client = mock_oauth
        
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value='{}')
        mock_resp.json = AsyncMock(return_value=api_response)
        
        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)
        
        runner_map = {"Alice": 111, "Bob": 222, "Charlie": 333}
        
        with patch('aiohttp.ClientSession', return_value=mock_session_cm):
            matches, participants = await api_client.fetch_matches(runner_map=runner_map)
        
        # Verify matches were transformed correctly
        assert len(matches) == 2
        
        # Check first match (winners bracket)
        assert matches[0].match_id == "12345"
        assert matches[0].state == "open"
        assert matches[0].round == 2
        assert matches[0].player1.username == "Alice"
        assert matches[0].player1.mention == "<@111>"
        assert matches[0].player2.username == "Bob"
        assert matches[0].player2.mention == "<@222>"
        
        # Check second match (losers bracket)
        assert matches[1].match_id == "67890"
        assert matches[1].state == "complete"
        assert matches[1].round == -1
        assert matches[1].player1.username == "Charlie"
        assert matches[1].player1.mention == "<@333>"
        assert matches[1].player2.username == "Diana"
        assert matches[1].player2.mention == "Diana"  # No Discord mapping
        
        # Verify participant index
        assert len(participants) == 4
        assert participants["100"]["attributes"]["username"] == "Alice"
    
    @pytest.mark.asyncio
    async def test_match_with_runner_map_integration(self):
        """Test that runner map properly integrates with match creation."""
        from tourney_threads.discord_client.formatters import format_thread_message
        
        config = {
            "oauth2": {"client_id": "test", "client_secret": "test"},
            "challonge": {"tournament": "test"}
        }
        
        api_client = ChallongeAPIClient(config, debug=False)
        
        api_response = {
            "data": [{
                "id": "m1",
                "attributes": {"state": "open", "round": 1},
                "relationships": {
                    "player1": {"data": {"id": "p1"}},
                    "player2": {"data": {"id": "p2"}}
                }
            }],
            "included": [
                {"type": "participant", "id": "p1", "attributes": {"username": "TestPlayer1"}},
                {"type": "participant", "id": "p2", "attributes": {"username": "TestPlayer2"}}
            ]
        }
        
        mock_oauth = MagicMock()
        mock_oauth.get_token = AsyncMock(return_value="token")
        api_client._oauth_client = mock_oauth
        
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value='{}')
        mock_resp.json = AsyncMock(return_value=api_response)
        
        mock_get_cm = MagicMock()
        mock_get_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_get_cm.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_cm = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get = MagicMock(return_value=mock_get_cm)
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_cm.__aexit__ = AsyncMock(return_value=None)
        
        runner_map = {"TestPlayer1": 999888777}
        
        with patch('aiohttp.ClientSession', return_value=mock_session_cm):
            matches, _ = await api_client.fetch_matches(runner_map=runner_map)
        
        # Verify match has proper mentions from runner map
        match = matches[0]
        message = format_thread_message(match, "Elimination", {})
        
        # Player1 should have Discord mention
        assert "<@999888777>" in message
        # Player2 should use plain name
        assert "TestPlayer2" in message
