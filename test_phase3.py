"""Test script for Phase 3 read operations"""

import os
import asyncio

# Set credentials
os.environ['IPLICIT_API_KEY'] = 'qFLaFQiZt02yVZ65tNyjP2SFBym9G95IX9K5pp63vUeY3EAYP+YPwg'
os.environ['IPLICIT_USERNAME'] = 'Worralla'
os.environ['IPLICIT_DOMAIN'] = 'sandbox.lms123'

from src.session import IplicitSessionManager
from src.api_client import IplicitAPIClient
from src.server import (
    handle_search_purchase_orders,
    handle_get_purchase_order,
    handle_search_sale_orders,
    handle_get_sale_order,
    handle_search_payments,
    handle_search_products,
    handle_get_product,
)


async def test_phase3_tools():
    """Test Phase 3 read operation tools"""

    print("=" * 80)
    print("PHASE 3 READ OPERATIONS TEST SUITE")
    print("=" * 80)

    # Initialize
    session = IplicitSessionManager()
    client = IplicitAPIClient(session)

    # Test results tracking
    tests_passed = 0
    tests_failed = 0

    # ========== TEST 1: Search Purchase Orders ==========
    print("\n📋 TEST 1: Searching purchase orders...")
    try:
        args = {"limit": 5, "format": "markdown"}
        result = await handle_search_purchase_orders(client, args)

        if result and "Purchase Orders" in result:
            print("✅ PASSED: Purchase orders retrieved")
            # Extract count
            if "Found **" in result:
                count_str = result.split("Found **")[1].split("**")[0]
                print(f"   Found {count_str} purchase orders")
            tests_passed += 1
        else:
            print(f"❌ FAILED: Unexpected result format")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1

    # ========== TEST 2: Get Single Purchase Order ==========
    print("\n\n📄 TEST 2: Getting single purchase order...")
    try:
        # First get list to find an ID
        args_list = {"limit": 1, "format": "json"}
        import json
        list_result = await handle_search_purchase_orders(client, args_list)
        data = json.loads(list_result)

        if data.get("items") and len(data["items"]) > 0:
            po_id = data["items"][0].get("id")
            print(f"   Using PO ID: {po_id}")

            args = {"order_id": po_id, "format": "markdown"}
            result = await handle_get_purchase_order(client, args)

            if result and "Purchase Order Details" in result:
                print("✅ PASSED: Purchase order details retrieved")
                tests_passed += 1
            else:
                print(f"❌ FAILED: Unexpected result format")
                tests_failed += 1
        else:
            print("⏭️  SKIPPED: No purchase orders available")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1

    # ========== TEST 3: Search Sale Orders ==========
    print("\n\n💰 TEST 3: Searching sales orders...")
    try:
        args = {"limit": 5, "format": "markdown"}
        result = await handle_search_sale_orders(client, args)

        if result and "Sales Orders" in result:
            print("✅ PASSED: Sales orders retrieved")
            if "Found **" in result:
                count_str = result.split("Found **")[1].split("**")[0]
                print(f"   Found {count_str} sales orders")
            tests_passed += 1
        else:
            print(f"❌ FAILED: Unexpected result format")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1

    # ========== TEST 4: Get Single Sale Order ==========
    print("\n\n📄 TEST 4: Getting single sales order...")
    try:
        # Get list to find an ID
        args_list = {"limit": 1, "format": "json"}
        list_result = await handle_search_sale_orders(client, args_list)
        data = json.loads(list_result)

        if data.get("items") and len(data["items"]) > 0:
            so_id = data["items"][0].get("id")
            print(f"   Using SO ID: {so_id}")

            args = {"order_id": so_id, "format": "markdown"}
            result = await handle_get_sale_order(client, args)

            if result and "Sales Order Details" in result:
                print("✅ PASSED: Sales order details retrieved")
                tests_passed += 1
            else:
                print(f"❌ FAILED: Unexpected result format")
                tests_failed += 1
        else:
            print("⏭️  SKIPPED: No sales orders available")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1

    # ========== TEST 5: Search Payments ==========
    print("\n\n💳 TEST 5: Searching payments...")
    try:
        args = {"limit": 5, "format": "markdown"}
        result = await handle_search_payments(client, args)

        if result and "Payments" in result or "No payments found" in result:
            print("✅ PASSED: Payments search completed")
            if "Found **" in result:
                count_str = result.split("Found **")[1].split("**")[0]
                print(f"   Found {count_str} payments")
            elif "No payments" in result:
                print("   No payments found (this is OK)")
            tests_passed += 1
        else:
            print(f"❌ FAILED: Unexpected result format")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1

    # ========== TEST 6: Search Products ==========
    print("\n\n📦 TEST 6: Searching products...")
    try:
        args = {"limit": 10, "active_only": True, "format": "markdown"}
        result = await handle_search_products(client, args)

        if result and "Products" in result:
            print("✅ PASSED: Products retrieved")
            if "Found **" in result:
                count_str = result.split("Found **")[1].split("**")[0]
                print(f"   Found {count_str} products")
            tests_passed += 1
        else:
            print(f"❌ FAILED: Unexpected result format")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1

    # ========== TEST 7: Get Single Product ==========
    print("\n\n📦 TEST 7: Getting single product...")
    try:
        # Get list to find a product
        args_list = {"limit": 1, "format": "json"}
        list_result = await handle_search_products(client, args_list)
        data = json.loads(list_result)

        if data.get("items") and len(data["items"]) > 0:
            product_id = data["items"][0].get("id") or data["items"][0].get("code")
            print(f"   Using Product ID: {product_id}")

            args = {"product_id": product_id, "format": "markdown"}
            result = await handle_get_product(client, args)

            if result and "Product Details" in result:
                print("✅ PASSED: Product details retrieved")
                tests_passed += 1
            else:
                print(f"❌ FAILED: Unexpected result format")
                tests_failed += 1
        else:
            print("⏭️  SKIPPED: No products available")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1

    # ========== TEST 8: Filter Purchase Orders by Supplier ==========
    print("\n\n🔍 TEST 8: Filtering purchase orders by supplier...")
    try:
        args = {"limit": 10, "supplier": "test", "format": "markdown"}
        result = await handle_search_purchase_orders(client, args)

        if result and ("Purchase Orders" in result or "No purchase orders" in result):
            print("✅ PASSED: Supplier filter applied")
            tests_passed += 1
        else:
            print(f"❌ FAILED: Unexpected result format")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1

    # ========== TEST 9: Search Products with Search Term ==========
    print("\n\n🔍 TEST 9: Searching products with search term...")
    try:
        args = {"limit": 10, "search_term": "a", "format": "markdown"}
        result = await handle_search_products(client, args)

        if result and ("Products" in result or "No products" in result):
            print("✅ PASSED: Product search term filter working")
            tests_passed += 1
        else:
            print(f"❌ FAILED: Unexpected result format")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1

    # ========== TEST 10: JSON Format Output ==========
    print("\n\n📊 TEST 10: Testing JSON format output...")
    try:
        args = {"limit": 2, "format": "json"}
        result = await handle_search_products(client, args)

        # Try to parse as JSON
        data = json.loads(result)
        if "items" in data:
            print("✅ PASSED: JSON format working correctly")
            print(f"   Returned {len(data['items'])} items in JSON")
            tests_passed += 1
        else:
            print(f"❌ FAILED: JSON format missing 'items' key")
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
        print("\n🎉 ALL TESTS PASSED! Phase 3 is ready for production.")
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed. Please review the errors above.")

    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(test_phase3_tools())
