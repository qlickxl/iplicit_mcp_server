"""
iplicit MCP Server - Session Management

Copyright (c) 2025 QLickXL
Licensed under MIT License - see LICENSE file for details

Repository: https://github.com/qlickxl/iplicit_mcp_server
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional
import httpx


class IplicitSessionManager:
    """Manages API session tokens with automatic refresh"""

    def __init__(self):
        self.api_key = os.getenv("IPLICIT_API_KEY")
        self.username = os.getenv("IPLICIT_USERNAME")
        self.domain = os.getenv("IPLICIT_DOMAIN")
        self.base_url = "https://api.iplicit.com/api"

        if not all([self.api_key, self.username, self.domain]):
            raise ValueError(
                "Missing required environment variables: "
                "IPLICIT_API_KEY, IPLICIT_USERNAME, IPLICIT_DOMAIN"
            )

        self._session_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._lock = asyncio.Lock()

    async def get_valid_token(self) -> str:
        """Returns a valid session token, refreshing if needed"""
        async with self._lock:
            # Check if we need a new token
            if not self._session_token or self._is_token_expired():
                await self._create_session()

            return self._session_token

    def _is_token_expired(self) -> bool:
        """Check if the current token is expired or about to expire"""
        if not self._token_expiry:
            return True

        # Refresh 5 minutes before actual expiry for safety
        # Make sure both datetimes are timezone-aware
        from datetime import timezone
        now = datetime.now(timezone.utc)
        return now >= (self._token_expiry - timedelta(minutes=5))

    async def _create_session(self):
        """Creates a new session with the API"""
        url = f"{self.base_url}/session/create/api"
        headers = {
            "Domain": self.domain,
            "Content-Type": "application/json"
        }
        payload = {
            "username": self.username,
            "userApiKey": self.api_key
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                data = response.json()
                self._session_token = data.get("sessionToken")

                # Parse token expiry
                token_due = data.get("tokenDue")
                if token_due:
                    # Parse ISO format: 2025-11-04T16:45:13.183Z
                    self._token_expiry = datetime.fromisoformat(
                        token_due.replace("Z", "+00:00")
                    )
                else:
                    # Default to 30 minutes if not provided
                    self._token_expiry = datetime.utcnow() + timedelta(minutes=30)

                if not self._session_token:
                    raise ValueError("No session token received from API")

            except httpx.HTTPStatusError as e:
                raise ConnectionError(
                    f"Failed to authenticate with iplicit API: {e.response.status_code} - {e.response.text}"
                )
            except Exception as e:
                raise ConnectionError(f"Failed to create iplicit session: {str(e)}")

    def get_domain(self) -> str:
        """Returns the configured domain"""
        return self.domain

    async def close(self):
        """Cleanup method for graceful shutdown"""
        # Could implement session termination if API supports it
        pass
