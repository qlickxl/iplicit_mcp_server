"""
iplicit MCP Server - Pydantic Models

Copyright (c) 2025 QLickXL
Licensed under MIT License - see LICENSE file for details

Repository: https://github.com/qlickxl/iplicit_mcp_server
"""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field, field_validator
from datetime import date


class SearchDocumentsInput(BaseModel):
    """Input schema for searching documents"""

    doc_class: Optional[str] = Field(
        None,
        description="Document class filter: e.g., SaleInvoice, PurchaseInvoice, PurchaseOrder, etc."
    )
    status: Optional[str] = Field(
        None,
        description="Document status: draft, outstanding, posted, approved, reversed, abandoned"
    )
    from_date: Optional[str] = Field(
        None,
        description="Start date filter (ISO format: YYYY-MM-DD)"
    )
    to_date: Optional[str] = Field(
        None,
        description="End date filter (ISO format: YYYY-MM-DD)"
    )
    contact_account: Optional[str] = Field(
        None,
        description="Filter by customer or supplier code/name"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of results to return"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class GetDocumentInput(BaseModel):
    """Input schema for retrieving a specific document"""

    document_id: str = Field(
        description="Document ID or reference"
    )
    include_details: bool = Field(
        default=True,
        description="Include line item details"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class SearchContactAccountsInput(BaseModel):
    """Input schema for searching contact accounts"""

    account_type: Optional[Literal["customer", "supplier", "all"]] = Field(
        default="all",
        description="Type of contact account to search"
    )
    search_term: Optional[str] = Field(
        None,
        description="Search by name, code, or email"
    )
    active_only: bool = Field(
        default=True,
        description="Return only active accounts"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of results"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class GetContactAccountInput(BaseModel):
    """Input schema for retrieving a specific contact account"""

    account_id: str = Field(
        description="Contact account ID or code"
    )
    include_contacts: bool = Field(
        default=True,
        description="Include associated contact persons"
    )
    include_balance: bool = Field(
        default=True,
        description="Include account balance information"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class SearchProjectsInput(BaseModel):
    """Input schema for searching projects"""

    search_term: Optional[str] = Field(
        None,
        description="Search by project code or name"
    )
    status: Optional[str] = Field(
        None,
        description="Filter by project status (e.g., active, completed)"
    )
    legal_entity: Optional[str] = Field(
        None,
        description="Filter by legal entity"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of results"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


# ===== PHASE 2: WRITE OPERATIONS =====


class InvoiceLineItem(BaseModel):
    """Schema for invoice line item"""

    description: str = Field(
        description="Line item description"
    )
    quantity: float = Field(
        default=1.0,
        gt=0,
        description="Quantity"
    )
    net_currency_unit_price: float = Field(
        description="Unit price excluding tax"
    )
    tax_code_id: Optional[str] = Field(
        None,
        description="Tax code UUID (optional, will use default if not provided)"
    )
    account_id: Optional[str] = Field(
        None,
        description="General ledger account UUID (optional)"
    )


class CreatePurchaseInvoiceInput(BaseModel):
    """Input schema for creating a purchase invoice"""

    # Required fields
    contact_account_id: str = Field(
        description="Supplier contact account ID (UUID) or code - will lookup if code provided"
    )
    doc_date: str = Field(
        description="Document date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
    )
    due_date: str = Field(
        description="Payment due date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
    )

    # Optional fields with smart defaults
    currency: str = Field(
        default="GBP",
        description="Currency code (e.g., GBP, USD, EUR)"
    )
    doc_type_id: Optional[str] = Field(
        None,
        description="Document type UUID (optional, will use default purchase invoice type if not provided)"
    )
    legal_entity_id: Optional[str] = Field(
        None,
        description="Legal entity UUID (optional, will use default if not provided)"
    )

    # Invoice details
    description: Optional[str] = Field(
        None,
        description="Invoice description"
    )
    their_doc_no: Optional[str] = Field(
        None,
        description="Supplier's invoice number/reference"
    )
    payment_terms_id: Optional[str] = Field(
        None,
        description="Payment terms UUID (optional)"
    )
    project_id: Optional[str] = Field(
        None,
        description="Project UUID for project-based invoices (optional)"
    )

    # Line items
    lines: Optional[List[InvoiceLineItem]] = Field(
        None,
        description="Invoice line items (optional for simple invoices)"
    )

    # Response format
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )

    @field_validator('contact_account_id', 'doc_type_id', 'legal_entity_id', 'payment_terms_id', 'project_id')
    @classmethod
    def validate_uuid_or_code(cls, v):
        """Allow UUIDs or codes for ID fields"""
        if v is None:
            return v
        # Don't validate format - let the API handle it
        return v


class CreateSaleInvoiceInput(BaseModel):
    """Input schema for creating a sales invoice"""

    # Required fields
    contact_account_id: str = Field(
        description="Customer contact account ID (UUID) or code - will lookup if code provided"
    )
    doc_date: str = Field(
        description="Document date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
    )
    due_date: str = Field(
        description="Payment due date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
    )

    # Optional fields with smart defaults
    currency: str = Field(
        default="GBP",
        description="Currency code (e.g., GBP, USD, EUR)"
    )
    doc_type_id: Optional[str] = Field(
        None,
        description="Document type UUID (optional, will use default sales invoice type if not provided)"
    )
    legal_entity_id: Optional[str] = Field(
        None,
        description="Legal entity UUID (optional, will use default if not provided)"
    )

    # Invoice details
    description: Optional[str] = Field(
        None,
        description="Invoice description"
    )
    reference: Optional[str] = Field(
        None,
        description="Invoice reference/number"
    )
    payment_terms_id: Optional[str] = Field(
        None,
        description="Payment terms UUID (optional)"
    )
    project_id: Optional[str] = Field(
        None,
        description="Project UUID for project-based invoices (optional)"
    )

    # Line items
    lines: Optional[List[InvoiceLineItem]] = Field(
        None,
        description="Invoice line items (optional for simple invoices)"
    )

    # Response format
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )

    @field_validator('contact_account_id', 'doc_type_id', 'legal_entity_id', 'payment_terms_id', 'project_id')
    @classmethod
    def validate_uuid_or_code(cls, v):
        """Allow UUIDs or codes for ID fields"""
        if v is None:
            return v
        # Don't validate format - let the API handle it
        return v


class UpdateDocumentInput(BaseModel):
    """Input schema for updating an existing document"""

    # Required field
    document_id: str = Field(
        description="Document ID (UUID) or reference number to update"
    )

    # Optional update fields (at least one must be provided)
    description: Optional[str] = Field(
        None,
        description="Update document description"
    )
    their_doc_no: Optional[str] = Field(
        None,
        description="Update supplier/customer reference number"
    )
    reference: Optional[str] = Field(
        None,
        description="Update document reference"
    )
    doc_date: Optional[str] = Field(
        None,
        description="Update document date (ISO format: YYYY-MM-DD)"
    )
    due_date: Optional[str] = Field(
        None,
        description="Update due date (ISO format: YYYY-MM-DD)"
    )
    contact_account_id: Optional[str] = Field(
        None,
        description="Change contact account (UUID or code)"
    )
    lines: Optional[List[InvoiceLineItem]] = Field(
        None,
        description="Update line items (will replace existing lines)"
    )

    # Response format
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


# ===== PHASE 3: ADDITIONAL READ OPERATIONS =====


class SearchPurchaseOrdersInput(BaseModel):
    """Input schema for searching purchase orders"""

    status: Optional[str] = Field(
        None,
        description="Filter by status (e.g., draft, approved, outstanding, posted)"
    )
    supplier: Optional[str] = Field(
        None,
        description="Filter by supplier name or code"
    )
    from_date: Optional[str] = Field(
        None,
        description="Start date filter (ISO format: YYYY-MM-DD)"
    )
    to_date: Optional[str] = Field(
        None,
        description="End date filter (ISO format: YYYY-MM-DD)"
    )
    project_id: Optional[str] = Field(
        None,
        description="Filter by project ID"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of results"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class GetPurchaseOrderInput(BaseModel):
    """Input schema for retrieving a specific purchase order"""

    order_id: str = Field(
        description="Purchase order ID or reference"
    )
    include_details: bool = Field(
        default=True,
        description="Include line item details"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class SearchSaleOrdersInput(BaseModel):
    """Input schema for searching sales orders"""

    status: Optional[str] = Field(
        None,
        description="Filter by status (e.g., draft, approved, outstanding, posted)"
    )
    customer: Optional[str] = Field(
        None,
        description="Filter by customer name or code"
    )
    from_date: Optional[str] = Field(
        None,
        description="Start date filter (ISO format: YYYY-MM-DD)"
    )
    to_date: Optional[str] = Field(
        None,
        description="End date filter (ISO format: YYYY-MM-DD)"
    )
    project_id: Optional[str] = Field(
        None,
        description="Filter by project ID"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of results"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class GetSaleOrderInput(BaseModel):
    """Input schema for retrieving a specific sales order"""

    order_id: str = Field(
        description="Sales order ID or reference"
    )
    include_details: bool = Field(
        default=True,
        description="Include line item details"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class SearchPaymentsInput(BaseModel):
    """Input schema for searching payments"""

    payment_type: Optional[Literal["received", "made", "all"]] = Field(
        default="all",
        description="Type of payment: received (from customers), made (to suppliers), or all"
    )
    from_date: Optional[str] = Field(
        None,
        description="Start date filter (ISO format: YYYY-MM-DD)"
    )
    to_date: Optional[str] = Field(
        None,
        description="End date filter (ISO format: YYYY-MM-DD)"
    )
    contact: Optional[str] = Field(
        None,
        description="Filter by customer/supplier name or code"
    )
    min_amount: Optional[float] = Field(
        None,
        ge=0,
        description="Minimum payment amount"
    )
    max_amount: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum payment amount"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of results"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class SearchProductsInput(BaseModel):
    """Input schema for searching products"""

    search_term: Optional[str] = Field(
        None,
        description="Search by product code or description"
    )
    active_only: bool = Field(
        default=True,
        description="Show only active products"
    )
    product_type: Optional[str] = Field(
        None,
        description="Filter by product type"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of results"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class GetProductInput(BaseModel):
    """Input schema for retrieving a specific product"""

    product_id: str = Field(
        description="Product ID or code"
    )
    include_pricing: bool = Field(
        default=True,
        description="Include pricing information"
    )
    include_stock: bool = Field(
        default=True,
        description="Include stock level information"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


# ===== PHASE 4: ORGANIZATIONAL HIERARCHY & WORKFLOWS =====


class SearchDepartmentsInput(BaseModel):
    """Input schema for searching departments"""

    search_term: Optional[str] = Field(
        None,
        description="Search by department code or name"
    )
    active_only: bool = Field(
        default=True,
        description="Show only active departments"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of results"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class GetDepartmentInput(BaseModel):
    """Input schema for retrieving a specific department"""

    department_id: str = Field(
        description="Department ID or code"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class SearchCostCentresInput(BaseModel):
    """Input schema for searching cost centres"""

    search_term: Optional[str] = Field(
        None,
        description="Search by cost centre code or name"
    )
    active_only: bool = Field(
        default=True,
        description="Show only active cost centres"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of results"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class GetCostCentreInput(BaseModel):
    """Input schema for retrieving a specific cost centre"""

    cost_centre_id: str = Field(
        description="Cost centre ID or code"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class PostDocumentInput(BaseModel):
    """Input schema for posting a document"""

    document_id: str = Field(
        description="Document ID or reference to post"
    )
    posting_date: Optional[str] = Field(
        None,
        description="Posting date (ISO format: YYYY-MM-DD) - uses document date if not provided"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class ApproveDocumentInput(BaseModel):
    """Input schema for approving a document"""

    document_id: str = Field(
        description="Document ID or reference to approve"
    )
    approval_note: Optional[str] = Field(
        None,
        description="Optional approval note/comment"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class ReverseDocumentInput(BaseModel):
    """Input schema for reversing a posted document"""

    document_id: str = Field(
        description="Document ID or reference to reverse"
    )
    reversal_date: str = Field(
        description="Reversal date (ISO format: YYYY-MM-DD)"
    )
    reversal_reason: Optional[str] = Field(
        None,
        description="Reason for reversal (optional but recommended)"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )


class SearchBatchPaymentsInput(BaseModel):
    """Input schema for searching batch payments"""

    from_date: Optional[str] = Field(
        None,
        description="Start date filter (ISO format: YYYY-MM-DD)"
    )
    to_date: Optional[str] = Field(
        None,
        description="End date filter (ISO format: YYYY-MM-DD)"
    )
    status: Optional[str] = Field(
        None,
        description="Filter by status (e.g., draft, posted)"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of results"
    )
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="Response format"
    )
