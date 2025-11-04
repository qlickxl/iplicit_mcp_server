"""Main MCP server for iplicit API integration"""

import os
from typing import Any
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent

from .session import IplicitSessionManager
from .api_client import IplicitAPIClient
from .formatters import format_response
from .models import (
    SearchDocumentsInput,
    GetDocumentInput,
    SearchContactAccountsInput,
    GetContactAccountInput,
    SearchProjectsInput,
)

# Load environment variables
load_dotenv()

# Initialize server
app = Server("iplicit-mcp-server")

# Initialize clients (lazy initialization)
session_manager: IplicitSessionManager = None
api_client: IplicitAPIClient = None


def get_api_client() -> IplicitAPIClient:
    """Get or create API client"""
    global session_manager, api_client

    if api_client is None:
        session_manager = IplicitSessionManager()
        api_client = IplicitAPIClient(session_manager)

    return api_client


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_documents",
            description=(
                "Search for financial documents (invoices, purchase orders, journals, etc.) "
                "in iplicit. Filter by document type, status, date range, and contact account. "
                "Returns a list of matching documents with key details."
            ),
            inputSchema=SearchDocumentsInput.model_json_schema(),
        ),
        Tool(
            name="get_document",
            description=(
                "Retrieve full details of a specific document by its ID. "
                "Includes header information and line item details. "
                "Use this after finding a document with search_documents."
            ),
            inputSchema=GetDocumentInput.model_json_schema(),
        ),
        Tool(
            name="search_contact_accounts",
            description=(
                "Search for contact accounts (customers, suppliers, or all contacts) in iplicit. "
                "Filter by account type, name/code, and active status. "
                "Returns a list of matching contact accounts."
            ),
            inputSchema=SearchContactAccountsInput.model_json_schema(),
        ),
        Tool(
            name="get_contact_account",
            description=(
                "Get detailed information about a specific contact account by ID or code. "
                "Includes contact details, balance information, and associated contacts."
            ),
            inputSchema=GetContactAccountInput.model_json_schema(),
        ),
        Tool(
            name="search_projects",
            description=(
                "Search for projects in iplicit. Filter by project code, name, status, "
                "or legal entity. Returns a list of matching projects."
            ),
            inputSchema=SearchProjectsInput.model_json_schema(),
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    try:
        client = get_api_client()

        if name == "search_documents":
            result = await handle_search_documents(client, arguments)
        elif name == "get_document":
            result = await handle_get_document(client, arguments)
        elif name == "search_contact_accounts":
            result = await handle_search_contact_accounts(client, arguments)
        elif name == "get_contact_account":
            result = await handle_get_contact_account(client, arguments)
        elif name == "search_projects":
            result = await handle_search_projects(client, arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=result)]

    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


async def handle_search_documents(client: IplicitAPIClient, args: dict) -> str:
    """Handle search_documents tool"""
    input_data = SearchDocumentsInput(**args)

    # Build query parameters
    params = {}

    if input_data.from_date:
        params["fromDate"] = input_data.from_date
    if input_data.to_date:
        params["toDate"] = input_data.to_date
    if input_data.doc_class:
        params["docClass"] = input_data.doc_class
    if input_data.status:
        params["status"] = input_data.status
    if input_data.contact_account:
        params["contactAccount"] = input_data.contact_account

    # Note: pageSize may or may not be supported, we'll try it
    params["pageSize"] = min(input_data.limit, 100)

    # Make API request
    response = await client.make_request("document", params=params)

    # Format response
    return format_response(response, input_data.format, "documents")


async def handle_get_document(client: IplicitAPIClient, args: dict) -> str:
    """Handle get_document tool"""
    input_data = GetDocumentInput(**args)

    # Get document by ID
    endpoint = f"document/{input_data.document_id}"

    # Make API request
    response = await client.make_request(endpoint)

    # Format response
    return format_response(response, input_data.format, "document")


async def handle_search_contact_accounts(client: IplicitAPIClient, args: dict) -> str:
    """Handle search_contact_accounts tool"""
    input_data = SearchContactAccountsInput(**args)

    # Make API request
    response = await client.make_request("contactaccount")

    # Filter results based on criteria
    if isinstance(response, dict) and "items" in response:
        items = response["items"]
    elif isinstance(response, list):
        items = response
    else:
        items = [response]

    # Filter by account type
    if input_data.account_type != "all":
        if input_data.account_type == "supplier":
            items = [item for item in items if "supplier" in item]
        elif input_data.account_type == "customer":
            items = [item for item in items if "customer" in item]

    # Filter by active status
    if input_data.active_only:
        filtered_items = []
        for item in items:
            is_active = True
            if "supplier" in item:
                is_active = item["supplier"].get("isActive", True)
            elif "customer" in item:
                is_active = item["customer"].get("isActive", True)
            if is_active:
                filtered_items.append(item)
        items = filtered_items

    # Filter by search term
    if input_data.search_term:
        search_lower = input_data.search_term.lower()
        items = [
            item for item in items
            if (search_lower in item.get("description", "").lower() or
                search_lower in item.get("code", "").lower())
        ]

    # Apply limit
    items = items[:input_data.limit]

    # Format response
    filtered_response = {"items": items, "totalCount": len(items)}
    return format_response(filtered_response, input_data.format, "contacts")


async def handle_get_contact_account(client: IplicitAPIClient, args: dict) -> str:
    """Handle get_contact_account tool"""
    input_data = GetContactAccountInput(**args)

    # First, get all contact accounts
    response = await client.make_request("contactaccount")

    # Find the specific account
    if isinstance(response, dict) and "items" in response:
        items = response["items"]
    elif isinstance(response, list):
        items = response
    else:
        items = [response]

    # Search by ID or code
    account = None
    for item in items:
        if (item.get("id") == input_data.account_id or
            item.get("code") == input_data.account_id):
            account = item
            break

    if not account:
        raise FileNotFoundError(
            f"Contact account '{input_data.account_id}' not found. "
            "Use search_contact_accounts to find valid account codes or IDs."
        )

    # Format response
    return format_response(account, input_data.format, "contact")


async def handle_search_projects(client: IplicitAPIClient, args: dict) -> str:
    """Handle search_projects tool"""
    input_data = SearchProjectsInput(**args)

    # Make API request
    response = await client.make_request("project")

    # Filter results
    if isinstance(response, dict) and "items" in response:
        items = response["items"]
    elif isinstance(response, list):
        items = response
    else:
        items = [response]

    # Filter by search term
    if input_data.search_term:
        search_lower = input_data.search_term.lower()
        items = [
            item for item in items
            if (search_lower in item.get("description", "").lower() or
                search_lower in item.get("code", "").lower())
        ]

    # Filter by status
    if input_data.status:
        status_lower = input_data.status.lower()
        if status_lower in ["active", "inactive"]:
            is_active = status_lower == "active"
            items = [item for item in items if item.get("isActive") == is_active]

    # Apply limit
    items = items[:input_data.limit]

    # Format response
    filtered_response = {"items": items, "totalCount": len(items)}
    return format_response(filtered_response, input_data.format, "projects")


def main():
    """Run the MCP server"""
    import asyncio
    from mcp.server.stdio import stdio_server

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
