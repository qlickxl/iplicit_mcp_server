# iplicit MCP Server - Phase 3 Design Document

**Date:** November 4, 2025
**Status:** Design Phase

---

## API Exploration Summary

### ✅ Available Endpoints Discovered

From comprehensive API exploration, **8 additional endpoints are available**:

1. ✅ `/legalentity` - Legal Entities (3 items)
2. ✅ `/purchaseorder` - Purchase Orders (14 items)
3. ✅ `/saleorder` - Sales Orders (12 items)
4. ✅ `/payment` - Payments (18 items)
5. ✅ `/batchpayment` - Batch Payments (8 items)
6. ✅ `/product` - Products (24 items)
7. ✅ `/department` - Departments (5 items)
8. ✅ `/costcentre` - Cost Centres (6 items)

### ❌ Unavailable Endpoints

The following endpoints return 404 and will NOT be implemented:
- Journals, GL Accounts, Tax Codes, Document Types
- Financial Reports (P&L, Balance Sheet, Trial Balance, Cash Flow)
- Bank Accounts, Employees, Users, Periods
- Approvals, Workflows, Attachments, Dimensions

---

## Phase 3 Scope

Based on API availability, Phase 3 will implement **7 new MCP tools** (all read operations):

### High Priority Tools (5)

1. **search_purchase_orders** - Search purchase orders
2. **get_purchase_order** - Get PO details
3. **search_sale_orders** - Search sales orders
4. **get_sale_order** - Get sales order details
5. **search_payments** - Search payment transactions

### Medium Priority Tools (2)

6. **search_products** - Search product catalog
7. **get_product** - Get product details

---

## Tool Specifications

### 1. search_purchase_orders

**Purpose:** Search and filter purchase orders

**Parameters:**
- `status` (optional): Filter by status (e.g., "draft", "approved", "outstanding")
- `supplier` (optional): Filter by supplier name/code
- `from_date` (optional): Start date filter (YYYY-MM-DD)
- `to_date` (optional): End date filter (YYYY-MM-DD)
- `project_id` (optional): Filter by project
- `limit` (default: 50, max: 500): Maximum results
- `format` (default: "markdown"): Response format

**Response:** List of purchase orders with key details (PO number, supplier, date, amount, status)

**Example Usage:**
```
"Show me all outstanding purchase orders from October 2025"
"Find purchase orders for supplier B023"
```

---

### 2. get_purchase_order

**Purpose:** Get detailed information about a specific purchase order

**Parameters:**
- `order_id` (required): Purchase order ID or reference
- `include_details` (default: true): Include line item details
- `format` (default: "markdown"): Response format

**Response:** Full PO details including line items, delivery information, approval status

**Example Usage:**
```
"Get details for purchase order PO000123"
```

---

### 3. search_sale_orders

**Purpose:** Search and filter sales orders

**Parameters:**
- `status` (optional): Filter by status
- `customer` (optional): Filter by customer name/code
- `from_date` (optional): Start date filter
- `to_date` (optional): End date filter
- `project_id` (optional): Filter by project
- `limit` (default: 50, max: 500): Maximum results
- `format` (default: "markdown"): Response format

**Response:** List of sales orders with key details

**Example Usage:**
```
"Show me all sales orders for customer 10723"
"Find outstanding sales orders"
```

---

### 4. get_sale_order

**Purpose:** Get detailed information about a specific sales order

**Parameters:**
- `order_id` (required): Sales order ID or reference
- `include_details` (default: true): Include line item details
- `format` (default: "markdown"): Response format

**Response:** Full sales order details including line items, delivery dates, invoicing status

**Example Usage:**
```
"Get details for sales order SO000456"
```

---

### 5. search_payments

**Purpose:** Search payment transactions (both received and made)

**Parameters:**
- `payment_type` (optional): "received" or "made" or "all"
- `from_date` (optional): Start date filter
- `to_date` (optional): End date filter
- `contact` (optional): Filter by customer/supplier
- `min_amount` (optional): Minimum payment amount
- `max_amount` (optional): Maximum payment amount
- `limit` (default: 50, max: 500): Maximum results
- `format` (default: "markdown"): Response format

**Response:** List of payments with amount, date, contact, reference

**Example Usage:**
```
"Show me all payments received in November"
"Find payments made to supplier B023"
```

---

### 6. search_products

**Purpose:** Search product catalog

**Parameters:**
- `search_term` (optional): Search by product code or description
- `active_only` (default: true): Show only active products
- `product_type` (optional): Filter by product type
- `limit` (default: 50, max: 500): Maximum results
- `format` (default: "markdown"): Response format

**Response:** List of products with code, description, price, stock info

**Example Usage:**
```
"Show me all products with 'Office' in the description"
"List active products"
```

---

### 7. get_product

**Purpose:** Get detailed information about a specific product

**Parameters:**
- `product_id` (required): Product ID or code
- `include_pricing` (default: true): Include pricing information
- `include_stock` (default: true): Include stock levels
- `format` (default: "markdown"): Response format

**Response:** Full product details including pricing, stock, dimensions, suppliers

**Example Usage:**
```
"Get details for product PROD-001"
```

---

## Implementation Plan

### Step 1: Extend models.py
Add Pydantic schemas for all 7 tools:
- `SearchPurchaseOrdersInput`
- `GetPurchaseOrderInput`
- `SearchSaleOrdersInput`
- `GetSaleOrderInput`
- `SearchPaymentsInput`
- `SearchProductsInput`
- `GetProductInput`

### Step 2: Extend formatters.py
Add specialized formatters for:
- Purchase orders (list and detail views)
- Sales orders (list and detail views)
- Payments (list view)
- Products (list and detail views)

### Step 3: Extend server.py
Add 7 new tool definitions and handlers:
- Implement filtering logic
- Handle response formatting
- Proper error handling

### Step 4: Testing
Create `test_phase3.py`:
- Test all 7 new tools
- Test filtering capabilities
- Test with various parameter combinations
- Verify formatters work correctly

### Step 5: Documentation
Update:
- README.md - Add Phase 3 tools
- examples/example_queries.md - Add Phase 3 examples
- Create PHASE_3_COMPLETE.md

---

## Alternative Tools Considered But Deferred

**Departments and Cost Centres:**
- **search_departments** - Could be useful for organizational queries
- **search_cost_centres** - Useful for cost allocation

**Reason for deferring:** Less commonly used in day-to-day workflows. Can be added in a Phase 3.5 if needed.

---

## Success Criteria for Phase 3

- [ ] All 7 tools implemented and tested
- [ ] Pydantic schemas with validation
- [ ] Specialized formatters for orders, payments, products
- [ ] Test script with 10+ scenarios passing
- [ ] Documentation updated
- [ ] Live API testing verified
- [ ] Committed to GitHub

---

## Key Design Patterns

### Consistency with Phase 1 & 2
- Same parameter naming conventions
- Same format options (markdown/json)
- Same error handling patterns
- Same filtering approaches

### Smart Defaults
- `limit` defaults to 50
- `active_only` defaults to true for products
- `include_details` defaults to true for detail views
- `format` defaults to "markdown"

### Client-Side vs Server-Side Filtering
- Use API parameters when available
- Fall back to client-side filtering when needed
- Document which filters are server-side vs client-side

---

## Expected Phase 3 Metrics

**Estimated Deliverables:**
- Production code: ~600 lines
- Test code: ~300 lines
- Documentation: ~400 lines
- Total: ~1,300 lines

**Development Time Estimate:**
- Design: 30 minutes (this document)
- Implementation: 2-3 hours
- Testing: 1 hour
- Documentation: 30 minutes
- Total: ~4-5 hours

---

## Next Steps

1. ✅ API exploration complete
2. **In Progress:** Design document (this file)
3. **Next:** Implement Pydantic models for Phase 3 tools
4. Extend formatters for orders, payments, products
5. Add tools to server.py
6. Create comprehensive test script
7. Update documentation
8. Commit to GitHub

---

**Generated:** November 4, 2025
**By:** Claude Code
**Project:** iplicit MCP Server Phase 3
