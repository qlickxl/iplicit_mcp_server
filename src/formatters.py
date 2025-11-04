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


# ===== PHASE 2: WRITE OPERATIONS FORMATTERS =====


def format_created_invoice(invoice: Dict, format_type: str) -> str:
    """
    Format a newly created invoice response

    Args:
        invoice: Created invoice data from API
        format_type: "json" or "markdown"

    Returns:
        Formatted string
    """
    if format_type == "json":
        return json.dumps(invoice, indent=2, default=str)

    # Markdown formatting
    md = "## ✅ Invoice Created Successfully\n\n"

    # Key info
    doc_class = invoice.get("docClass", "Invoice")
    doc_no = invoice.get("docNo", "N/A")
    doc_id = invoice.get("id", "N/A")

    md += f"**{doc_class}:** {doc_no}\n\n"

    # Details
    md += "### Details\n\n"
    md += f"- **Document ID:** `{doc_id}`\n"
    md += f"- **Document Number:** {doc_no}\n"
    md += f"- **Date:** {_format_date(invoice.get('docDate'))}\n"
    md += f"- **Due Date:** {_format_date(invoice.get('dueDate'))}\n"
    md += f"- **Contact:** {invoice.get('contactAccountDescription', 'N/A')}\n"
    md += f"- **Currency:** {invoice.get('currency', 'N/A')}\n"
    md += f"- **Status:** {invoice.get('status', 'draft')}\n"

    if invoice.get("description"):
        md += f"- **Description:** {invoice['description']}\n"

    # Amounts
    net = invoice.get("netAmount", invoice.get("netCurrencyAmount"))
    tax = invoice.get("taxAmount", invoice.get("taxCurrencyAmount"))
    gross = invoice.get("grossAmount", invoice.get("grossCurrencyAmount"))

    if net is not None or tax is not None or gross is not None:
        md += "\n### Amounts\n\n"
        if net is not None:
            md += f"- **Net:** {_format_currency(net)}\n"
        if tax is not None:
            md += f"- **Tax:** {_format_currency(tax)}\n"
        if gross is not None:
            md += f"- **Gross Total:** {_format_currency(gross)}\n"

    # Line items
    lines = invoice.get("details", invoice.get("lines", []))
    if lines:
        md += f"\n### Line Items ({len(lines)})\n\n"
        md += "| Description | Quantity | Unit Price | Amount |\n"
        md += "|-------------|----------|------------|--------|\n"

        for line in lines:
            desc = line.get("description", "N/A")
            qty = line.get("quantity", 1)
            price = _format_currency(line.get("netCurrencyUnitPrice", line.get("unitPrice")))
            line_net = line.get("netAmount", line.get("netCurrencyAmount"))
            amount = _format_currency(line_net)
            md += f"| {desc} | {qty} | {price} | {amount} |\n"

    # Next steps
    md += "\n### Next Steps\n\n"
    if invoice.get("status", "").lower() == "draft":
        md += "This invoice is in **draft** status. You can:\n"
        md += "- Update it using the `update_document` tool\n"
        md += "- Post it to finalize the transaction (when posting feature is available)\n"
    else:
        md += f"Invoice status: **{invoice.get('status')}**\n"

    return md


def format_updated_document(document: Dict, format_type: str) -> str:
    """
    Format an updated document response

    Args:
        document: Updated document data from API
        format_type: "json" or "markdown"

    Returns:
        Formatted string
    """
    if format_type == "json":
        return json.dumps(document, indent=2, default=str)

    # Markdown formatting
    md = "## ✅ Document Updated Successfully\n\n"

    # Key info
    doc_class = document.get("docClass", "Document")
    doc_no = document.get("docNo", document.get("number", "N/A"))
    doc_id = document.get("id", "N/A")

    md += f"**{doc_class}:** {doc_no}\n\n"

    # Details
    md += "### Updated Details\n\n"
    md += f"- **Document ID:** `{doc_id}`\n"
    md += f"- **Document Number:** {doc_no}\n"
    md += f"- **Date:** {_format_date(document.get('docDate'))}\n"
    md += f"- **Due Date:** {_format_date(document.get('dueDate'))}\n"
    md += f"- **Contact:** {document.get('contactAccountDescription', 'N/A')}\n"
    md += f"- **Status:** {document.get('status', 'N/A')}\n"

    if document.get("description"):
        md += f"- **Description:** {document['description']}\n"

    if document.get("theirDocNo"):
        md += f"- **Their Reference:** {document['theirDocNo']}\n"

    # Modification tracking
    if document.get("lastModified"):
        md += f"- **Last Modified:** {_format_date(document.get('lastModified'))}\n"
    if document.get("lastModifiedBy"):
        md += f"- **Modified By:** {document.get('lastModifiedBy')}\n"

    # Amounts
    net = document.get("netAmount", document.get("netCurrencyAmount"))
    tax = document.get("taxAmount", document.get("taxCurrencyAmount"))
    gross = document.get("grossAmount", document.get("grossCurrencyAmount"))

    if net is not None or tax is not None or gross is not None:
        md += "\n### Amounts\n\n"
        if net is not None:
            md += f"- **Net:** {_format_currency(net)}\n"
        if tax is not None:
            md += f"- **Tax:** {_format_currency(tax)}\n"
        if gross is not None:
            md += f"- **Gross Total:** {_format_currency(gross)}\n"

    # Line items if present
    lines = document.get("details", document.get("lines", []))
    if lines:
        md += f"\n### Line Items ({len(lines)})\n\n"
        md += "| Description | Quantity | Unit Price | Amount |\n"
        md += "|-------------|----------|------------|--------|\n"

        for line in lines:
            desc = line.get("description", "N/A")
            qty = line.get("quantity", 1)
            price = _format_currency(line.get("netCurrencyUnitPrice", line.get("unitPrice")))
            line_net = line.get("netAmount", line.get("netCurrencyAmount"))
            amount = _format_currency(line_net)
            md += f"| {desc} | {qty} | {price} | {amount} |\n"

    return md


# ===== PHASE 3: ADDITIONAL RESOURCE FORMATTERS =====


def format_purchase_orders(items: List[Dict], total_count: int) -> str:
    """Format purchase orders list as markdown table"""
    if not items:
        return "No purchase orders found."

    md = f"## Purchase Orders\n\n"
    md += f"Found **{len(items)}** purchase orders"
    if total_count > len(items):
        md += f" (showing first {len(items)} of {total_count} total)"
    md += "\n\n"

    # Create table
    md += "| PO Number | Date | Supplier | Amount | Status |\n"
    md += "|-----------|------|----------|--------|--------|\n"

    for order in items:
        po_no = order.get("docNo", order.get("number", "N/A"))
        po_date = _format_date(order.get("docDate", order.get("date")))
        supplier = order.get("contactAccountDescription", order.get("supplier", "N/A"))
        amount = _format_currency(order.get("grossAmount", order.get("total")))
        status = order.get("status", "N/A")

        md += f"| {po_no} | {po_date} | {supplier} | {amount} | {status} |\n"

    return md


def format_single_purchase_order(order: Dict) -> str:
    """Format single purchase order with details"""
    md = f"## Purchase Order Details\n\n"

    po_no = order.get("docNo", order.get("number", "N/A"))
    md += f"**PO Number:** {po_no}\n\n"

    # Header info
    md += f"- **Date:** {_format_date(order.get('docDate', order.get('date')))}\n"
    md += f"- **Supplier:** {order.get('contactAccountDescription', 'N/A')}\n"
    md += f"- **Status:** {order.get('status', 'N/A')}\n"
    md += f"- **Currency:** {order.get('currency', 'N/A')}\n"

    if order.get("description"):
        md += f"- **Description:** {order['description']}\n"

    # Amounts
    net = order.get("netAmount", order.get("netCurrencyAmount"))
    tax = order.get("taxAmount", order.get("taxCurrencyAmount"))
    gross = order.get("grossAmount", order.get("grossCurrencyAmount"))

    if net is not None or tax is not None or gross is not None:
        md += "\n### Amounts\n\n"
        if net is not None:
            md += f"- **Net:** {_format_currency(net)}\n"
        if tax is not None:
            md += f"- **Tax:** {_format_currency(tax)}\n"
        if gross is not None:
            md += f"- **Gross Total:** {_format_currency(gross)}\n"

    # Line items
    lines = order.get("details", order.get("lines", []))
    if lines:
        md += f"\n### Line Items ({len(lines)})\n\n"
        md += "| Description | Quantity | Unit Price | Amount |\n"
        md += "|-------------|----------|------------|--------|\n"

        for line in lines:
            desc = line.get("description", "N/A")
            qty = line.get("quantity", "")
            price = _format_currency(line.get("netCurrencyUnitPrice", line.get("unitPrice")))
            line_amount = line.get("netAmount", line.get("netCurrencyAmount"))
            amount = _format_currency(line_amount)
            md += f"| {desc} | {qty} | {price} | {amount} |\n"

    return md


def format_sale_orders(items: List[Dict], total_count: int) -> str:
    """Format sales orders list as markdown table"""
    if not items:
        return "No sales orders found."

    md = f"## Sales Orders\n\n"
    md += f"Found **{len(items)}** sales orders"
    if total_count > len(items):
        md += f" (showing first {len(items)} of {total_count} total)"
    md += "\n\n"

    # Create table
    md += "| SO Number | Date | Customer | Amount | Status |\n"
    md += "|-----------|------|----------|--------|--------|\n"

    for order in items:
        so_no = order.get("docNo", order.get("number", "N/A"))
        so_date = _format_date(order.get("docDate", order.get("date")))
        customer = order.get("contactAccountDescription", order.get("customer", "N/A"))
        amount = _format_currency(order.get("grossAmount", order.get("total")))
        status = order.get("status", "N/A")

        md += f"| {so_no} | {so_date} | {customer} | {amount} | {status} |\n"

    return md


def format_single_sale_order(order: Dict) -> str:
    """Format single sales order with details"""
    md = f"## Sales Order Details\n\n"

    so_no = order.get("docNo", order.get("number", "N/A"))
    md += f"**SO Number:** {so_no}\n\n"

    # Header info
    md += f"- **Date:** {_format_date(order.get('docDate', order.get('date')))}\n"
    md += f"- **Customer:** {order.get('contactAccountDescription', 'N/A')}\n"
    md += f"- **Status:** {order.get('status', 'N/A')}\n"
    md += f"- **Currency:** {order.get('currency', 'N/A')}\n"

    if order.get("description"):
        md += f"- **Description:** {order['description']}\n"

    # Amounts
    net = order.get("netAmount", order.get("netCurrencyAmount"))
    tax = order.get("taxAmount", order.get("taxCurrencyAmount"))
    gross = order.get("grossAmount", order.get("grossCurrencyAmount"))

    if net is not None or tax is not None or gross is not None:
        md += "\n### Amounts\n\n"
        if net is not None:
            md += f"- **Net:** {_format_currency(net)}\n"
        if tax is not None:
            md += f"- **Tax:** {_format_currency(tax)}\n"
        if gross is not None:
            md += f"- **Gross Total:** {_format_currency(gross)}\n"

    # Line items
    lines = order.get("details", order.get("lines", []))
    if lines:
        md += f"\n### Line Items ({len(lines)})\n\n"
        md += "| Description | Quantity | Unit Price | Amount |\n"
        md += "|-------------|----------|------------|--------|\n"

        for line in lines:
            desc = line.get("description", "N/A")
            qty = line.get("quantity", "")
            price = _format_currency(line.get("netCurrencyUnitPrice", line.get("unitPrice")))
            line_amount = line.get("netAmount", line.get("netCurrencyAmount"))
            amount = _format_currency(line_amount)
            md += f"| {desc} | {qty} | {price} | {amount} |\n"

    return md


def format_payments(items: List[Dict], total_count: int) -> str:
    """Format payments list as markdown table"""
    if not items:
        return "No payments found."

    md = f"## Payments\n\n"
    md += f"Found **{len(items)}** payments"
    if total_count > len(items):
        md += f" (showing first {len(items)} of {total_count} total)"
    md += "\n\n"

    # Create table
    md += "| Date | Contact | Amount | Type | Reference |\n"
    md += "|------|---------|--------|------|----------|\n"

    for payment in items:
        pay_date = _format_date(payment.get("paymentDate", payment.get("date")))
        contact = payment.get("contactAccountDescription", payment.get("contact", "N/A"))
        amount = _format_currency(payment.get("amount", payment.get("grossAmount")))
        pay_type = payment.get("paymentType", payment.get("type", "N/A"))
        reference = payment.get("reference", payment.get("docNo", "N/A"))

        md += f"| {pay_date} | {contact} | {amount} | {pay_type} | {reference} |\n"

    return md


def format_products(items: List[Dict], total_count: int) -> str:
    """Format products list as markdown table"""
    if not items:
        return "No products found."

    md = f"## Products\n\n"
    md += f"Found **{len(items)}** products"
    if total_count > len(items):
        md += f" (showing first {len(items)} of {total_count} total)"
    md += "\n\n"

    # Create table
    md += "| Code | Description | Price | Active |\n"
    md += "|------|-------------|-------|--------|\n"

    for product in items:
        code = product.get("code", "N/A")
        desc = product.get("description", product.get("name", "N/A"))
        price = _format_currency(product.get("salePrice", product.get("price")))
        is_active = "✓" if product.get("isActive", True) else "✗"

        md += f"| {code} | {desc} | {price} | {is_active} |\n"

    return md


def format_single_product(product: Dict) -> str:
    """Format single product with details"""
    md = f"## Product Details\n\n"

    code = product.get("code", "N/A")
    md += f"**Product Code:** {code}\n\n"

    # Basic info
    md += f"- **Description:** {product.get('description', product.get('name', 'N/A'))}\n"
    md += f"- **Active:** {'Yes' if product.get('isActive', True) else 'No'}\n"

    if product.get("productType"):
        md += f"- **Type:** {product['productType']}\n"

    # Pricing
    sale_price = product.get("salePrice")
    purchase_price = product.get("purchasePrice")

    if sale_price is not None or purchase_price is not None:
        md += "\n### Pricing\n\n"
        if sale_price is not None:
            md += f"- **Sale Price:** {_format_currency(sale_price)}\n"
        if purchase_price is not None:
            md += f"- **Purchase Price:** {_format_currency(purchase_price)}\n"

    # Stock
    stock_level = product.get("stockLevel", product.get("quantityOnHand"))
    if stock_level is not None:
        md += "\n### Stock\n\n"
        md += f"- **On Hand:** {stock_level}\n"

        reorder_level = product.get("reorderLevel")
        if reorder_level is not None:
            md += f"- **Reorder Level:** {reorder_level}\n"

    return md
