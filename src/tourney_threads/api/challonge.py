"""Challonge API client for fetching tournament data.

This module provides a high-level client for interacting with Challonge v2.1 API.
"""

import json
import aiohttp
from typing import Dict, List, Tuple, Optional, Any

from .oauth import OAuthClient
from .models import Match, Participant
from ..config.constants import DEFAULT_API_BASE_URL, DEFAULT_TOKEN_URL, DEFAULT_PATH_SUFFIX
from ..utils.names import clean_runner_name, participant_username, mention_for_name


class ChallongeAPIClient:
    """Client for interacting with Challonge API v2.1.
    
    Attributes:
        config: Configuration dictionary containing oauth2 and challonge settings.
        debug: Whether to print debug information.
    """
    
    def __init__(self, config: Dict[str, Any], debug: bool = False):
        """Initialize Challonge API client.
        
        Args:
            config: Configuration dictionary with oauth2 and challonge sections.
            debug: Whether to enable debug logging.
        """
        self.config = config
        self.debug = debug
        self._oauth_client: Optional[OAuthClient] = None
    
    def _get_oauth_client(self) -> OAuthClient:
        """Get or create OAuth client instance.
        
        Returns:
            Configured OAuthClient instance.
        """
        if self._oauth_client is None:
            oauth_cfg = self.config["oauth2"]
            token_url = oauth_cfg.get("token_url", DEFAULT_TOKEN_URL)
            self._oauth_client = OAuthClient(
                token_url=token_url,
                client_id=oauth_cfg["client_id"],
                client_secret=oauth_cfg["client_secret"],
                scope=oauth_cfg.get("scope"),
            )
        return self._oauth_client
    
    def _build_tournament_slug(self, tournament_override: Optional[str] = None) -> str:
        """Build tournament slug from config and optional override.
        
        Args:
            tournament_override: Optional tournament slug to use instead of config value.
            
        Returns:
            Tournament slug, potentially prefixed with subdomain.
        """
        challonge_cfg = self.config.get("challonge", {}) or {}
        tournament = tournament_override or challonge_cfg["tournament"]
        subdomain = challonge_cfg.get("subdomain") or ""
        return f"{subdomain}-{tournament}" if subdomain else tournament
    
    def _build_api_headers(self, token: str) -> Dict[str, str]:
        """Build HTTP headers for Challonge API requests.
        
        Args:
            token: OAuth access token.
            
        Returns:
            Dictionary of HTTP headers.
        """
        return {
            "Authorization": f"Bearer {token}",
            "Authorization-Type": "v2",
            "Accept": "application/json",
            "Content-Type": "application/vnd.api+json",
        }
    
    async def fetch_matches(
        self,
        tournament_override: Optional[str] = None,
        runner_map: Optional[Dict[str, int]] = None,
    ) -> Tuple[List[Match], Optional[str]]:
        """Fetch matches and participants from Challonge API.
        
        Args:
            tournament_override: Optional tournament slug override.
            runner_map: Optional mapping of usernames to Discord user IDs.
            
        Returns:
            Tuple of (list of Match objects, participants index dict).
            
        Raises:
            RuntimeError: If API request fails.
        """
        runner_map = runner_map or {}
        challonge_cfg = self.config.get("challonge", {}) or {}
        api_base = (challonge_cfg.get("base_url") or DEFAULT_API_BASE_URL).rstrip("/")
        slug = self._build_tournament_slug(tournament_override)
        
        # Pagination and filters from config
        page = int(challonge_cfg.get("page", 1))
        per_page = int(challonge_cfg.get("per_page", 25))
        state = challonge_cfg.get("state")  # optional ("open", "pending", "complete", "all")
        
        path_suffix = (self.config.get("oauth2", {}) or {}).get(
            "path_suffix", DEFAULT_PATH_SUFFIX
        )
        
        oauth = self._get_oauth_client()
        
        async with aiohttp.ClientSession() as session:
            token = await oauth.get_token(session)
            
            path = f"/tournaments/{slug}/matches{path_suffix}"
            url = f"{api_base}{path}"
            params = {"page": page, "per_page": per_page}
            if state:
                params["state"] = state
            
            headers = self._build_api_headers(token)
            
            if self.debug:
                dbg_headers = dict(headers, Authorization="Bearer …")
                print(f"[debug] GET {url} params={params} headers={dbg_headers}")
            
            async with session.get(url, headers=headers, params=params) as resp:
                text = await resp.text()
                if resp.status != 200:
                    raise RuntimeError(
                        f"GET {url} failed ({resp.status}): {text[:500]}"
                    )
                payload = await resp.json()
            
            if self.debug:
                print(json.dumps(payload, indent=2))
            
            # Parse matches and participants
            matches_data = payload.get("data") or []
            participants_index: Dict[str, dict] = {}
            
            for inc in (payload.get("included") or []):
                if inc.get("type") == "participant":
                    participants_index[str(inc.get("id"))] = inc
            
            # Convert to Match objects
            matches = self._parse_matches(matches_data, participants_index, runner_map)
            
            return matches, participants_index
    
    def _parse_matches(
        self,
        matches_data: List[dict],
        participants_index: Dict[str, dict],
        runner_map: Dict[str, int],
    ) -> List[Match]:
        """Parse raw match data into Match objects.
        
        Args:
            matches_data: List of match resources from API.
            participants_index: Index of participant ID to participant resource.
            runner_map: Mapping of usernames to Discord user IDs.
            
        Returns:
            List of Match objects.
        """
        matches = []
        
        for m in matches_data:
            match_id = str(m.get("id"))
            attrs = m.get("attributes") or {}
            state = attrs.get("state")
            round_num = attrs.get("round")
            
            rels = m.get("relationships") or {}
            p1_data = (rels.get("player1") or {}).get("data") or {}
            p2_data = (rels.get("player2") or {}).get("data") or {}
            
            p1_id = str(p1_data.get("id")) if p1_data else None
            p2_id = str(p2_data.get("id")) if p2_data else None
            
            player1 = self._parse_participant(p1_id, participants_index, runner_map)
            player2 = self._parse_participant(p2_id, participants_index, runner_map)
            
            matches.append(
                Match(
                    match_id=match_id,
                    state=state,
                    round=int(round_num) if round_num is not None else 0,
                    player1=player1,
                    player2=player2,
                )
            )
        
        return matches
    
    def _parse_participant(
        self,
        participant_id: Optional[str],
        participants_index: Dict[str, dict],
        runner_map: Dict[str, int],
    ) -> Optional[Participant]:
        """Parse participant data into Participant object.
        
        Args:
            participant_id: Participant ID string.
            participants_index: Index of participant resources.
            runner_map: Mapping of usernames to Discord user IDs.
            
        Returns:
            Participant object or None if ID not found.
        """
        if not participant_id:
            return None
        
        participant_item = participants_index.get(participant_id)
        if not participant_item:
            return None
        
        raw_name = participant_username(participant_item)
        username = clean_runner_name(raw_name)
        mention = mention_for_name(username, runner_map)
        
        return Participant(
            id=participant_id,
            username=username,
            raw_name=raw_name,
            mention=mention,
        )
    
    async def probe_stage_type(
        self, tournament_override: Optional[str] = None
    ) -> Optional[str]:
        """Probe tournament to detect stage type.
        
        Attempts to determine if the tournament is Swiss, Groups, or Elimination.
        
        Args:
            tournament_override: Optional tournament slug override.
            
        Returns:
            Stage type string ('Swiss', 'Groups', or 'Elimination'), or None on failure.
        """
        challonge_cfg = self.config.get("challonge", {}) or {}
        api_base = (challonge_cfg.get("base_url") or DEFAULT_API_BASE_URL).rstrip("/")
        slug = self._build_tournament_slug(tournament_override)
        path_suffix = (self.config.get("oauth2", {}) or {}).get(
            "path_suffix", DEFAULT_PATH_SUFFIX
        )
        
        oauth = self._get_oauth_client()
        
        try:
            async with aiohttp.ClientSession() as session:
                token = await oauth.get_token(session)
                path = f"/tournaments/{slug}{path_suffix}"
                url = f"{api_base}{path}"
                headers = self._build_api_headers(token)
                
                if self.debug:
                    dbg_headers = dict(headers, Authorization="Bearer …")
                    print(f"[debug] GET {url} (stage probe) headers={dbg_headers}")
                
                async with session.get(url, headers=headers) as resp:
                    text = await resp.text()
                    if resp.status != 200:
                        if self.debug:
                            print(
                                f"[debug] tournament stage probe failed "
                                f"{resp.status}: {text[:300]}"
                            )
                        return None
                    tournament_data = await resp.json()
            
            # Extract stage information
            data = tournament_data.get("data") or {}
            attrs = data.get("attributes") or {}
            state = (attrs.get("state") or "").lower()
            group_stage_enabled = bool(attrs.get("group_stage_enabled"))
            group_stage_options = attrs.get("group_stage_options") or {}
            stage_type = (group_stage_options.get("stage_type") or "").lower()
            
            # Determine human-friendly stage label
            if "group" in state or group_stage_enabled:
                return "Swiss" if stage_type == "swiss" else "Groups"
            return "Elimination"
            
        except Exception as e:
            if self.debug:
                print(f"[debug] stage probe exception: {e}")
            return None
