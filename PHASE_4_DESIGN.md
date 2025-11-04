# Phase 4 Design: Complete the Best iplicit MCP Server

**Goal:** Create the most comprehensive, production-ready iplicit MCP server with complete document lifecycle management, organizational hierarchies, and advanced operations.

**Status:** In Design
**Target:** Version 1.0.0

---

## API Capability Discovery Results

### Available Endpoints (Tested ✓)
- ✅ `/department` - Departments (READ access confirmed)
- ✅ `/costcentre` - Cost Centres (READ access confirmed)
- ✅ `/batchpayment` - Batch Payments (from Phase 3 exploration)

### Unavailable in Sandbox (404)
- ❌ `/journal` - Journal entries (not in sandbox)
- ❌ `/account` - GL accounts (not in sandbox)
- ❌ `/taxcode` - Tax codes (not in sandbox)
- ❌ `/paymentterms` - Payment terms (not in sandbox)
- ❌ `/currency` - Currencies (not in sandbox)
- ❌ `/bankaccount` - Bank accounts (not in sandbox)

### Document Workflow Operations (Needs Investigation)
- `POST /document/{id}/post` - Post documents
- `POST /document/{id}/approve` - Approve documents
- `POST /document/{id}/reverse` - Reverse posted documents

---

## Phase 4 Scope

### Category 1: Organizational Hierarchy (HIGH PRIORITY)

**Purpose:** Complete organizational structure management

**Tools to Implement (4 tools):**

1. **search_departments**
   - Search and filter departments
   - Parameters: search_term, active_only, limit, format
   - Returns: List of departments with code, name, description

2. **get_department**
   - Get detailed department information
   - Parameters: department_id, format
   - Returns: Full department details

3. **search_cost_centres**
   - Search and filter cost centres
   - Parameters: search_term, active_only, limit, format
   - Returns: List of cost centres with code, name, description

4. **get_cost_centre**
   - Get detailed cost centre information
   - Parameters: cost_centre_id, format
   - Returns: Full cost centre details

**Value:**
- Essential for project accounting and cost tracking
- Required for financial reporting by department
- Needed for budget management

---

### Category 2: Document Workflow Operations (HIGH PRIORITY)

**Purpose:** Complete document lifecycle from draft → posted → reversed

**API Client Extension Needed:**
- Add `post_document()` method to api_client.py
- Add `approve_document()` method to api_client.py
- Add `reverse_document()` method to api_client.py

**Tools to Implement (3 tools):**

5. **post_document**
   - Post a draft document to finalize it
   - Parameters: document_id, posting_date (optional), format
   - Returns: Posted document with new status and posting date
   - **Critical:** This completes the document creation workflow

6. **approve_document**
   - Approve a document for posting (if approval workflow enabled)
   - Parameters: document_id, approval_note (optional), format
   - Returns: Approved document ready for posting

7. **reverse_document**
   - Reverse a posted document (creates reversing entry)
   - Parameters: document_id, reversal_date, reversal_reason (optional), format
   - Returns: Reversing document details
   - **Critical:** Essential for error corrections

**Value:**
- Completes full document lifecycle
- Enables error correction through reversals
- Supports approval workflows
- Makes the MCP server production-ready for real accounting

---

### Category 3: Batch Operations (MEDIUM PRIORITY)

**Purpose:** Efficient handling of multiple payments

**Tools to Implement (1 tool):**

8. **search_batch_payments**
   - Search batch payment records
   - Parameters: from_date, to_date, status, limit, format
   - Returns: List of batch payments with totals and item counts

**Value:**
- Visibility into batch payment operations
- Useful for reconciliation
- Complements existing payment search

---

### Category 4: Document Validation & Quality (MEDIUM PRIORITY)

**Purpose:** Help prevent errors before posting

**Tools to Implement (1 tool):**

9. **validate_document**
   - Validate a draft document before posting
   - Parameters: document_id, format
   - Returns: Validation results with errors/warnings list
   - **Note:** This may be implicit in posting, needs testing

**Value:**
- Reduces posting errors
- Provides early feedback
- Improves user experience

---

### Category 5: Enhanced Search (NICE TO HAVE)

**Purpose:** More powerful search across entities

**Tools to Implement (1 tool):**

10. **search_across_documents**
    - Search across all document types at once
    - Parameters: search_term, doc_classes (list), from_date, to_date, limit, format
    - Returns: Combined results from multiple document types
    - **Implementation:** Client-side aggregation of multiple searches

**Value:**
- Convenience for broad searches
- Single query for "find anything related to customer X"

---

## Implementation Plan

### Phase 4A: Organizational Hierarchy (Tools 1-4)
**Estimated:** 2 hours
- Extend models.py with 4 new Pydantic schemas
- Extend formatters.py with 4 new formatters
- Extend server.py with 4 new tool handlers
- Test all 4 tools

### Phase 4B: Document Workflows (Tools 5-7)
**Estimated:** 3 hours
- Extend api_client.py with workflow methods
- Add 3 new Pydantic schemas for workflow operations
- Add 3 new formatters for workflow results
- Add 3 new tool handlers
- **Critical testing:** Test posting, approval, and reversal workflows
- Handle edge cases (already posted, validation errors, etc.)

### Phase 4C: Batch & Validation (Tools 8-9)
**Estimated:** 1.5 hours
- Add batch payment search (simpler since Phase 3 pattern)
- Add document validation if API supports it
- Test both tools

### Phase 4D: Enhanced Search (Tool 10)
**Estimated:** 1 hour
- Implement client-side aggregation
- Test across multiple document types

### Phase 4E: Documentation & Release
**Estimated:** 1 hour
- Update README with all Phase 4 tools
- Create PHASE_4_COMPLETE.md
- Update version to 1.0.0
- Create comprehensive CHANGELOG
- Tag v1.0.0 release

**Total Estimated Time:** 8.5 hours

---

## Success Criteria

**Must Have:**
- ✅ All 10 Phase 4 tools implemented and tested
- ✅ Document posting workflow fully functional
- ✅ Document reversal working correctly
- ✅ Department and cost centre search working
- ✅ All tests passing (aim for 15-20 Phase 4 tests)
- ✅ Documentation complete and accurate
- ✅ Version bumped to 1.0.0

**Quality Gates:**
- Zero breaking changes to existing tools
- All new tools follow established patterns
- Comprehensive error handling
- Clear, helpful error messages
- Dual format support (JSON + Markdown) for all tools

---

## Final Tool Count (v1.0.0)

**Phase 1:** 5 tools (document search, contacts, projects)
**Phase 2:** 3 tools (create invoices, update documents)
**Phase 3:** 7 tools (orders, payments, products)
**Phase 4:** 10 tools (departments, cost centres, workflows, batch, validation, search)

**Total:** **25 professional-grade MCP tools**

---

## Key Technical Considerations

### 1. API Client Extension for Workflows

Current api_client.py has:
- `make_request()` - GET requests
- `create_resource()` - POST to create
- `update_resource()` - PATCH to update

Need to add:
- `post_document(doc_id)` - POST to /document/{id}/post
- `approve_document(doc_id, data)` - POST to /document/{id}/approve
- `reverse_document(doc_id, data)` - POST to /document/{id}/reverse

### 2. Error Handling for Workflows

Workflow operations can fail for many reasons:
- Document not in correct status (can't post already posted doc)
- Missing required fields
- Balance errors
- Permission issues

Need comprehensive error messages that explain:
- Why it failed
- What status the document is in
- What needs to be fixed

### 3. Testing Strategy

**Unit Tests:**
- Test each tool individually
- Mock API responses
- Test error conditions

**Integration Tests:**
- Test full workflows: create → validate → post → reverse
- Test with real sandbox data
- Test all filter combinations

**Edge Case Tests:**
- Empty result sets
- Invalid IDs
- Permission errors
- Already-posted documents

### 4. Documentation Standards

Each tool needs:
- Clear description of what it does
- Complete parameter list with types and defaults
- Usage examples with realistic scenarios
- Return value description
- Common error conditions

---

## Risk Assessment

### Low Risk
- Departments and cost centres (simple read operations, proven pattern)
- Batch payment search (simple read operation)
- Enhanced search (client-side only)

### Medium Risk
- Document validation (API support uncertain, may not exist)

### Higher Risk (Requires Careful Testing)
- Document posting (changes document state, irreversible in some cases)
- Document approval (workflow state management)
- Document reversal (creates new documents, affects financials)

**Mitigation:**
- Extensive testing in sandbox
- Clear documentation of irreversible operations
- Helpful error messages
- Validation before destructive operations

---

## Post-v1.0.0 Roadmap (Future Phases)

### Phase 5: Advanced Reporting (if endpoints become available)
- Trial balance reports
- Profit & Loss statements
- Balance sheet queries
- Custom report generation

### Phase 6: Bulk Operations
- Bulk document updates
- Batch posting
- Mass reversals

### Phase 7: Real-time Integration
- Webhook support for document events
- Real-time notifications
- Event streaming

### Phase 8: Data Export & Analysis
- CSV/Excel export
- Data aggregations
- Analytics queries

---

## Conclusion

Phase 4 will make this the **most comprehensive iplicit MCP server** available by:

1. **Completing document lifecycle** (draft → approve → post → reverse)
2. **Adding organizational structure** (departments, cost centres)
3. **Enabling batch operations** (batch payment visibility)
4. **Improving quality** (validation before posting)
5. **Enhancing usability** (cross-document search)

With **25 professional tools**, comprehensive error handling, dual format support, and complete documentation, this will be a **production-ready v1.0.0 release**.

The server will handle:
- Complete CRUD operations for all major entities
- Full document workflows from creation to reversal
- Organizational hierarchy and cost tracking
- Batch operations
- Advanced search and filtering

**This will be the best MCP server for iplicit!** 🚀
