#!/usr/bin/env python3
"""
Comprehensive Testing for 4 Specific Bug Fixes
Tests the exact scenarios mentioned by the user
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
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def setup_test_data():
    """Create test data as mentioned by the user"""
    print_test_header("Setting Up Test Data")
    
    # Create test customers
    customers_data = [
        {
            "name": "Tech Startup Solutions",
            "phone": "+91-9876543210",
            "email": "contact@techstartup.com",
            "address": "123 Tech Park, Bangalore, Karnataka 560001"
        },
        {
            "name": "Digital Agency Pro",
            "phone": "+91-9876543211",
            "email": "info@digitalagency.com",
            "address": "456 Business District, Mumbai, Maharashtra 400001"
        },
        {
            "name": "Marketing Pro Services",
            "phone": "+91-9876543212",
            "email": "hello@marketing-pro.com",
            "address": "789 Commercial Street, Delhi, Delhi 110001"
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
                print_error(f"Failed to create customer {customer_data['name']}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating customer {customer_data['name']}: {str(e)}")
            return False
    
    # Create test projects with AMC amounts as mentioned by user (₹8000, ₹12000, ₹5000)
    projects_data = [
        {
            "customer_id": test_customers[0]['id'],
            "type": "E-commerce Website",
            "name": "TechStartup E-commerce Platform",
            "amount": 50000.00,
            "amc_amount": 8000.00,  # ₹8000 AMC
            "start_date": "2024-01-15",
            "end_date": "2024-04-15"
        },
        {
            "customer_id": test_customers[1]['id'],
            "type": "Corporate Website",
            "name": "Digital Agency Corporate Site",
            "amount": 75000.00,
            "amc_amount": 12000.00,  # ₹12000 AMC
            "start_date": "2024-02-01",
            "end_date": "2024-05-01"
        },
        {
            "customer_id": test_customers[2]['id'],
            "type": "Marketing Website",
            "name": "Marketing Pro Landing Pages",
            "amount": 30000.00,
            "amc_amount": 5000.00,  # ₹5000 AMC
            "start_date": "2024-03-01",
            "end_date": "2024-06-01"
        }
    ]
    
    print("\n📝 Creating test projects with AMC amounts...")
    for project_data in projects_data:
        try:
            response = requests.post(f"{API_URL}/projects", json=project_data)
            if response.status_code == 200:
                project = response.json()
                test_projects.append(project)
                print_success(f"Created project: {project['name']} (AMC: ₹{project['amc_amount']})")
            else:
                print_error(f"Failed to create project {project_data['name']}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating project {project_data['name']}: {str(e)}")
            return False
    
    # Create test domains with specific expiry dates as mentioned by user
    current_date = datetime.now().date()
    domains_data = [
        {
            "project_id": test_projects[0]['id'],
            "domain_name": "techstartup.com",
            "hosting_provider": "AWS",
            "username": "techstartup_admin",
            "password": "SecurePass123!",
            "validity_date": (current_date - timedelta(days=10)).isoformat(),  # Expired 10 days ago
            "renewal_amount": 1500.00
        },
        {
            "project_id": test_projects[1]['id'],
            "domain_name": "digitalagency.com",
            "hosting_provider": "DigitalOcean",
            "username": "digital_admin",
            "password": "DigitalPass456!",
            "validity_date": (current_date + timedelta(days=15)).isoformat(),  # Due in 15 days
            "renewal_amount": 2000.00
        },
        {
            "project_id": test_projects[2]['id'],
            "domain_name": "marketing-pro.com",
            "hosting_provider": "Google Cloud",
            "username": "marketing_admin",
            "password": "MarketingPass789!",
            "validity_date": (current_date + timedelta(days=200)).isoformat(),  # Due in 200 days - should NOT appear
            "renewal_amount": 1800.00
        }
    ]
    
    print("\n📝 Creating test domains with specific expiry dates...")
    for domain_data in domains_data:
        try:
            response = requests.post(f"{API_URL}/domains", json=domain_data)
            if response.status_code == 200:
                domain = response.json()
                test_domains.append(domain)
                validity_date = datetime.fromisoformat(domain_data['validity_date']).date()
                days_diff = (validity_date - current_date).days
                status = "EXPIRED" if days_diff < 0 else f"Due in {days_diff} days"
                print_success(f"Created domain: {domain['domain_name']} ({status})")
            else:
                print_error(f"Failed to create domain {domain_data['domain_name']}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating domain {domain_data['domain_name']}: {str(e)}")
            return False
    
    print_success("Test data setup completed successfully")
    return True

def test_bug_fix_1_amc_amount_fetching():
    """Test Bug Fix 1: AMC amount fetching in /dashboard/amc-projects endpoint"""
    print_test_header("BUG FIX 1: AMC Amount Fetching in AMC Projects")
    
    print("\n🔍 Testing /dashboard/amc-projects endpoint...")
    try:
        response = requests.get(f"{API_URL}/dashboard/amc-projects")
        if response.status_code == 200:
            amc_projects = response.json()
            print_success(f"Retrieved {len(amc_projects)} AMC projects")
            
            # Verify that amc_amount field is present and correct
            expected_amc_amounts = [8000.00, 12000.00, 5000.00]
            found_amc_amounts = []
            
            for project in amc_projects:
                # Check if amc_amount field exists
                if 'amc_amount' not in project:
                    print_error(f"❌ BUG FIX 1 FAILED: amc_amount field missing in project {project.get('project_name', 'Unknown')}")
                    return False
                
                amc_amount = project['amc_amount']
                found_amc_amounts.append(amc_amount)
                
                # Verify other required fields
                required_fields = ['project_id', 'project_name', 'amc_amount', 'customer_name', 'customer_email', 'customer_phone']
                missing_fields = [field for field in required_fields if field not in project]
                if missing_fields:
                    print_error(f"Missing fields in AMC project: {missing_fields}")
                    return False
                
                print_info(f"Project: {project['project_name']} | AMC Amount: ₹{amc_amount} | Customer: {project['customer_name']}")
            
            # Verify we have the expected AMC amounts
            for expected_amount in expected_amc_amounts:
                if expected_amount in found_amc_amounts:
                    print_success(f"✅ Found expected AMC amount: ₹{expected_amount}")
                else:
                    print_error(f"❌ Expected AMC amount ₹{expected_amount} not found")
                    return False
            
            print_success("✅ BUG FIX 1 PASSED: AMC amount field is properly included in all AMC projects")
            return True
        else:
            print_error(f"❌ BUG FIX 1 FAILED: /dashboard/amc-projects endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"❌ BUG FIX 1 FAILED: Error testing AMC projects endpoint: {str(e)}")
        return False

def test_bug_fix_2_domain_renewal_functionality():
    """Test Bug Fix 2: Domain renewal functionality with both payment types"""
    print_test_header("BUG FIX 2: Domain Renewal Functionality")
    
    if not test_domains:
        print_error("No test domains available for renewal testing")
        return False
    
    # Test 1: Client payment type
    print("\n💳 Testing domain renewal with 'client' payment type...")
    domain_id = test_domains[0]['id']  # techstartup.com
    
    client_renewal = {
        "domain_id": domain_id,
        "payment_type": "client",
        "notes": "Client pays directly for renewal"
    }
    
    try:
        response = requests.post(f"{API_URL}/domain-renewal/{domain_id}", json=client_renewal)
        if response.status_code == 200:
            result = response.json()
            print_success(f"✅ Client payment renewal successful: {result.get('message')}")
            
            # Verify domain was updated with correct payment type
            domain_response = requests.get(f"{API_URL}/domains/{domain_id}")
            if domain_response.status_code == 200:
                updated_domain = domain_response.json()
                if updated_domain.get('payment_type') == 'client':
                    print_success("✅ Domain payment type correctly set to 'client'")
                else:
                    print_error(f"❌ Expected payment_type 'client', got '{updated_domain.get('payment_type')}'")
                    return False
                
                # Verify validity date was extended by 1 year
                new_validity = datetime.fromisoformat(updated_domain['validity_date']).date()
                print_success(f"✅ Domain validity extended to: {new_validity}")
            else:
                print_error("❌ Failed to retrieve updated domain")
                return False
        else:
            print_error(f"❌ BUG FIX 2 FAILED: Client payment renewal failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"❌ BUG FIX 2 FAILED: Error testing client payment renewal: {str(e)}")
        return False
    
    # Test 2: Agency payment type
    print("\n🏢 Testing domain renewal with 'agency' payment type...")
    if len(test_domains) > 1:
        domain_id = test_domains[1]['id']  # digitalagency.com
        
        agency_renewal = {
            "domain_id": domain_id,
            "payment_type": "agency",
            "notes": "Agency pays upfront, customer owes amount"
        }
        
        try:
            response = requests.post(f"{API_URL}/domain-renewal/{domain_id}", json=agency_renewal)
            if response.status_code == 200:
                result = response.json()
                print_success(f"✅ Agency payment renewal successful: {result.get('message')}")
                
                # Verify domain was updated with correct payment type
                domain_response = requests.get(f"{API_URL}/domains/{domain_id}")
                if domain_response.status_code == 200:
                    updated_domain = domain_response.json()
                    if updated_domain.get('payment_type') == 'agency':
                        print_success("✅ Domain payment type correctly set to 'agency'")
                    else:
                        print_error(f"❌ Expected payment_type 'agency', got '{updated_domain.get('payment_type')}'")
                        return False
                    
                    # Verify validity date was extended by 1 year
                    new_validity = datetime.fromisoformat(updated_domain['validity_date']).date()
                    print_success(f"✅ Domain validity extended to: {new_validity}")
                else:
                    print_error("❌ Failed to retrieve updated domain")
                    return False
                
                # Verify customer ledger entry was created for agency payment
                project = None
                for p in test_projects:
                    if any(d['id'] == domain_id for d in test_domains if d['project_id'] == p['id']):
                        project = p
                        break
                
                if project:
                    customer_id = project['customer_id']
                    ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
                    if ledger_response.status_code == 200:
                        ledger_entries = ledger_response.json()
                        debt_entry_found = False
                        for entry in ledger_entries:
                            if (entry.get('transaction_type') == 'debit' and 
                                'domain renewal' in entry.get('description', '').lower() and
                                entry.get('reference_id') == domain_id):
                                debt_entry_found = True
                                print_success("✅ Customer debt entry created for agency-paid renewal")
                                break
                        
                        if not debt_entry_found:
                            print_error("❌ Customer debt entry not found in ledger")
                            return False
                    else:
                        print_error("❌ Failed to retrieve customer ledger")
                        return False
            else:
                print_error(f"❌ BUG FIX 2 FAILED: Agency payment renewal failed with status {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
        except Exception as e:
            print_error(f"❌ BUG FIX 2 FAILED: Error testing agency payment renewal: {str(e)}")
            return False
    
    print_success("✅ BUG FIX 2 PASSED: Both 'client' and 'agency' payment types work correctly")
    return True

def test_bug_fix_3_domains_due_renewal():
    """Test Bug Fix 3: Domains due for renewal endpoint"""
    print_test_header("BUG FIX 3: Domains Due for Renewal")
    
    print("\n📅 Testing /domains-due-renewal endpoint...")
    try:
        response = requests.get(f"{API_URL}/domains-due-renewal")
        if response.status_code == 200:
            due_domains = response.json()
            print_success(f"Retrieved {len(due_domains)} domains due for renewal")
            
            # Expected domains: techstartup.com (expired) and digitalagency.com (due in 15 days)
            # marketing-pro.com (due in 200 days) should NOT appear
            
            expected_domains = ['techstartup.com', 'digitalagency.com']
            should_not_appear = ['marketing-pro.com']
            
            found_domains = []
            for domain in due_domains:
                # Verify required fields
                required_fields = ['domain_id', 'domain_name', 'hosting_provider', 
                                 'validity_date', 'days_until_expiry', 'renewal_amount',
                                 'project_name', 'customer_name', 'customer_id', 'is_expired']
                
                missing_fields = [field for field in required_fields if field not in domain]
                if missing_fields:
                    print_error(f"❌ BUG FIX 3 FAILED: Missing fields in due domain: {missing_fields}")
                    return False
                
                domain_name = domain['domain_name']
                found_domains.append(domain_name)
                days_until_expiry = domain['days_until_expiry']
                is_expired = domain['is_expired']
                
                print_info(f"Domain: {domain_name} | Days until expiry: {days_until_expiry} | Expired: {is_expired} | Customer: {domain['customer_name']}")
                
                # Verify logic: domains due within 30 days or already expired
                if days_until_expiry > 30:
                    print_error(f"❌ BUG FIX 3 FAILED: Domain {domain_name} has {days_until_expiry} days until expiry (should be ≤30)")
                    return False
                
                # Verify is_expired flag
                if days_until_expiry < 0 and not is_expired:
                    print_error(f"❌ BUG FIX 3 FAILED: Domain {domain_name} is expired but is_expired=False")
                    return False
                elif days_until_expiry >= 0 and is_expired:
                    print_error(f"❌ BUG FIX 3 FAILED: Domain {domain_name} is not expired but is_expired=True")
                    return False
            
            # Verify expected domains are present
            for expected_domain in expected_domains:
                if expected_domain in found_domains:
                    print_success(f"✅ Found expected domain: {expected_domain}")
                else:
                    print_error(f"❌ BUG FIX 3 FAILED: Expected domain {expected_domain} not found in results")
                    return False
            
            # Verify domains that should not appear are absent
            for domain_name in should_not_appear:
                if domain_name in found_domains:
                    print_error(f"❌ BUG FIX 3 FAILED: Domain {domain_name} should not appear (due in >30 days)")
                    return False
                else:
                    print_success(f"✅ Correctly excluded domain: {domain_name} (due in >30 days)")
            
            print_success("✅ BUG FIX 3 PASSED: Domains due for renewal endpoint correctly returns expired and due-soon domains")
            return True
        else:
            print_error(f"❌ BUG FIX 3 FAILED: /domains-due-renewal endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"❌ BUG FIX 3 FAILED: Error testing domains due for renewal: {str(e)}")
        return False

def test_bug_fix_4_domain_editing():
    """Test Bug Fix 4: Domain editing capability for renewal_amount"""
    print_test_header("BUG FIX 4: Domain Editing Capability")
    
    if not test_domains:
        print_error("No test domains available for editing testing")
        return False
    
    print("\n✏️  Testing domain renewal_amount editing...")
    domain_id = test_domains[0]['id']  # techstartup.com
    
    # Get current domain data
    try:
        response = requests.get(f"{API_URL}/domains/{domain_id}")
        if response.status_code == 200:
            original_domain = response.json()
            original_renewal_amount = original_domain.get('renewal_amount', 0)
            print_info(f"Original renewal amount: ₹{original_renewal_amount}")
        else:
            print_error(f"❌ Failed to get original domain data: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"❌ Error getting original domain data: {str(e)}")
        return False
    
    # Test updating renewal_amount
    new_renewal_amount = 2000.00  # Change from ₹1500 to ₹2000
    update_data = {"renewal_amount": new_renewal_amount}
    
    try:
        response = requests.put(f"{API_URL}/domains/{domain_id}", json=update_data)
        if response.status_code == 200:
            updated_domain = response.json()
            updated_renewal_amount = updated_domain.get('renewal_amount')
            
            if updated_renewal_amount == new_renewal_amount:
                print_success(f"✅ Successfully updated renewal amount: ₹{original_renewal_amount} → ₹{updated_renewal_amount}")
                
                # Verify the update persisted by fetching the domain again
                verify_response = requests.get(f"{API_URL}/domains/{domain_id}")
                if verify_response.status_code == 200:
                    verified_domain = verify_response.json()
                    verified_renewal_amount = verified_domain.get('renewal_amount')
                    
                    if verified_renewal_amount == new_renewal_amount:
                        print_success("✅ Domain renewal amount update persisted correctly")
                        print_success("✅ BUG FIX 4 PASSED: Domain renewal_amount can be updated successfully")
                        return True
                    else:
                        print_error(f"❌ BUG FIX 4 FAILED: Update did not persist. Expected ₹{new_renewal_amount}, got ₹{verified_renewal_amount}")
                        return False
                else:
                    print_error(f"❌ BUG FIX 4 FAILED: Failed to verify domain update: {verify_response.status_code}")
                    return False
            else:
                print_error(f"❌ BUG FIX 4 FAILED: Expected renewal amount ₹{new_renewal_amount}, got ₹{updated_renewal_amount}")
                return False
        else:
            print_error(f"❌ BUG FIX 4 FAILED: Domain update failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"❌ BUG FIX 4 FAILED: Error updating domain: {str(e)}")
        return False

def run_all_bug_fix_tests():
    """Run all 4 bug fix tests"""
    print("🚀 Starting Comprehensive Bug Fix Testing")
    print("=" * 80)
    
    # Setup test data first
    if not setup_test_data():
        print_error("❌ FAILED: Could not set up test data")
        return False
    
    # Track test results
    test_results = []
    
    # Run each bug fix test
    tests = [
        ("Bug Fix 1: AMC Amount Fetching", test_bug_fix_1_amc_amount_fetching),
        ("Bug Fix 2: Domain Renewal Functionality", test_bug_fix_2_domain_renewal_functionality),
        ("Bug Fix 3: Domains Due for Renewal", test_bug_fix_3_domains_due_renewal),
        ("Bug Fix 4: Domain Editing Capability", test_bug_fix_4_domain_editing)
    ]
    
    for test_name, test_function in tests:
        try:
            result = test_function()
            test_results.append((test_name, result))
        except Exception as e:
            print_error(f"❌ {test_name} FAILED with exception: {str(e)}")
            test_results.append((test_name, False))
    
    # Print final summary
    print("\n" + "=" * 80)
    print("🎯 FINAL BUG FIX TEST RESULTS")
    print("=" * 80)
    
    passed_count = 0
    failed_count = 0
    
    for test_name, result in test_results:
        if result:
            print_success(f"{test_name}: PASSED")
            passed_count += 1
        else:
            print_error(f"{test_name}: FAILED")
            failed_count += 1
    
    print(f"\n📊 SUMMARY: {passed_count} PASSED, {failed_count} FAILED")
    
    if failed_count == 0:
        print_success("🎉 ALL 4 BUG FIXES ARE WORKING CORRECTLY!")
        return True
    else:
        print_error(f"⚠️  {failed_count} BUG FIX(ES) NEED ATTENTION")
        return False

if __name__ == "__main__":
    success = run_all_bug_fix_tests()
    sys.exit(0 if success else 1)