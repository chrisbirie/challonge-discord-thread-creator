"""Tests for OAuth2 client functionality."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from tourney_threads.api.oauth import OAuthClient


class TestOAuthClient:
    """Tests for OAuth2 client."""

    def test_oauth_client_initialization(self):
        """Test OAuth client initialization."""
        client = OAuthClient(
            token_url="https://test.com/token",
            client_id="test_id",
            client_secret="test_secret",
            scope="test_scope",
        )

        assert client.token_url == "https://test.com/token"
        assert client.client_id == "test_id"
        assert client.client_secret == "test_secret"
        assert client.scope == "test_scope"
        assert client._token is None

    def test_oauth_client_initialization_no_scope(self):
        """Test OAuth client initialization without scope."""
        client = OAuthClient(
            token_url="https://test.com/token", client_id="test_id", client_secret="test_secret"
        )

        assert client.scope is None

    @pytest.mark.asyncio
    async def test_get_token_success(self):
        """Test successful token retrieval with proper async mock."""
        client = OAuthClient(
            token_url="https://test.com/token", client_id="test_id", client_secret="test_secret"
        )

        # Create a mock response
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value='{"access_token": "test_token"}')
        mock_resp.json = AsyncMock(return_value={"access_token": "test_token"})

        # Create a mock context manager
        mock_post_cm = MagicMock()
        mock_post_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_post_cm.__aexit__ = AsyncMock(return_value=None)

        # Create a mock session
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post_cm)

        token = await client.get_token(mock_session)

        assert token == "test_token"
        assert client._token == "test_token"
        mock_session.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_token_with_scope(self):
        """Test token retrieval with scope parameter."""
        client = OAuthClient(
            token_url="https://test.com/token",
            client_id="test_id",
            client_secret="test_secret",
            scope="read write",
        )

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value='{"access_token": "test_token"}')
        mock_resp.json = AsyncMock(return_value={"access_token": "test_token"})

        mock_post_cm = MagicMock()
        mock_post_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_post_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post_cm)

        await client.get_token(mock_session)

        # Verify scope was included in the call
        call_kwargs = mock_session.post.call_args[1]
        assert "scope" in call_kwargs["data"]

    @pytest.mark.asyncio
    async def test_get_token_failure_status(self):
        """Test token request failure with error status."""
        client = OAuthClient(
            token_url="https://test.com/token", client_id="test_id", client_secret="test_secret"
        )

        mock_resp = MagicMock()
        mock_resp.status = 401
        mock_resp.text = AsyncMock(return_value='{"error": "unauthorized"}')

        mock_post_cm = MagicMock()
        mock_post_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_post_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post_cm)

        with pytest.raises(RuntimeError, match="OAuth token request failed"):
            await client.get_token(mock_session)

    @pytest.mark.asyncio
    async def test_get_token_missing_access_token(self):
        """Test token response without access_token field."""
        client = OAuthClient(
            token_url="https://test.com/token", client_id="test_id", client_secret="test_secret"
        )

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value='{"no_token": "here"}')
        mock_resp.json = AsyncMock(return_value={"no_token": "here"})

        mock_post_cm = MagicMock()
        mock_post_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_post_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post_cm)

        with pytest.raises(RuntimeError, match="missing access_token"):
            await client.get_token(mock_session)

    @pytest.mark.asyncio
    async def test_get_token_caching(self):
        """Test that token is cached after first request."""
        client = OAuthClient(
            token_url="https://test.com/token", client_id="test_id", client_secret="test_secret"
        )

        # First call - should make HTTP request
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value='{"access_token": "cached_token"}')
        mock_resp.json = AsyncMock(return_value={"access_token": "cached_token"})

        mock_post_cm = MagicMock()
        mock_post_cm.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_post_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post_cm)

        token1 = await client.get_token(mock_session)
        assert token1 == "cached_token"
        assert mock_session.post.call_count == 1

        # Second call - should return cached token without HTTP request
        token2 = await client.get_token(mock_session)
        assert token2 == "cached_token"
        assert mock_session.post.call_count == 1  # Still 1, not 2
