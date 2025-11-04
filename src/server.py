"""Main MCP server for iplicit API integration"""

import os
from typing import Any
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent

from .session import IplicitSessionManager
from .api_client import IplicitAPIClient
from .formatters import (
    format_response,
    format_created_invoice,
    format_updated_document,
    # Phase 3: Additional formatters
    format_purchase_orders,
    format_single_purchase_order,
    format_sale_orders,
    format_single_sale_order,
    format_payments,
    format_products,
    format_single_product,
    # Phase 4: Organizational hierarchy & workflows
    format_departments,
    format_single_department,
    format_cost_centres,
    format_single_cost_centre,
    format_posted_document,
    format_approved_document,
    format_reversed_document,
    format_batch_payments,
)
from .models import (
    SearchDocumentsInput,
    GetDocumentInput,
    SearchContactAccountsInput,
    GetContactAccountInput,
    SearchProjectsInput,
    # Phase 2: Write operations
    CreatePurchaseInvoiceInput,
    CreateSaleInvoiceInput,
    UpdateDocumentInput,
    # Phase 3: Additional read operations
    SearchPurchaseOrdersInput,
    GetPurchaseOrderInput,
    SearchSaleOrdersInput,
    GetSaleOrderInput,
    SearchPaymentsInput,
    SearchProductsInput,
    GetProductInput,
    # Phase 4: Organizational hierarchy & workflows
    SearchDepartmentsInput,
    GetDepartmentInput,
    SearchCostCentresInput,
    GetCostCentreInput,
    PostDocumentInput,
    ApproveDocumentInput,
    ReverseDocumentInput,
    SearchBatchPaymentsInput,
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
        # Phase 2: Write operations
        Tool(
            name="create_purchase_invoice",
            description=(
                "Create a new purchase invoice (supplier invoice) in iplicit. "
                "Requires contact account (supplier), document date, and due date. "
                "Optionally include line items, description, and other details. "
                "Returns the created invoice with document number and ID."
            ),
            inputSchema=CreatePurchaseInvoiceInput.model_json_schema(),
        ),
        Tool(
            name="create_sale_invoice",
            description=(
                "Create a new sales invoice (customer invoice) in iplicit. "
                "Requires contact account (customer), document date, and due date. "
                "Optionally include line items, description, and other details. "
                "Returns the created invoice with document number and ID."
            ),
            inputSchema=CreateSaleInvoiceInput.model_json_schema(),
        ),
        Tool(
            name="update_document",
            description=(
                "Update an existing document in iplicit. IMPORTANT: Only draft documents "
                "can be updated. Posted or approved documents cannot be modified. "
                "Provide the document ID and the fields you want to update "
                "(e.g., description, dates, line items). Returns the updated document details."
            ),
            inputSchema=UpdateDocumentInput.model_json_schema(),
        ),
        # Phase 3: Additional read operations
        Tool(
            name="search_purchase_orders",
            description=(
                "Search for purchase orders in iplicit. Filter by status, supplier, "
                "date range, or project. Returns a list of purchase orders with key details "
                "(PO number, supplier, date, amount, status)."
            ),
            inputSchema=SearchPurchaseOrdersInput.model_json_schema(),
        ),
        Tool(
            name="get_purchase_order",
            description=(
                "Get detailed information about a specific purchase order by ID or reference. "
                "Includes line items, delivery information, and approval status."
            ),
            inputSchema=GetPurchaseOrderInput.model_json_schema(),
        ),
        Tool(
            name="search_sale_orders",
            description=(
                "Search for sales orders in iplicit. Filter by status, customer, "
                "date range, or project. Returns a list of sales orders with key details "
                "(SO number, customer, date, amount, status)."
            ),
            inputSchema=SearchSaleOrdersInput.model_json_schema(),
        ),
        Tool(
            name="get_sale_order",
            description=(
                "Get detailed information about a specific sales order by ID or reference. "
                "Includes line items, delivery dates, and invoicing status."
            ),
            inputSchema=GetSaleOrderInput.model_json_schema(),
        ),
        Tool(
            name="search_payments",
            description=(
                "Search payment transactions (both received from customers and made to suppliers). "
                "Filter by payment type, date range, contact, or amount. "
                "Returns a list of payments with amount, date, contact, and reference."
            ),
            inputSchema=SearchPaymentsInput.model_json_schema(),
        ),
        Tool(
            name="search_products",
            description=(
                "Search the product catalog in iplicit. Filter by product code, description, "
                "active status, or product type. Returns a list of products with code, "
                "description, price, and active status."
            ),
            inputSchema=SearchProductsInput.model_json_schema(),
        ),
        Tool(
            name="get_product",
            description=(
                "Get detailed information about a specific product by ID or code. "
                "Includes pricing information, stock levels, dimensions, and supplier details."
            ),
            inputSchema=GetProductInput.model_json_schema(),
        ),

        # ===== PHASE 4: ORGANIZATIONAL HIERARCHY & WORKFLOWS =====

        Tool(
            name="search_departments",
            description=(
                "Search for departments in iplicit. Filter by search term and active status. "
                "Returns a list of departments with code, name, and status."
            ),
            inputSchema=SearchDepartmentsInput.model_json_schema(),
        ),
        Tool(
            name="get_department",
            description=(
                "Get detailed information about a specific department by ID or code."
            ),
            inputSchema=GetDepartmentInput.model_json_schema(),
        ),
        Tool(
            name="search_cost_centres",
            description=(
                "Search for cost centres in iplicit. Filter by search term and active status. "
                "Returns a list of cost centres with code, name, and status."
            ),
            inputSchema=SearchCostCentresInput.model_json_schema(),
        ),
        Tool(
            name="get_cost_centre",
            description=(
                "Get detailed information about a specific cost centre by ID or code."
            ),
            inputSchema=GetCostCentreInput.model_json_schema(),
        ),
        Tool(
            name="post_document",
            description=(
                "Post a draft document to finalize it in the ledger. This is a critical operation "
                "that changes the document status from draft to posted. Posted documents affect "
                "financial reports and cannot be edited (only reversed). Use with caution."
            ),
            inputSchema=PostDocumentInput.model_json_schema(),
        ),
        Tool(
            name="approve_document",
            description=(
                "Approve a document if approval workflow is enabled. This moves the document "
                "to approved status, making it ready for posting."
            ),
            inputSchema=ApproveDocumentInput.model_json_schema(),
        ),
        Tool(
            name="reverse_document",
            description=(
                "Reverse a posted document by creating a reversing entry. This is the correct "
                "way to correct errors in posted documents. Creates both a reversal record and "
                "a new reversing document."
            ),
            inputSchema=ReverseDocumentInput.model_json_schema(),
        ),
        Tool(
            name="search_batch_payments",
            description=(
                "Search for batch payment records. Filter by date range and status. "
                "Returns a list of batch payments with totals, item counts, and status."
            ),
            inputSchema=SearchBatchPaymentsInput.model_json_schema(),
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
        # Phase 2: Write operations
        elif name == "create_purchase_invoice":
            result = await handle_create_purchase_invoice(client, arguments)
        elif name == "create_sale_invoice":
            result = await handle_create_sale_invoice(client, arguments)
        elif name == "update_document":
            result = await handle_update_document(client, arguments)
        # Phase 3: Additional read operations
        elif name == "search_purchase_orders":
            result = await handle_search_purchase_orders(client, arguments)
        elif name == "get_purchase_order":
            result = await handle_get_purchase_order(client, arguments)
        elif name == "search_sale_orders":
            result = await handle_search_sale_orders(client, arguments)
        elif name == "get_sale_order":
            result = await handle_get_sale_order(client, arguments)
        elif name == "search_payments":
            result = await handle_search_payments(client, arguments)
        elif name == "search_products":
            result = await handle_search_products(client, arguments)
        elif name == "get_product":
            result = await handle_get_product(client, arguments)

        # Phase 4: Organizational hierarchy & workflows
        elif name == "search_departments":
            result = await handle_search_departments(client, arguments)
        elif name == "get_department":
            result = await handle_get_department(client, arguments)
        elif name == "search_cost_centres":
            result = await handle_search_cost_centres(client, arguments)
        elif name == "get_cost_centre":
            result = await handle_get_cost_centre(client, arguments)
        elif name == "post_document":
            result = await handle_post_document(client, arguments)
        elif name == "approve_document":
            result = await handle_approve_document(client, arguments)
        elif name == "reverse_document":
            result = await handle_reverse_document(client, arguments)
        elif name == "search_batch_payments":
            result = await handle_search_batch_payments(client, arguments)

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


# ===== PHASE 2: WRITE OPERATION HANDLERS =====


async def handle_create_purchase_invoice(client: IplicitAPIClient, args: dict) -> str:
    """Handle create_purchase_invoice tool"""
    input_data = CreatePurchaseInvoiceInput(**args)

    # Convert input to dict for API client
    data = {
        "contactAccountId": input_data.contact_account_id,
        "docDate": input_data.doc_date,
        "dueDate": input_data.due_date,
        "currency": input_data.currency,
    }

    # Optional fields
    if input_data.doc_type_id:
        data["docTypeId"] = input_data.doc_type_id
    if input_data.legal_entity_id:
        data["legalEntityId"] = input_data.legal_entity_id
    if input_data.description:
        data["description"] = input_data.description
    if input_data.their_doc_no:
        data["theirDocNo"] = input_data.their_doc_no
    if input_data.payment_terms_id:
        data["paymentTermsId"] = input_data.payment_terms_id
    if input_data.project_id:
        data["projectId"] = input_data.project_id
    if input_data.lines:
        # Convert Pydantic models to dicts
        data["lines"] = [line.model_dump() for line in input_data.lines]

    # Create invoice via API client
    response = await client.create_purchase_invoice(data)

    # Format and return response
    return format_created_invoice(response, input_data.format)


async def handle_create_sale_invoice(client: IplicitAPIClient, args: dict) -> str:
    """Handle create_sale_invoice tool"""
    input_data = CreateSaleInvoiceInput(**args)

    # Convert input to dict for API client
    data = {
        "contactAccountId": input_data.contact_account_id,
        "docDate": input_data.doc_date,
        "dueDate": input_data.due_date,
        "currency": input_data.currency,
    }

    # Optional fields
    if input_data.doc_type_id:
        data["docTypeId"] = input_data.doc_type_id
    if input_data.legal_entity_id:
        data["legalEntityId"] = input_data.legal_entity_id
    if input_data.description:
        data["description"] = input_data.description
    if input_data.reference:
        data["reference"] = input_data.reference
    if input_data.payment_terms_id:
        data["paymentTermsId"] = input_data.payment_terms_id
    if input_data.project_id:
        data["projectId"] = input_data.project_id
    if input_data.lines:
        # Convert Pydantic models to dicts
        data["lines"] = [line.model_dump() for line in input_data.lines]

    # Create invoice via API client
    response = await client.create_sale_invoice(data)

    # Format and return response
    return format_created_invoice(response, input_data.format)


async def handle_update_document(client: IplicitAPIClient, args: dict) -> str:
    """Handle update_document tool"""
    input_data = UpdateDocumentInput(**args)

    # Build update data dict with only provided fields
    data = {}

    if input_data.description is not None:
        data["description"] = input_data.description
    if input_data.their_doc_no is not None:
        data["theirDocNo"] = input_data.their_doc_no
    if input_data.reference is not None:
        data["reference"] = input_data.reference
    if input_data.doc_date is not None:
        data["docDate"] = input_data.doc_date
    if input_data.due_date is not None:
        data["dueDate"] = input_data.due_date
    if input_data.contact_account_id is not None:
        data["contactAccountId"] = input_data.contact_account_id
    if input_data.lines is not None:
        # Convert Pydantic models to dicts
        data["lines"] = [line.model_dump() for line in input_data.lines]

    # Update document via API client
    response = await client.update_document(input_data.document_id, data)

    # Format and return response
    return format_updated_document(response, input_data.format)


# ===== PHASE 3: ADDITIONAL READ OPERATION HANDLERS =====


async def handle_search_purchase_orders(client: IplicitAPIClient, args: dict) -> str:
    """Handle search_purchase_orders tool"""
    input_data = SearchPurchaseOrdersInput(**args)

    # Build query parameters
    params = {}
    if input_data.from_date:
        params["fromDate"] = input_data.from_date
    if input_data.to_date:
        params["toDate"] = input_data.to_date
    if input_data.status:
        params["status"] = input_data.status
    if input_data.project_id:
        params["projectId"] = input_data.project_id

    params["maxRecordCount"] = min(input_data.limit, 500)

    # Make API request
    response = await client.make_request("purchaseorder", params=params)

    # Handle response format
    items = response if isinstance(response, list) else response.get("items", [])

    # Client-side filter by supplier if provided
    if input_data.supplier:
        filtered = []
        for item in items:
            supplier = item.get("contactAccountDescription", item.get("supplier", ""))
            if input_data.supplier.lower() in supplier.lower():
                filtered.append(item)
        items = filtered

    # Apply limit
    items = items[:input_data.limit]

    # Format response
    if input_data.format == "json":
        return format_response({"items": items, "totalCount": len(items)}, "json")
    else:
        return format_purchase_orders(items, len(items))


async def handle_get_purchase_order(client: IplicitAPIClient, args: dict) -> str:
    """Handle get_purchase_order tool"""
    input_data = GetPurchaseOrderInput(**args)

    # Get purchase order by ID
    response = await client.make_request(f"purchaseorder/{input_data.order_id}")

    # Format response
    if input_data.format == "json":
        return format_response(response, "json")
    else:
        return format_single_purchase_order(response)


async def handle_search_sale_orders(client: IplicitAPIClient, args: dict) -> str:
    """Handle search_sale_orders tool"""
    input_data = SearchSaleOrdersInput(**args)

    # Build query parameters
    params = {}
    if input_data.from_date:
        params["fromDate"] = input_data.from_date
    if input_data.to_date:
        params["toDate"] = input_data.to_date
    if input_data.status:
        params["status"] = input_data.status
    if input_data.project_id:
        params["projectId"] = input_data.project_id

    params["maxRecordCount"] = min(input_data.limit, 500)

    # Make API request
    response = await client.make_request("saleorder", params=params)

    # Handle response format
    items = response if isinstance(response, list) else response.get("items", [])

    # Client-side filter by customer if provided
    if input_data.customer:
        filtered = []
        for item in items:
            customer = item.get("contactAccountDescription", item.get("customer", ""))
            if input_data.customer.lower() in customer.lower():
                filtered.append(item)
        items = filtered

    # Apply limit
    items = items[:input_data.limit]

    # Format response
    if input_data.format == "json":
        return format_response({"items": items, "totalCount": len(items)}, "json")
    else:
        return format_sale_orders(items, len(items))


async def handle_get_sale_order(client: IplicitAPIClient, args: dict) -> str:
    """Handle get_sale_order tool"""
    input_data = GetSaleOrderInput(**args)

    # Get sale order by ID
    response = await client.make_request(f"saleorder/{input_data.order_id}")

    # Format response
    if input_data.format == "json":
        return format_response(response, "json")
    else:
        return format_single_sale_order(response)


async def handle_search_payments(client: IplicitAPIClient, args: dict) -> str:
    """Handle search_payments tool"""
    input_data = SearchPaymentsInput(**args)

    # Build query parameters
    params = {}
    if input_data.from_date:
        params["fromDate"] = input_data.from_date
    if input_data.to_date:
        params["toDate"] = input_data.to_date

    params["maxRecordCount"] = min(input_data.limit, 500)

    # Make API request
    response = await client.make_request("payment", params=params)

    # Handle response format
    items = response if isinstance(response, list) else response.get("items", [])

    # Client-side filters
    if input_data.contact:
        filtered = []
        for item in items:
            contact = item.get("contactAccountDescription", item.get("contact", ""))
            if input_data.contact.lower() in contact.lower():
                filtered.append(item)
        items = filtered

    if input_data.min_amount is not None:
        items = [item for item in items if item.get("amount", 0) >= input_data.min_amount]

    if input_data.max_amount is not None:
        items = [item for item in items if item.get("amount", 0) <= input_data.max_amount]

    # Apply limit
    items = items[:input_data.limit]

    # Format response
    if input_data.format == "json":
        return format_response({"items": items, "totalCount": len(items)}, "json")
    else:
        return format_payments(items, len(items))


async def handle_search_products(client: IplicitAPIClient, args: dict) -> str:
    """Handle search_products tool"""
    input_data = SearchProductsInput(**args)

    # Build query parameters
    params = {"maxRecordCount": min(input_data.limit, 500)}

    # Make API request
    response = await client.make_request("product", params=params)

    # Handle response format
    items = response if isinstance(response, list) else response.get("items", [])

    # Client-side filters
    if input_data.search_term:
        filtered = []
        for item in items:
            code = item.get("code", "").lower()
            desc = item.get("description", item.get("name", "")).lower()
            if input_data.search_term.lower() in code or input_data.search_term.lower() in desc:
                filtered.append(item)
        items = filtered

    if input_data.active_only:
        items = [item for item in items if item.get("isActive", True)]

    if input_data.product_type:
        items = [item for item in items if item.get("productType") == input_data.product_type]

    # Apply limit
    items = items[:input_data.limit]

    # Format response
    if input_data.format == "json":
        return format_response({"items": items, "totalCount": len(items)}, "json")
    else:
        return format_products(items, len(items))


async def handle_get_product(client: IplicitAPIClient, args: dict) -> str:
    """Handle get_product tool"""
    input_data = GetProductInput(**args)

    # Get product by ID
    response = await client.make_request(f"product/{input_data.product_id}")

    # Format response
    if input_data.format == "json":
        return format_response(response, "json")
    else:
        return format_single_product(response)


# ===== PHASE 4: ORGANIZATIONAL HIERARCHY & WORKFLOWS =====


async def handle_search_departments(client: IplicitAPIClient, args: dict) -> str:
    """Handle search_departments tool"""
    input_data = SearchDepartmentsInput(**args)

    params = {"maxRecordCount": min(input_data.limit, 500)}

    response = await client.make_request("department", params=params)
    items = response if isinstance(response, list) else response.get("items", [])

    # Client-side filter by search term
    if input_data.search_term:
        filtered = []
        for item in items:
            code = item.get("code", "").lower()
            name = item.get("description", item.get("name", "")).lower()
            if input_data.search_term.lower() in code or input_data.search_term.lower() in name:
                filtered.append(item)
        items = filtered

    # Filter by active status
    if input_data.active_only:
        items = [item for item in items if item.get("active", True)]

    items = items[:input_data.limit]

    if input_data.format == "json":
        return format_response({"items": items, "totalCount": len(items)}, "json")
    else:
        return format_departments(items, len(items))


async def handle_get_department(client: IplicitAPIClient, args: dict) -> str:
    """Handle get_department tool"""
    input_data = GetDepartmentInput(**args)

    # Try to get by ID first, then search by code if not a UUID
    if len(input_data.department_id) == 36 and "-" in input_data.department_id:
        # Looks like a UUID
        dept = await client.make_request(f"department/{input_data.department_id}")
    else:
        # Search by code
        response = await client.make_request("department", params={"maxRecordCount": 100})
        items = response if isinstance(response, list) else response.get("items", [])

        dept = None
        for item in items:
            if item.get("code") == input_data.department_id:
                dept = item
                break

        if not dept:
            return f"Department with code '{input_data.department_id}' not found."

    if input_data.format == "json":
        return format_response(dept, "json")
    else:
        return format_single_department(dept)


async def handle_search_cost_centres(client: IplicitAPIClient, args: dict) -> str:
    """Handle search_cost_centres tool"""
    input_data = SearchCostCentresInput(**args)

    params = {"maxRecordCount": min(input_data.limit, 500)}

    response = await client.make_request("costcentre", params=params)
    items = response if isinstance(response, list) else response.get("items", [])

    # Client-side filter by search term
    if input_data.search_term:
        filtered = []
        for item in items:
            code = item.get("code", "").lower()
            name = item.get("description", item.get("name", "")).lower()
            if input_data.search_term.lower() in code or input_data.search_term.lower() in name:
                filtered.append(item)
        items = filtered

    # Filter by active status
    if input_data.active_only:
        items = [item for item in items if item.get("active", True)]

    items = items[:input_data.limit]

    if input_data.format == "json":
        return format_response({"items": items, "totalCount": len(items)}, "json")
    else:
        return format_cost_centres(items, len(items))


async def handle_get_cost_centre(client: IplicitAPIClient, args: dict) -> str:
    """Handle get_cost_centre tool"""
    input_data = GetCostCentreInput(**args)

    # Try to get by ID first, then search by code if not a UUID
    if len(input_data.cost_centre_id) == 36 and "-" in input_data.cost_centre_id:
        # Looks like a UUID
        cc = await client.make_request(f"costcentre/{input_data.cost_centre_id}")
    else:
        # Search by code
        response = await client.make_request("costcentre", params={"maxRecordCount": 100})
        items = response if isinstance(response, list) else response.get("items", [])

        cc = None
        for item in items:
            if item.get("code") == input_data.cost_centre_id:
                cc = item
                break

        if not cc:
            return f"Cost centre with code '{input_data.cost_centre_id}' not found."

    if input_data.format == "json":
        return format_response(cc, "json")
    else:
        return format_single_cost_centre(cc)


async def handle_post_document(client: IplicitAPIClient, args: dict) -> str:
    """Handle post_document tool"""
    input_data = PostDocumentInput(**args)

    try:
        # Post the document
        posted_doc = await client.post_document(
            input_data.document_id,
            input_data.posting_date
        )

        if input_data.format == "json":
            return format_response(posted_doc, "json")
        else:
            return format_posted_document(posted_doc)

    except ValueError as e:
        error_msg = str(e)
        if "draft" in error_msg.lower():
            return f"❌ Error: Document cannot be posted. {error_msg}\n\nOnly draft documents can be posted. Check the document status."
        elif "validation" in error_msg.lower():
            return f"❌ Validation Error: {error_msg}\n\nPlease fix the validation errors before posting."
        else:
            return f"❌ Error posting document: {error_msg}"
    except FileNotFoundError:
        return f"❌ Document '{input_data.document_id}' not found. Please check the document ID or reference."
    except Exception as e:
        return f"❌ Unexpected error posting document: {str(e)}"


async def handle_approve_document(client: IplicitAPIClient, args: dict) -> str:
    """Handle approve_document tool"""
    input_data = ApproveDocumentInput(**args)

    try:
        # Approve the document
        approved_doc = await client.approve_document(
            input_data.document_id,
            input_data.approval_note
        )

        if input_data.format == "json":
            return format_response(approved_doc, "json")
        else:
            return format_approved_document(approved_doc)

    except ValueError as e:
        error_msg = str(e)
        return f"❌ Error approving document: {error_msg}\n\nCheck the document status and approval workflow settings."
    except FileNotFoundError:
        return f"❌ Document '{input_data.document_id}' not found. Please check the document ID or reference."
    except Exception as e:
        return f"❌ Unexpected error approving document: {str(e)}"


async def handle_reverse_document(client: IplicitAPIClient, args: dict) -> str:
    """Handle reverse_document tool"""
    input_data = ReverseDocumentInput(**args)

    try:
        # Reverse the document
        reversal_result = await client.reverse_document(
            input_data.document_id,
            input_data.reversal_date,
            input_data.reversal_reason
        )

        if input_data.format == "json":
            return format_response(reversal_result, "json")
        else:
            return format_reversed_document(reversal_result)

    except ValueError as e:
        error_msg = str(e)
        if "posted" in error_msg.lower():
            return f"❌ Error: Document cannot be reversed. {error_msg}\n\nOnly posted documents can be reversed."
        else:
            return f"❌ Error reversing document: {error_msg}"
    except FileNotFoundError:
        return f"❌ Document '{input_data.document_id}' not found. Please check the document ID or reference."
    except Exception as e:
        return f"❌ Unexpected error reversing document: {str(e)}"


async def handle_search_batch_payments(client: IplicitAPIClient, args: dict) -> str:
    """Handle search_batch_payments tool"""
    input_data = SearchBatchPaymentsInput(**args)

    params = {}
    if input_data.from_date:
        params["fromDate"] = input_data.from_date
    if input_data.to_date:
        params["toDate"] = input_data.to_date
    if input_data.status:
        params["status"] = input_data.status
    params["maxRecordCount"] = min(input_data.limit, 500)

    response = await client.make_request("batchpayment", params=params)
    items = response if isinstance(response, list) else response.get("items", [])

    items = items[:input_data.limit]

    if input_data.format == "json":
        return format_response({"items": items, "totalCount": len(items)}, "json")
    else:
        return format_batch_payments(items, len(items))


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
