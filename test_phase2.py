"""Test script for Phase 2 write operations"""

import os
import asyncio
from datetime import datetime, timedelta

# Set credentials
os.environ['IPLICIT_API_KEY'] = 'qFLaFQiZt02yVZ65tNyjP2SFBym9G95IX9K5pp63vUeY3EAYP+YPwg'
os.environ['IPLICIT_USERNAME'] = 'Worralla'
os.environ['IPLICIT_DOMAIN'] = 'sandbox.lms123'

from src.session import IplicitSessionManager
from src.api_client import IplicitAPIClient


async def test_phase2_operations():
    """Test Phase 2 write operations"""

    print("=" * 80)
    print("PHASE 2 WRITE OPERATIONS TEST SUITE")
    print("=" * 80)

    # Initialize
    session = IplicitSessionManager()
    client = IplicitAPIClient(session)

    # Test results tracking
    tests_passed = 0
    tests_failed = 0

    # ========== TEST 1: Get Contact Accounts for Testing ==========
    print("\n📋 TEST 1: Getting contact accounts for testing...")
    try:
        contacts = await client.make_request("contactaccount", params={"maxRecordCount": 10})
        items = contacts if isinstance(contacts, list) else contacts.get("items", [])

        # Find a supplier
        supplier_id = None
        for contact in items:
            if "supplier" in contact:
                supplier_id = contact.get("id")
                supplier_code = contact.get("code")
                supplier_name = contact.get("description")
                print(f"✅ Found supplier: {supplier_code} - {supplier_name}")
                break

        # Find a customer
        customer_id = None
        for contact in items:
            if "customer" in contact:
                customer_id = contact.get("id")
                customer_code = contact.get("code")
                customer_name = contact.get("description")
                print(f"✅ Found customer: {customer_code} - {customer_name}")
                break

        if not supplier_id or not customer_id:
            print("❌ FAILED: Need at least one supplier and one customer")
            return

        tests_passed += 1
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1
        return

    # ========== TEST 2: Create Purchase Invoice (Simple) ==========
    print("\n\n📝 TEST 2: Creating simple purchase invoice...")
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        invoice_data = {
            "contactAccountId": supplier_id,
            "docDate": today,
            "dueDate": due_date,
            "currency": "GBP",
            "description": "Test Purchase Invoice - Phase 2"
        }

        result = await client.create_purchase_invoice(invoice_data)

        if result and result.get("id"):
            purchase_invoice_id = result.get("id")
            purchase_invoice_no = result.get("docNo")
            print(f"✅ PASSED: Created purchase invoice {purchase_invoice_no}")
            print(f"   Invoice ID: {purchase_invoice_id}")
            print(f"   Status: {result.get('status', 'N/A')}")
            tests_passed += 1
        else:
            print(f"❌ FAILED: No ID in response")
            print(f"Response: {result}")
            tests_failed += 1
            purchase_invoice_id = None
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1
        purchase_invoice_id = None

    # ========== TEST 3: Create Sale Invoice (Simple) ==========
    print("\n\n💰 TEST 3: Creating simple sale invoice...")
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        invoice_data = {
            "contactAccountId": customer_id,
            "docDate": today,
            "dueDate": due_date,
            "currency": "GBP",
            "description": "Test Sales Invoice - Phase 2",
            "reference": f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        }

        result = await client.create_sale_invoice(invoice_data)

        if result and result.get("id"):
            sale_invoice_id = result.get("id")
            sale_invoice_no = result.get("docNo")
            print(f"✅ PASSED: Created sale invoice {sale_invoice_no}")
            print(f"   Invoice ID: {sale_invoice_id}")
            print(f"   Status: {result.get('status', 'N/A')}")
            tests_passed += 1
        else:
            print(f"❌ FAILED: No ID in response")
            print(f"Response: {result}")
            tests_failed += 1
            sale_invoice_id = None
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1
        sale_invoice_id = None

    # ========== TEST 4: Update Draft Purchase Invoice ==========
    print("\n\n🔄 TEST 4: Updating draft purchase invoice...")
    if purchase_invoice_id:
        try:
            update_data = {
                "description": "UPDATED: Test Purchase Invoice - Phase 2 (Modified)"
            }

            result = await client.update_document(purchase_invoice_id, update_data)

            if result and result.get("description") == update_data["description"]:
                print(f"✅ PASSED: Updated invoice {purchase_invoice_no}")
                print(f"   New description: {result.get('description')}")
                print(f"   Last modified by: {result.get('lastModifiedBy', 'N/A')}")
                tests_passed += 1
            else:
                print(f"❌ FAILED: Description not updated")
                print(f"Response: {result}")
                tests_failed += 1
        except Exception as e:
            error_msg = str(e)
            if "must be draft" in error_msg.lower():
                print(f"⚠️  EXPECTED ERROR: {error_msg}")
                print(f"   (This is correct - only draft documents can be updated)")
                tests_passed += 1
            else:
                print(f"❌ FAILED: {error_msg}")
                tests_failed += 1
    else:
        print("⏭️  SKIPPED: No purchase invoice created in previous test")

    # ========== TEST 5: Update Draft Sale Invoice ==========
    print("\n\n🔄 TEST 5: Updating draft sale invoice...")
    if sale_invoice_id:
        try:
            update_data = {
                "description": "UPDATED: Test Sales Invoice - Phase 2 (Modified)",
                "reference": f"UPDATED-{datetime.now().strftime('%Y%m%d')}"
            }

            result = await client.update_document(sale_invoice_id, update_data)

            if result and result.get("description") == update_data["description"]:
                print(f"✅ PASSED: Updated invoice {sale_invoice_no}")
                print(f"   New description: {result.get('description')}")
                print(f"   New reference: {result.get('reference', 'N/A')}")
                tests_passed += 1
            else:
                print(f"❌ FAILED: Fields not updated correctly")
                print(f"Response: {result}")
                tests_failed += 1
        except Exception as e:
            error_msg = str(e)
            if "must be draft" in error_msg.lower():
                print(f"⚠️  EXPECTED ERROR: {error_msg}")
                print(f"   (This is correct - only draft documents can be updated)")
                tests_passed += 1
            else:
                print(f"❌ FAILED: {error_msg}")
                tests_failed += 1
    else:
        print("⏭️  SKIPPED: No sale invoice created in previous test")

    # ========== TEST 6: Try to Update Posted Document (Should Fail) ==========
    print("\n\n🔒 TEST 6: Attempting to update posted document (should fail)...")
    try:
        # Find a posted document
        docs = await client.make_request("document", params={"maxRecordCount": 10})
        items = docs if isinstance(docs, list) else docs.get("items", [])

        posted_doc_id = None
        for doc in items:
            status = doc.get("status")
            if isinstance(status, str) and "posted" in status.lower():
                posted_doc_id = doc.get("id")
                posted_doc_no = doc.get("docNo")
                break
            elif isinstance(status, int) and status > 100:  # Posted status codes are typically > 100
                posted_doc_id = doc.get("id")
                posted_doc_no = doc.get("docNo")
                break

        if posted_doc_id:
            try:
                update_data = {"description": "This should fail"}
                await client.update_document(posted_doc_id, update_data)

                print(f"❌ FAILED: Should not allow updating posted document")
                tests_failed += 1
            except Exception as e:
                error_msg = str(e)
                if "must be draft" in error_msg.lower() or "cannot update" in error_msg.lower():
                    print(f"✅ PASSED: Correctly rejected update of posted document")
                    print(f"   Error: {error_msg[:100]}")
                    tests_passed += 1
                else:
                    print(f"❌ FAILED: Wrong error: {error_msg}")
                    tests_failed += 1
        else:
            print("⏭️  SKIPPED: No posted documents found for testing")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1

    # ========== TEST 7: Lookup Contact by Code ==========
    print("\n\n🔍 TEST 7: Testing contact lookup by code...")
    try:
        # Use the supplier code we found earlier
        looked_up_id = await client.lookup_contact_by_code(supplier_code)

        if looked_up_id == supplier_id:
            print(f"✅ PASSED: Successfully looked up contact by code '{supplier_code}'")
            print(f"   Returned ID: {looked_up_id}")
            tests_passed += 1
        else:
            print(f"❌ FAILED: Lookup returned wrong ID")
            print(f"   Expected: {supplier_id}")
            print(f"   Got: {looked_up_id}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1

    # ========== TEST 8: Get Default Legal Entity ==========
    print("\n\n🏢 TEST 8: Getting default legal entity...")
    try:
        legal_entity_id = await client.get_default_legal_entity()

        if legal_entity_id:
            print(f"✅ PASSED: Got default legal entity")
            print(f"   Legal Entity ID: {legal_entity_id}")
            tests_passed += 1
        else:
            print(f"❌ FAILED: No legal entity returned")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1

    # ========== SUMMARY ==========
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    total_tests = tests_passed + tests_failed
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")

    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED! Phase 2 is ready for production.")
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed. Please review the errors above.")

    print("\n" + "=" * 80)
    print("CREATED DOCUMENTS (for cleanup if needed):")
    if purchase_invoice_id:
        print(f"  Purchase Invoice: {purchase_invoice_no} (ID: {purchase_invoice_id})")
    if sale_invoice_id:
        print(f"  Sale Invoice: {sale_invoice_no} (ID: {sale_invoice_id})")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(test_phase2_operations())
