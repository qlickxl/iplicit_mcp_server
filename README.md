# iplicit MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An MCP (Model Context Protocol) server that integrates Claude AI with the iplicit cloud accounting API. Query your financial data, search documents, manage contacts, and generate reports using natural language through Claude.

## Features

- 🔍 **Search Documents** - Find invoices, purchase orders, journals, and other financial documents
- 📄 **Document Details** - Get complete information about specific documents including line items
- 👥 **Contact Management** - Search and retrieve customer and supplier information
- 📊 **Project Tracking** - Query project data and profitability information
- 🔄 **Automatic Authentication** - Session token management with auto-refresh
- 📝 **Multiple Formats** - Get responses in JSON or human-readable Markdown
- ⚡ **Rate Limiting** - Built-in request throttling to respect API limits

## Prerequisites

- **Python 3.10 or higher**
- **iplicit account** with API access enabled
- **API credentials** from your iplicit administrator (API key, username, domain)
- **Claude Desktop** or another MCP-compatible client

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/qlickxl/iplicit_mcp_server.git
cd iplicit_mcp_server
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example environment file and fill in your iplicit credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
IPLICIT_API_KEY=your_api_key_here
IPLICIT_USERNAME=your_username_here
IPLICIT_DOMAIN=your_domain_here
```

**Where to get credentials:**
- Contact your iplicit administrator or email `apisupport@iplicit.com`
- Your domain is typically something like `mycompany.iplicit` or `sandbox.demo`

### 4. Configure Claude Desktop

Add the server to your Claude Desktop configuration file:

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration:**

```json
{
  "mcpServers": {
    "iplicit": {
      "command": "python",
      "args": ["-m", "iplicit_mcp_server"],
      "cwd": "/path/to/iplicit_mcp_server",
      "env": {
        "IPLICIT_API_KEY": "your_api_key_here",
        "IPLICIT_USERNAME": "your_username_here",
        "IPLICIT_DOMAIN": "your_domain_here"
      }
    }
  }
}
```

**Note:** Replace `/path/to/iplicit_mcp_server` with the actual path to your installation.

### 5. Restart Claude Desktop

After updating the configuration, restart Claude Desktop for the changes to take effect.

## Usage

Once configured, you can ask Claude natural language questions about your iplicit data:

### Example Queries

**Search for documents:**
```
"Show me all outstanding purchase invoices from October 2025"
"Find sales invoices posted this week"
"List all journals created yesterday"
```

**Get document details:**
```
"Get full details for invoice SIN100"
"Show me the line items for purchase order PO-2025-001"
```

**Search contacts:**
```
"Find all suppliers with 'Office' in their name"
"List active customers"
"Show me all contacts in the United Kingdom"
```

**Get contact information:**
```
"Get details for supplier code SUP001"
"Show me information about customer 'Acme Corp'"
```

**Search projects:**
```
"List all active projects"
"Find projects containing 'Website' in the description"
"Show me completed projects"
```

See [examples/example_queries.md](examples/example_queries.md) for more examples.

## Available Tools

### 1. search_documents

Search for financial documents with flexible filtering.

**Parameters:**
- `doc_class` (optional): Document type (e.g., "SaleInvoice", "PurchaseInvoice")
- `status` (optional): Document status (e.g., "posted", "outstanding", "draft")
- `from_date` (optional): Start date (YYYY-MM-DD)
- `to_date` (optional): End date (YYYY-MM-DD)
- `contact_account` (optional): Filter by customer/supplier
- `limit` (default: 50): Maximum results (1-500)
- `format` (default: "markdown"): Output format ("json" or "markdown")

### 2. get_document

Retrieve full details of a specific document.

**Parameters:**
- `document_id` (required): Document ID or reference
- `include_details` (default: true): Include line item details
- `format` (default: "markdown"): Output format

### 3. search_contact_accounts

Search for customers, suppliers, or all contacts.

**Parameters:**
- `account_type` (default: "all"): "customer", "supplier", or "all"
- `search_term` (optional): Search by name or code
- `active_only` (default: true): Show only active accounts
- `limit` (default: 50): Maximum results
- `format` (default: "markdown"): Output format

### 4. get_contact_account

Get detailed information about a specific contact.

**Parameters:**
- `account_id` (required): Contact account ID or code
- `include_contacts` (default: true): Include associated contacts
- `include_balance` (default: true): Include balance information
- `format` (default: "markdown"): Output format

### 5. search_projects

Search for projects.

**Parameters:**
- `search_term` (optional): Search by code or name
- `status` (optional): Filter by status ("active", "completed")
- `legal_entity` (optional): Filter by legal entity
- `limit` (default: 50): Maximum results
- `format` (default: "markdown"): Output format

---

## Phase 2: Write Operations ⚠️

**IMPORTANT:** Phase 2 tools create and modify real financial data. Use with caution!

### 6. create_purchase_invoice

Create a new purchase invoice (supplier invoice).

**Parameters:**
- `contact_account_id` (required): Supplier contact ID or code (auto-resolves codes to UUIDs)
- `doc_date` (required): Document date (YYYY-MM-DD)
- `due_date` (required): Payment due date (YYYY-MM-DD)
- `currency` (default: "GBP"): Currency code
- `doc_type_id` (optional): Document type UUID (auto-fetched if not provided)
- `legal_entity_id` (optional): Legal entity UUID (auto-fetched if not provided)
- `description` (optional): Invoice description
- `their_doc_no` (optional): Supplier's invoice number
- `payment_terms_id` (optional): Payment terms UUID
- `project_id` (optional): Project UUID
- `lines` (optional): Array of line items with: description, quantity, net_currency_unit_price, tax_code_id, account_id
- `format` (default: "markdown"): Output format

**Example:**
```
"Create a purchase invoice for supplier B023 for £1,500 due in 30 days"
```

**Returns:** Created invoice with document number, ID, and full details

### 7. create_sale_invoice

Create a new sales invoice (customer invoice).

**Parameters:**
- `contact_account_id` (required): Customer contact ID or code (auto-resolves codes to UUIDs)
- `doc_date` (required): Document date (YYYY-MM-DD)
- `due_date` (required): Payment due date (YYYY-MM-DD)
- `currency` (default: "GBP"): Currency code
- `doc_type_id` (optional): Document type UUID (auto-fetched if not provided)
- `legal_entity_id` (optional): Legal entity UUID (auto-fetched if not provided)
- `description` (optional): Invoice description
- `reference` (optional): Invoice reference number
- `payment_terms_id` (optional): Payment terms UUID
- `project_id` (optional): Project UUID
- `lines` (optional): Array of line items
- `format` (default: "markdown"): Output format

**Example:**
```
"Create a sales invoice for customer 10723 for £2,400 for consulting services"
```

**Returns:** Created invoice with document number, ID, and full details

### 8. update_document

Update an existing document. **IMPORTANT:** Only draft documents can be updated. Posted/approved documents will be rejected.

**Parameters:**
- `document_id` (required): Document ID or reference number
- `description` (optional): Update description
- `their_doc_no` (optional): Update supplier/customer reference
- `reference` (optional): Update document reference
- `doc_date` (optional): Update document date (YYYY-MM-DD)
- `due_date` (optional): Update due date (YYYY-MM-DD)
- `contact_account_id` (optional): Change contact account (ID or code)
- `lines` (optional): Update line items (replaces existing)
- `format` (default: "markdown"): Output format

**Example:**
```
"Update invoice PIN000048 to change the description to 'Office supplies Q4'"
```

**Returns:** Updated document with modification tracking

**Note:** At least one field must be provided to update.

---

## Phase 3: Orders, Payments & Products

### 9. search_purchase_orders

Search for purchase orders with flexible filtering.

**Parameters:**
- `status` (optional): Filter by status (draft, approved, outstanding, posted)
- `supplier` (optional): Filter by supplier name or code
- `from_date` (optional): Start date (YYYY-MM-DD)
- `to_date` (optional): End date (YYYY-MM-DD)
- `project_id` (optional): Filter by project
- `limit` (default: 50, max: 500): Maximum results
- `format` (default: "markdown"): Output format

**Example:**
```
"Show me all outstanding purchase orders"
"Find purchase orders for supplier B023"
```

### 10. get_purchase_order

Get detailed information about a specific purchase order.

**Parameters:**
- `order_id` (required): Purchase order ID or reference
- `include_details` (default: true): Include line items
- `format` (default: "markdown"): Output format

**Example:**
```
"Get details for purchase order PO000123"
```

### 11. search_sale_orders

Search for sales orders with filtering options.

**Parameters:**
- `status` (optional): Filter by status
- `customer` (optional): Filter by customer name or code
- `from_date` (optional): Start date (YYYY-MM-DD)
- `to_date` (optional): End date (YYYY-MM-DD)
- `project_id` (optional): Filter by project
- `limit` (default: 50, max: 500): Maximum results
- `format` (default: "markdown"): Output format

**Example:**
```
"Show me sales orders for customer 10723"
```

### 12. get_sale_order

Get detailed information about a specific sales order.

**Parameters:**
- `order_id` (required): Sales order ID or reference
- `include_details` (default: true): Include line items
- `format` (default: "markdown"): Output format

**Example:**
```
"Get details for sales order SO000456"
```

### 13. search_payments

Search payment transactions (received and made).

**Parameters:**
- `payment_type` (default: "all"): "received", "made", or "all"
- `from_date` (optional): Start date (YYYY-MM-DD)
- `to_date` (optional): End date (YYYY-MM-DD)
- `contact` (optional): Filter by customer/supplier
- `min_amount` (optional): Minimum amount
- `max_amount` (optional): Maximum amount
- `limit` (default: 50, max: 500): Maximum results
- `format` (default: "markdown"): Output format

**Example:**
```
"Show me all payments received in November"
```

### 14. search_products

Search the product catalog.

**Parameters:**
- `search_term` (optional): Search by code or description
- `active_only` (default: true): Show only active products
- `product_type` (optional): Filter by product type
- `limit` (default: 50, max: 500): Maximum results
- `format` (default: "markdown"): Output format

**Example:**
```
"Show me all active products with 'Office' in the description"
```

### 15. get_product

Get detailed information about a specific product.

**Parameters:**
- `product_id` (required): Product ID or code
- `include_pricing` (default: true): Include pricing info
- `include_stock` (default: true): Include stock levels
- `format` (default: "markdown"): Output format

**Example:**
```
"Get details for product PROD-001"
```

---

## Phase 4: Organizational Hierarchy & Document Workflows ⚠️

**IMPORTANT:** Phase 4 includes document workflow operations (post, approve, reverse) that modify financial data and are irreversible. Use with extreme caution!

### 16. search_departments

Search for departments in your organization.

**Parameters:**
- `search_term` (optional): Search by department code or name
- `active_only` (default: true): Show only active departments
- `limit` (default: 50, max: 500): Maximum results
- `format` (default: "markdown"): Output format

**Example:**
```
"Show me all active departments"
"Find departments with 'Sales' in the name"
```

### 17. get_department

Get detailed information about a specific department.

**Parameters:**
- `department_id` (required): Department ID or code
- `format` (default: "markdown"): Output format

**Example:**
```
"Get details for department SALES"
```

### 18. search_cost_centres

Search for cost centres in your organization.

**Parameters:**
- `search_term` (optional): Search by cost centre code or name
- `active_only` (default: true): Show only active cost centres
- `limit` (default: 50, max: 500): Maximum results
- `format` (default: "markdown"): Output format

**Example:**
```
"Show me all cost centres"
"Find cost centres for project tracking"
```

### 19. get_cost_centre

Get detailed information about a specific cost centre.

**Parameters:**
- `cost_centre_id` (required): Cost centre ID or code
- `format` (default: "markdown"): Output format

**Example:**
```
"Get details for cost centre CC-001"
```

### 20. post_document ⚠️⚠️⚠️

**CRITICAL OPERATION:** Post a draft document to finalize it in the ledger. This operation:
- Changes document status from draft to posted
- Makes the document affect financial reports
- Makes the document non-editable (can only be reversed)
- **Cannot be undone** (except through reversal)

**Use with extreme caution!**

**Parameters:**
- `document_id` (required): Document ID or reference to post
- `posting_date` (optional): Posting date (YYYY-MM-DD) - uses document date if not provided
- `format` (default: "markdown"): Output format

**Example:**
```
"Post draft invoice SIN000041"
"Post document PIN000048 with posting date 2025-11-04"
```

**Returns:** Posted document with updated status and posting date

**Important Notes:**
- Only draft documents can be posted
- Document must pass all validations
- Once posted, document affects ledger balances
- To correct posted documents, use reverse_document

### 21. approve_document

Approve a document if approval workflow is enabled. This moves the document to approved status, making it ready for posting.

**Parameters:**
- `document_id` (required): Document ID or reference to approve
- `approval_note` (optional): Optional approval note/comment
- `format` (default: "markdown"): Output format

**Example:**
```
"Approve document SIN000042"
"Approve invoice PIN000049 with note 'Approved by finance manager'"
```

**Returns:** Approved document ready for posting

### 22. reverse_document ⚠️⚠️

**IMPORTANT OPERATION:** Reverse a posted document by creating a reversing entry. This is the correct way to correct errors in posted documents.

**Parameters:**
- `document_id` (required): Document ID or reference to reverse
- `reversal_date` (required): Reversal date (YYYY-MM-DD)
- `reversal_reason` (optional): Reason for reversal (recommended for audit trail)
- `format` (default: "markdown"): Output format

**Example:**
```
"Reverse posted invoice SIN000040 on 2025-11-04 due to pricing error"
```

**Returns:** Reversal result with original and reversing document details

**Important Notes:**
- Only posted documents can be reversed
- Creates a new reversing document
- Both original and reversing documents remain in the system
- Reversal affects ledger balances

### 23. search_batch_payments

Search for batch payment records.

**Parameters:**
- `from_date` (optional): Start date filter (YYYY-MM-DD)
- `to_date` (optional): End date filter (YYYY-MM-DD)
- `status` (optional): Filter by status (e.g., draft, posted)
- `limit` (default: 50, max: 500): Maximum results
- `format` (default: "markdown"): Output format

**Example:**
```
"Show me all batch payments from November"
"Find posted batch payments"
```

**Returns:** List of batch payments with totals, item counts, and status

---

## Troubleshooting

### Authentication Errors

**Error:** "Missing required environment variables"

**Solution:** Ensure all three environment variables are set:
- `IPLICIT_API_KEY`
- `IPLICIT_USERNAME`
- `IPLICIT_DOMAIN`

### Connection Errors

**Error:** "Failed to authenticate with iplicit API"

**Solutions:**
- Verify your API key is correct and not expired
- Check your username and domain are correct
- Ensure you have network connectivity
- Contact your iplicit administrator to verify API access is enabled

### Resource Not Found

**Error:** "Resource not found in iplicit"

**Solutions:**
- Verify the document ID or account code is correct
- Use search tools first to find valid IDs
- Check you have permission to access the resource

### Rate Limiting

**Error:** "iplicit API rate limit exceeded"

**Solution:** The server has built-in rate limiting (1500 requests per 5 minutes). If you hit this limit, wait a few minutes before making more requests.

## Security Considerations

- ⚠️ **Never commit your `.env` file** to version control
- 🔐 **Keep your API key secure** - treat it like a password
- 👤 **Use dedicated API users** with minimum required permissions
- 📊 **Monitor API usage** through your iplicit admin panel
- 🔄 **Rotate API keys periodically** as recommended by your security policy

## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
iplicit_mcp_server/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Entry point
│   ├── server.py            # Main MCP server with tools
│   ├── session.py           # Session token management
│   ├── api_client.py        # API request handler
│   ├── formatters.py        # Response formatters
│   └── models.py            # Pydantic input models
├── tests/                   # Test files
├── examples/                # Example queries
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment file
└── README.md               # This file
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## API Documentation

For detailed iplicit API documentation:
- **API Docs:** https://docs.iplicit.com/api/
- **Swagger Reference:** https://api.iplicit.com/api-docs/index.html
- **Support:** apisupport@iplicit.com

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues:** https://github.com/qlickxl/iplicit_mcp_server/issues
- **iplicit API Support:** apisupport@iplicit.com
- **MCP Documentation:** https://modelcontextprotocol.io/

## Roadmap

### Phase 1 ✅ (Completed)
- [x] Read-only document search
- [x] Contact account search and retrieval
- [x] Project search
- [x] Session management with auto-refresh
- [x] Markdown and JSON formatting

### Phase 2 ✅ (Completed)
- [x] Document creation (purchase and sales invoices)
- [x] Document updates (draft documents)
- [x] Smart defaults (auto-lookup of IDs)
- [x] Comprehensive error handling

### Phase 3 ✅ (Completed)
- [x] Purchase order search and retrieval
- [x] Sales order search and retrieval
- [x] Payment search (received and made)
- [x] Product catalog search and retrieval
- [x] Advanced filtering and client-side search

### Phase 4 ✅ (Completed - v1.0.0)
- [x] Department and cost centre management
- [x] Document workflow operations (post/approve/reverse)
- [x] Batch payment search
- [x] Complete document lifecycle support
- [x] Production-ready error handling

### Phase 5 (Future Enhancements)
- [ ] Journal entry creation and management
- [ ] Financial reporting (trial balance, P&L, balance sheet)
- [ ] Real-time webhooks for document events
- [ ] Data export and analysis tools
- [ ] PyPI package publication
- [ ] Bulk operations
- [ ] Advanced analytics and reporting

## Acknowledgments

- Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- Designed for [Claude Desktop](https://claude.ai/download)
- Powered by [iplicit API](https://www.iplicit.com)

---

**Version:** 1.0.0
**Last Updated:** November 4, 2025
