"""Comprehensive API capability exploration for Phase 4

This script explores:
1. Write operations (POST) on additional endpoints
2. Special operations (posting, approval, batch)
3. Reporting and aggregation endpoints
4. Additional entity types
"""

import os
import asyncio
from typing import Dict, List

# Set credentials
os.environ['IPLICIT_API_KEY'] = 'qFLaFQiZt02yVZ65tNyjP2SFBym9G95IX9K5pp63vUeY3EAYP+YPwg'
os.environ['IPLICIT_USERNAME'] = 'Worralla'
os.environ['IPLICIT_DOMAIN'] = 'sandbox.lms123'

from src.session import IplicitSessionManager
from src.api_client import IplicitAPIClient


async def test_get_endpoint(client: IplicitAPIClient, endpoint: str) -> bool:
    """Test if an endpoint supports GET"""
    try:
        response = await client.make_request(endpoint, params={"maxRecordCount": 1})
        return True
    except Exception as e:
        return False


async def test_create_endpoint(client: IplicitAPIClient, endpoint: str, test_data: dict) -> str:
    """Test if an endpoint supports POST for creation"""
    try:
        response = await client.create_resource(endpoint, test_data)
        return "✓ Accepts POST (creates resources)"
    except Exception as e:
        error_msg = str(e).lower()
        if "400" in error_msg or "422" in error_msg or "validation" in error_msg:
            return "✓ Accepts POST (validation error - endpoint exists)"
        elif "404" in error_msg or "not found" in error_msg:
            return "✗ POST not supported (404)"
        elif "405" in error_msg or "not allowed" in error_msg:
            return "✗ POST not allowed (405)"
        else:
            return f"? Unclear ({str(e)[:30]})"


async def main():
    """Main exploration routine"""
    print("=" * 80)
    print("PHASE 4 API CAPABILITY EXPLORATION")
    print("=" * 80)

    session = IplicitSessionManager()
    client = IplicitAPIClient(session)

    # Test GET capabilities for new endpoints
    print("\n📋 Testing READ access to additional endpoints...")
    print("-" * 80)

    additional_endpoints = [
        ("journal", "Journal Entries"),
        ("account", "GL Accounts"),
        ("taxcode", "Tax Codes"),
        ("paymentterms", "Payment Terms"),
        ("currency", "Currencies"),
        ("bankaccount", "Bank Accounts"),
        ("department", "Departments"),
        ("costcentre", "Cost Centres"),
    ]

    available_reads = []
    for endpoint, description in additional_endpoints:
        print(f"\n{description} (/{endpoint})...", end=" ")
        can_read = await test_get_endpoint(client, endpoint)
        if can_read:
            print("✓ READ available")
            available_reads.append((endpoint, description))
        else:
            print("✗ Not available")

    # Test CREATE capabilities for known endpoints
    print("\n\n📝 Testing WRITE capabilities...")
    print("-" * 80)

    write_tests = [
        ("journal", "Journal Entry Creation", {
            "docDate": "2025-11-04",
            "description": "Test journal entry"
        }),
        ("department", "Department Creation", {
            "code": "TEST",
            "description": "Test Department"
        }),
        ("costcentre", "Cost Centre Creation", {
            "code": "TEST",
            "description": "Test Cost Centre"
        }),
    ]

    write_capabilities = []
    for endpoint, description, test_data in write_tests:
        print(f"\n{description} (/{endpoint})...", end=" ")
        result = await test_create_endpoint(client, endpoint, test_data)
        print(result)
        if "✓" in result:
            write_capabilities.append((endpoint, description))

    # Test special document operations
    print("\n\n🔄 Testing special document operations...")
    print("-" * 80)

    # Get a draft document to test operations on
    print("\nFinding a draft document...", end=" ")
    try:
        docs_response = await client.make_request("document", params={
            "status": "draft",
            "maxRecordCount": 1
        })
        items = docs_response if isinstance(docs_response, list) else docs_response.get("items", [])

        if items:
            doc_id = items[0].get("id")
            doc_no = items[0].get("docNo", "N/A")
            print(f"Found {doc_no} (ID: {doc_id})")

            # Test posting
            print(f"\nTesting POST /document/{doc_id}/post...", end=" ")
            try:
                # This will likely fail due to validation, but tells us if operation exists
                post_response = await client.update_resource(f"document/{doc_id}/post", {})
                print("✓ Posting endpoint exists")
            except Exception as e:
                error_msg = str(e).lower()
                if "400" in error_msg or "422" in error_msg or "validation" in error_msg:
                    print("✓ Posting endpoint exists (validation error expected)")
                else:
                    print(f"✗ Posting not available ({str(e)[:40]})")

            # Test approval
            print(f"Testing POST /document/{doc_id}/approve...", end=" ")
            try:
                approve_response = await client.update_resource(f"document/{doc_id}/approve", {})
                print("✓ Approval endpoint exists")
            except Exception as e:
                error_msg = str(e).lower()
                if "400" in error_msg or "422" in error_msg or "validation" in error_msg:
                    print("✓ Approval endpoint exists (validation error expected)")
                else:
                    print(f"✗ Approval not available ({str(e)[:40]})")

        else:
            print("No draft documents found (skipping workflow tests)")

    except Exception as e:
        print(f"Error: {str(e)[:50]}")

    # Summary and recommendations
    print("\n\n" + "=" * 80)
    print("PHASE 4 RECOMMENDATIONS")
    print("=" * 80)

    print("\n🎯 HIGH PRIORITY - New Tools to Implement:")
    print("\n1. Journal Entry Management")
    if ("journal", "Journal Entries") in available_reads:
        print("   ✓ search_journals - Search journal entries")
        print("   ✓ get_journal - Get journal entry details")
    if ("journal", "Journal Entry Creation") in write_capabilities:
        print("   ✓ create_journal - Create journal entries")

    print("\n2. Document Workflows")
    print("   ✓ post_document - Post draft documents to finalize them")
    print("   ✓ approve_document - Approve documents for posting")
    print("   ✓ reverse_document - Reverse posted documents")

    print("\n3. Batch Operations")
    print("   ✓ create_batch_payment - Create batch payments for multiple invoices")
    print("   ✓ search_batch_payments - Search batch payment records")

    print("\n4. Department & Cost Centre Management")
    if ("department", "Departments") in available_reads:
        print("   ✓ search_departments - Search departments")
        print("   ✓ get_department - Get department details")
    if ("costcentre", "Cost Centres") in available_reads:
        print("   ✓ search_cost_centres - Search cost centres")
        print("   ✓ get_cost_centre - Get cost centre details")

    print("\n📊 MEDIUM PRIORITY - Configuration & Reference Data:")
    if ("account", "GL Accounts") in available_reads:
        print("   ✓ search_gl_accounts - Search general ledger accounts")
    if ("taxcode", "Tax Codes") in available_reads:
        print("   ✓ search_tax_codes - Search tax codes and rates")
    if ("paymentterms", "Payment Terms") in available_reads:
        print("   ✓ search_payment_terms - Search payment terms")
    if ("bankaccount", "Bank Accounts") in available_reads:
        print("   ✓ search_bank_accounts - Search bank accounts")

    print("\n🚀 NICE TO HAVE - Advanced Features:")
    print("   ✓ bulk_update_documents - Update multiple documents at once")
    print("   ✓ document_validation - Validate documents before posting")
    print("   ✓ advanced_search - Cross-entity search with aggregations")

    print("\n" + "=" * 80)
    print(f"Total Available READ Endpoints: {len(available_reads)}")
    print(f"Total Available WRITE Endpoints: {len(write_capabilities)}")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
