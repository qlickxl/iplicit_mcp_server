# iplicit MCP Server - Phase 2 Design Document

**Date:** November 4, 2025
**Status:** Design Phase

---

## API Exploration Summary

### ✅ Available Write Operations

Based on live API testing, the following write operations are confirmed working:

1. **POST /purchaseinvoice** - Create purchase invoice (400 validation - endpoint exists)
2. **POST /saleinvoice** - Create sale invoice (400 validation - endpoint exists)
3. **PATCH /document/{id}** - Update document (confirmed working, draft documents only)

### ❌ Unavailable Operations

The following operations return 404 (Not Found) and will NOT be implemented in Phase 2:

- Journals (GET /journal, POST /journal)
- Contact creation (POST /contact)
- Document posting/approval (POST /document/{id}/post, POST /document/{id}/approve)
- Financial reporting (GET /profitandloss, /balancesheet, /trialbalance, /cashflow)

---

## Phase 2 Scope (Revised)

Based on API availability, Phase 2 will implement **3 new MCP tools**:

### Tool 1: create_purchase_invoice
Create a new purchase invoice (supplier invoice)

### Tool 2: create_sale_invoice
Create a new sales invoice (customer invoice)

### Tool 3: update_document
Update an existing document (draft documents only)

---

## Tool Specifications

### 1. create_purchase_invoice

**Purpose:** Create a new purchase invoice from a supplier

**Required Parameters:**
- `doc_type_id` (string): Document type identifier (UUID)
- `contact_account_id` (string): Supplier contact account ID (UUID)
- `legal_entity_id` (string): Legal entity ID (UUID)
- `currency` (string): Currency code (e.g., "GBP", "USD", "EUR")
- `doc_date` (string): Document date (ISO format: "YYYY-MM-DD")
- `due_date` (string): Payment due date (ISO format: "YYYY-MM-DD")

**Optional Parameters:**
- `description` (string): Invoice description
- `their_doc_no` (string): Supplier's invoice number
- `lines` (array): Line items with details
  - `description` (string): Line description
  - `quantity` (number): Quantity
  - `net_currency_unit_price` (number): Unit price excluding tax
  - `tax_code_id` (string): Tax code UUID
  - `account_id` (string): GL account UUID
- `payment_terms_id` (string): Payment terms UUID
- `project_id` (string): Project UUID (for project-based invoices)

**Response:** Created document ID and details (JSON or Markdown)

**Example Usage:**
```
"Create a purchase invoice for supplier ABC Ltd for £500 due in 30 days"
```

---

### 2. create_sale_invoice

**Purpose:** Create a new sales invoice for a customer

**Required Parameters:**
- `doc_type_id` (string): Document type identifier (UUID)
- `contact_account_id` (string): Customer contact account ID (UUID)
- `legal_entity_id` (string): Legal entity ID (UUID)
- `currency` (string): Currency code (e.g., "GBP", "USD", "EUR")
- `doc_date` (string): Document date (ISO format: "YYYY-MM-DD")
- `due_date` (string): Payment due date (ISO format: "YYYY-MM-DD")

**Optional Parameters:**
- `description` (string): Invoice description
- `reference` (string): Invoice reference/number
- `lines` (array): Line items with details (same structure as purchase invoice)
- `payment_terms_id` (string): Payment terms UUID
- `project_id` (string): Project UUID

**Response:** Created document ID and details (JSON or Markdown)

**Example Usage:**
```
"Create a sales invoice for customer XYZ Corp for £1,200 for consulting services"
```

---

### 3. update_document

**Purpose:** Update an existing document (draft status only)

**Required Parameters:**
- `document_id` (string): Document ID or reference to update

**Optional Parameters (at least one required):**
- `description` (string): Update description
- `their_doc_no` (string): Update supplier/customer reference
- `doc_date` (string): Update document date
- `due_date` (string): Update due date
- `contact_account_id` (string): Change contact account
- `lines` (array): Update line items

**Important Constraints:**
- Document must be in "draft" status
- Posted/approved documents cannot be updated
- Will return error 400 if document is not draft

**Response:** Updated document details (JSON or Markdown)

**Example Usage:**
```
"Update invoice PIN000040 to change the description to 'Consulting services Q4'"
```

---

## Helper Tools (Supporting Infrastructure)

To make the creation tools user-friendly, we'll need helper functions to:

1. **Lookup Document Types** - Search for doc type IDs by name/description
2. **Lookup Legal Entities** - Get legal entity IDs
3. **Lookup Payment Terms** - Get payment terms IDs
4. **Lookup Tax Codes** - Get tax code IDs for line items
5. **Lookup GL Accounts** - Get account IDs for line items

These can be implemented as:
- Additional MCP tools (user-facing)
- Internal utility functions (hidden)
- Smart parameter handling with search capability

**Recommendation:** Start with internal utility functions, expose as tools if needed.

---

## Implementation Plan

### Step 1: Extend models.py
Add Pydantic schemas for:
- `CreatePurchaseInvoiceInput`
- `CreateSaleInvoiceInput`
- `UpdateDocumentInput`
- `InvoiceLineItem` (for line item structure)

### Step 2: Extend api_client.py
Add methods:
- `create_purchase_invoice(data: dict)`
- `create_sale_invoice(data: dict)`
- `update_document(document_id: str, data: dict)`

Helper methods:
- `get_document_types()` - For smart doc type lookup
- `get_legal_entities()` - For legal entity lookup
- `get_payment_terms()` - For payment terms lookup
- `get_tax_codes()` - For tax code lookup

### Step 3: Extend formatters.py
Add formatters:
- `format_created_document()` - Format creation response
- `format_updated_document()` - Format update response

### Step 4: Extend server.py
Add tool definitions and handlers:
- `@app.call_tool()` handlers for the 3 new tools
- Parameter validation
- Error handling for business rules (draft status, required fields)

### Step 5: Testing
Create test script:
- Test purchase invoice creation
- Test sale invoice creation
- Test document update (draft vs posted)
- Test validation errors
- Test with minimal vs full parameters

### Step 6: Documentation
Update:
- README.md - Add Phase 2 tools
- examples/example_queries.md - Add creation/update examples
- Create PHASE_2_EXAMPLES.md with detailed examples

---

## Error Handling Strategy

### Validation Errors (400/422)
- Missing required fields → User-friendly message listing missing fields
- Invalid UUIDs → "Invalid ID format for {field}"
- Invalid dates → "Date must be in YYYY-MM-DD format"

### Business Rule Errors (400)
- Document not draft → "Cannot update document {id}: must be in draft status"
- Invalid contact → "Contact account {id} not found or inactive"
- Invalid legal entity → "Legal entity {id} not found"

### Permission Errors (403)
- No write access → "You don't have permission to create/update documents"

### Not Found Errors (404)
- Document doesn't exist → "Document {id} not found"

---

## Security Considerations

### Write Operations are Destructive
- All write operations create or modify financial data
- Add confirmation step for users? (optional)
- Log all write operations

### Sandbox vs Production
- Currently using sandbox.lms123
- Add clear warnings in documentation
- Consider adding a "dry_run" mode

### Validation Before Submission
- Validate all UUIDs are properly formatted
- Validate dates are in correct format
- Validate currency codes against known list
- Validate amounts are positive numbers

---

## Example Scenarios

### Scenario 1: Simple Purchase Invoice Creation

**User Query:**
```
"Create a purchase invoice for supplier B023 (Bristow Software) for £1,000 due in 30 days for software licenses"
```

**Tool Workflow:**
1. Search for contact account "B023" → get `contactAccountId`
2. Get default legal entity → get `legalEntityId`
3. Get default purchase invoice doc type → get `docTypeId`
4. Calculate due date (today + 30 days)
5. Call `create_purchase_invoice` with parameters
6. Return formatted result with invoice number

### Scenario 2: Sales Invoice with Line Items

**User Query:**
```
"Create a sales invoice for customer CUST001 with two items:
- 10 hours of consulting at £100/hour
- Travel expenses £50
Invoice date October 1, 2025, due November 1, 2025"
```

**Tool Workflow:**
1. Lookup customer CUST001 → get `contactAccountId`
2. Get sales invoice doc type → get `docTypeId`
3. Get default legal entity → get `legalEntityId`
4. Build lines array with 2 items
5. Call `create_sale_invoice` with parameters
6. Return formatted result

### Scenario 3: Update Draft Invoice

**User Query:**
```
"Update invoice PIN000040 to change the description to 'Office supplies Q3 2025'"
```

**Tool Workflow:**
1. Call `update_document` with document_id="PIN000040" and description
2. If error "must be draft" → Inform user document is already posted
3. Return formatted updated document

---

## Success Criteria for Phase 2

- [ ] All 3 tools implemented and tested
- [ ] Pydantic schemas with full validation
- [ ] Helper functions for UUID lookups
- [ ] Comprehensive error messages
- [ ] Test script with 10+ scenarios passing
- [ ] Documentation updated with examples
- [ ] Security considerations documented
- [ ] Ready for production use (with caution)

---

## Future Enhancements (Phase 3)

When/if additional API endpoints become available:

- **Journals** - Create general journals for manual entries
- **Document Posting** - Post draft documents to finalize them
- **Document Approval** - Approve documents in workflow
- **Financial Reports** - Generate P&L, balance sheet, etc.
- **Batch Operations** - Create/update multiple documents at once
- **Contact Creation** - Create new suppliers/customers
- **Delete Operations** - Delete draft documents

---

## Next Steps

1. ✅ API exploration complete
2. **In Progress:** Design document (this file)
3. **Next:** Implement Pydantic models for Phase 2 tools
4. Extend API client with write methods
5. Add formatters for creation/update responses
6. Add tools to server.py
7. Create comprehensive test script
8. Update documentation

---

**Generated:** November 4, 2025
**By:** Claude Code
**Project:** iplicit MCP Server Phase 2
