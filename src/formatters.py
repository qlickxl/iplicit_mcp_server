"""Response formatters for converting API data to JSON or Markdown"""

import json
from typing import Any, Dict, List
from datetime import datetime


def format_response(data: Any, format_type: str, context: str = "") -> str:
    """
    Format API response as JSON or Markdown

    Args:
        data: Response data from API
        format_type: "json" or "markdown"
        context: Context string for better formatting (e.g., "documents", "contacts")

    Returns:
        Formatted string
    """
    if format_type == "json":
        return json.dumps(data, indent=2, default=str)

    # Markdown formatting
    if isinstance(data, dict):
        if "items" in data:
            # Handle paginated response
            items = data.get("items", [])
            total_count = data.get("totalCount", len(items))

            if context == "documents":
                return _format_documents_markdown(items, total_count)
            elif context == "contacts":
                return _format_contacts_markdown(items, total_count)
            elif context == "projects":
                return _format_projects_markdown(items, total_count)
            else:
                return _format_generic_list_markdown(items, total_count, context)
        else:
            # Single item response
            if context == "document":
                return _format_single_document_markdown(data)
            elif context == "contact":
                return _format_single_contact_markdown(data)
            else:
                return _format_generic_item_markdown(data, context)

    elif isinstance(data, list):
        # List of items
        return _format_generic_list_markdown(data, len(data), context)

    # Fallback
    return str(data)


def _format_documents_markdown(items: List[Dict], total_count: int) -> str:
    """Format documents list as markdown table"""
    if not items:
        return "No documents found."

    md = f"## Documents\n\n"
    md += f"Found **{len(items)}** documents"
    if total_count > len(items):
        md += f" (showing first {len(items)} of {total_count} total)"
    md += "\n\n"

    # Create table
    md += "| Doc Class | Doc No | Date | Contact | Amount | Status |\n"
    md += "|-----------|--------|------|---------|--------|--------|\n"

    for doc in items:
        doc_class = doc.get("docClass", "N/A")
        doc_no = doc.get("docNo", doc.get("number", "N/A"))
        doc_date = _format_date(doc.get("docDate", doc.get("date")))
        contact = doc.get("contactAccountDescription", doc.get("contact", "N/A"))
        amount = _format_currency(doc.get("total", doc.get("amount")))
        status = doc.get("status", "N/A")

        md += f"| {doc_class} | {doc_no} | {doc_date} | {contact} | {amount} | {status} |\n"

    return md


def _format_single_document_markdown(doc: Dict) -> str:
    """Format single document with details"""
    md = f"## Document Details\n\n"

    # Header info
    md += f"**Document:** {doc.get('docClass', 'N/A')} {doc.get('docNo', doc.get('number', 'N/A'))}\n\n"
    md += f"- **Date:** {_format_date(doc.get('docDate', doc.get('date')))}\n"
    md += f"- **Contact:** {doc.get('contactAccountDescription', 'N/A')}\n"
    md += f"- **Status:** {doc.get('status', 'N/A')}\n"
    md += f"- **Total:** {_format_currency(doc.get('total', doc.get('amount')))}\n"

    if doc.get("description"):
        md += f"- **Description:** {doc['description']}\n"

    # Line items if available
    lines = doc.get("lines", doc.get("items", []))
    if lines:
        md += f"\n### Line Items ({len(lines)} items)\n\n"
        md += "| Description | Quantity | Unit Price | Amount |\n"
        md += "|-------------|----------|------------|--------|\n"

        for line in lines:
            desc = line.get("description", "N/A")
            qty = line.get("quantity", "")
            price = _format_currency(line.get("unitPrice", line.get("price")))
            amount = _format_currency(line.get("amount", line.get("total")))
            md += f"| {desc} | {qty} | {price} | {amount} |\n"

    return md


def _format_contacts_markdown(items: List[Dict], total_count: int) -> str:
    """Format contact accounts as markdown table"""
    if not items:
        return "No contact accounts found."

    md = f"## Contact Accounts\n\n"
    md += f"Found **{len(items)}** contacts"
    if total_count > len(items):
        md += f" (showing first {len(items)} of {total_count} total)"
    md += "\n\n"

    # Create table
    md += "| Code | Name | Type | Country | Active |\n"
    md += "|------|------|------|---------|--------|\n"

    for contact in items:
        code = contact.get("code", "N/A")
        name = contact.get("description", contact.get("name", "N/A"))

        # Determine type
        contact_type = "Contact"
        if "supplier" in contact:
            contact_type = "Supplier"
        elif "customer" in contact:
            contact_type = "Customer"

        country = contact.get("countryCode", "N/A")

        # Check active status
        is_active = "✓"
        if "supplier" in contact:
            is_active = "✓" if contact["supplier"].get("isActive", True) else "✗"
        elif "customer" in contact:
            is_active = "✓" if contact["customer"].get("isActive", True) else "✗"

        md += f"| {code} | {name} | {contact_type} | {country} | {is_active} |\n"

    return md


def _format_single_contact_markdown(contact: Dict) -> str:
    """Format single contact account"""
    md = f"## Contact Account: {contact.get('description', contact.get('name', 'N/A'))}\n\n"

    md += f"- **Code:** {contact.get('code', 'N/A')}\n"
    md += f"- **Country:** {contact.get('countryCode', 'N/A')}\n"
    md += f"- **ID:** {contact.get('id', 'N/A')}\n"

    if "supplier" in contact:
        supplier = contact["supplier"]
        md += f"\n### Supplier Information\n\n"
        md += f"- **Active:** {'Yes' if supplier.get('isActive') else 'No'}\n"
        md += f"- **Currency:** {supplier.get('currency', 'N/A')}\n"

    if "customer" in contact:
        customer = contact["customer"]
        md += f"\n### Customer Information\n\n"
        md += f"- **Active:** {'Yes' if customer.get('isActive') else 'No'}\n"
        md += f"- **Currency:** {customer.get('currency', 'N/A')}\n"

    return md


def _format_projects_markdown(items: List[Dict], total_count: int) -> str:
    """Format projects as markdown table"""
    if not items:
        return "No projects found."

    md = f"## Projects\n\n"
    md += f"Found **{len(items)}** projects"
    if total_count > len(items):
        md += f" (showing first {len(items)} of {total_count} total)"
    md += "\n\n"

    md += "| Code | Description | Start Date | Status |\n"
    md += "|------|-------------|------------|--------|\n"

    for project in items:
        code = project.get("code", "N/A")
        desc = project.get("description", "N/A")
        start_date = _format_date(project.get("dateFrom"))
        status = "Active" if project.get("isActive", True) else "Inactive"

        md += f"| {code} | {desc} | {start_date} | {status} |\n"

    return md


def _format_generic_list_markdown(items: List[Dict], total_count: int, context: str) -> str:
    """Generic markdown formatter for lists"""
    if not items:
        return f"No {context} found."

    md = f"## {context.title()}\n\n"
    md += f"Found **{len(items)}** items"
    if total_count > len(items):
        md += f" (showing first {len(items)} of {total_count} total)"
    md += "\n\n"

    for i, item in enumerate(items, 1):
        md += f"### Item {i}\n\n"
        md += _format_dict_as_list(item)
        md += "\n"

    return md


def _format_generic_item_markdown(item: Dict, context: str) -> str:
    """Generic markdown formatter for single item"""
    md = f"## {context.title()}\n\n"
    md += _format_dict_as_list(item)
    return md


def _format_dict_as_list(d: Dict) -> str:
    """Format dictionary as markdown list"""
    md = ""
    for key, value in d.items():
        if isinstance(value, (dict, list)):
            continue  # Skip complex nested structures
        md += f"- **{key}:** {value}\n"
    return md


def _format_date(date_str: Any) -> str:
    """Format ISO date string to readable format"""
    if not date_str:
        return "N/A"

    try:
        if isinstance(date_str, str):
            # Try to parse ISO format
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    return str(date_str)


def _format_currency(amount: Any, currency: str = "£") -> str:
    """Format currency amount"""
    if amount is None:
        return "N/A"

    try:
        amount_float = float(amount)
        return f"{currency}{amount_float:,.2f}"
    except (ValueError, TypeError):
        return str(amount)
