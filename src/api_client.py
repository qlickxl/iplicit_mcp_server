"""API client for making requests to iplicit API"""

import asyncio
from typing import Optional, Dict, Any
import httpx
from .session import IplicitSessionManager


class IplicitAPIClient:
    """Handles API requests with automatic token management and error handling"""

    def __init__(self, session_manager: IplicitSessionManager):
        self.session_manager = session_manager
        self.base_url = "https://api.iplicit.com/api"
        self.request_count = 0
        self.request_window_start = asyncio.get_event_loop().time()

    async def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an API request with automatic token injection and error handling

        Args:
            endpoint: API endpoint (e.g., "document", "contactaccount")
            method: HTTP method (GET, POST, PUT, DELETE)
            params: Query parameters
            body: Request body for POST/PUT
            headers: Additional headers

        Returns:
            Response data as dict

        Raises:
            ValueError: For validation errors (400)
            PermissionError: For permission errors (403)
            FileNotFoundError: For resource not found (404)
            ConnectionError: For network/timeout errors
            RuntimeError: For other API errors
        """
        # Check rate limiting
        await self._check_rate_limit()

        # Get valid session token
        token = await self.session_manager.get_valid_token()

        # Build headers
        request_headers = {
            "Domain": self.session_manager.get_domain(),
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        if headers:
            request_headers.update(headers)

        # Build URL
        url = f"{self.base_url}/{endpoint}"

        # Make request with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    if method == "GET":
                        response = await client.get(url, headers=request_headers, params=params)
                    elif method == "POST":
                        response = await client.post(url, headers=request_headers, json=body, params=params)
                    elif method == "PUT":
                        response = await client.put(url, headers=request_headers, json=body, params=params)
                    elif method == "DELETE":
                        response = await client.delete(url, headers=request_headers, params=params)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")

                    # Handle response
                    return await self._handle_response(response)

            except httpx.TimeoutException:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise ConnectionError(
                        f"Request to iplicit API timed out after {max_retries} attempts. "
                        "The iplicit server may be slow or unavailable."
                    )

            except httpx.NetworkError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise ConnectionError(
                        f"Network error connecting to iplicit API: {str(e)}. "
                        "Check your internet connection."
                    )

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and errors"""

        # Success (200-299)
        if response.is_success:
            self.request_count += 1
            if response.status_code == 204:  # No content
                return {}
            try:
                return response.json()
            except Exception:
                return {"raw_response": response.text}

        # Authentication error (401)
        if response.status_code == 401:
            raise PermissionError(
                "Session token expired or invalid. The MCP server will automatically "
                "refresh the token and retry your request."
            )

        # Permission denied (403)
        if response.status_code == 403:
            raise PermissionError(
                f"Your iplicit user account doesn't have permission to access this resource. "
                f"Contact your iplicit administrator to grant API access. "
                f"Response: {response.text[:200]}"
            )

        # Not found (404)
        if response.status_code == 404:
            raise FileNotFoundError(
                f"Resource not found in iplicit. The endpoint or resource ID may be incorrect. "
                f"URL: {response.url}"
            )

        # Method not allowed (405)
        if response.status_code == 405:
            raise ValueError(
                f"HTTP method not supported for this endpoint. "
                f"The endpoint may require a different HTTP method (GET/POST/PUT/DELETE)."
            )

        # Validation error (400)
        if response.status_code == 400:
            try:
                error_data = response.json()
                errors = error_data.get("errors", {})
                error_msg = "Invalid request to iplicit API:\n"
                for field, messages in errors.items():
                    error_msg += f"  • {field}: {', '.join(messages)}\n"
                raise ValueError(error_msg)
            except Exception:
                raise ValueError(
                    f"Invalid request to iplicit API: {response.text[:300]}"
                )

        # Rate limit (429)
        if response.status_code == 429:
            raise RuntimeError(
                "iplicit API rate limit exceeded (1500 requests per 5 minutes). "
                "Please wait a few minutes before making more requests."
            )

        # Server error (500+)
        if response.status_code >= 500:
            raise RuntimeError(
                f"iplicit server error ({response.status_code}). "
                f"The iplicit API may be experiencing issues. Try again later."
            )

        # Other errors
        raise RuntimeError(
            f"Unexpected error from iplicit API: {response.status_code} - {response.text[:300]}"
        )

    async def _check_rate_limit(self):
        """Track and enforce rate limiting (1500 requests per 5 minutes)"""
        current_time = asyncio.get_event_loop().time()

        # Reset counter if 5-minute window has passed
        if current_time - self.request_window_start >= 300:  # 5 minutes
            self.request_count = 0
            self.request_window_start = current_time

        # Check if we're approaching the limit
        if self.request_count >= 1400:  # Leave some buffer
            wait_time = 300 - (current_time - self.request_window_start)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.request_window_start = asyncio.get_event_loop().time()
