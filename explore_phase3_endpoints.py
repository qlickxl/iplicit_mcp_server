"""Explore available endpoints for Phase 3"""

import os
import asyncio
import httpx

# Set credentials
os.environ['IPLICIT_API_KEY'] = 'qFLaFQiZt02yVZ65tNyjP2SFBym9G95IX9K5pp63vUeY3EAYP+YPwg'
os.environ['IPLICIT_USERNAME'] = 'Worralla'
os.environ['IPLICIT_DOMAIN'] = 'sandbox.lms123'

from src.session import IplicitSessionManager


async def explore_endpoints():
    """Explore potential Phase 3 endpoints"""

    print("=" * 80)
    print("PHASE 3 API ENDPOINT EXPLORATION")
    print("=" * 80)

    session = IplicitSessionManager()
    token = await session.get_valid_token()
    domain = session.get_domain()

    base_url = 'https://api.iplicit.com/api'
    headers = {
        'Domain': domain,
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient(timeout=30.0) as client:

        # Test various resource endpoints
        endpoints_to_test = [
            # Financial entities
            ('GET', '/glaccount', {}, 'GL Accounts'),
            ('GET', '/account', {}, 'Accounts (alternate)'),
            ('GET', '/taxcode', {}, 'Tax Codes'),
            ('GET', '/currency', {}, 'Currencies'),
            ('GET', '/paymentterms', {}, 'Payment Terms'),
            ('GET', '/legalentity', {}, 'Legal Entities'),

            # Document-related
            ('GET', '/doctype', {}, 'Document Types'),
            ('GET', '/docserie', {}, 'Document Series'),
            ('GET', '/purchaseorder', {}, 'Purchase Orders'),
            ('GET', '/saleorder', {}, 'Sales Orders'),
            ('GET', '/journal', {}, 'Journals'),
            ('GET', '/payment', {}, 'Payments'),
            ('GET', '/batchpayment', {}, 'Batch Payments'),

            # Products and inventory
            ('GET', '/product', {}, 'Products'),
            ('GET', '/stock', {}, 'Stock'),
            ('GET', '/warehouse', {}, 'Warehouses'),
            ('GET', '/uom', {}, 'Units of Measure'),

            # Organizational
            ('GET', '/department', {}, 'Departments'),
            ('GET', '/costcentre', {}, 'Cost Centres'),
            ('GET', '/location', {}, 'Locations'),

            # People
            ('GET', '/employee', {}, 'Employees'),
            ('GET', '/user', {}, 'Users'),

            # Financial reporting/period
            ('GET', '/period', {}, 'Accounting Periods'),
            ('GET', '/fiscalyear', {}, 'Fiscal Years'),

            # Reporting (various patterns)
            ('GET', '/report', {}, 'Reports'),
            ('GET', '/trialbalance', {'periodId': ''}, 'Trial Balance'),
            ('GET', '/balancesheet', {}, 'Balance Sheet'),
            ('GET', '/profitandloss', {}, 'Profit & Loss'),
            ('GET', '/cashflow', {}, 'Cash Flow'),

            # Bank and cash management
            ('GET', '/bankaccount', {}, 'Bank Accounts'),
            ('GET', '/banktransaction', {}, 'Bank Transactions'),
            ('GET', '/bankreconciliation', {}, 'Bank Reconciliations'),

            # Approvals and workflow
            ('GET', '/approval', {}, 'Approvals'),
            ('GET', '/workflow', {}, 'Workflows'),

            # Attachments and notes
            ('GET', '/attachment', {}, 'Attachments'),
            ('GET', '/note', {}, 'Notes'),

            # Custom dimensions
            ('GET', '/dimension', {}, 'Dimensions'),
            ('GET', '/dimensionvalue', {}, 'Dimension Values'),
        ]

        print(f"\nTesting {len(endpoints_to_test)} potential endpoints...\n")

        available = []
        not_found = []
        needs_params = []

        for method, path, params, description in endpoints_to_test:
            url = f'{base_url}{path}'
            try:
                response = await client.get(url, headers=headers, params=params)
                status = response.status_code

                if status == 200:
                    print(f'✅ {path:30} - {description:25} - AVAILABLE')
                    available.append((path, description))
                    # Try to get count
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f'   └─ Returned {len(data)} items')
                        elif isinstance(data, dict) and 'items' in data:
                            print(f'   └─ Returned {len(data["items"])} items')
                    except:
                        pass
                elif status == 400:
                    print(f'⚠️  {path:30} - {description:25} - NEEDS PARAMS')
                    needs_params.append((path, description))
                elif status == 403:
                    print(f'🔒 {path:30} - {description:25} - FORBIDDEN')
                elif status == 404:
                    print(f'❌ {path:30} - {description:25} - NOT FOUND')
                    not_found.append((path, description))
                elif status == 405:
                    print(f'⚠️  {path:30} - {description:25} - METHOD NOT ALLOWED')
                else:
                    print(f'❓ {path:30} - {description:25} - HTTP {status}')

            except Exception as e:
                print(f'❌ {path:30} - {description:25} - ERROR: {str(e)[:50]}')

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"✅ Available endpoints: {len(available)}")
        print(f"⚠️  Endpoints needing parameters: {len(needs_params)}")
        print(f"❌ Not found: {len(not_found)}")

        if available:
            print("\n📋 AVAILABLE ENDPOINTS FOR PHASE 3:")
            for path, desc in available:
                print(f"   • {path:30} - {desc}")

        if needs_params:
            print("\n⚠️  ENDPOINTS THAT NEED PARAMETERS:")
            for path, desc in needs_params:
                print(f"   • {path:30} - {desc}")


if __name__ == '__main__':
    asyncio.run(explore_endpoints())
