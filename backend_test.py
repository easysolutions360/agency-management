#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Agency Management System
Tests all CRUD operations, relationships, and dashboard functionality
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

# Test data
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

def test_api_health():
    """Test basic API health endpoint"""
    print_test_header("API Health Check")
    
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            data = response.json()
            if "message" in data:
                print_success(f"API is healthy: {data['message']}")
                return True
            else:
                print_error("API response missing message field")
                return False
        else:
            print_error(f"API health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"API health check failed: {str(e)}")
        return False

def test_customer_crud():
    """Test Customer CRUD operations"""
    print_test_header("Customer Management API")
    
    # Test data for customers
    customers_data = [
        {
            "name": "Sarah Johnson",
            "phone": "+1-555-0123",
            "email": "sarah.johnson@techcorp.com",
            "address": "123 Business Ave, Tech City, TC 12345"
        },
        {
            "name": "Michael Chen",
            "phone": "+1-555-0456",
            "email": "michael.chen@startupinc.com", 
            "address": "456 Innovation St, Startup Valley, SV 67890"
        }
    ]
    
    # Test CREATE customers
    print("\n📝 Testing Customer Creation...")
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
    
    # Test READ all customers
    print("\n📖 Testing Get All Customers...")
    try:
        response = requests.get(f"{API_URL}/customers")
        if response.status_code == 200:
            customers = response.json()
            print_success(f"Retrieved {len(customers)} customers")
            if len(customers) >= len(test_customers):
                print_success("All created customers found in list")
            else:
                print_error("Not all created customers found in list")
        else:
            print_error(f"Failed to get customers: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting customers: {str(e)}")
        return False
    
    # Test READ individual customer
    print("\n🔍 Testing Get Individual Customer...")
    if test_customers:
        customer_id = test_customers[0]['id']
        try:
            response = requests.get(f"{API_URL}/customers/{customer_id}")
            if response.status_code == 200:
                customer = response.json()
                print_success(f"Retrieved customer: {customer['name']}")
            else:
                print_error(f"Failed to get customer {customer_id}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error getting customer {customer_id}: {str(e)}")
            return False
    
    # Test UPDATE customer
    print("\n✏️  Testing Customer Update...")
    if test_customers:
        customer_id = test_customers[0]['id']
        update_data = {"phone": "+1-555-9999", "address": "999 Updated Ave, New City, NC 99999"}
        try:
            response = requests.put(f"{API_URL}/customers/{customer_id}", json=update_data)
            if response.status_code == 200:
                updated_customer = response.json()
                if updated_customer['phone'] == update_data['phone']:
                    print_success(f"Updated customer phone: {updated_customer['phone']}")
                    test_customers[0] = updated_customer  # Update our test data
                else:
                    print_error("Customer update did not persist correctly")
                    return False
            else:
                print_error(f"Failed to update customer {customer_id}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error updating customer {customer_id}: {str(e)}")
            return False
    
    # Test error handling - non-existent customer
    print("\n🚫 Testing Error Handling...")
    try:
        response = requests.get(f"{API_URL}/customers/non-existent-id")
        if response.status_code == 404:
            print_success("Correctly returned 404 for non-existent customer")
        else:
            print_error(f"Expected 404 for non-existent customer, got {response.status_code}")
    except Exception as e:
        print_error(f"Error testing non-existent customer: {str(e)}")
    
    print_success("Customer CRUD operations completed successfully")
    return True

def test_project_crud():
    """Test Project CRUD operations with customer relationship validation"""
    print_test_header("Project Management API")
    
    if not test_customers:
        print_error("No test customers available for project testing")
        return False
    
    # Test data for projects
    projects_data = [
        {
            "customer_id": test_customers[0]['id'],
            "type": "E-commerce Website",
            "name": "TechCorp Online Store",
            "amount": 15000.00,
            "start_date": "2024-01-15",
            "end_date": "2024-04-15"
        },
        {
            "customer_id": test_customers[1]['id'],
            "type": "Mobile App Development",
            "name": "StartupInc Mobile App",
            "amount": 25000.00,
            "start_date": "2024-02-01",
            "end_date": "2024-06-01"
        }
    ]
    
    # Test CREATE projects
    print("\n📝 Testing Project Creation...")
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
    
    # Test customer relationship validation
    print("\n🔗 Testing Customer Relationship Validation...")
    invalid_project = {
        "customer_id": "non-existent-customer-id",
        "type": "Test Project",
        "name": "Invalid Customer Project",
        "amount": 1000.00,
        "start_date": "2024-01-01",
        "end_date": "2024-02-01"
    }
    try:
        response = requests.post(f"{API_URL}/projects", json=invalid_project)
        if response.status_code == 404:
            print_success("Correctly rejected project with non-existent customer")
        else:
            print_error(f"Expected 404 for invalid customer, got {response.status_code}")
    except Exception as e:
        print_error(f"Error testing invalid customer: {str(e)}")
    
    # Test READ all projects
    print("\n📖 Testing Get All Projects...")
    try:
        response = requests.get(f"{API_URL}/projects")
        if response.status_code == 200:
            projects = response.json()
            print_success(f"Retrieved {len(projects)} projects")
        else:
            print_error(f"Failed to get projects: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting projects: {str(e)}")
        return False
    
    # Test READ individual project
    print("\n🔍 Testing Get Individual Project...")
    if test_projects:
        project_id = test_projects[0]['id']
        try:
            response = requests.get(f"{API_URL}/projects/{project_id}")
            if response.status_code == 200:
                project = response.json()
                print_success(f"Retrieved project: {project['name']}")
            else:
                print_error(f"Failed to get project {project_id}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error getting project {project_id}: {str(e)}")
            return False
    
    # Test UPDATE project
    print("\n✏️  Testing Project Update...")
    if test_projects:
        project_id = test_projects[0]['id']
        update_data = {"amount": 18000.00, "type": "Enhanced E-commerce Website"}
        try:
            response = requests.put(f"{API_URL}/projects/{project_id}", json=update_data)
            if response.status_code == 200:
                updated_project = response.json()
                if updated_project['amount'] == update_data['amount']:
                    print_success(f"Updated project amount: ${updated_project['amount']}")
                    test_projects[0] = updated_project
                else:
                    print_error("Project update did not persist correctly")
                    return False
            else:
                print_error(f"Failed to update project {project_id}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error updating project {project_id}: {str(e)}")
            return False
    
    print_success("Project CRUD operations completed successfully")
    return True

def test_domain_hosting_crud():
    """Test Domain/Hosting CRUD operations with project relationship validation"""
    print_test_header("Domain/Hosting Management API")
    
    if not test_projects:
        print_error("No test projects available for domain testing")
        return False
    
    # Test data for domains
    domains_data = [
        {
            "project_id": test_projects[0]['id'],
            "domain_name": "techcorp-store.com",
            "hosting_provider": "AWS",
            "username": "techcorp_admin",
            "password": "SecurePass123!",
            "validity_date": "2024-12-31"
        },
        {
            "project_id": test_projects[0]['id'],
            "domain_name": "techcorp.net",
            "hosting_provider": "DigitalOcean",
            "username": "techcorp_backup",
            "password": "BackupPass456!",
            "validity_date": "2025-06-30"
        },
        {
            "project_id": test_projects[1]['id'],
            "domain_name": "startupinc-app.com",
            "hosting_provider": "Google Cloud",
            "username": "startup_admin",
            "password": "StartupSecure789!",
            "validity_date": "2024-03-15"  # This will be expiring soon
        }
    ]
    
    # Test CREATE domains
    print("\n📝 Testing Domain Creation...")
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
    
    # Test project relationship validation
    print("\n🔗 Testing Project Relationship Validation...")
    invalid_domain = {
        "project_id": "non-existent-project-id",
        "domain_name": "invalid-project.com",
        "hosting_provider": "Test Provider",
        "username": "test_user",
        "password": "test_pass",
        "validity_date": "2024-12-31"
    }
    try:
        response = requests.post(f"{API_URL}/domains", json=invalid_domain)
        if response.status_code == 404:
            print_success("Correctly rejected domain with non-existent project")
        else:
            print_error(f"Expected 404 for invalid project, got {response.status_code}")
    except Exception as e:
        print_error(f"Error testing invalid project: {str(e)}")
    
    # Test READ all domains
    print("\n📖 Testing Get All Domains...")
    try:
        response = requests.get(f"{API_URL}/domains")
        if response.status_code == 200:
            domains = response.json()
            print_success(f"Retrieved {len(domains)} domains")
        else:
            print_error(f"Failed to get domains: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting domains: {str(e)}")
        return False
    
    # Test READ domains by project
    print("\n🔍 Testing Get Domains by Project...")
    if test_projects:
        project_id = test_projects[0]['id']
        try:
            response = requests.get(f"{API_URL}/domains/project/{project_id}")
            if response.status_code == 200:
                project_domains = response.json()
                print_success(f"Retrieved {len(project_domains)} domains for project {project_id}")
                # Should have 2 domains for first project
                if len(project_domains) == 2:
                    print_success("Correct number of domains returned for project")
                else:
                    print_error(f"Expected 2 domains for project, got {len(project_domains)}")
            else:
                print_error(f"Failed to get domains for project {project_id}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error getting domains for project {project_id}: {str(e)}")
            return False
    
    # Test READ individual domain
    print("\n🔍 Testing Get Individual Domain...")
    if test_domains:
        domain_id = test_domains[0]['id']
        try:
            response = requests.get(f"{API_URL}/domains/{domain_id}")
            if response.status_code == 200:
                domain = response.json()
                print_success(f"Retrieved domain: {domain['domain_name']}")
            else:
                print_error(f"Failed to get domain {domain_id}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error getting domain {domain_id}: {str(e)}")
            return False
    
    # Test UPDATE domain
    print("\n✏️  Testing Domain Update...")
    if test_domains:
        domain_id = test_domains[0]['id']
        update_data = {"hosting_provider": "AWS Premium", "validity_date": "2025-12-31"}
        try:
            response = requests.put(f"{API_URL}/domains/{domain_id}", json=update_data)
            if response.status_code == 200:
                updated_domain = response.json()
                if updated_domain['hosting_provider'] == update_data['hosting_provider']:
                    print_success(f"Updated domain hosting provider: {updated_domain['hosting_provider']}")
                    test_domains[0] = updated_domain
                else:
                    print_error("Domain update did not persist correctly")
                    return False
            else:
                print_error(f"Failed to update domain {domain_id}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error updating domain {domain_id}: {str(e)}")
            return False
    
    print_success("Domain/Hosting CRUD operations completed successfully")
    return True

def test_dashboard_api():
    """Test Dashboard API with comprehensive data aggregation"""
    print_test_header("Dashboard API with Data Aggregation")
    
    # Test dashboard projects endpoint
    print("\n📊 Testing Dashboard Projects...")
    try:
        response = requests.get(f"{API_URL}/dashboard/projects")
        if response.status_code == 200:
            dashboard_projects = response.json()
            print_success(f"Retrieved {len(dashboard_projects)} dashboard projects")
            
            # Verify data structure and relationships
            for project in dashboard_projects:
                required_fields = ['id', 'customer_name', 'customer_email', 'customer_phone', 
                                 'name', 'type', 'amount', 'domains']
                missing_fields = [field for field in required_fields if field not in project]
                if missing_fields:
                    print_error(f"Project missing fields: {missing_fields}")
                    return False
                
                print_info(f"Project: {project['name']} | Customer: {project['customer_name']} | Domains: {len(project['domains'])}")
            
            print_success("Dashboard projects data structure is correct")
        else:
            print_error(f"Failed to get dashboard projects: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting dashboard projects: {str(e)}")
        return False
    
    print_success("Dashboard API completed successfully")
    return True

def test_expiring_domains():
    """Test expiring domains functionality with current and future dates"""
    print_test_header("Expiring Domains Detection")
    
    # Test expiring domains endpoint
    print("\n⏰ Testing Expiring Domains...")
    try:
        response = requests.get(f"{API_URL}/dashboard/expiring-domains")
        if response.status_code == 200:
            expiring_domains = response.json()
            print_success(f"Retrieved {len(expiring_domains)} expiring domains")
            
            # Verify data structure
            for domain in expiring_domains:
                required_fields = ['domain_name', 'hosting_provider', 'validity_date', 
                                 'project_name', 'customer_name', 'customer_email', 'days_remaining']
                missing_fields = [field for field in required_fields if field not in domain]
                if missing_fields:
                    print_error(f"Expiring domain missing fields: {missing_fields}")
                    return False
                
                print_info(f"Domain: {domain['domain_name']} | Days remaining: {domain['days_remaining']} | Customer: {domain['customer_name']}")
            
            # Check if we have the domain that should be expiring (startupinc-app.com with validity 2024-03-15)
            expiring_found = False
            for domain in expiring_domains:
                if domain['domain_name'] == 'startupinc-app.com':
                    expiring_found = True
                    if domain['days_remaining'] < 30:
                        print_success("Correctly identified domain expiring within 30 days")
                    break
            
            if not expiring_found:
                print_info("Test expiring domain not found (may have already expired)")
            
            print_success("Expiring domains data structure is correct")
        else:
            print_error(f"Failed to get expiring domains: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting expiring domains: {str(e)}")
        return False
    
    print_success("Expiring domains functionality completed successfully")
    return True

def test_enhanced_payment_system():
    """Test Enhanced Payment System with Project AMC Support"""
    print_test_header("Enhanced Payment System with Project AMC Support")
    
    if not test_customers or not test_projects:
        print_error("No test data available for payment testing")
        return False
    
    # Test 1: Create project with AMC amount
    print("\n💰 Testing Project Creation with AMC Amount...")
    project_with_amc = {
        "customer_id": test_customers[0]['id'],
        "type": "Website with AMC",
        "name": "Corporate Website with Annual Maintenance",
        "amount": 20000.00,
        "amc_amount": 5000.00,
        "start_date": "2024-01-01",
        "end_date": "2024-03-01"
    }
    
    try:
        response = requests.post(f"{API_URL}/projects", json=project_with_amc)
        if response.status_code == 200:
            amc_project = response.json()
            test_projects.append(amc_project)
            if amc_project.get('amc_amount') == 5000.00:
                print_success(f"Created project with AMC: {amc_project['name']} (AMC: ${amc_project['amc_amount']})")
            else:
                print_error("AMC amount not stored correctly")
                return False
        else:
            print_error(f"Failed to create project with AMC: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error creating project with AMC: {str(e)}")
        return False
    
    # Test 2: Record advance payment and verify status updates
    print("\n💳 Testing Payment Recording and Status Updates...")
    project_id = test_projects[0]['id']
    
    # Record partial payment
    payment_data = {
        "customer_id": test_customers[0]['id'],
        "type": "project_advance",
        "reference_id": project_id,
        "amount": 8000.00,
        "description": "Advance payment for project development"
    }
    
    try:
        response = requests.post(f"{API_URL}/payments", json=payment_data)
        if response.status_code == 200:
            payment = response.json()
            print_success(f"Recorded payment: ${payment['amount']} for project")
            
            # Check if project payment status updated
            project_response = requests.get(f"{API_URL}/projects/{project_id}")
            if project_response.status_code == 200:
                updated_project = project_response.json()
                if updated_project.get('payment_status') == 'partial':
                    print_success("Project payment status correctly updated to 'partial'")
                else:
                    print_error(f"Expected 'partial' status, got '{updated_project.get('payment_status')}'")
                    return False
            else:
                print_error("Failed to retrieve updated project")
                return False
        else:
            print_error(f"Failed to record payment: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error recording payment: {str(e)}")
        return False
    
    # Test 3: Complete payment and verify 'paid' status
    print("\n💯 Testing Complete Payment...")
    remaining_payment = {
        "customer_id": test_customers[0]['id'],
        "type": "project_advance",
        "reference_id": project_id,
        "amount": 10000.00,  # This should complete the payment (8000 + 10000 = 18000 total)
        "description": "Final payment for project completion"
    }
    
    try:
        response = requests.post(f"{API_URL}/payments", json=remaining_payment)
        if response.status_code == 200:
            print_success("Recorded final payment")
            
            # Check if project payment status updated to 'paid'
            project_response = requests.get(f"{API_URL}/projects/{project_id}")
            if project_response.status_code == 200:
                updated_project = project_response.json()
                if updated_project.get('payment_status') == 'paid':
                    print_success("Project payment status correctly updated to 'paid'")
                else:
                    print_error(f"Expected 'paid' status, got '{updated_project.get('payment_status')}'")
                    return False
            else:
                print_error("Failed to retrieve updated project")
                return False
        else:
            print_error(f"Failed to record final payment: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error recording final payment: {str(e)}")
        return False
    
    print_success("Enhanced Payment System tests completed successfully")
    return True

def test_domain_renewal_payment_system():
    """Test Domain Renewal Payment System with dual payment options"""
    print_test_header("Domain Renewal Payment System")
    
    if not test_domains:
        print_error("No test domains available for renewal testing")
        return False
    
    # Test 1: Client pays for domain renewal
    print("\n🌐 Testing Client-Paid Domain Renewal...")
    domain_id = test_domains[0]['id']
    
    client_renewal = {
        "domain_id": domain_id,
        "payment_type": "client",
        "notes": "Client will pay directly for renewal"
    }
    
    try:
        response = requests.post(f"{API_URL}/domain-renewal/{domain_id}", json=client_renewal)
        if response.status_code == 200:
            result = response.json()
            print_success(f"Domain renewed with client payment: {result.get('message')}")
            
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
            print_error(f"Failed to renew domain with client payment: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing client-paid renewal: {str(e)}")
        return False
    
    # Test 2: Agency pays for domain renewal (creates customer debt)
    print("\n🏢 Testing Agency-Paid Domain Renewal...")
    if len(test_domains) > 1:
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
                print_success(f"Domain renewed with agency payment: {result.get('message')}")
                
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
                customer_id = test_customers[0]['id']  # Assuming domain belongs to first customer
                ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
                if ledger_response.status_code == 200:
                    ledger_entries = ledger_response.json()
                    debt_entry_found = False
                    for entry in ledger_entries:
                        if entry.get('transaction_type') == 'debit' and 'domain renewal' in entry.get('description', '').lower():
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
                print_error(f"Failed to renew domain with agency payment: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error testing agency-paid renewal: {str(e)}")
            return False
    
    print_success("Domain Renewal Payment System tests completed successfully")
    return True

def test_amc_payment_processing():
    """Test AMC Payment Processing with Auto-Renewal"""
    print_test_header("AMC Payment Processing with Auto-Renewal")
    
    if not test_projects:
        print_error("No test projects available for AMC testing")
        return False
    
    # Find project with AMC amount
    amc_project = None
    for project in test_projects:
        if project.get('amc_amount', 0) > 0:
            amc_project = project
            break
    
    if not amc_project:
        print_error("No project with AMC amount found for testing")
        return False
    
    # Test AMC payment recording
    print("\n🔄 Testing AMC Payment Recording...")
    project_id = amc_project['id']
    
    amc_payment_data = {
        "project_id": project_id,
        "amount": amc_project['amc_amount'],
        "payment_date": datetime.utcnow().isoformat()
    }
    
    try:
        response = requests.post(f"{API_URL}/amc-payment/{project_id}", json=amc_payment_data)
        if response.status_code == 200:
            result = response.json()
            print_success(f"AMC payment recorded: {result.get('message')}")
            
            # Verify payment was recorded in payments table
            customer_id = amc_project['customer_id']
            payments_response = requests.get(f"{API_URL}/payments/customer/{customer_id}")
            if payments_response.status_code == 200:
                payments = payments_response.json()
                amc_payment_found = False
                for payment in payments:
                    if payment.get('type') == 'amc_payment' and payment.get('reference_id') == project_id:
                        amc_payment_found = True
                        print_success("AMC payment found in payments table")
                        break
                
                if not amc_payment_found:
                    print_error("AMC payment not found in payments table")
                    return False
            else:
                print_error("Failed to retrieve customer payments")
                return False
            
            # Verify ledger entry was created
            ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
            if ledger_response.status_code == 200:
                ledger_entries = ledger_response.json()
                amc_ledger_found = False
                for entry in ledger_entries:
                    if entry.get('reference_type') == 'amc' and entry.get('reference_id') == project_id:
                        amc_ledger_found = True
                        print_success("AMC payment ledger entry created")
                        break
                
                if not amc_ledger_found:
                    print_error("AMC payment ledger entry not found")
                    return False
            else:
                print_error("Failed to retrieve customer ledger")
                return False
        else:
            print_error(f"Failed to record AMC payment: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error recording AMC payment: {str(e)}")
        return False
    
    print_success("AMC Payment Processing tests completed successfully")
    return True

def test_customer_payment_summary():
    """Test Customer Payment Summary endpoint"""
    print_test_header("Customer Payment Summary")
    
    if not test_customers:
        print_error("No test customers available for payment summary testing")
        return False
    
    customer_id = test_customers[0]['id']
    
    print("\n📊 Testing Customer Payment Summary...")
    try:
        response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
        if response.status_code == 200:
            summary = response.json()
            
            # Verify required fields
            required_fields = ['customer_id', 'customer_name', 'total_projects', 
                             'total_project_amount', 'total_paid_amount', 'outstanding_amount',
                             'credit_balance', 'recent_payments']
            
            missing_fields = [field for field in required_fields if field not in summary]
            if missing_fields:
                print_error(f"Payment summary missing fields: {missing_fields}")
                return False
            
            print_success(f"Customer: {summary['customer_name']}")
            print_info(f"Total Projects: {summary['total_projects']}")
            print_info(f"Total Project Amount: ${summary['total_project_amount']}")
            print_info(f"Total Paid Amount: ${summary['total_paid_amount']}")
            print_info(f"Outstanding Amount: ${summary['outstanding_amount']}")
            print_info(f"Credit Balance: ${summary['credit_balance']}")
            print_info(f"Recent Payments: {len(summary['recent_payments'])}")
            
            # Verify recent payments structure
            for payment in summary['recent_payments']:
                payment_fields = ['date', 'amount', 'type', 'description']
                missing_payment_fields = [field for field in payment_fields if field not in payment]
                if missing_payment_fields:
                    print_error(f"Recent payment missing fields: {missing_payment_fields}")
                    return False
            
            print_success("Customer payment summary structure is correct")
        else:
            print_error(f"Failed to get customer payment summary: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting customer payment summary: {str(e)}")
        return False
    
    print_success("Customer Payment Summary tests completed successfully")
    return True

def test_domains_due_renewal():
    """Test Domains Due for Renewal endpoint"""
    print_test_header("Domains Due for Renewal")
    
    print("\n📅 Testing Domains Due for Renewal...")
    try:
        response = requests.get(f"{API_URL}/domains-due-renewal")
        if response.status_code == 200:
            due_domains = response.json()
            print_success(f"Retrieved {len(due_domains)} domains due for renewal")
            
            # Verify data structure
            for domain in due_domains:
                required_fields = ['domain_id', 'domain_name', 'hosting_provider', 
                                 'validity_date', 'days_until_expiry', 'renewal_amount',
                                 'project_name', 'customer_name', 'customer_id', 'is_expired']
                
                missing_fields = [field for field in required_fields if field not in domain]
                if missing_fields:
                    print_error(f"Due domain missing fields: {missing_fields}")
                    return False
                
                print_info(f"Domain: {domain['domain_name']} | Days until expiry: {domain['days_until_expiry']} | Customer: {domain['customer_name']}")
            
            print_success("Domains due for renewal data structure is correct")
        else:
            print_error(f"Failed to get domains due for renewal: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting domains due for renewal: {str(e)}")
        return False
    
    print_success("Domains Due for Renewal tests completed successfully")
    return True

def test_customer_ledger():
    """Test Customer Ledger functionality"""
    print_test_header("Customer Ledger")
    
    if not test_customers:
        print_error("No test customers available for ledger testing")
        return False
    
    customer_id = test_customers[0]['id']
    
    print("\n📋 Testing Customer Ledger...")
    try:
        response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
        if response.status_code == 200:
            ledger_entries = response.json()
            print_success(f"Retrieved {len(ledger_entries)} ledger entries")
            
            # Verify data structure and transaction types
            transaction_types_found = set()
            for entry in ledger_entries:
                required_fields = ['id', 'customer_id', 'transaction_type', 'amount',
                                 'description', 'reference_type', 'reference_id', 'date', 'balance']
                
                missing_fields = [field for field in required_fields if field not in entry]
                if missing_fields:
                    print_error(f"Ledger entry missing fields: {missing_fields}")
                    return False
                
                transaction_types_found.add(entry['transaction_type'])
                print_info(f"{entry['transaction_type'].upper()}: ${entry['amount']} - {entry['description']} (Balance: ${entry['balance']})")
            
            # Check if we have both credit and debit entries
            if 'credit' in transaction_types_found:
                print_success("Credit transactions found in ledger")
            if 'debit' in transaction_types_found:
                print_success("Debit transactions found in ledger")
            
            print_success("Customer ledger data structure is correct")
        else:
            print_error(f"Failed to get customer ledger: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting customer ledger: {str(e)}")
        return False
    
    print_success("Customer Ledger tests completed successfully")
    return True

def test_payment_status():
    """Test Payment Status endpoint"""
    print_test_header("Payment Status")
    
    if not test_projects:
        print_error("No test projects available for payment status testing")
        return False
    
    project_id = test_projects[0]['id']
    
    print("\n💳 Testing Payment Status...")
    try:
        response = requests.get(f"{API_URL}/payment-status/{project_id}")
        if response.status_code == 200:
            status = response.json()
            
            # Verify required fields
            required_fields = ['project_id', 'total_amount', 'paid_amount', 'remaining_amount',
                             'payment_status', 'amc_amount', 'amc_due_date', 'amc_paid']
            
            missing_fields = [field for field in required_fields if field not in status]
            if missing_fields:
                print_error(f"Payment status missing fields: {missing_fields}")
                return False
            
            print_success(f"Project ID: {status['project_id']}")
            print_info(f"Total Amount: ${status['total_amount']}")
            print_info(f"Paid Amount: ${status['paid_amount']}")
            print_info(f"Remaining Amount: ${status['remaining_amount']}")
            print_info(f"Payment Status: {status['payment_status']}")
            print_info(f"AMC Amount: ${status['amc_amount']}")
            print_info(f"AMC Due Date: {status['amc_due_date']}")
            print_info(f"AMC Paid: {status['amc_paid']}")
            
            print_success("Payment status data structure is correct")
        else:
            print_error(f"Failed to get payment status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting payment status: {str(e)}")
        return False
    
    print_success("Payment Status tests completed successfully")
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    print_test_header("Edge Cases and Error Handling")
    
    # Test 1: Invalid payment amounts
    print("\n❌ Testing Invalid Payment Amounts...")
    if test_customers and test_projects:
        invalid_payment = {
            "customer_id": test_customers[0]['id'],
            "type": "project_advance",
            "reference_id": test_projects[0]['id'],
            "amount": -1000.00,  # Negative amount
            "description": "Invalid negative payment"
        }
        
        try:
            response = requests.post(f"{API_URL}/payments", json=invalid_payment)
            # Should either reject or handle gracefully
            print_info(f"Negative payment response: {response.status_code}")
        except Exception as e:
            print_info(f"Negative payment error handled: {str(e)}")
    
    # Test 2: Payments for non-existent projects
    print("\n❌ Testing Payments for Non-existent Projects...")
    if test_customers:
        nonexistent_payment = {
            "customer_id": test_customers[0]['id'],
            "type": "project_advance",
            "reference_id": "non-existent-project-id",
            "amount": 1000.00,
            "description": "Payment for non-existent project"
        }
        
        try:
            response = requests.post(f"{API_URL}/payments", json=nonexistent_payment)
            print_info(f"Non-existent project payment response: {response.status_code}")
        except Exception as e:
            print_info(f"Non-existent project payment error handled: {str(e)}")
    
    # Test 3: AMC payments for projects without AMC amounts
    print("\n❌ Testing AMC Payments for Projects without AMC...")
    if test_projects:
        # Find a project without AMC amount
        non_amc_project = None
        for project in test_projects:
            if project.get('amc_amount', 0) == 0:
                non_amc_project = project
                break
        
        if non_amc_project:
            amc_payment_data = {
                "project_id": non_amc_project['id'],
                "amount": 1000.00,
                "payment_date": datetime.utcnow().isoformat()
            }
            
            try:
                response = requests.post(f"{API_URL}/amc-payment/{non_amc_project['id']}", json=amc_payment_data)
                print_info(f"AMC payment for non-AMC project response: {response.status_code}")
            except Exception as e:
                print_info(f"AMC payment for non-AMC project error handled: {str(e)}")
    
    # Test 4: Domain renewal for non-existent domain
    print("\n❌ Testing Domain Renewal for Non-existent Domain...")
    renewal_request = {
        "domain_id": "non-existent-domain-id",
        "payment_type": "client",
        "notes": "Test renewal for non-existent domain"
    }
    
    try:
        response = requests.post(f"{API_URL}/domain-renewal/non-existent-domain-id", json=renewal_request)
        if response.status_code == 404:
            print_success("Correctly returned 404 for non-existent domain renewal")
        else:
            print_info(f"Non-existent domain renewal response: {response.status_code}")
    except Exception as e:
        print_info(f"Non-existent domain renewal error handled: {str(e)}")
    
    print_success("Edge Cases and Error Handling tests completed")
    return True

def test_cleanup():
    """Clean up test data (optional - for clean testing environment)"""
    print_test_header("Test Data Cleanup")
    
    # Delete test domains
    print("\n🗑️  Cleaning up test domains...")
    for domain in test_domains:
        try:
            response = requests.delete(f"{API_URL}/domains/{domain['id']}")
            if response.status_code == 200:
                print_success(f"Deleted domain: {domain['domain_name']}")
            else:
                print_error(f"Failed to delete domain {domain['domain_name']}: {response.status_code}")
        except Exception as e:
            print_error(f"Error deleting domain {domain['domain_name']}: {str(e)}")
    
    # Delete test projects
    print("\n🗑️  Cleaning up test projects...")
    for project in test_projects:
        try:
            response = requests.delete(f"{API_URL}/projects/{project['id']}")
            if response.status_code == 200:
                print_success(f"Deleted project: {project['name']}")
            else:
                print_error(f"Failed to delete project {project['name']}: {response.status_code}")
        except Exception as e:
            print_error(f"Error deleting project {project['name']}: {str(e)}")
    
    # Delete test customers
    print("\n🗑️  Cleaning up test customers...")
    for customer in test_customers:
        try:
            response = requests.delete(f"{API_URL}/customers/{customer['id']}")
            if response.status_code == 200:
                print_success(f"Deleted customer: {customer['name']}")
            else:
                print_error(f"Failed to delete customer {customer['name']}: {response.status_code}")
        except Exception as e:
            print_error(f"Error deleting customer {customer['name']}: {str(e)}")
    
    print_success("Test data cleanup completed")

def main():
    """Run all backend API tests"""
    print("🚀 Starting Comprehensive Backend API Testing")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Run all tests in sequence
    tests = [
        ("API Health Check", test_api_health),
        ("Customer CRUD Operations", test_customer_crud),
        ("Project CRUD Operations", test_project_crud),
        ("Domain/Hosting CRUD Operations", test_domain_hosting_crud),
        ("Dashboard API", test_dashboard_api),
        ("Expiring Domains Functionality", test_expiring_domains),
        # Enhanced Payment System Tests
        ("Enhanced Payment System with Project AMC Support", test_enhanced_payment_system),
        ("Domain Renewal Payment System", test_domain_renewal_payment_system),
        ("AMC Payment Processing with Auto-Renewal", test_amc_payment_processing),
        ("Customer Payment Summary", test_customer_payment_summary),
        ("Domains Due for Renewal", test_domains_due_renewal),
        ("Customer Ledger", test_customer_ledger),
        ("Payment Status", test_payment_status),
        ("Edge Cases and Error Handling", test_edge_cases)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print_error(f"Test {test_name} failed with exception: {str(e)}")
            test_results.append((test_name, False))
    
    # Optional cleanup
    try:
        test_cleanup()
    except Exception as e:
        print_error(f"Cleanup failed: {str(e)}")
    
    # Print final results
    print(f"\n{'='*60}")
    print("📋 FINAL TEST RESULTS")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        if result:
            print_success(f"{test_name}")
            passed += 1
        else:
            print_error(f"{test_name}")
            failed += 1
    
    print(f"\n📊 SUMMARY: {passed} passed, {failed} failed out of {len(test_results)} tests")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Backend API is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)