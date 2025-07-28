#!/usr/bin/env python3
"""
Critical Bug Fixes Testing for Agency Management System
Tests the 6 critical bug fixes that were just implemented:

1. Customer Ledger Debt Tracking and Advance Payment Processing
2. Domain Renewal Payment System - Both Client and Agency Options  
3. Enhanced Payment System Balance Calculations
4. API Endpoints testing
5. Data Consistency Tests
6. Balance calculation logic fixes
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
print(f"🔗 Testing Critical Bug Fixes at: {API_URL}")

# Test data storage
test_customers = []
test_projects = []
test_domains = []

def print_test_header(test_name):
    print(f"\n{'='*80}")
    print(f"🧪 CRITICAL BUG FIX TEST: {test_name}")
    print(f"{'='*80}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def setup_test_data():
    """Setup test customers, projects, and domains for testing"""
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
    
    print("\n📝 Creating test customers...")
    for customer_data in customers_data:
        try:
            response = requests.post(f"{API_URL}/customers", json=customer_data)
            if response.status_code == 200:
                customer = response.json()
                test_customers.append(customer)
                print_success(f"Created customer: {customer['name']} (ID: {customer['id']})")
            else:
                print_error(f"Failed to create customer {customer_data['name']}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating customer {customer_data['name']}: {str(e)}")
            return False
    
    # Create test projects
    projects_data = [
        {
            "customer_id": test_customers[0]['id'],
            "type": "E-commerce Website",
            "name": "Online Electronics Store",
            "amount": 50000.00,
            "amc_amount": 12000.00,
            "start_date": "2024-01-15",
            "end_date": "2024-04-15"
        },
        {
            "customer_id": test_customers[1]['id'],
            "type": "Corporate Website",
            "name": "Digital Agency Portfolio",
            "amount": 35000.00,
            "amc_amount": 8000.00,
            "start_date": "2024-02-01",
            "end_date": "2024-05-01"
        }
    ]
    
    print("\n📝 Creating test projects...")
    for project_data in projects_data:
        try:
            response = requests.post(f"{API_URL}/projects", json=project_data)
            if response.status_code == 200:
                project = response.json()
                test_projects.append(project)
                print_success(f"Created project: {project['name']} (ID: {project['id']})")
            else:
                print_error(f"Failed to create project {project_data['name']}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating project {project_data['name']}: {str(e)}")
            return False
    
    # Create test domains
    domains_data = [
        {
            "project_id": test_projects[0]['id'],
            "domain_name": "electronics-store.in",
            "hosting_provider": "AWS India",
            "username": "admin_electronics",
            "password": "SecurePass123!",
            "validity_date": "2024-12-31",
            "renewal_amount": 2500.00
        },
        {
            "project_id": test_projects[1]['id'],
            "domain_name": "digitalagency.in",
            "hosting_provider": "DigitalOcean India",
            "username": "admin_agency",
            "password": "AgencyPass456!",
            "validity_date": "2025-01-15",
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
                print_success(f"Created domain: {domain['domain_name']} (ID: {domain['id']})")
            else:
                print_error(f"Failed to create domain {domain_data['domain_name']}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating domain {domain_data['domain_name']}: {str(e)}")
            return False
    
    print_success("Test data setup completed successfully")
    return True

def test_customer_ledger_debt_tracking():
    """Test Customer Ledger Debt Tracking and Advance Payment Processing"""
    print_test_header("Customer Ledger Debt Tracking and Advance Payment Processing")
    
    if not test_customers or not test_projects:
        print_error("Test data not available")
        return False
    
    customer_id = test_customers[0]['id']
    project_id = test_projects[0]['id']
    
    # Test 1: Verify customer ledger entry was created on project creation
    print("\n💰 Testing Automatic Customer Ledger Entry on Project Creation...")
    try:
        response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
        if response.status_code == 200:
            ledger_entries = response.json()
            
            # Find project creation entry
            project_entry = None
            for entry in ledger_entries:
                if (entry.get('reference_type') == 'project' and 
                    entry.get('reference_id') == project_id and
                    entry.get('transaction_type') == 'debit'):
                    project_entry = entry
                    break
            
            if project_entry:
                print_success("✅ Customer ledger entry created on project creation")
                print_info(f"   Debit Amount: ₹{project_entry['amount']}")
                print_info(f"   Description: {project_entry['description']}")
                print_info(f"   Balance after transaction: ₹{project_entry['balance']}")
                
                # Verify amount matches project amount
                if project_entry['amount'] == test_projects[0]['amount']:
                    print_success("✅ Ledger entry amount matches project amount")
                else:
                    print_error(f"❌ Amount mismatch - Project: ₹{test_projects[0]['amount']}, Ledger: ₹{project_entry['amount']}")
                    return False
            else:
                print_error("❌ Customer ledger entry not found for project creation")
                return False
        else:
            print_error(f"Failed to get customer ledger: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing customer ledger: {str(e)}")
        return False
    
    # Test 2: Test advance payment processing and balance updates
    print("\n💳 Testing Advance Payment Processing and Balance Updates...")
    
    # Get initial balance
    try:
        balance_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
        if balance_response.status_code == 200:
            initial_summary = balance_response.json()
            initial_balance = initial_summary['credit_balance']
            print_info(f"Initial customer balance: ₹{initial_balance}")
        else:
            print_error("Failed to get initial balance")
            return False
    except Exception as e:
        print_error(f"Error getting initial balance: {str(e)}")
        return False
    
    # Record advance payment
    advance_payment = {
        "customer_id": customer_id,
        "type": "project_advance",
        "reference_id": project_id,
        "amount": 25000.00,
        "description": "Advance payment for Online Electronics Store project"
    }
    
    try:
        payment_response = requests.post(f"{API_URL}/payments", json=advance_payment)
        if payment_response.status_code == 200:
            payment = payment_response.json()
            print_success("✅ Advance payment recorded successfully")
            print_info(f"   Payment Amount: ₹{payment['amount']}")
            print_info(f"   Payment Type: {payment['type']}")
            
            # Verify balance updated correctly
            updated_balance_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
            if updated_balance_response.status_code == 200:
                updated_summary = updated_balance_response.json()
                updated_balance = updated_summary['credit_balance']
                expected_balance = initial_balance + advance_payment['amount']
                
                print_info(f"Updated customer balance: ₹{updated_balance}")
                print_info(f"Expected balance: ₹{expected_balance}")
                
                if abs(updated_balance - expected_balance) < 0.01:
                    print_success("✅ Customer balance updated correctly after advance payment")
                else:
                    print_error(f"❌ Balance calculation error - Expected: ₹{expected_balance}, Got: ₹{updated_balance}")
                    return False
            else:
                print_error("Failed to get updated balance")
                return False
            
            # Verify credit entry in ledger
            ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
            if ledger_response.status_code == 200:
                ledger_entries = ledger_response.json()
                
                credit_entry = None
                for entry in ledger_entries:
                    if (entry.get('transaction_type') == 'credit' and 
                        entry.get('amount') == advance_payment['amount'] and
                        'Advance payment' in entry.get('description', '')):
                        credit_entry = entry
                        break
                
                if credit_entry:
                    print_success("✅ Credit entry created in customer ledger for advance payment")
                    print_info(f"   Credit Amount: ₹{credit_entry['amount']}")
                    print_info(f"   Balance after credit: ₹{credit_entry['balance']}")
                else:
                    print_error("❌ Credit entry not found in customer ledger")
                    return False
            else:
                print_error("Failed to get updated ledger")
                return False
        else:
            print_error(f"Failed to record advance payment: {payment_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error recording advance payment: {str(e)}")
        return False
    
    # Test 3: Verify negative balance shows debt correctly
    print("\n📊 Testing Debt Calculation Logic...")
    
    # Create another project to increase debt
    debt_project = {
        "customer_id": customer_id,
        "type": "Mobile App",
        "name": "Electronics Store Mobile App",
        "amount": 40000.00,
        "amc_amount": 10000.00,
        "start_date": "2024-03-01",
        "end_date": "2024-07-01"
    }
    
    try:
        project_response = requests.post(f"{API_URL}/projects", json=debt_project)
        if project_response.status_code == 200:
            new_project = project_response.json()
            test_projects.append(new_project)
            print_success("✅ Additional project created to test debt calculation")
            
            # Check final balance
            final_balance_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
            if final_balance_response.status_code == 200:
                final_summary = final_balance_response.json()
                final_balance = final_summary['credit_balance']
                
                print_info(f"Final customer balance: ₹{final_balance}")
                
                # Calculate expected balance manually
                # Initial: 0, Project 1: -50000, Advance payment: +25000, Project 2: -40000
                # Expected: -65000
                expected_final = -65000.00
                
                if abs(final_balance - expected_final) < 0.01:
                    print_success("✅ Debt calculation logic working correctly")
                    if final_balance < 0:
                        print_success(f"✅ Negative balance correctly shows customer debt: ₹{abs(final_balance)}")
                    else:
                        print_info("Customer has credit balance")
                else:
                    print_error(f"❌ Debt calculation error - Expected: ₹{expected_final}, Got: ₹{final_balance}")
                    return False
            else:
                print_error("Failed to get final balance")
                return False
        else:
            print_error(f"Failed to create additional project: {project_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing debt calculation: {str(e)}")
        return False
    
    print_success("Customer Ledger Debt Tracking and Advance Payment Processing tests PASSED")
    return True

def test_domain_renewal_payment_system():
    """Test Domain Renewal Payment System - Both Client and Agency Options"""
    print_test_header("Domain Renewal Payment System - Both Client and Agency Options")
    
    if not test_domains or not test_customers:
        print_error("Test data not available")
        return False
    
    # Test 1: Domain renewal with CLIENT payment type
    print("\n🌐 Testing Domain Renewal with CLIENT Payment Type...")
    domain_id = test_domains[0]['id']
    customer_id = test_customers[0]['id']
    
    # Get initial domain state
    try:
        domain_response = requests.get(f"{API_URL}/domains/{domain_id}")
        if domain_response.status_code == 200:
            initial_domain = domain_response.json()
            initial_validity = initial_domain['validity_date']
            print_info(f"Initial domain validity: {initial_validity}")
        else:
            print_error("Failed to get initial domain state")
            return False
    except Exception as e:
        print_error(f"Error getting initial domain: {str(e)}")
        return False
    
    # Perform client renewal
    client_renewal = {
        "domain_id": domain_id,
        "payment_type": "client",
        "notes": "Client pays directly for domain renewal"
    }
    
    try:
        renewal_response = requests.post(f"{API_URL}/domain-renewal/{domain_id}", json=client_renewal)
        if renewal_response.status_code == 200:
            result = renewal_response.json()
            print_success("✅ Domain renewal with client payment completed")
            print_info(f"   Result: {result.get('message')}")
            print_info(f"   New validity date: {result.get('new_validity_date')}")
            
            # Verify domain was updated
            updated_domain_response = requests.get(f"{API_URL}/domains/{domain_id}")
            if updated_domain_response.status_code == 200:
                updated_domain = updated_domain_response.json()
                
                # Check validity date extended by 1 year
                initial_date = datetime.fromisoformat(initial_validity).date()
                updated_date = datetime.fromisoformat(updated_domain['validity_date']).date()
                expected_date = initial_date + timedelta(days=365)
                
                if updated_date == expected_date:
                    print_success("✅ Domain validity extended by 1 year correctly")
                else:
                    print_error(f"❌ Validity date error - Expected: {expected_date}, Got: {updated_date}")
                    return False
                
                # Check payment type
                if updated_domain.get('payment_type') == 'client':
                    print_success("✅ Domain payment type set to 'client' correctly")
                else:
                    print_error(f"❌ Payment type error - Expected: client, Got: {updated_domain.get('payment_type')}")
                    return False
            else:
                print_error("Failed to get updated domain")
                return False
            
            # Verify completed payment record created (no ledger debt)
            payments_response = requests.get(f"{API_URL}/payments/customer/{customer_id}")
            if payments_response.status_code == 200:
                payments = payments_response.json()
                
                client_payment = None
                for payment in payments:
                    if (payment.get('type') == 'domain_renewal_client' and 
                        payment.get('reference_id') == domain_id):
                        client_payment = payment
                        break
                
                if client_payment:
                    print_success("✅ Completed payment record created for client renewal")
                    print_info(f"   Payment status: {client_payment['status']}")
                    print_info(f"   Payment amount: ₹{client_payment['amount']}")
                    
                    if client_payment['status'] == 'completed':
                        print_success("✅ Payment status correctly set to 'completed'")
                    else:
                        print_error(f"❌ Payment status error - Expected: completed, Got: {client_payment['status']}")
                        return False
                else:
                    print_error("❌ Client payment record not found")
                    return False
            else:
                print_error("Failed to get customer payments")
                return False
        else:
            print_error(f"Failed to renew domain with client payment: {renewal_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing client renewal: {str(e)}")
        return False
    
    # Test 2: Domain renewal with AGENCY payment type
    print("\n🏢 Testing Domain Renewal with AGENCY Payment Type...")
    if len(test_domains) > 1:
        domain_id = test_domains[1]['id']
        customer_id = test_customers[1]['id']
        
        # Get initial customer balance
        try:
            balance_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
            if balance_response.status_code == 200:
                initial_summary = balance_response.json()
                initial_balance = initial_summary['credit_balance']
                print_info(f"Initial customer balance: ₹{initial_balance}")
            else:
                print_error("Failed to get initial balance")
                return False
        except Exception as e:
            print_error(f"Error getting initial balance: {str(e)}")
            return False
        
        # Perform agency renewal
        agency_renewal = {
            "domain_id": domain_id,
            "payment_type": "agency",
            "notes": "Agency pays upfront, customer owes amount"
        }
        
        try:
            renewal_response = requests.post(f"{API_URL}/domain-renewal/{domain_id}", json=agency_renewal)
            if renewal_response.status_code == 200:
                result = renewal_response.json()
                print_success("✅ Domain renewal with agency payment completed")
                print_info(f"   Result: {result.get('message')}")
                
                # Verify domain payment type
                updated_domain_response = requests.get(f"{API_URL}/domains/{domain_id}")
                if updated_domain_response.status_code == 200:
                    updated_domain = updated_domain_response.json()
                    
                    if updated_domain.get('payment_type') == 'agency':
                        print_success("✅ Domain payment type set to 'agency' correctly")
                    else:
                        print_error(f"❌ Payment type error - Expected: agency, Got: {updated_domain.get('payment_type')}")
                        return False
                else:
                    print_error("Failed to get updated domain")
                    return False
                
                # Verify customer ledger debit entry created
                ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
                if ledger_response.status_code == 200:
                    ledger_entries = ledger_response.json()
                    
                    debit_entry = None
                    for entry in ledger_entries:
                        if (entry.get('transaction_type') == 'debit' and 
                            entry.get('reference_type') == 'domain_renewal' and
                            entry.get('reference_id') == domain_id):
                            debit_entry = entry
                            break
                    
                    if debit_entry:
                        print_success("✅ Customer ledger debit entry created for agency payment")
                        print_info(f"   Debit amount: ₹{debit_entry['amount']}")
                        print_info(f"   Description: {debit_entry['description']}")
                        print_info(f"   Balance after debit: ₹{debit_entry['balance']}")
                        
                        # Verify balance calculation
                        expected_balance = initial_balance - debit_entry['amount']
                        if abs(debit_entry['balance'] - expected_balance) < 0.01:
                            print_success("✅ Balance calculation correct for agency payment")
                        else:
                            print_error(f"❌ Balance calculation error - Expected: ₹{expected_balance}, Got: ₹{debit_entry['balance']}")
                            return False
                    else:
                        print_error("❌ Customer ledger debit entry not found")
                        return False
                else:
                    print_error("Failed to get customer ledger")
                    return False
                
                # Verify pending payment record created
                payments_response = requests.get(f"{API_URL}/payments/customer/{customer_id}")
                if payments_response.status_code == 200:
                    payments = payments_response.json()
                    
                    agency_payment = None
                    for payment in payments:
                        if (payment.get('type') == 'domain_renewal_agency' and 
                            payment.get('reference_id') == domain_id):
                            agency_payment = payment
                            break
                    
                    if agency_payment:
                        print_success("✅ Pending payment record created for agency renewal")
                        print_info(f"   Payment status: {agency_payment['status']}")
                        print_info(f"   Payment amount: ₹{agency_payment['amount']}")
                        
                        if agency_payment['status'] == 'pending':
                            print_success("✅ Payment status correctly set to 'pending'")
                        else:
                            print_error(f"❌ Payment status error - Expected: pending, Got: {agency_payment['status']}")
                            return False
                    else:
                        print_error("❌ Agency payment record not found")
                        return False
                else:
                    print_error("Failed to get customer payments")
                    return False
            else:
                print_error(f"Failed to renew domain with agency payment: {renewal_response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error testing agency renewal: {str(e)}")
            return False
    
    print_success("Domain Renewal Payment System tests PASSED")
    return True

def test_enhanced_payment_system_balance_calculations():
    """Test Enhanced Payment System Balance Calculations"""
    print_test_header("Enhanced Payment System Balance Calculations")
    
    if not test_customers or not test_projects:
        print_error("Test data not available")
        return False
    
    customer_id = test_customers[0]['id']
    
    # Test 1: Payment recording with correct balance calculation
    print("\n💳 Testing Payment Recording with Balance Calculation...")
    
    # Get current balance
    try:
        balance_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
        if balance_response.status_code == 200:
            current_summary = balance_response.json()
            current_balance = current_summary['credit_balance']
            print_info(f"Current customer balance: ₹{current_balance}")
        else:
            print_error("Failed to get current balance")
            return False
    except Exception as e:
        print_error(f"Error getting current balance: {str(e)}")
        return False
    
    # Record a payment
    test_payment = {
        "customer_id": customer_id,
        "type": "project_advance",
        "reference_id": test_projects[0]['id'],
        "amount": 15000.00,
        "description": "Additional payment for balance calculation test"
    }
    
    try:
        payment_response = requests.post(f"{API_URL}/payments", json=test_payment)
        if payment_response.status_code == 200:
            payment = payment_response.json()
            print_success("✅ Payment recorded successfully")
            
            # Verify balance updated correctly
            updated_balance_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
            if updated_balance_response.status_code == 200:
                updated_summary = updated_balance_response.json()
                updated_balance = updated_summary['credit_balance']
                expected_balance = current_balance + test_payment['amount']
                
                print_info(f"Updated balance: ₹{updated_balance}")
                print_info(f"Expected balance: ₹{expected_balance}")
                
                if abs(updated_balance - expected_balance) < 0.01:
                    print_success("✅ Balance calculation correct after payment recording")
                else:
                    print_error(f"❌ Balance calculation error - Expected: ₹{expected_balance}, Got: ₹{updated_balance}")
                    return False
            else:
                print_error("Failed to get updated balance")
                return False
        else:
            print_error(f"Failed to record payment: {payment_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error recording payment: {str(e)}")
        return False
    
    # Test 2: AMC payment processing with balance updates
    print("\n🔄 Testing AMC Payment Processing with Balance Updates...")
    
    # Find project with AMC amount
    amc_project = None
    for project in test_projects:
        if project.get('amc_amount', 0) > 0:
            amc_project = project
            break
    
    if not amc_project:
        print_error("No project with AMC amount found")
        return False
    
    # Get balance before AMC payment
    try:
        pre_amc_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
        if pre_amc_response.status_code == 200:
            pre_amc_summary = pre_amc_response.json()
            pre_amc_balance = pre_amc_summary['credit_balance']
            print_info(f"Balance before AMC payment: ₹{pre_amc_balance}")
        else:
            print_error("Failed to get pre-AMC balance")
            return False
    except Exception as e:
        print_error(f"Error getting pre-AMC balance: {str(e)}")
        return False
    
    # Record AMC payment
    amc_payment_data = {
        "project_id": amc_project['id'],
        "amount": amc_project['amc_amount'],
        "payment_date": datetime.utcnow().isoformat()
    }
    
    try:
        amc_response = requests.post(f"{API_URL}/amc-payment/{amc_project['id']}", json=amc_payment_data)
        if amc_response.status_code == 200:
            result = amc_response.json()
            print_success("✅ AMC payment recorded successfully")
            print_info(f"   Result: {result.get('message')}")
            
            # Verify balance updated correctly
            post_amc_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
            if post_amc_response.status_code == 200:
                post_amc_summary = post_amc_response.json()
                post_amc_balance = post_amc_summary['credit_balance']
                expected_balance = pre_amc_balance + amc_payment_data['amount']
                
                print_info(f"Balance after AMC payment: ₹{post_amc_balance}")
                print_info(f"Expected balance: ₹{expected_balance}")
                
                if abs(post_amc_balance - expected_balance) < 0.01:
                    print_success("✅ Balance calculation correct after AMC payment")
                else:
                    print_error(f"❌ AMC balance calculation error - Expected: ₹{expected_balance}, Got: ₹{post_amc_balance}")
                    return False
            else:
                print_error("Failed to get post-AMC balance")
                return False
        else:
            print_error(f"Failed to record AMC payment: {amc_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error recording AMC payment: {str(e)}")
        return False
    
    print_success("Enhanced Payment System Balance Calculations tests PASSED")
    return True

def test_api_endpoints():
    """Test all critical API endpoints"""
    print_test_header("Critical API Endpoints Testing")
    
    if not test_customers or not test_projects or not test_domains:
        print_error("Test data not available")
        return False
    
    customer_id = test_customers[0]['id']
    project_id = test_projects[0]['id']
    domain_id = test_domains[0]['id']
    
    # Test 1: GET /api/ledger/customer/{customer_id}
    print("\n📋 Testing Customer Ledger API...")
    try:
        response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
        if response.status_code == 200:
            ledger_entries = response.json()
            print_success(f"✅ Customer ledger API working - {len(ledger_entries)} entries")
            
            # Verify data structure
            if ledger_entries:
                entry = ledger_entries[0]
                required_fields = ['id', 'customer_id', 'transaction_type', 'amount', 'description', 'reference_type', 'reference_id', 'date', 'balance']
                missing_fields = [field for field in required_fields if field not in entry]
                
                if not missing_fields:
                    print_success("✅ Ledger entry structure is correct")
                else:
                    print_error(f"❌ Missing fields in ledger entry: {missing_fields}")
                    return False
        else:
            print_error(f"Customer ledger API failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing customer ledger API: {str(e)}")
        return False
    
    # Test 2: GET /api/domains-due-renewal
    print("\n📅 Testing Domains Due Renewal API...")
    try:
        response = requests.get(f"{API_URL}/domains-due-renewal")
        if response.status_code == 200:
            due_domains = response.json()
            print_success(f"✅ Domains due renewal API working - {len(due_domains)} domains")
            
            # Verify data structure
            if due_domains:
                domain = due_domains[0]
                required_fields = ['domain_id', 'domain_name', 'hosting_provider', 'validity_date', 'days_until_expiry', 'renewal_amount', 'project_name', 'customer_name', 'customer_id', 'is_expired']
                missing_fields = [field for field in required_fields if field not in domain]
                
                if not missing_fields:
                    print_success("✅ Due domains structure is correct")
                else:
                    print_error(f"❌ Missing fields in due domains: {missing_fields}")
                    return False
        else:
            print_error(f"Domains due renewal API failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing domains due renewal API: {str(e)}")
        return False
    
    # Test 3: GET /api/customer-payment-summary/{customer_id}
    print("\n💰 Testing Customer Payment Summary API...")
    try:
        response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
        if response.status_code == 200:
            summary = response.json()
            print_success("✅ Customer payment summary API working")
            
            # Verify data structure
            required_fields = ['customer_id', 'customer_name', 'total_projects', 'total_project_amount', 'total_paid_amount', 'outstanding_amount', 'credit_balance', 'recent_payments']
            missing_fields = [field for field in required_fields if field not in summary]
            
            if not missing_fields:
                print_success("✅ Payment summary structure is correct")
                print_info(f"   Customer: {summary['customer_name']}")
                print_info(f"   Total Projects: {summary['total_projects']}")
                print_info(f"   Credit Balance: ₹{summary['credit_balance']}")
            else:
                print_error(f"❌ Missing fields in payment summary: {missing_fields}")
                return False
        else:
            print_error(f"Customer payment summary API failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing customer payment summary API: {str(e)}")
        return False
    
    # Test 4: GET /api/payment-status/{project_id}
    print("\n📊 Testing Payment Status API...")
    try:
        response = requests.get(f"{API_URL}/payment-status/{project_id}")
        if response.status_code == 200:
            status = response.json()
            print_success("✅ Payment status API working")
            
            # Verify data structure
            required_fields = ['project_id', 'total_amount', 'paid_amount', 'remaining_amount', 'payment_status', 'amc_amount', 'amc_due_date', 'amc_paid']
            missing_fields = [field for field in required_fields if field not in status]
            
            if not missing_fields:
                print_success("✅ Payment status structure is correct")
                print_info(f"   Project ID: {status['project_id']}")
                print_info(f"   Payment Status: {status['payment_status']}")
                print_info(f"   Total Amount: ₹{status['total_amount']}")
            else:
                print_error(f"❌ Missing fields in payment status: {missing_fields}")
                return False
        else:
            print_error(f"Payment status API failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing payment status API: {str(e)}")
        return False
    
    print_success("Critical API Endpoints tests PASSED")
    return True

def test_data_consistency():
    """Test Data Consistency across all operations"""
    print_test_header("Data Consistency Testing")
    
    if not test_customers or not test_projects:
        print_error("Test data not available")
        return False
    
    customer_id = test_customers[0]['id']
    
    # Test 1: Create project → verify ledger debit entry created
    print("\n📝 Testing Project Creation → Ledger Entry Consistency...")
    
    consistency_project = {
        "customer_id": customer_id,
        "type": "Consistency Test Project",
        "name": "Data Consistency Verification Project",
        "amount": 30000.00,
        "amc_amount": 6000.00,
        "start_date": "2024-04-01",
        "end_date": "2024-08-01"
    }
    
    try:
        # Get ledger count before
        ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
        if ledger_response.status_code == 200:
            initial_ledger = ledger_response.json()
            initial_count = len(initial_ledger)
        else:
            print_error("Failed to get initial ledger")
            return False
        
        # Create project
        project_response = requests.post(f"{API_URL}/projects", json=consistency_project)
        if project_response.status_code == 200:
            new_project = project_response.json()
            test_projects.append(new_project)
            print_success("✅ Project created successfully")
            
            # Verify ledger entry created
            updated_ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
            if updated_ledger_response.status_code == 200:
                updated_ledger = updated_ledger_response.json()
                new_count = len(updated_ledger)
                
                if new_count == initial_count + 1:
                    print_success("✅ Ledger entry created automatically with project")
                    
                    # Find and verify the entry
                    project_entry = None
                    for entry in updated_ledger:
                        if (entry.get('reference_type') == 'project' and 
                            entry.get('reference_id') == new_project['id']):
                            project_entry = entry
                            break
                    
                    if project_entry and project_entry['amount'] == consistency_project['amount']:
                        print_success("✅ Ledger entry amount matches project amount")
                    else:
                        print_error("❌ Ledger entry amount mismatch")
                        return False
                else:
                    print_error(f"❌ Ledger count mismatch - Expected: {initial_count + 1}, Got: {new_count}")
                    return False
            else:
                print_error("Failed to get updated ledger")
                return False
        else:
            print_error(f"Failed to create consistency project: {project_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing project-ledger consistency: {str(e)}")
        return False
    
    # Test 2: Record advance payment → verify balance increases
    print("\n💳 Testing Payment Recording → Balance Update Consistency...")
    
    try:
        # Get balance before payment
        balance_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
        if balance_response.status_code == 200:
            pre_payment_summary = balance_response.json()
            pre_payment_balance = pre_payment_summary['credit_balance']
        else:
            print_error("Failed to get pre-payment balance")
            return False
        
        # Record payment
        consistency_payment = {
            "customer_id": customer_id,
            "type": "project_advance",
            "reference_id": new_project['id'],
            "amount": 20000.00,
            "description": "Consistency test payment"
        }
        
        payment_response = requests.post(f"{API_URL}/payments", json=consistency_payment)
        if payment_response.status_code == 200:
            print_success("✅ Payment recorded successfully")
            
            # Verify balance updated
            post_payment_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
            if post_payment_response.status_code == 200:
                post_payment_summary = post_payment_response.json()
                post_payment_balance = post_payment_summary['credit_balance']
                expected_balance = pre_payment_balance + consistency_payment['amount']
                
                if abs(post_payment_balance - expected_balance) < 0.01:
                    print_success("✅ Balance updated correctly after payment")
                else:
                    print_error(f"❌ Balance inconsistency - Expected: ₹{expected_balance}, Got: ₹{post_payment_balance}")
                    return False
            else:
                print_error("Failed to get post-payment balance")
                return False
        else:
            print_error(f"Failed to record consistency payment: {payment_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing payment-balance consistency: {str(e)}")
        return False
    
    # Test 3: Manual balance calculation vs API balance
    print("\n🧮 Testing Manual vs API Balance Calculation Consistency...")
    
    try:
        # Get all ledger entries
        ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
        if ledger_response.status_code == 200:
            all_entries = ledger_response.json()
            
            # Calculate balance manually
            manual_balance = 0.0
            for entry in all_entries:
                if entry['transaction_type'] == 'credit':
                    manual_balance += entry['amount']
                else:  # debit
                    manual_balance -= entry['amount']
            
            # Get API balance
            api_balance_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
            if api_balance_response.status_code == 200:
                api_summary = api_balance_response.json()
                api_balance = api_summary['credit_balance']
                
                print_info(f"Manual calculation: ₹{manual_balance}")
                print_info(f"API calculation: ₹{api_balance}")
                
                if abs(manual_balance - api_balance) < 0.01:
                    print_success("✅ Manual and API balance calculations are consistent")
                else:
                    print_error(f"❌ Balance calculation inconsistency - Manual: ₹{manual_balance}, API: ₹{api_balance}")
                    return False
            else:
                print_error("Failed to get API balance")
                return False
        else:
            print_error("Failed to get ledger entries")
            return False
    except Exception as e:
        print_error(f"Error testing balance calculation consistency: {str(e)}")
        return False
    
    print_success("Data Consistency tests PASSED")
    return True

def run_all_critical_tests():
    """Run all critical bug fix tests"""
    print("🚀 Starting Critical Bug Fixes Testing Suite")
    print("=" * 80)
    
    # Setup test data
    if not setup_test_data():
        print_error("Failed to setup test data")
        return False
    
    # Run all critical tests
    tests = [
        ("Customer Ledger Debt Tracking", test_customer_ledger_debt_tracking),
        ("Domain Renewal Payment System", test_domain_renewal_payment_system),
        ("Enhanced Payment System Balance Calculations", test_enhanced_payment_system_balance_calculations),
        ("Critical API Endpoints", test_api_endpoints),
        ("Data Consistency", test_data_consistency)
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
                print_success(f"✅ {test_name} - PASSED")
            else:
                failed_tests += 1
                print_error(f"❌ {test_name} - FAILED")
        except Exception as e:
            failed_tests += 1
            print_error(f"❌ {test_name} - ERROR: {str(e)}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("🏁 CRITICAL BUG FIXES TESTING SUMMARY")
    print("=" * 80)
    print_success(f"✅ PASSED: {passed_tests} tests")
    if failed_tests > 0:
        print_error(f"❌ FAILED: {failed_tests} tests")
    else:
        print_success("🎉 ALL CRITICAL BUG FIXES WORKING CORRECTLY!")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_all_critical_tests()
    sys.exit(0 if success else 1)