"""
iplicit MCP Server - API Client Module

Copyright (c) 2025 QlickXL Limited
Licensed under MIT License - see LICENSE file for details

Repository: https://github.com/qlickxl/iplicit_mcp_server
"""

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
                    elif method == "PATCH":
                        response = await client.patch(url, headers=request_headers, json=body, params=params)
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

    # ===== PHASE 2: WRITE OPERATIONS =====

    async def lookup_contact_by_code(self, code: str) -> Optional[str]:
        """
        Lookup contact account ID by code

        Args:
            code: Contact account code

        Returns:
            Contact account UUID or None if not found
        """
        try:
            response = await self.make_request(
                "contactaccount",
                method="GET",
                params={"maxRecordCount": 100}
            )

            items = response if isinstance(response, list) else response.get("items", [])

            for contact in items:
                if contact.get("code") == code:
                    return contact.get("id")

            return None
        except Exception:
            return None

    async def get_default_legal_entity(self) -> Optional[str]:
        """
        Get the first available legal entity ID

        Returns:
            Legal entity UUID or None if not found
        """
        try:
            response = await self.make_request(
                "legalentity",
                method="GET",
                params={"maxRecordCount": 1}
            )

            items = response if isinstance(response, list) else response.get("items", [])

            if items and len(items) > 0:
                return items[0].get("id")

            return None
        except Exception:
            return None

    async def get_default_doc_type(self, doc_class: str) -> Optional[str]:
        """
        Get default document type ID for a document class

        Args:
            doc_class: Document class (e.g., "PurchaseInvoice", "SaleInvoice")

        Returns:
            Document type UUID or None if not found
        """
        try:
            response = await self.make_request(
                "purchaseinvoice" if doc_class == "PurchaseInvoice" else "saleinvoice",
                method="GET",
                params={"maxRecordCount": 1}
            )

            items = response if isinstance(response, list) else response.get("items", [])

            if items and len(items) > 0:
                return items[0].get("docTypeId")

            return None
        except Exception:
            return None

    async def create_purchase_invoice(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new purchase invoice

        Args:
            data: Invoice data including required fields:
                  - contactAccountId or contact code
                  - docDate
                  - dueDate
                  - currency (optional, defaults to GBP)
                  - docTypeId (optional, will fetch default)
                  - legalEntityId (optional, will fetch default)
                  - description (optional)
                  - theirDocNo (optional)
                  - lines (optional)

        Returns:
            Created invoice data

        Raises:
            ValueError: For missing or invalid required fields
            PermissionError: For permission errors
            RuntimeError: For other API errors
        """
        # Prepare request body
        body = {}

        # Handle contact account (lookup by code if needed)
        contact_id = data.get("contactAccountId")
        if contact_id and len(contact_id) < 36:  # Not a UUID, try as code
            looked_up_id = await self.lookup_contact_by_code(contact_id)
            if looked_up_id:
                contact_id = looked_up_id
            else:
                raise ValueError(f"Contact account with code '{contact_id}' not found")

        body["contactAccountId"] = contact_id

        # Handle doc type (use default if not provided)
        doc_type_id = data.get("docTypeId")
        if not doc_type_id:
            doc_type_id = await self.get_default_doc_type("PurchaseInvoice")
            if not doc_type_id:
                raise ValueError(
                    "Could not determine default document type. Please provide docTypeId."
                )

        body["docTypeId"] = doc_type_id

        # Handle legal entity (use default if not provided)
        legal_entity_id = data.get("legalEntityId")
        if not legal_entity_id:
            legal_entity_id = await self.get_default_legal_entity()
            if not legal_entity_id:
                raise ValueError(
                    "Could not determine default legal entity. Please provide legalEntityId."
                )

        body["legalEntityId"] = legal_entity_id

        # Required dates and currency
        body["docDate"] = data["docDate"]
        body["dueDate"] = data["dueDate"]
        body["currency"] = data.get("currency", "GBP")

        # Optional fields
        if "description" in data:
            body["description"] = data["description"]
        if "theirDocNo" in data:
            body["theirDocNo"] = data["theirDocNo"]
        if "paymentTermsId" in data:
            body["paymentTermsId"] = data["paymentTermsId"]
        if "projectId" in data:
            body["projectId"] = data["projectId"]
        if "lines" in data:
            body["details"] = data["lines"]  # API uses "details" not "lines"

        # Make request
        response = await self.make_request(
            "purchaseinvoice",
            method="POST",
            body=body
        )

        # If response is just an ID string, fetch the full document
        if isinstance(response, str):
            document_id = response
            # Fetch full document details
            full_document = await self.make_request(f"purchaseinvoice/{document_id}")
            return full_document

        return response

    async def create_sale_invoice(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new sales invoice

        Args:
            data: Invoice data including required fields:
                  - contactAccountId or contact code
                  - docDate
                  - dueDate
                  - currency (optional, defaults to GBP)
                  - docTypeId (optional, will fetch default)
                  - legalEntityId (optional, will fetch default)
                  - description (optional)
                  - reference (optional)
                  - lines (optional)

        Returns:
            Created invoice data

        Raises:
            ValueError: For missing or invalid required fields
            PermissionError: For permission errors
            RuntimeError: For other API errors
        """
        # Prepare request body
        body = {}

        # Handle contact account (lookup by code if needed)
        contact_id = data.get("contactAccountId")
        if contact_id and len(contact_id) < 36:  # Not a UUID, try as code
            looked_up_id = await self.lookup_contact_by_code(contact_id)
            if looked_up_id:
                contact_id = looked_up_id
            else:
                raise ValueError(f"Contact account with code '{contact_id}' not found")

        body["contactAccountId"] = contact_id

        # Handle doc type (use default if not provided)
        doc_type_id = data.get("docTypeId")
        if not doc_type_id:
            doc_type_id = await self.get_default_doc_type("SaleInvoice")
            if not doc_type_id:
                raise ValueError(
                    "Could not determine default document type. Please provide docTypeId."
                )

        body["docTypeId"] = doc_type_id

        # Handle legal entity (use default if not provided)
        legal_entity_id = data.get("legalEntityId")
        if not legal_entity_id:
            legal_entity_id = await self.get_default_legal_entity()
            if not legal_entity_id:
                raise ValueError(
                    "Could not determine default legal entity. Please provide legalEntityId."
                )

        body["legalEntityId"] = legal_entity_id

        # Required dates and currency
        body["docDate"] = data["docDate"]
        body["dueDate"] = data["dueDate"]
        body["currency"] = data.get("currency", "GBP")

        # Optional fields
        if "description" in data:
            body["description"] = data["description"]
        if "reference" in data:
            body["reference"] = data["reference"]
        if "paymentTermsId" in data:
            body["paymentTermsId"] = data["paymentTermsId"]
        if "projectId" in data:
            body["projectId"] = data["projectId"]
        if "lines" in data:
            body["details"] = data["lines"]  # API uses "details" not "lines"

        # Make request
        response = await self.make_request(
            "saleinvoice",
            method="POST",
            body=body
        )

        # If response is just an ID string, fetch the full document
        if isinstance(response, str):
            document_id = response
            # Fetch full document details
            full_document = await self.make_request(f"saleinvoice/{document_id}")
            return full_document

        return response

    async def update_document(self, document_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing document (draft status only)

        Args:
            document_id: Document ID or reference
            data: Fields to update (at least one required):
                  - description
                  - theirDocNo or reference
                  - docDate
                  - dueDate
                  - contactAccountId
                  - lines

        Returns:
            Updated document data

        Raises:
            ValueError: For missing or invalid fields, or document not in draft status
            FileNotFoundError: If document not found
            PermissionError: For permission errors
            RuntimeError: For other API errors
        """
        # Prepare request body with only provided fields
        body = {}

        if "description" in data:
            body["description"] = data["description"]
        if "theirDocNo" in data:
            body["theirDocNo"] = data["theirDocNo"]
        if "reference" in data:
            body["reference"] = data["reference"]
        if "docDate" in data:
            body["docDate"] = data["docDate"]
        if "dueDate" in data:
            body["dueDate"] = data["dueDate"]
        if "contactAccountId" in data:
            # Handle contact code lookup
            contact_id = data["contactAccountId"]
            if contact_id and len(contact_id) < 36:  # Not a UUID
                looked_up_id = await self.lookup_contact_by_code(contact_id)
                if looked_up_id:
                    contact_id = looked_up_id
            body["contactAccountId"] = contact_id
        if "lines" in data:
            body["details"] = data["lines"]  # API uses "details" not "lines"

        if not body:
            raise ValueError("At least one field must be provided to update")

        # Make request (using PATCH method)
        response = await self.make_request(
            f"document/{document_id}",
            method="PATCH",
            body=body
        )

        # If response is empty (204 No Content), fetch the updated document
        if not response or response == {} or (isinstance(response, dict) and "raw_response" in response and response["raw_response"] == ""):
            # Fetch the updated document
            updated_document = await self.make_request(f"document/{document_id}")
            return updated_document

        return response

    # ===== PHASE 4: DOCUMENT WORKFLOW OPERATIONS =====

    async def post_document(self, document_id: str, posting_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Post a draft document to finalize it

        Args:
            document_id: Document ID or reference to post
            posting_date: Optional posting date (ISO format YYYY-MM-DD)
                         If not provided, uses document date

        Returns:
            Posted document data

        Raises:
            ValueError: If document not in draft status or validation fails
            FileNotFoundError: If document not found
            PermissionError: For permission errors
            RuntimeError: For other API errors
        """
        body = {}
        if posting_date:
            body["postingDate"] = posting_date

        response = await self.make_request(
            f"document/{document_id}/post",
            method="POST",
            body=body
        )

        # If response is empty or just an ID, fetch the posted document
        if not response or isinstance(response, str):
            posted_document = await self.make_request(f"document/{document_id}")
            return posted_document

        return response

    async def approve_document(self, document_id: str, approval_note: Optional[str] = None) -> Dict[str, Any]:
        """
        Approve a document (if approval workflow is enabled)

        Args:
            document_id: Document ID or reference to approve
            approval_note: Optional approval note/comment

        Returns:
            Approved document data

        Raises:
            ValueError: If document not in correct status or validation fails
            FileNotFoundError: If document not found
            PermissionError: For permission errors
            RuntimeError: For other API errors
        """
        body = {}
        if approval_note:
            body["note"] = approval_note

        response = await self.make_request(
            f"document/{document_id}/approve",
            method="POST",
            body=body
        )

        # If response is empty or just an ID, fetch the approved document
        if not response or isinstance(response, str):
            approved_document = await self.make_request(f"document/{document_id}")
            return approved_document

        return response

    async def reverse_document(
        self,
        document_id: str,
        reversal_date: str,
        reversal_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reverse a posted document (creates reversing entry)

        Args:
            document_id: Document ID or reference to reverse
            reversal_date: Reversal date (ISO format YYYY-MM-DD)
            reversal_reason: Optional reason for reversal

        Returns:
            Reversal result with original and reversing document data

        Raises:
            ValueError: If document not posted or validation fails
            FileNotFoundError: If document not found
            PermissionError: For permission errors
            RuntimeError: For other API errors
        """
        body = {
            "reversalDate": reversal_date
        }
        if reversal_reason:
            body["reason"] = reversal_reason

        response = await self.make_request(
            f"document/{document_id}/reverse",
            method="POST",
            body=body
        )

        # Response should include both original and reversing document
        # If not, fetch the reversed document
        if not response or isinstance(response, str):
            reversed_document = await self.make_request(f"document/{document_id}")
            return reversed_document

        return response

    async def create_resource(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic create operation for any resource

        Args:
            endpoint: API endpoint (e.g., "department", "costcentre")
            data: Resource data

        Returns:
            Created resource data
        """
        response = await self.make_request(
            endpoint,
            method="POST",
            body=data
        )
        return response

    async def update_resource(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic update operation for any resource

        Args:
            endpoint: API endpoint with ID (e.g., "department/123" or "document/123/post")
            data: Resource data to update

        Returns:
            Updated resource data
        """
        response = await self.make_request(
            endpoint,
            method="POST",  # Some operations use POST even for updates
            body=data
        )
        return response
