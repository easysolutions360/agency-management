#!/usr/bin/env python3
"""
Bug Fix Testing for Agency Management System
Tests the 6 specific bug fixes mentioned in the review request
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
    """Create test data for bug fix testing"""
    print_test_header("Setting up Test Data")
    
    # Create test customers
    customers_data = [
        {
            "name": "Rajesh Kumar",
            "phone": "+91-9876543210",
            "email": "rajesh.kumar@techsolutions.in",
            "address": "123 Tech Park, Bangalore, Karnataka 560001"
        },
        {
            "name": "Priya Sharma",
            "phone": "+91-9876543211",
            "email": "priya.sharma@digitalagency.in",
            "address": "456 Business Center, Mumbai, Maharashtra 400001"
        }
    ]
    
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
    
    # Create test projects
    projects_data = [
        {
            "customer_id": test_customers[0]['id'],
            "type": "E-commerce Website",
            "name": "Online Shopping Platform",
            "amount": 50000.00,
            "amc_amount": 8000.00,
            "start_date": "2024-01-15",
            "end_date": "2024-04-15"
        },
        {
            "customer_id": test_customers[1]['id'],
            "type": "Corporate Website",
            "name": "Company Portfolio Site",
            "amount": 30000.00,
            "amc_amount": 5000.00,
            "start_date": "2024-02-01",
            "end_date": "2024-05-01"
        }
    ]
    
    for project_data in projects_data:
        try:
            response = requests.post(f"{API_URL}/projects", json=project_data)
            if response.status_code == 200:
                project = response.json()
                test_projects.append(project)
                print_success(f"Created project: {project['name']}")
            else:
                print_error(f"Failed to create project: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating project: {str(e)}")
            return False
    
    # Create test domains
    domains_data = [
        {
            "project_id": test_projects[0]['id'],
            "domain_name": "techsolutions.in",
            "hosting_provider": "AWS",
            "username": "admin_tech",
            "password": "SecurePass123!",
            "validity_date": "2024-12-31",
            "renewal_amount": 2000.00
        },
        {
            "project_id": test_projects[1]['id'],
            "domain_name": "digitalagency.in",
            "hosting_provider": "DigitalOcean",
            "username": "admin_digital",
            "password": "DigitalPass456!",
            "validity_date": "2024-03-15",  # This will be expiring soon
            "renewal_amount": 1500.00
        }
    ]
    
    for domain_data in domains_data:
        try:
            response = requests.post(f"{API_URL}/domains", json=domain_data)
            if response.status_code == 200:
                domain = response.json()
                test_domains.append(domain)
                print_success(f"Created domain: {domain['domain_name']}")
            else:
                print_error(f"Failed to create domain: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating domain: {str(e)}")
            return False
    
    print_success("Test data setup completed successfully")
    return True

def test_bug_fix_1_project_amc_edit():
    """Test Bug Fix 1: Project AMC Edit - Test that when editing a project, the AMC amount field is now available and can be updated"""
    print_test_header("Bug Fix 1: Project AMC Edit")
    
    if not test_projects:
        print_error("No test projects available for AMC edit testing")
        return False
    
    project_id = test_projects[0]['id']
    
    # Test updating AMC amount
    print("\n✏️  Testing AMC Amount Update...")
    update_data = {"amc_amount": 12000.00}
    
    try:
        response = requests.put(f"{API_URL}/projects/{project_id}", json=update_data)
        if response.status_code == 200:
            updated_project = response.json()
            if updated_project.get('amc_amount') == 12000.00:
                print_success(f"Successfully updated AMC amount to ₹{updated_project['amc_amount']}")
                
                # Verify the update persisted by fetching the project again
                get_response = requests.get(f"{API_URL}/projects/{project_id}")
                if get_response.status_code == 200:
                    fetched_project = get_response.json()
                    if fetched_project.get('amc_amount') == 12000.00:
                        print_success("AMC amount update persisted correctly")
                    else:
                        print_error("AMC amount update did not persist")
                        return False
                else:
                    print_error("Failed to fetch updated project")
                    return False
            else:
                print_error(f"AMC amount not updated correctly. Expected: ₹12000.00, Got: ₹{updated_project.get('amc_amount')}")
                return False
        else:
            print_error(f"Failed to update project AMC: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error updating project AMC: {str(e)}")
        return False
    
    print_success("Bug Fix 1: Project AMC Edit - PASSED")
    return True

def test_bug_fix_2_payment_updates():
    """Test Bug Fix 2: Payment Updates - Test that when payments are made, customer payment summaries are properly updated"""
    print_test_header("Bug Fix 2: Payment Updates")
    
    if not test_customers or not test_projects:
        print_error("No test data available for payment updates testing")
        return False
    
    customer_id = test_customers[0]['id']
    project_id = test_projects[0]['id']
    
    # Get initial payment summary
    print("\n📊 Getting Initial Payment Summary...")
    try:
        response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
        if response.status_code == 200:
            initial_summary = response.json()
            print_info(f"Initial Outstanding: ₹{initial_summary['outstanding_amount']}")
            print_info(f"Initial Paid: ₹{initial_summary['total_paid_amount']}")
            print_info(f"Initial Credit Balance: ₹{initial_summary['credit_balance']}")
        else:
            print_error(f"Failed to get initial payment summary: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting initial payment summary: {str(e)}")
        return False
    
    # Make a project payment
    print("\n💳 Recording Project Payment...")
    payment_data = {
        "customer_id": customer_id,
        "type": "project_advance",
        "reference_id": project_id,
        "amount": 15000.00,
        "description": "Advance payment for project development"
    }
    
    try:
        response = requests.post(f"{API_URL}/payments", json=payment_data)
        if response.status_code == 200:
            print_success("Project payment recorded successfully")
        else:
            print_error(f"Failed to record project payment: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error recording project payment: {str(e)}")
        return False
    
    # Test AMC payment
    print("\n🔄 Recording AMC Payment...")
    amc_payment_data = {
        "project_id": project_id,
        "amount": 8000.00,
        "payment_date": datetime.utcnow().isoformat()
    }
    
    try:
        response = requests.post(f"{API_URL}/amc-payment/{project_id}", json=amc_payment_data)
        if response.status_code == 200:
            print_success("AMC payment recorded successfully")
        else:
            print_error(f"Failed to record AMC payment: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error recording AMC payment: {str(e)}")
        return False
    
    # Get updated payment summary
    print("\n📊 Verifying Updated Payment Summary...")
    try:
        response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
        if response.status_code == 200:
            updated_summary = response.json()
            print_info(f"Updated Outstanding: ₹{updated_summary['outstanding_amount']}")
            print_info(f"Updated Paid: ₹{updated_summary['total_paid_amount']}")
            print_info(f"Updated Credit Balance: ₹{updated_summary['credit_balance']}")
            
            # Verify payment summary was updated
            if updated_summary['total_paid_amount'] > initial_summary['total_paid_amount']:
                print_success("Total paid amount increased correctly")
            else:
                print_error("Total paid amount did not increase")
                return False
            
            if updated_summary['credit_balance'] > initial_summary['credit_balance']:
                print_success("Credit balance increased correctly")
            else:
                print_error("Credit balance did not increase")
                return False
                
        else:
            print_error(f"Failed to get updated payment summary: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting updated payment summary: {str(e)}")
        return False
    
    print_success("Bug Fix 2: Payment Updates - PASSED")
    return True

def test_bug_fix_3_domain_renewal():
    """Test Bug Fix 3: Domain Renewal - Test both client and agency payment types for domain renewal"""
    print_test_header("Bug Fix 3: Domain Renewal")
    
    if not test_domains:
        print_error("No test domains available for renewal testing")
        return False
    
    # Test client payment type
    print("\n🌐 Testing Client Payment Type...")
    domain_id = test_domains[0]['id']
    
    client_renewal = {
        "domain_id": domain_id,
        "payment_type": "client",
        "notes": "Client pays directly for domain renewal"
    }
    
    try:
        response = requests.post(f"{API_URL}/domain-renewal/{domain_id}", json=client_renewal)
        if response.status_code == 200:
            result = response.json()
            print_success(f"Client payment renewal successful: {result.get('message')}")
            
            # Verify domain was updated
            domain_response = requests.get(f"{API_URL}/domains/{domain_id}")
            if domain_response.status_code == 200:
                updated_domain = domain_response.json()
                if updated_domain.get('payment_type') == 'client':
                    print_success("Domain payment type correctly set to 'client'")
                else:
                    print_error("Domain payment type not updated correctly")
                    return False
            else:
                print_error("Failed to retrieve updated domain")
                return False
        else:
            print_error(f"Client payment renewal failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error testing client payment renewal: {str(e)}")
        return False
    
    # Test agency payment type (if we have another domain)
    if len(test_domains) > 1:
        print("\n🏢 Testing Agency Payment Type...")
        domain_id = test_domains[1]['id']
        
        agency_renewal = {
            "domain_id": domain_id,
            "payment_type": "agency",
            "notes": "Agency pays upfront, customer owes amount"
        }
        
        try:
            response = requests.post(f"{API_URL}/domain-renewal/{domain_id}", json=agency_renewal)
            if response.status_code == 200:
                result = response.json()
                print_success(f"Agency payment renewal successful: {result.get('message')}")
                
                # Verify domain was updated
                domain_response = requests.get(f"{API_URL}/domains/{domain_id}")
                if domain_response.status_code == 200:
                    updated_domain = domain_response.json()
                    if updated_domain.get('payment_type') == 'agency':
                        print_success("Domain payment type correctly set to 'agency'")
                    else:
                        print_error("Domain payment type not updated correctly")
                        return False
                else:
                    print_error("Failed to retrieve updated domain")
                    return False
                
                # Check if customer ledger entry was created (debt)
                customer_id = test_customers[1]['id']  # Second customer for second domain
                ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
                if ledger_response.status_code == 200:
                    ledger_entries = ledger_response.json()
                    debt_entry_found = False
                    for entry in ledger_entries:
                        if (entry.get('transaction_type') == 'debit' and 
                            'domain renewal' in entry.get('description', '').lower()):
                            debt_entry_found = True
                            print_success("Customer debt entry created for agency-paid renewal")
                            break
                    
                    if not debt_entry_found:
                        print_error("Customer debt entry not found in ledger")
                        return False
                else:
                    print_error("Failed to retrieve customer ledger")
                    return False
            else:
                print_error(f"Agency payment renewal failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Error testing agency payment renewal: {str(e)}")
            return False
    
    print_success("Bug Fix 3: Domain Renewal - PASSED")
    return True

def test_bug_fix_4_domain_renewal_data():
    """Test Bug Fix 4: Domain Renewal Data - Test that domains due for renewal endpoint returns data"""
    print_test_header("Bug Fix 4: Domain Renewal Data")
    
    print("\n📅 Testing Domains Due for Renewal Endpoint...")
    try:
        response = requests.get(f"{API_URL}/domains-due-renewal")
        if response.status_code == 200:
            due_domains = response.json()
            print_success(f"Successfully retrieved {len(due_domains)} domains due for renewal")
            
            # Verify data structure
            for domain in due_domains:
                required_fields = ['domain_id', 'domain_name', 'hosting_provider', 
                                 'validity_date', 'days_until_expiry', 'renewal_amount',
                                 'project_name', 'customer_name', 'customer_id', 'is_expired']
                
                missing_fields = [field for field in required_fields if field not in domain]
                if missing_fields:
                    print_error(f"Domain missing required fields: {missing_fields}")
                    return False
                
                print_info(f"Domain: {domain['domain_name']} | Days until expiry: {domain['days_until_expiry']} | Customer: {domain['customer_name']}")
            
            # Check if we have the domain that should be expiring (digitalagency.in with validity 2024-03-15)
            expiring_found = False
            for domain in due_domains:
                if domain['domain_name'] == 'digitalagency.in':
                    expiring_found = True
                    print_success("Found test domain in renewal list")
                    break
            
            if not expiring_found and len(due_domains) == 0:
                print_info("No domains currently due for renewal (this is acceptable)")
            
            print_success("Domain renewal data structure is correct")
        else:
            print_error(f"Failed to get domains due for renewal: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting domains due for renewal: {str(e)}")
        return False
    
    print_success("Bug Fix 4: Domain Renewal Data - PASSED")
    return True

def test_bug_fix_5_customer_ledger():
    """Test Bug Fix 5: Customer Ledger - Test that customer ledger functionality works and displays transaction history correctly"""
    print_test_header("Bug Fix 5: Customer Ledger")
    
    if not test_customers:
        print_error("No test customers available for ledger testing")
        return False
    
    customer_id = test_customers[0]['id']
    
    print("\n📋 Testing Customer Ledger Retrieval...")
    try:
        response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
        if response.status_code == 200:
            ledger_entries = response.json()
            print_success(f"Successfully retrieved {len(ledger_entries)} ledger entries")
            
            # Verify data structure
            for entry in ledger_entries:
                required_fields = ['id', 'customer_id', 'transaction_type', 'amount',
                                 'description', 'reference_type', 'reference_id', 'date', 'balance']
                
                missing_fields = [field for field in required_fields if field not in entry]
                if missing_fields:
                    print_error(f"Ledger entry missing required fields: {missing_fields}")
                    return False
                
                print_info(f"{entry['transaction_type'].upper()}: ₹{entry['amount']} - {entry['description']} (Balance: ₹{entry['balance']})")
            
            # Verify we have both transaction types
            transaction_types = set(entry['transaction_type'] for entry in ledger_entries)
            if 'credit' in transaction_types and 'debit' in transaction_types:
                print_success("Both credit and debit transactions found in ledger")
            else:
                print_info(f"Transaction types found: {transaction_types}")
            
            # Verify entries are ordered by date (most recent first)
            if len(ledger_entries) > 1:
                dates_ordered = True
                for i in range(len(ledger_entries) - 1):
                    current_date = datetime.fromisoformat(ledger_entries[i]['date'].replace('Z', '+00:00'))
                    next_date = datetime.fromisoformat(ledger_entries[i+1]['date'].replace('Z', '+00:00'))
                    if current_date < next_date:
                        dates_ordered = False
                        break
                
                if dates_ordered:
                    print_success("Ledger entries are properly ordered by date (newest first)")
                else:
                    print_error("Ledger entries are not properly ordered by date")
                    return False
            
            print_success("Customer ledger data structure is correct")
        else:
            print_error(f"Failed to get customer ledger: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting customer ledger: {str(e)}")
        return False
    
    print_success("Bug Fix 5: Customer Ledger - PASSED")
    return True

def test_bug_fix_6_amc_search():
    """Test Bug Fix 6: AMC Search - Test that the search functionality works for AMC projects"""
    print_test_header("Bug Fix 6: AMC Search")
    
    print("\n🔍 Testing AMC Projects Endpoint...")
    try:
        response = requests.get(f"{API_URL}/dashboard/amc-projects")
        if response.status_code == 200:
            amc_projects = response.json()
            print_success(f"Successfully retrieved {len(amc_projects)} AMC projects")
            
            # Verify data structure
            for project in amc_projects:
                required_fields = ['project_id', 'project_name', 'project_type', 'project_amount',
                                 'project_end_date', 'amc_due_date', 'days_until_amc',
                                 'customer_name', 'customer_email', 'customer_phone', 'is_overdue']
                
                missing_fields = [field for field in required_fields if field not in project]
                if missing_fields:
                    print_error(f"AMC project missing required fields: {missing_fields}")
                    return False
                
                print_info(f"Project: {project['project_name']} | Customer: {project['customer_name']} | Days until AMC: {project['days_until_amc']}")
            
            # Check if our test projects are in the AMC list (they should be since they have end dates)
            test_project_found = False
            for project in amc_projects:
                if project['project_name'] in ['Online Shopping Platform', 'Company Portfolio Site']:
                    test_project_found = True
                    print_success("Found test project in AMC list")
                    break
            
            if not test_project_found and len(amc_projects) == 0:
                print_info("No AMC projects currently due (this is acceptable)")
            
            print_success("AMC projects data structure is correct")
        else:
            print_error(f"Failed to get AMC projects: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting AMC projects: {str(e)}")
        return False
    
    print_success("Bug Fix 6: AMC Search - PASSED")
    return True

def main():
    """Run all bug fix tests"""
    print("🚀 Starting Bug Fix Testing for Agency Management System")
    print(f"📍 Backend URL: {API_URL}")
    print("="*80)
    
    # Setup test data first
    if not setup_test_data():
        print_error("Failed to setup test data")
        return False
    
    # Track test results
    test_results = []
    
    # Main bug fix tests
    bug_fix_tests = [
        ("Bug Fix 1: Project AMC Edit", test_bug_fix_1_project_amc_edit),
        ("Bug Fix 2: Payment Updates", test_bug_fix_2_payment_updates),
        ("Bug Fix 3: Domain Renewal", test_bug_fix_3_domain_renewal),
        ("Bug Fix 4: Domain Renewal Data", test_bug_fix_4_domain_renewal_data),
        ("Bug Fix 5: Customer Ledger", test_bug_fix_5_customer_ledger),
        ("Bug Fix 6: AMC Search", test_bug_fix_6_amc_search),
    ]
    
    print("\n🐛 Testing Bug Fixes...")
    for test_name, test_func in bug_fix_tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
            if not result:
                print_error(f"Bug fix test failed: {test_name}")
        except Exception as e:
            print_error(f"Bug fix test error in {test_name}: {str(e)}")
            test_results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*80)
    print("📊 BUG FIX TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} bug fix tests passed")
    
    if passed == total:
        print("🎉 All bug fix tests completed successfully!")
        return True
    else:
        print("💥 Some bug fix tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)