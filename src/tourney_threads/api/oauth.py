"""OAuth2 client for Challonge API authentication.

This module provides OAuth2 client credentials flow authentication.
"""

import aiohttp


class OAuthClient:
    """OAuth2 client for obtaining access tokens via client credentials flow.

    Attributes:
        token_url: OAuth token endpoint URL.
        client_id: OAuth client ID.
        client_secret: OAuth client secret.
        scope: Optional OAuth scope.
    """

    def __init__(
        self, token_url: str, client_id: str, client_secret: str, scope: str | None = None
    ):
        """Initialize OAuth client.

        Args:
            token_url: OAuth token endpoint URL.
            client_id: OAuth client ID.
            client_secret: OAuth client secret.
            scope: Optional OAuth scope string.
        """
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self._token: str | None = None

    async def get_token(self, session: aiohttp.ClientSession) -> str:
        """Obtain an OAuth access token.

        Caches the token after first retrieval. Note: Does not handle token expiry.

        Args:
            session: aiohttp ClientSession for making the request.

        Returns:
            Access token string.

        Raises:
            RuntimeError: If token request fails or response is invalid.
        """
        if self._token:
            return self._token

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        if self.scope:
            data["scope"] = self.scope

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        async with session.post(self.token_url, data=data, headers=headers) as resp:
            text = await resp.text()
            if resp.status != 200:
                raise RuntimeError(f"OAuth token request failed ({resp.status}): {text[:500]}")
            payload = await resp.json()

        token_value = payload.get("access_token")
        if not isinstance(token_value, str) or not token_value:
            raise RuntimeError("OAuth token response missing access_token")

        self._token = token_value
        return token_value
