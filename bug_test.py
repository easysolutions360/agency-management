#!/usr/bin/env python3
"""
Bug Testing Script for 4 Specific Issues
Tests the 4 reported bugs in the backend system
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys
import os

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("❌ Could not get backend URL from frontend/.env")
    sys.exit(1)

API_URL = f"{BASE_URL}/api"
print(f"🔗 Testing API at: {API_URL}")

# Test data storage
test_customers = []
test_projects = []
test_domains = []

def print_test_header(test_name):
    print(f"\n{'='*80}")
    print(f"🧪 TESTING BUG: {test_name}")
    print(f"{'='*80}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def setup_test_data():
    """Create test data for bug testing"""
    print_test_header("Setting up Test Data")
    
    # Create test customers
    customers_data = [
        {
            "name": "Alice Johnson",
            "phone": "+1-555-1001",
            "email": "alice.johnson@example.com",
            "address": "123 Main St, City, State 12345"
        },
        {
            "name": "Bob Smith", 
            "phone": "+1-555-1002",
            "email": "bob.smith@example.com",
            "address": "456 Oak Ave, City, State 67890"
        }
    ]
    
    print("\n📝 Creating test customers...")
    for customer_data in customers_data:
        try:
            response = requests.post(f"{API_URL}/customers", json=customer_data)
            if response.status_code == 200:
                customer = response.json()
                test_customers.append(customer)
                print_success(f"Created customer: {customer['name']}")
            else:
                print_error(f"Failed to create customer: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating customer: {str(e)}")
            return False
    
    # Create test projects with AMC amounts and different end dates
    projects_data = [
        {
            "customer_id": test_customers[0]['id'],
            "type": "E-commerce Website",
            "name": "Online Store Development",
            "amount": 25000.00,
            "amc_amount": 8000.00,  # This should show in AMC checker
            "start_date": "2024-01-01",
            "end_date": "2024-03-01"  # Ended, AMC should be due
        },
        {
            "customer_id": test_customers[1]['id'],
            "type": "Mobile App",
            "name": "Business Mobile App",
            "amount": 30000.00,
            "amc_amount": 12000.00,  # This should show in AMC checker
            "start_date": "2024-02-01",
            "end_date": "2024-05-01"  # Ended, AMC should be due
        },
        {
            "customer_id": test_customers[0]['id'],
            "type": "Website Maintenance",
            "name": "Ongoing Website Support",
            "amount": 15000.00,
            "amc_amount": 0.00,  # No AMC - should not show in AMC checker
            "start_date": "2024-01-01"
            # No end_date - should not show in AMC checker
        }
    ]
    
    print("\n📝 Creating test projects...")
    for project_data in projects_data:
        try:
            response = requests.post(f"{API_URL}/projects", json=project_data)
            if response.status_code == 200:
                project = response.json()
                test_projects.append(project)
                print_success(f"Created project: {project['name']} (AMC: ₹{project.get('amc_amount', 0)})")
            else:
                print_error(f"Failed to create project: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating project: {str(e)}")
            return False
    
    # Create test domains with different expiry dates
    domains_data = [
        {
            "project_id": test_projects[0]['id'],
            "domain_name": "onlinestore.com",
            "hosting_provider": "AWS",
            "username": "admin_store",
            "password": "StorePass123!",
            "validity_date": "2024-12-25",  # Expiring within 30 days
            "renewal_amount": 1500.00
        },
        {
            "project_id": test_projects[1]['id'],
            "domain_name": "businessapp.com",
            "hosting_provider": "Google Cloud",
            "username": "admin_app",
            "password": "AppPass456!",
            "validity_date": "2024-12-20",  # Expiring within 30 days
            "renewal_amount": 2000.00
        },
        {
            "project_id": test_projects[0]['id'],
            "domain_name": "expired-domain.com",
            "hosting_provider": "DigitalOcean",
            "username": "admin_expired",
            "password": "ExpiredPass789!",
            "validity_date": "2024-11-15",  # Already expired
            "renewal_amount": 1200.00
        },
        {
            "project_id": test_projects[1]['id'],
            "domain_name": "future-domain.com",
            "hosting_provider": "Cloudflare",
            "username": "admin_future",
            "password": "FuturePass000!",
            "validity_date": "2025-06-15",  # Not expiring soon
            "renewal_amount": 1800.00
        }
    ]
    
    print("\n📝 Creating test domains...")
    for domain_data in domains_data:
        try:
            response = requests.post(f"{API_URL}/domains", json=domain_data)
            if response.status_code == 200:
                domain = response.json()
                test_domains.append(domain)
                print_success(f"Created domain: {domain['domain_name']} (Expires: {domain['validity_date']})")
            else:
                print_error(f"Failed to create domain: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating domain: {str(e)}")
            return False
    
    print_success("Test data setup completed successfully")
    return True

def test_bug_1_amc_amount_not_fetching():
    """
    BUG 1: AMC amount not fetching in AMC checker view
    Test /dashboard/amc-projects endpoint to verify AMC amounts are returned correctly
    """
    print_test_header("BUG 1: AMC amount not fetching in AMC checker view")
    
    print("\n🔍 Testing /dashboard/amc-projects endpoint...")
    try:
        response = requests.get(f"{API_URL}/dashboard/amc-projects")
        if response.status_code == 200:
            amc_projects = response.json()
            print_success(f"Retrieved {len(amc_projects)} AMC projects")
            
            if len(amc_projects) == 0:
                print_error("❌ BUG CONFIRMED: No AMC projects returned, but we created projects with AMC amounts and end dates")
                return False
            
            # Check if AMC amounts are included in response
            amc_amounts_found = 0
            for project in amc_projects:
                print_info(f"Project: {project.get('project_name')} | AMC Amount: ₹{project.get('amc_amount', 'MISSING')}")
                
                # Verify required fields are present
                required_fields = ['project_id', 'project_name', 'amc_amount', 'customer_name']
                missing_fields = [field for field in required_fields if field not in project]
                
                if missing_fields:
                    print_error(f"❌ BUG CONFIRMED: Missing fields in AMC project: {missing_fields}")
                    return False
                
                if project.get('amc_amount') and project.get('amc_amount') > 0:
                    amc_amounts_found += 1
                    print_success(f"✅ AMC amount found: ₹{project['amc_amount']} for {project['project_name']}")
                else:
                    print_error(f"❌ BUG CONFIRMED: AMC amount missing or zero for {project.get('project_name')}")
            
            if amc_amounts_found >= 2:  # We created 2 projects with AMC amounts
                print_success("✅ BUG 1 FIXED: AMC amounts are being fetched correctly in AMC checker view")
                return True
            else:
                print_error(f"❌ BUG CONFIRMED: Expected 2 projects with AMC amounts, found {amc_amounts_found}")
                return False
                
        else:
            print_error(f"❌ API Error: Failed to get AMC projects: {response.status_code}")
            if response.status_code == 404:
                print_error("❌ BUG CONFIRMED: AMC projects endpoint not found")
            return False
            
    except Exception as e:
        print_error(f"❌ Exception testing AMC projects: {str(e)}")
        return False

def test_bug_2_domain_renewal_not_working():
    """
    BUG 2: Domain renewal option not working
    Test /domain-renewal/{domain_id} endpoint with both 'client' and 'agency' payment types
    """
    print_test_header("BUG 2: Domain renewal option not working")
    
    if not test_domains:
        print_error("No test domains available for renewal testing")
        return False
    
    # Test 1: Client payment type
    print("\n🌐 Testing domain renewal with CLIENT payment type...")
    domain_id = test_domains[0]['id']
    
    client_renewal_data = {
        "domain_id": domain_id,
        "payment_type": "client",
        "notes": "Client pays directly for renewal"
    }
    
    try:
        response = requests.post(f"{API_URL}/domain-renewal/{domain_id}", json=client_renewal_data)
        if response.status_code == 200:
            result = response.json()
            print_success(f"✅ Client renewal successful: {result.get('message')}")
            
            # Verify domain was updated
            domain_response = requests.get(f"{API_URL}/domains/{domain_id}")
            if domain_response.status_code == 200:
                updated_domain = domain_response.json()
                if updated_domain.get('payment_type') == 'client':
                    print_success("✅ Domain payment type correctly set to 'client'")
                else:
                    print_error(f"❌ Domain payment type not updated correctly: {updated_domain.get('payment_type')}")
                    return False
            else:
                print_error("❌ Failed to retrieve updated domain")
                return False
        else:
            print_error(f"❌ BUG CONFIRMED: Client renewal failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"❌ Exception testing client renewal: {str(e)}")
        return False
    
    # Test 2: Agency payment type
    print("\n🏢 Testing domain renewal with AGENCY payment type...")
    if len(test_domains) > 1:
        domain_id = test_domains[1]['id']
        
        agency_renewal_data = {
            "domain_id": domain_id,
            "payment_type": "agency",
            "notes": "Agency pays upfront, customer owes amount"
        }
        
        try:
            response = requests.post(f"{API_URL}/domain-renewal/{domain_id}", json=agency_renewal_data)
            if response.status_code == 200:
                result = response.json()
                print_success(f"✅ Agency renewal successful: {result.get('message')}")
                
                # Verify domain was updated
                domain_response = requests.get(f"{API_URL}/domains/{domain_id}")
                if domain_response.status_code == 200:
                    updated_domain = domain_response.json()
                    if updated_domain.get('payment_type') == 'agency':
                        print_success("✅ Domain payment type correctly set to 'agency'")
                    else:
                        print_error(f"❌ Domain payment type not updated correctly: {updated_domain.get('payment_type')}")
                        return False
                else:
                    print_error("❌ Failed to retrieve updated domain")
                    return False
                    
                # Check if customer ledger entry was created for agency payment
                project = None
                for p in test_projects:
                    if p['id'] == updated_domain['project_id']:
                        project = p
                        break
                
                if project:
                    customer_id = project['customer_id']
                    ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
                    if ledger_response.status_code == 200:
                        ledger_entries = ledger_response.json()
                        agency_entry_found = False
                        for entry in ledger_entries:
                            if (entry.get('transaction_type') == 'debit' and 
                                'domain renewal' in entry.get('description', '').lower() and
                                entry.get('reference_id') == domain_id):
                                agency_entry_found = True
                                print_success("✅ Customer ledger entry created for agency payment")
                                break
                        
                        if not agency_entry_found:
                            print_error("❌ Customer ledger entry not found for agency payment")
                            return False
                    else:
                        print_error("❌ Failed to retrieve customer ledger")
                        return False
            else:
                print_error(f"❌ BUG CONFIRMED: Agency renewal failed with status {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
        except Exception as e:
            print_error(f"❌ Exception testing agency renewal: {str(e)}")
            return False
    
    print_success("✅ BUG 2 FIXED: Domain renewal is working for both client and agency payment types")
    return True

def test_bug_3_domains_due_renewal_incomplete():
    """
    BUG 3: Domains due for renewal not showing all expired/about to expire
    Test /domains-due-renewal endpoint with test data
    """
    print_test_header("BUG 3: Domains due for renewal not showing all expired/about to expire")
    
    print("\n📅 Testing /domains-due-renewal endpoint...")
    try:
        response = requests.get(f"{API_URL}/domains-due-renewal")
        if response.status_code == 200:
            due_domains = response.json()
            print_success(f"Retrieved {len(due_domains)} domains due for renewal")
            
            # We created 4 domains:
            # 1. onlinestore.com - expires 2024-12-25 (should be included)
            # 2. businessapp.com - expires 2024-12-20 (should be included)  
            # 3. expired-domain.com - expires 2024-11-15 (already expired, should be included)
            # 4. future-domain.com - expires 2025-06-15 (should NOT be included)
            
            expected_domains = ['onlinestore.com', 'businessapp.com', 'expired-domain.com']
            found_domains = []
            
            for domain in due_domains:
                print_info(f"Domain: {domain.get('domain_name')} | Days until expiry: {domain.get('days_until_expiry')} | Expired: {domain.get('is_expired')}")
                
                # Verify required fields
                required_fields = ['domain_id', 'domain_name', 'hosting_provider', 'validity_date', 
                                 'days_until_expiry', 'renewal_amount', 'project_name', 'customer_name', 
                                 'customer_id', 'is_expired']
                missing_fields = [field for field in required_fields if field not in domain]
                
                if missing_fields:
                    print_error(f"❌ Missing fields in due domain: {missing_fields}")
                    return False
                
                domain_name = domain.get('domain_name')
                if domain_name in expected_domains:
                    found_domains.append(domain_name)
                    
                    # Verify logic for expired vs due domains
                    days_until_expiry = domain.get('days_until_expiry')
                    is_expired = domain.get('is_expired')
                    
                    if days_until_expiry < 0 and not is_expired:
                        print_error(f"❌ Logic error: {domain_name} has negative days but is_expired is False")
                        return False
                    elif days_until_expiry >= 0 and is_expired:
                        print_error(f"❌ Logic error: {domain_name} has positive days but is_expired is True")
                        return False
                    
                    print_success(f"✅ Found expected domain: {domain_name}")
            
            # Check if we found all expected domains
            missing_domains = set(expected_domains) - set(found_domains)
            if missing_domains:
                print_error(f"❌ BUG CONFIRMED: Missing domains that should be due for renewal: {missing_domains}")
                return False
            
            # Check if future domain is incorrectly included
            future_domain_found = False
            for domain in due_domains:
                if domain.get('domain_name') == 'future-domain.com':
                    future_domain_found = True
                    break
            
            if future_domain_found:
                print_error("❌ BUG CONFIRMED: Future domain incorrectly included in due for renewal list")
                return False
            
            print_success("✅ BUG 3 FIXED: All expected domains due for renewal are showing correctly")
            return True
            
        else:
            print_error(f"❌ API Error: Failed to get domains due for renewal: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"❌ Exception testing domains due for renewal: {str(e)}")
        return False

def test_bug_4_no_edit_domain_renewal_price():
    """
    BUG 4: No option to edit domain renewal price
    Check if domain model supports updating renewal_amount field
    """
    print_test_header("BUG 4: No option to edit domain renewal price")
    
    if not test_domains:
        print_error("No test domains available for renewal price testing")
        return False
    
    domain_id = test_domains[0]['id']
    
    # Get current domain data
    print("\n🔍 Getting current domain data...")
    try:
        response = requests.get(f"{API_URL}/domains/{domain_id}")
        if response.status_code == 200:
            current_domain = response.json()
            current_renewal_amount = current_domain.get('renewal_amount', 0)
            print_info(f"Current renewal amount: ₹{current_renewal_amount}")
        else:
            print_error(f"Failed to get current domain: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting current domain: {str(e)}")
        return False
    
    # Test updating renewal amount
    print("\n✏️  Testing domain renewal amount update...")
    new_renewal_amount = current_renewal_amount + 500.00
    update_data = {
        "renewal_amount": new_renewal_amount
    }
    
    try:
        response = requests.put(f"{API_URL}/domains/{domain_id}", json=update_data)
        if response.status_code == 200:
            updated_domain = response.json()
            updated_renewal_amount = updated_domain.get('renewal_amount')
            
            if updated_renewal_amount == new_renewal_amount:
                print_success(f"✅ BUG 4 FIXED: Successfully updated renewal amount from ₹{current_renewal_amount} to ₹{updated_renewal_amount}")
                
                # Verify the update persisted
                verify_response = requests.get(f"{API_URL}/domains/{domain_id}")
                if verify_response.status_code == 200:
                    verified_domain = verify_response.json()
                    if verified_domain.get('renewal_amount') == new_renewal_amount:
                        print_success("✅ Renewal amount update persisted correctly")
                        return True
                    else:
                        print_error("❌ Renewal amount update did not persist")
                        return False
                else:
                    print_error("❌ Failed to verify renewal amount update")
                    return False
            else:
                print_error(f"❌ BUG CONFIRMED: Renewal amount not updated correctly. Expected: ₹{new_renewal_amount}, Got: ₹{updated_renewal_amount}")
                return False
        else:
            print_error(f"❌ BUG CONFIRMED: Failed to update domain renewal amount: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"❌ Exception testing renewal amount update: {str(e)}")
        return False

def run_all_bug_tests():
    """Run all bug tests"""
    print("🚀 Starting Bug Testing Suite")
    print(f"Testing against: {API_URL}")
    
    # Setup test data
    if not setup_test_data():
        print_error("❌ Failed to setup test data")
        return False
    
    # Track test results
    results = {}
    
    # Test each bug
    print("\n" + "="*100)
    print("🔍 RUNNING BUG TESTS")
    print("="*100)
    
    results['bug_1'] = test_bug_1_amc_amount_not_fetching()
    results['bug_2'] = test_bug_2_domain_renewal_not_working()
    results['bug_3'] = test_bug_3_domains_due_renewal_incomplete()
    results['bug_4'] = test_bug_4_no_edit_domain_renewal_price()
    
    # Print summary
    print("\n" + "="*100)
    print("📊 BUG TEST SUMMARY")
    print("="*100)
    
    passed = 0
    failed = 0
    
    for bug, result in results.items():
        status = "✅ FIXED" if result else "❌ CONFIRMED"
        print(f"{bug.upper().replace('_', ' ')}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 RESULTS: {passed} Fixed, {failed} Still Broken")
    
    if failed == 0:
        print("🎉 ALL BUGS HAVE BEEN FIXED!")
    else:
        print(f"⚠️  {failed} BUGS STILL NEED ATTENTION")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_bug_tests()
    sys.exit(0 if success else 1)