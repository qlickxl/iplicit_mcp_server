# Example Queries for iplicit MCP Server

This document provides realistic examples of how to query your iplicit data through Claude using natural language.

## Document Searches

### Find Invoices

```
"Show me all sales invoices from last month"
"Find outstanding purchase invoices greater than £1000"
"List all posted sales invoices for customer 'Acme Corp'"
"Show invoices created this week"
"Find all draft invoices that need review"
```

### Find Purchase Orders

```
"List all purchase orders from October 2025"
"Show me outstanding purchase orders"
"Find POs for supplier 'Office Supplies Ltd'"
"Get all approved purchase orders waiting for delivery"
```

### Find Journals

```
"Show me all journals posted today"
"Find manual journals from last quarter"
"List journals created by user 'john.smith'"
"Show me correction journals from this month"
```

### Complex Date Filters

```
"Find all documents between 2025-10-01 and 2025-10-31"
"Show me invoices from Q3 2025"
"List all documents posted in the last 7 days"
"Find year-end journals from December 2024"
```

## Document Details

### Get Specific Documents

```
"Get details for invoice SIN-2025-001"
"Show me the line items for purchase order PO-12345"
"Display full information for journal JNL-2025-100"
"What are the details of document ID abc-123-def"
```

### Analyze Document Information

```
"Show me the line items and total for invoice SIN100"
"Get the supplier and payment terms for PO-2025-001"
"What items are on sales invoice SIN-2025-050?"
"Show me who approved purchase order PO-12345"
```

## Contact Account Searches

### Find Suppliers

```
"List all active suppliers"
"Find suppliers with 'Services' in their name"
"Show me suppliers in the United Kingdom"
"Find supplier with code SUP001"
"List all suppliers we've purchased from this year"
```

### Find Customers

```
"Show me all active customers"
"Find customers in London"
"List customers with outstanding balances"
"Find customer 'ABC Corporation'"
"Show me new customers added this quarter"
```

### General Contact Searches

```
"Find all contacts with 'Ltd' in their name"
"List all inactive accounts"
"Show me contacts in the United States"
"Find contact with code 'ACME001'"
"List all parent accounts"
```

## Contact Account Details

### Get Specific Contact Information

```
"Get details for supplier SUP001"
"Show me information about customer 'Widget Company'"
"Display contact details for account CUST-123"
"What's the currency and payment terms for supplier 'Office Depot'?"
"Show me the balance and credit limit for customer ABC Corp"
```

### Analyze Contact Relationships

```
"Show me all sub-accounts under parent account PAR001"
"Get the contact persons for supplier 'Tech Solutions Ltd'"
"What's the payment method for customer 'Acme Corp'?"
"Show me the tax settings for supplier SUP-UK-001"
```

## Project Searches

### Find Projects

```
"List all active projects"
"Find projects containing 'Website' in the name"
"Show me completed projects"
"List projects for legal entity 'UK Operations'"
"Find project with code PROJ-2025-001"
```

### Analyze Project Information

```
"Show me all projects for client 'Acme Corp'"
"List projects started this quarter"
"Find projects that allow timesheets"
"Show me projects managed by 'John Smith'"
"What projects are associated with the London office?"
```

## Combined Queries

### Multi-Step Analysis

```
"Find supplier 'Office Supplies Ltd' and show me all their purchase invoices from last month"

"Get the details for invoice SIN-2025-001 and tell me if the customer has any other outstanding invoices"

"Show me all projects for customer 'ABC Corp' and list the invoices associated with those projects"

"Find all suppliers in the UK and show me which ones we've purchased from in the last 3 months"
```

### Aggregation and Reporting

```
"Show me the total value of outstanding sales invoices"

"How many purchase orders do we have waiting for approval?"

"What's the total amount invoiced to customer 'Acme Corp' this year?"

"Count the number of active suppliers and customers"
```

### Filtering and Sorting

```
"Show me the top 10 suppliers by purchase value"

"List customers sorted by outstanding balance"

"Find the 5 most recent sales invoices"

"Show me suppliers we haven't purchased from in 6 months"
```

## Tips for Best Results

### Be Specific

❌ **Vague:** "Show me some invoices"

✅ **Specific:** "Show me all outstanding sales invoices from October 2025"

### Use Exact Codes When Possible

❌ **Inexact:** "Find that supplier with Office in the name"

✅ **Exact:** "Get details for supplier code SUP-001"

### Specify Date Formats

❌ **Ambiguous:** "Last month's invoices"

✅ **Clear:** "Invoices between 2025-10-01 and 2025-10-31"

### Ask for Context

❌ **Basic:** "Get invoice SIN100"

✅ **Contextual:** "Get invoice SIN100 and tell me if there are any similar invoices for the same customer"

### Chain Queries for Complex Analysis

Instead of one complex query, break it down:

1. "Find all suppliers with 'Technology' in their name"
2. "Get details for supplier TEC-001"
3. "Show me purchase invoices for supplier TEC-001 from this year"

## Format Preferences

### Request Specific Formats

```
"Show me all customers in JSON format"
"List invoices in a markdown table"
"Export supplier data as JSON for analysis"
```

### Limit Results

```
"Show me the first 10 suppliers"
"List up to 20 recent invoices"
"Find maximum 5 projects matching 'Website'"
```

## Error Handling Examples

### When Resources Aren't Found

If Claude says a document/contact isn't found:

1. First search: "Find documents with 'SIN100' in the number"
2. Then get details using the correct ID

### When Permissions Are Denied

If you get a permission error:
- Contact your iplicit administrator
- Request API access for the specific resource type
- Verify your API user has the correct role

### When Too Many Results

If a query returns too many results:
- Add more specific filters
- Reduce the date range
- Use the limit parameter
- Be more specific in search terms

## Advanced Use Cases

### Financial Analysis

```
"Compare sales invoices from Q3 2025 vs Q3 2024"
"Show me supplier spending trends over the last 6 months"
"List customers with decreasing purchase volumes"
"Find invoices that are overdue by more than 30 days"
```

### Compliance and Audit

```
"Find all journals that were posted without approval"
"List invoices modified after they were posted"
"Show me documents created outside business hours"
"Find invoices with missing purchase order references"
```

### Operations

```
"Which suppliers have the longest payment terms?"
"Show me customers on credit hold"
"List projects that are over budget"
"Find purchase orders awaiting delivery for more than 30 days"
```

---

## Need Help?

If you're not getting the results you expect:

1. **Check your filters** - Are dates, codes, and names correct?
2. **Verify permissions** - Do you have API access to the resource?
3. **Try simpler queries first** - Break complex requests into steps
4. **Use exact codes** - When you know the specific document/contact ID
5. **Ask Claude for suggestions** - "What questions can I ask about invoices?"

For more information, see the [README.md](../README.md) or contact your iplicit administrator.
