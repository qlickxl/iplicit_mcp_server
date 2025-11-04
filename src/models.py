"""Pydantic models for iplicit MCP Server"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


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
