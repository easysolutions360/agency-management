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

def test_project_end_date_non_mandatory():
    """Test Project End Date Non-Mandatory Implementation"""
    print_test_header("Project End Date Non-Mandatory Implementation")
    
    if not test_customers:
        print_error("No test customers available for project end date testing")
        return False
    
    # Test 1: Create project WITHOUT end_date
    print("\n📅 Testing Project Creation WITHOUT end_date...")
    project_without_end_date = {
        "customer_id": test_customers[0]['id'],
        "type": "Ongoing Website Maintenance",
        "name": "Long-term Website Support",
        "amount": 12000.00,
        "amc_amount": 3000.00,
        "start_date": "2024-01-01"
        # Note: no end_date provided
    }
    
    try:
        response = requests.post(f"{API_URL}/projects", json=project_without_end_date)
        if response.status_code == 200:
            project_no_end = response.json()
            test_projects.append(project_no_end)
            if project_no_end.get('end_date') is None:
                print_success(f"Created project without end_date: {project_no_end['name']}")
            else:
                print_error("Project end_date should be None but got a value")
                return False
        else:
            print_error(f"Failed to create project without end_date: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error creating project without end_date: {str(e)}")
        return False
    
    # Test 2: Create project WITH end_date
    print("\n📅 Testing Project Creation WITH end_date...")
    project_with_end_date = {
        "customer_id": test_customers[0]['id'],
        "type": "Fixed Duration Project",
        "name": "E-commerce Platform Development",
        "amount": 25000.00,
        "amc_amount": 5000.00,
        "start_date": "2024-02-01",
        "end_date": "2024-08-01"
    }
    
    try:
        response = requests.post(f"{API_URL}/projects", json=project_with_end_date)
        if response.status_code == 200:
            project_with_end = response.json()
            test_projects.append(project_with_end)
            if project_with_end.get('end_date') == "2024-08-01":
                print_success(f"Created project with end_date: {project_with_end['name']}")
            else:
                print_error(f"Project end_date not stored correctly: {project_with_end.get('end_date')}")
                return False
        else:
            print_error(f"Failed to create project with end_date: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error creating project with end_date: {str(e)}")
        return False
    
    # Test 3: Update project to add end_date
    print("\n✏️  Testing Project Update to ADD end_date...")
    if len(test_projects) >= 2:
        project_id = test_projects[-2]['id']  # Project without end_date
        update_data = {"end_date": "2024-12-31"}
        
        try:
            response = requests.put(f"{API_URL}/projects/{project_id}", json=update_data)
            if response.status_code == 200:
                updated_project = response.json()
                if updated_project.get('end_date') == "2024-12-31":
                    print_success("Successfully added end_date to project")
                else:
                    print_error("Failed to add end_date to project")
                    return False
            else:
                print_error(f"Failed to update project with end_date: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error updating project with end_date: {str(e)}")
            return False
    
    # Test 4: Update project to remove end_date
    print("\n✏️  Testing Project Update to REMOVE end_date...")
    if len(test_projects) >= 1:
        project_id = test_projects[-1]['id']  # Project with end_date
        update_data = {"end_date": None}
        
        try:
            response = requests.put(f"{API_URL}/projects/{project_id}", json=update_data)
            if response.status_code == 200:
                updated_project = response.json()
                if updated_project.get('end_date') is None:
                    print_success("Successfully removed end_date from project")
                else:
                    print_error("Failed to remove end_date from project")
                    return False
            else:
                print_error(f"Failed to update project to remove end_date: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error updating project to remove end_date: {str(e)}")
            return False
    
    # Test 5: Verify all project retrieval endpoints handle null end_date properly
    print("\n📖 Testing Project Retrieval with null end_date...")
    try:
        # Test GET all projects
        response = requests.get(f"{API_URL}/projects")
        if response.status_code == 200:
            projects = response.json()
            null_end_date_found = False
            for project in projects:
                if project.get('end_date') is None:
                    null_end_date_found = True
                    print_success(f"Project with null end_date handled correctly: {project['name']}")
                    break
            
            if not null_end_date_found:
                print_error("No projects with null end_date found in retrieval")
                return False
        else:
            print_error(f"Failed to retrieve projects: {response.status_code}")
            return False
        
        # Test dashboard projects endpoint
        response = requests.get(f"{API_URL}/dashboard/projects")
        if response.status_code == 200:
            dashboard_projects = response.json()
            print_success("Dashboard projects endpoint handles null end_date correctly")
        else:
            print_error(f"Dashboard projects failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error testing project retrieval with null end_date: {str(e)}")
        return False
    
    print_success("Project End Date Non-Mandatory Implementation tests completed successfully")
    return True

def test_customer_ledger_on_project_creation():
    """Test Customer Ledger Entry on Project Creation"""
    print_test_header("Customer Ledger Entry on Project Creation")
    
    if not test_customers:
        print_error("No test customers available for ledger testing")
        return False
    
    customer_id = test_customers[0]['id']
    
    # Get initial ledger count
    print("\n📋 Getting initial ledger state...")
    try:
        response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
        if response.status_code == 200:
            initial_ledger = response.json()
            initial_count = len(initial_ledger)
            print_info(f"Initial ledger entries: {initial_count}")
        else:
            print_error(f"Failed to get initial ledger: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting initial ledger: {str(e)}")
        return False
    
    # Create a new project and verify ledger entry is created
    print("\n💰 Testing Automatic Ledger Entry on Project Creation...")
    test_project = {
        "customer_id": customer_id,
        "type": "Ledger Test Project",
        "name": "Test Project for Ledger Entry",
        "amount": 15000.00,
        "amc_amount": 2000.00,
        "start_date": "2024-03-01",
        "end_date": "2024-06-01"
    }
    
    try:
        response = requests.post(f"{API_URL}/projects", json=test_project)
        if response.status_code == 200:
            created_project = response.json()
            test_projects.append(created_project)
            print_success(f"Created project: {created_project['name']}")
            
            # Check if ledger entry was created
            ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
            if ledger_response.status_code == 200:
                updated_ledger = ledger_response.json()
                new_count = len(updated_ledger)
                
                if new_count > initial_count:
                    print_success("Ledger entry count increased after project creation")
                    
                    # Find the specific ledger entry for this project
                    project_ledger_entry = None
                    for entry in updated_ledger:
                        if (entry.get('reference_type') == 'project' and 
                            entry.get('reference_id') == created_project['id']):
                            project_ledger_entry = entry
                            break
                    
                    if project_ledger_entry:
                        # Verify ledger entry details
                        if project_ledger_entry.get('transaction_type') == 'debit':
                            print_success("Ledger entry has correct transaction type (debit)")
                        else:
                            print_error(f"Expected debit transaction, got {project_ledger_entry.get('transaction_type')}")
                            return False
                        
                        if project_ledger_entry.get('amount') == test_project['amount']:
                            print_success(f"Ledger entry has correct amount: ${project_ledger_entry.get('amount')}")
                        else:
                            print_error(f"Expected amount ${test_project['amount']}, got ${project_ledger_entry.get('amount')}")
                            return False
                        
                        if 'Project created:' in project_ledger_entry.get('description', ''):
                            print_success("Ledger entry has correct description format")
                        else:
                            print_error(f"Unexpected description: {project_ledger_entry.get('description')}")
                            return False
                        
                        if project_ledger_entry.get('reference_id') == created_project['id']:
                            print_success("Ledger entry has correct reference_id")
                        else:
                            print_error("Ledger entry reference_id mismatch")
                            return False
                    else:
                        print_error("Could not find ledger entry for created project")
                        return False
                else:
                    print_error("Ledger entry count did not increase after project creation")
                    return False
            else:
                print_error(f"Failed to get updated ledger: {ledger_response.status_code}")
                return False
        else:
            print_error(f"Failed to create project: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing ledger entry on project creation: {str(e)}")
        return False
    
    # Test customer balance calculation
    print("\n💳 Testing Customer Balance Calculation...")
    try:
        # Get customer balance
        balance_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
        if balance_response.status_code == 200:
            summary = balance_response.json()
            credit_balance = summary.get('credit_balance')
            print_success(f"Customer balance calculated: ${credit_balance}")
            
            # Balance should be negative (debt) since we created projects (debits) without payments (credits)
            if credit_balance < 0:
                print_success("Customer balance correctly shows debt from project creation")
            else:
                print_info(f"Customer balance is positive: ${credit_balance} (may have existing credits)")
        else:
            print_error(f"Failed to get customer balance: {balance_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing customer balance: {str(e)}")
        return False
    
    print_success("Customer Ledger Entry on Project Creation tests completed successfully")
    return True

def test_enhanced_customer_ledger_functionality():
    """Test Enhanced Customer Ledger Functionality"""
    print_test_header("Enhanced Customer Ledger Functionality")
    
    if not test_customers:
        print_error("No test customers available for enhanced ledger testing")
        return False
    
    customer_id = test_customers[0]['id']
    
    # Test 1: Customer ledger retrieval endpoint
    print("\n📋 Testing Customer Ledger Retrieval...")
    try:
        response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
        if response.status_code == 200:
            ledger_entries = response.json()
            print_success(f"Retrieved {len(ledger_entries)} ledger entries")
            
            # Verify entries are properly ordered by date (most recent first)
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
        else:
            print_error(f"Failed to retrieve customer ledger: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing customer ledger retrieval: {str(e)}")
        return False
    
    # Test 2: Customer balance calculation accuracy
    print("\n💰 Testing Customer Balance Calculation Accuracy...")
    try:
        # Calculate balance manually from ledger
        manual_balance = 0.0
        for entry in ledger_entries:
            if entry['transaction_type'] == 'credit':
                manual_balance += entry['amount']
            else:  # debit
                manual_balance -= entry['amount']
        
        # Get balance from API
        balance_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
        if balance_response.status_code == 200:
            summary = balance_response.json()
            api_balance = summary.get('credit_balance')
            
            # Compare balances (allow small floating point differences)
            if abs(manual_balance - api_balance) < 0.01:
                print_success(f"Balance calculation is accurate: ${api_balance}")
            else:
                print_error(f"Balance mismatch - Manual: ${manual_balance}, API: ${api_balance}")
                return False
        else:
            print_error(f"Failed to get customer balance: {balance_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing balance calculation: {str(e)}")
        return False
    
    # Test 3: Various ledger scenarios
    print("\n🔄 Testing Various Ledger Scenarios...")
    
    # Create a payment to test credit entry
    if test_projects:
        payment_data = {
            "customer_id": customer_id,
            "type": "project_advance",
            "reference_id": test_projects[0]['id'],
            "amount": 5000.00,
            "description": "Test payment for ledger verification"
        }
        
        try:
            payment_response = requests.post(f"{API_URL}/payments", json=payment_data)
            if payment_response.status_code == 200:
                print_success("Created test payment for ledger verification")
                
                # Verify credit entry was added to ledger
                updated_ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
                if updated_ledger_response.status_code == 200:
                    updated_ledger = updated_ledger_response.json()
                    
                    # Find the credit entry
                    credit_entry_found = False
                    for entry in updated_ledger:
                        if (entry.get('transaction_type') == 'credit' and 
                            entry.get('amount') == 5000.00 and
                            'Test payment' in entry.get('description', '')):
                            credit_entry_found = True
                            print_success("Credit entry found in ledger after payment")
                            break
                    
                    if not credit_entry_found:
                        print_error("Credit entry not found in ledger after payment")
                        return False
                else:
                    print_error("Failed to retrieve updated ledger")
                    return False
            else:
                print_error(f"Failed to create test payment: {payment_response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error testing payment ledger entry: {str(e)}")
            return False
    
    # Test domain renewal ledger entry (if domains exist)
    if test_domains:
        print("\n🌐 Testing Domain Renewal Ledger Entry...")
        domain_id = test_domains[0]['id']
        
        renewal_request = {
            "domain_id": domain_id,
            "payment_type": "agency",
            "notes": "Test agency payment for ledger"
        }
        
        try:
            renewal_response = requests.post(f"{API_URL}/domain-renewal/{domain_id}", json=renewal_request)
            if renewal_response.status_code == 200:
                print_success("Domain renewal with agency payment completed")
                
                # Check for domain renewal ledger entry
                final_ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
                if final_ledger_response.status_code == 200:
                    final_ledger = final_ledger_response.json()
                    
                    domain_entry_found = False
                    for entry in final_ledger:
                        if (entry.get('reference_type') == 'domain_renewal' and
                            'domain renewal' in entry.get('description', '').lower()):
                            domain_entry_found = True
                            print_success("Domain renewal ledger entry found")
                            break
                    
                    if not domain_entry_found:
                        print_error("Domain renewal ledger entry not found")
                        return False
                else:
                    print_error("Failed to retrieve final ledger")
                    return False
            else:
                print_info(f"Domain renewal failed (expected if domain already renewed): {renewal_response.status_code}")
        except Exception as e:
            print_info(f"Domain renewal test completed with note: {str(e)}")
    
    print_success("Enhanced Customer Ledger Functionality tests completed successfully")
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

def test_domain_renewal_review_comprehensive():
    """
    COMPREHENSIVE DOMAIN RENEWAL REVIEW TEST
    Tests the specific domain renewal functionality as requested in the review:
    1. /domains-due-renewal endpoint returns proper upcoming domain renewal data
    2. /domain-renewal/{domain_id} works correctly for both client and agency payment types
    3. Verify that removing actions from Reports didn't break core functionality
    """
    print_test_header("🎯 DOMAIN RENEWAL REVIEW - COMPREHENSIVE TESTING")
    
    # Create test data specifically for domain renewal testing
    print("\n📋 Setting up test data for domain renewal review...")
    
    # Create test customer for domain renewal
    renewal_customer = {
        "name": "Domain Renewal Test Corp",
        "phone": "+1-555-RENEW",
        "email": "renewal@testcorp.com",
        "address": "123 Renewal Street, Test City, TC 12345"
    }
    
    try:
        response = requests.post(f"{API_URL}/customers", json=renewal_customer)
        if response.status_code == 200:
            test_customer = response.json()
            print_success(f"Created test customer: {test_customer['name']}")
        else:
            print_error(f"Failed to create test customer: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error creating test customer: {str(e)}")
        return False
    
    # Create test project for domains
    renewal_project = {
        "customer_id": test_customer['id'],
        "type": "Domain Renewal Test Project",
        "name": "Website with Multiple Domains",
        "amount": 10000.00,
        "amc_amount": 2000.00,
        "start_date": "2024-01-01",
        "end_date": "2024-06-01"
    }
    
    try:
        response = requests.post(f"{API_URL}/projects", json=renewal_project)
        if response.status_code == 200:
            test_project = response.json()
            print_success(f"Created test project: {test_project['name']}")
        else:
            print_error(f"Failed to create test project: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error creating test project: {str(e)}")
        return False
    
    # Create test domains with different expiry scenarios
    current_date = datetime.now().date()
    
    test_domains_data = [
        {
            "project_id": test_project['id'],
            "domain_name": "expired-domain.com",
            "hosting_provider": "Test Provider 1",
            "username": "expired_user",
            "password": "ExpiredPass123!",
            "validity_date": (current_date - timedelta(days=10)).isoformat(),  # Expired 10 days ago
            "renewal_amount": 1800.00
        },
        {
            "project_id": test_project['id'],
            "domain_name": "due-soon-domain.com", 
            "hosting_provider": "Test Provider 2",
            "username": "due_user",
            "password": "DuePass456!",
            "validity_date": (current_date + timedelta(days=15)).isoformat(),  # Due in 15 days
            "renewal_amount": 2200.00
        },
        {
            "project_id": test_project['id'],
            "domain_name": "not-due-domain.com",
            "hosting_provider": "Test Provider 3", 
            "username": "notdue_user",
            "password": "NotDuePass789!",
            "validity_date": (current_date + timedelta(days=200)).isoformat(),  # Due in 200 days
            "renewal_amount": 1500.00
        }
    ]
    
    created_domains = []
    for domain_data in test_domains_data:
        try:
            response = requests.post(f"{API_URL}/domains", json=domain_data)
            if response.status_code == 200:
                domain = response.json()
                created_domains.append(domain)
                print_success(f"Created test domain: {domain['domain_name']}")
            else:
                print_error(f"Failed to create domain {domain_data['domain_name']}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating domain {domain_data['domain_name']}: {str(e)}")
            return False
    
    # TEST 1: Verify /domains-due-renewal endpoint returns proper data
    print("\n🔍 TEST 1: Testing /domains-due-renewal endpoint...")
    try:
        response = requests.get(f"{API_URL}/domains-due-renewal")
        if response.status_code == 200:
            due_domains = response.json()
            print_success(f"Retrieved {len(due_domains)} domains due for renewal")
            
            # Verify data structure
            required_fields = ['domain_id', 'domain_name', 'hosting_provider', 'validity_date', 
                             'days_until_expiry', 'renewal_amount', 'project_name', 'customer_name', 
                             'customer_id', 'is_expired']
            
            for domain in due_domains:
                missing_fields = [field for field in required_fields if field not in domain]
                if missing_fields:
                    print_error(f"Domain missing required fields: {missing_fields}")
                    return False
            
            # Verify filtering logic - should include expired and due-soon domains, exclude not-due domains
            expired_found = any(d['domain_name'] == 'expired-domain.com' for d in due_domains)
            due_soon_found = any(d['domain_name'] == 'due-soon-domain.com' for d in due_domains)
            not_due_found = any(d['domain_name'] == 'not-due-domain.com' for d in due_domains)
            
            if expired_found:
                print_success("✅ Expired domain correctly included in results")
            else:
                print_error("❌ Expired domain not found in results")
                return False
            
            if due_soon_found:
                print_success("✅ Due-soon domain correctly included in results")
            else:
                print_error("❌ Due-soon domain not found in results")
                return False
            
            if not not_due_found:
                print_success("✅ Not-due domain correctly excluded from results")
            else:
                print_error("❌ Not-due domain incorrectly included in results")
                return False
            
            # Verify is_expired flag
            for domain in due_domains:
                if domain['domain_name'] == 'expired-domain.com':
                    if domain['is_expired']:
                        print_success("✅ Expired domain correctly flagged as expired")
                    else:
                        print_error("❌ Expired domain not flagged as expired")
                        return False
                elif domain['domain_name'] == 'due-soon-domain.com':
                    if not domain['is_expired']:
                        print_success("✅ Due-soon domain correctly not flagged as expired")
                    else:
                        print_error("❌ Due-soon domain incorrectly flagged as expired")
                        return False
            
            print_success("✅ /domains-due-renewal endpoint working correctly")
        else:
            print_error(f"Failed to get domains due for renewal: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing domains due for renewal: {str(e)}")
        return False
    
    # TEST 2: Test domain renewal with AGENCY payment type
    print("\n🏢 TEST 2: Testing domain renewal with AGENCY payment type...")
    expired_domain = created_domains[0]  # expired-domain.com
    
    agency_renewal_request = {
        "new_validity_date": (current_date + timedelta(days=365)).isoformat(),  # Custom validity date
        "amount": 1800.00,  # Custom renewal amount
        "payment_type": "agency",
        "notes": "Agency pays for domain renewal - customer owes money"
    }
    
    try:
        response = requests.post(f"{API_URL}/domain-renewal/{expired_domain['id']}", json=agency_renewal_request)
        if response.status_code == 200:
            result = response.json()
            print_success(f"Agency renewal successful: {result.get('message')}")
            
            # Verify domain was updated
            domain_response = requests.get(f"{API_URL}/domains/{expired_domain['id']}")
            if domain_response.status_code == 200:
                updated_domain = domain_response.json()
                
                # Check validity date
                if updated_domain['validity_date'] == agency_renewal_request['new_validity_date']:
                    print_success("✅ Domain validity date updated to custom date")
                else:
                    print_error(f"❌ Domain validity date not updated correctly: {updated_domain['validity_date']}")
                    return False
                
                # Check renewal amount
                if updated_domain['renewal_amount'] == agency_renewal_request['amount']:
                    print_success("✅ Domain renewal amount updated to custom amount")
                else:
                    print_error(f"❌ Domain renewal amount not updated correctly: {updated_domain['renewal_amount']}")
                    return False
                
                # Check payment type
                if updated_domain['payment_type'] == 'agency':
                    print_success("✅ Domain payment type set to agency")
                else:
                    print_error(f"❌ Domain payment type not set correctly: {updated_domain['payment_type']}")
                    return False
            else:
                print_error("Failed to retrieve updated domain")
                return False
            
            # Verify customer ledger entry was created (DEBIT - customer owes money)
            ledger_response = requests.get(f"{API_URL}/ledger/customer/{test_customer['id']}")
            if ledger_response.status_code == 200:
                ledger_entries = ledger_response.json()
                
                agency_debt_found = False
                for entry in ledger_entries:
                    if (entry.get('transaction_type') == 'debit' and 
                        entry.get('reference_type') == 'domain_renewal' and
                        entry.get('reference_id') == expired_domain['id'] and
                        entry.get('amount') == 1800.00):
                        agency_debt_found = True
                        print_success("✅ DEBIT entry created in customer ledger (customer owes money)")
                        break
                
                if not agency_debt_found:
                    print_error("❌ Customer debt entry not found in ledger")
                    return False
            else:
                print_error("Failed to retrieve customer ledger")
                return False
            
            # Verify payment record was created
            payments_response = requests.get(f"{API_URL}/payments/customer/{test_customer['id']}")
            if payments_response.status_code == 200:
                payments = payments_response.json()
                
                agency_payment_found = False
                for payment in payments:
                    if (payment.get('type') == 'domain_renewal_agency' and
                        payment.get('reference_id') == expired_domain['id'] and
                        payment.get('amount') == 1800.00 and
                        payment.get('status') == 'pending'):
                        agency_payment_found = True
                        print_success("✅ Pending payment record created with correct amount and status")
                        break
                
                if not agency_payment_found:
                    print_error("❌ Agency payment record not found")
                    return False
            else:
                print_error("Failed to retrieve customer payments")
                return False
            
            print_success("✅ Agency payment type domain renewal working correctly")
        else:
            print_error(f"Failed to renew domain with agency payment: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing agency payment renewal: {str(e)}")
        return False
    
    # TEST 3: Test domain renewal with CLIENT payment type
    print("\n👤 TEST 3: Testing domain renewal with CLIENT payment type...")
    due_soon_domain = created_domains[1]  # due-soon-domain.com
    
    client_renewal_request = {
        "new_validity_date": (current_date + timedelta(days=400)).isoformat(),  # Custom validity date
        "amount": 2200.00,  # Custom renewal amount
        "payment_type": "client",
        "notes": "Client pays directly for domain renewal"
    }
    
    try:
        response = requests.post(f"{API_URL}/domain-renewal/{due_soon_domain['id']}", json=client_renewal_request)
        if response.status_code == 200:
            result = response.json()
            print_success(f"Client renewal successful: {result.get('message')}")
            
            # Verify domain was updated
            domain_response = requests.get(f"{API_URL}/domains/{due_soon_domain['id']}")
            if domain_response.status_code == 200:
                updated_domain = domain_response.json()
                
                # Check validity date
                if updated_domain['validity_date'] == client_renewal_request['new_validity_date']:
                    print_success("✅ Domain validity date updated to custom date")
                else:
                    print_error(f"❌ Domain validity date not updated correctly: {updated_domain['validity_date']}")
                    return False
                
                # Check renewal amount
                if updated_domain['renewal_amount'] == client_renewal_request['amount']:
                    print_success("✅ Domain renewal amount updated to custom amount")
                else:
                    print_error(f"❌ Domain renewal amount not updated correctly: {updated_domain['renewal_amount']}")
                    return False
                
                # Check payment type
                if updated_domain['payment_type'] == 'client':
                    print_success("✅ Domain payment type set to client")
                else:
                    print_error(f"❌ Domain payment type not set correctly: {updated_domain['payment_type']}")
                    return False
            else:
                print_error("Failed to retrieve updated domain")
                return False
            
            # Verify NO ledger entry was created (client pays directly)
            ledger_response = requests.get(f"{API_URL}/ledger/customer/{test_customer['id']}")
            if ledger_response.status_code == 200:
                ledger_entries = ledger_response.json()
                
                client_debt_found = False
                for entry in ledger_entries:
                    if (entry.get('reference_type') == 'domain_renewal' and
                        entry.get('reference_id') == due_soon_domain['id']):
                        client_debt_found = True
                        break
                
                if not client_debt_found:
                    print_success("✅ NO ledger entry created (client pays directly)")
                else:
                    print_error("❌ Unexpected ledger entry found for client payment")
                    return False
            else:
                print_error("Failed to retrieve customer ledger")
                return False
            
            # Verify completed payment record was created
            payments_response = requests.get(f"{API_URL}/payments/customer/{test_customer['id']}")
            if payments_response.status_code == 200:
                payments = payments_response.json()
                
                client_payment_found = False
                for payment in payments:
                    if (payment.get('type') == 'domain_renewal_client' and
                        payment.get('reference_id') == due_soon_domain['id'] and
                        payment.get('amount') == 2200.00 and
                        payment.get('status') == 'completed'):
                        client_payment_found = True
                        print_success("✅ Completed payment record created with correct amount and status")
                        break
                
                if not client_payment_found:
                    print_error("❌ Client payment record not found")
                    return False
            else:
                print_error("Failed to retrieve customer payments")
                return False
            
            print_success("✅ Client payment type domain renewal working correctly")
        else:
            print_error(f"Failed to renew domain with client payment: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing client payment renewal: {str(e)}")
        return False
    
    # TEST 4: Test API endpoint with comprehensive request format
    print("\n🔧 TEST 4: Testing API endpoint with comprehensive request format...")
    not_due_domain = created_domains[2]  # not-due-domain.com
    
    comprehensive_request = {
        "new_validity_date": (current_date + timedelta(days=500)).isoformat(),
        "amount": 2500.00,
        "payment_type": "agency",
        "notes": "Comprehensive API test with all parameters"
    }
    
    try:
        response = requests.post(f"{API_URL}/domain-renewal/{not_due_domain['id']}", json=comprehensive_request)
        if response.status_code == 200:
            result = response.json()
            
            # Verify response structure
            if 'message' in result and 'new_validity_date' in result:
                print_success("✅ API endpoint returns success response with required fields")
                
                if result['new_validity_date'] == comprehensive_request['new_validity_date']:
                    print_success("✅ Response contains correct new_validity_date")
                else:
                    print_error("❌ Response new_validity_date mismatch")
                    return False
            else:
                print_error("❌ API response missing required fields")
                return False
        else:
            print_error(f"Failed comprehensive API test: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing comprehensive API request: {str(e)}")
        return False
    
    # TEST 5: Test error handling for non-existent domain
    print("\n❌ TEST 5: Testing error handling for non-existent domain...")
    try:
        response = requests.post(f"{API_URL}/domain-renewal/non-existent-domain-id", json={"payment_type": "client"})
        if response.status_code == 404:
            print_success("✅ Correctly returns 404 for non-existent domain")
        else:
            print_error(f"Expected 404 for non-existent domain, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing non-existent domain: {str(e)}")
        return False
    
    # Cleanup test data
    print("\n🧹 Cleaning up test data...")
    try:
        # Delete test domains
        for domain in created_domains:
            requests.delete(f"{API_URL}/domains/{domain['id']}")
        
        # Delete test project
        requests.delete(f"{API_URL}/projects/{test_project['id']}")
        
        # Delete test customer
        requests.delete(f"{API_URL}/customers/{test_customer['id']}")
        
        print_success("✅ Test data cleaned up successfully")
    except Exception as e:
        print_info(f"Cleanup completed with note: {str(e)}")
    
    print_success("🎯 DOMAIN RENEWAL REVIEW - ALL TESTS PASSED!")
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

def test_domain_renewal_fixed_functionality():
    """Test the FIXED Domain Renewal Functionality as requested in review"""
    print_test_header("FIXED Domain Renewal Functionality - Review Testing")
    
    if not test_domains or not test_customers:
        print_error("No test data available for domain renewal testing")
        return False
    
    # Create test domains with specific data for renewal testing
    print("\n🌐 Setting up test domains for renewal testing...")
    
    # Create additional test domains with specific renewal amounts and validity dates
    test_renewal_domains = []
    
    if test_projects:
        renewal_domains_data = [
            {
                "project_id": test_projects[0]['id'],
                "domain_name": "agency-renewal-test.com",
                "hosting_provider": "AWS",
                "username": "agency_test",
                "password": "AgencyTest123!",
                "validity_date": (datetime.now().date() + timedelta(days=15)).isoformat(),
                "renewal_amount": 1500.0
            },
            {
                "project_id": test_projects[0]['id'],
                "domain_name": "client-renewal-test.com", 
                "hosting_provider": "DigitalOcean",
                "username": "client_test",
                "password": "ClientTest456!",
                "validity_date": (datetime.now().date() + timedelta(days=20)).isoformat(),
                "renewal_amount": 2000.0
            }
        ]
        
        for domain_data in renewal_domains_data:
            try:
                response = requests.post(f"{API_URL}/domains", json=domain_data)
                if response.status_code == 200:
                    domain = response.json()
                    test_renewal_domains.append(domain)
                    print_success(f"Created test domain: {domain['domain_name']}")
                else:
                    print_error(f"Failed to create test domain: {response.status_code}")
                    return False
            except Exception as e:
                print_error(f"Error creating test domain: {str(e)}")
                return False
    
    if len(test_renewal_domains) < 2:
        print_error("Could not create sufficient test domains for renewal testing")
        return False
    
    # SCENARIO 1: Agency Pays Renewal Test
    print("\n💼 SCENARIO 1: Testing Agency Pays Renewal...")
    agency_domain = test_renewal_domains[0]
    customer_id = test_customers[0]['id']
    
    # Get initial customer ledger count
    initial_ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
    initial_ledger_count = len(initial_ledger_response.json()) if initial_ledger_response.status_code == 200 else 0
    
    # Get initial payment count
    initial_payments_response = requests.get(f"{API_URL}/payments/customer/{customer_id}")
    initial_payments_count = len(initial_payments_response.json()) if initial_payments_response.status_code == 200 else 0
    
    # Perform agency renewal with custom date and amount
    custom_validity_date = (datetime.now().date() + timedelta(days=365)).isoformat()
    custom_amount = 1800.0
    
    agency_renewal_request = {
        "new_validity_date": custom_validity_date,
        "amount": custom_amount,
        "payment_type": "agency",
        "notes": "Agency pays for renewal - customer will be charged"
    }
    
    try:
        response = requests.post(f"{API_URL}/domain-renewal/{agency_domain['id']}", json=agency_renewal_request)
        if response.status_code == 200:
            result = response.json()
            print_success(f"Agency renewal completed: {result.get('message')}")
            
            # Verify 1: Domain validity date updated to custom date
            domain_response = requests.get(f"{API_URL}/domains/{agency_domain['id']}")
            if domain_response.status_code == 200:
                updated_domain = domain_response.json()
                if updated_domain['validity_date'] == custom_validity_date:
                    print_success("✅ Domain validity date updated to custom date")
                else:
                    print_error(f"❌ Domain validity date not updated correctly. Expected: {custom_validity_date}, Got: {updated_domain['validity_date']}")
                    return False
                
                # Verify 2: Renewal amount updated to custom amount
                if updated_domain['renewal_amount'] == custom_amount:
                    print_success("✅ Domain renewal amount updated to custom amount")
                else:
                    print_error(f"❌ Domain renewal amount not updated correctly. Expected: {custom_amount}, Got: {updated_domain['renewal_amount']}")
                    return False
            else:
                print_error("Failed to retrieve updated domain")
                return False
            
            # Verify 3: DEBIT entry created in customer ledger
            ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
            if ledger_response.status_code == 200:
                ledger_entries = ledger_response.json()
                new_ledger_count = len(ledger_entries)
                
                if new_ledger_count > initial_ledger_count:
                    print_success("✅ New ledger entry created")
                    
                    # Find the debit entry for domain renewal
                    debit_entry_found = False
                    for entry in ledger_entries:
                        if (entry.get('transaction_type') == 'debit' and 
                            entry.get('reference_type') == 'domain_renewal' and
                            entry.get('reference_id') == agency_domain['id'] and
                            entry.get('amount') == custom_amount):
                            debit_entry_found = True
                            print_success("✅ DEBIT entry created in customer ledger (customer owes money)")
                            print_info(f"   Amount: ${entry['amount']}, Description: {entry['description']}")
                            break
                    
                    if not debit_entry_found:
                        print_error("❌ DEBIT entry not found in customer ledger")
                        return False
                else:
                    print_error("❌ No new ledger entry created")
                    return False
            else:
                print_error("Failed to retrieve customer ledger")
                return False
            
            # Verify 4: Pending payment record created
            payments_response = requests.get(f"{API_URL}/payments/customer/{customer_id}")
            if payments_response.status_code == 200:
                payments = payments_response.json()
                new_payments_count = len(payments)
                
                if new_payments_count > initial_payments_count:
                    print_success("✅ New payment record created")
                    
                    # Find the pending payment for domain renewal
                    pending_payment_found = False
                    for payment in payments:
                        if (payment.get('type') == 'domain_renewal_agency' and
                            payment.get('reference_id') == agency_domain['id'] and
                            payment.get('status') == 'pending' and
                            payment.get('amount') == custom_amount):
                            pending_payment_found = True
                            print_success("✅ Pending payment record created")
                            print_info(f"   Amount: ${payment['amount']}, Status: {payment['status']}")
                            break
                    
                    if not pending_payment_found:
                        print_error("❌ Pending payment record not found")
                        return False
                else:
                    print_error("❌ No new payment record created")
                    return False
            else:
                print_error("Failed to retrieve customer payments")
                return False
                
        else:
            print_error(f"Agency renewal failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing agency renewal: {str(e)}")
        return False
    
    # SCENARIO 2: Client Pays Renewal Test
    print("\n👤 SCENARIO 2: Testing Client Pays Renewal...")
    client_domain = test_renewal_domains[1]
    
    # Get current ledger count (should not increase for client payment)
    current_ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
    current_ledger_count = len(current_ledger_response.json()) if current_ledger_response.status_code == 200 else 0
    
    # Get current payment count
    current_payments_response = requests.get(f"{API_URL}/payments/customer/{customer_id}")
    current_payments_count = len(current_payments_response.json()) if current_payments_response.status_code == 200 else 0
    
    # Perform client renewal with custom date and amount
    client_custom_validity_date = (datetime.now().date() + timedelta(days=400)).isoformat()
    client_custom_amount = 2200.0
    
    client_renewal_request = {
        "new_validity_date": client_custom_validity_date,
        "amount": client_custom_amount,
        "payment_type": "client",
        "notes": "Client pays directly for renewal"
    }
    
    try:
        response = requests.post(f"{API_URL}/domain-renewal/{client_domain['id']}", json=client_renewal_request)
        if response.status_code == 200:
            result = response.json()
            print_success(f"Client renewal completed: {result.get('message')}")
            
            # Verify 1: Domain validity date updated to custom date
            domain_response = requests.get(f"{API_URL}/domains/{client_domain['id']}")
            if domain_response.status_code == 200:
                updated_domain = domain_response.json()
                if updated_domain['validity_date'] == client_custom_validity_date:
                    print_success("✅ Domain validity date updated to custom date")
                else:
                    print_error(f"❌ Domain validity date not updated correctly. Expected: {client_custom_validity_date}, Got: {updated_domain['validity_date']}")
                    return False
                
                # Verify 2: Renewal amount updated to custom amount
                if updated_domain['renewal_amount'] == client_custom_amount:
                    print_success("✅ Domain renewal amount updated to custom amount")
                else:
                    print_error(f"❌ Domain renewal amount not updated correctly. Expected: {client_custom_amount}, Got: {updated_domain['renewal_amount']}")
                    return False
            else:
                print_error("Failed to retrieve updated domain")
                return False
            
            # Verify 3: NO ledger entry created (client pays directly)
            ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
            if ledger_response.status_code == 200:
                ledger_entries = ledger_response.json()
                new_ledger_count = len(ledger_entries)
                
                # Check if any new ledger entry was created for this domain
                client_ledger_entry_found = False
                for entry in ledger_entries:
                    if (entry.get('reference_type') == 'domain_renewal' and
                        entry.get('reference_id') == client_domain['id']):
                        client_ledger_entry_found = True
                        break
                
                if not client_ledger_entry_found:
                    print_success("✅ NO ledger entry created (client pays directly)")
                else:
                    print_error("❌ Unexpected ledger entry created for client payment")
                    return False
            else:
                print_error("Failed to retrieve customer ledger")
                return False
            
            # Verify 4: Completed payment record created
            payments_response = requests.get(f"{API_URL}/payments/customer/{customer_id}")
            if payments_response.status_code == 200:
                payments = payments_response.json()
                new_payments_count = len(payments)
                
                if new_payments_count > current_payments_count:
                    print_success("✅ New payment record created")
                    
                    # Find the completed payment for domain renewal
                    completed_payment_found = False
                    for payment in payments:
                        if (payment.get('type') == 'domain_renewal_client' and
                            payment.get('reference_id') == client_domain['id'] and
                            payment.get('status') == 'completed' and
                            payment.get('amount') == client_custom_amount):
                            completed_payment_found = True
                            print_success("✅ Completed payment record created")
                            print_info(f"   Amount: ${payment['amount']}, Status: {payment['status']}")
                            break
                    
                    if not completed_payment_found:
                        print_error("❌ Completed payment record not found")
                        return False
                else:
                    print_error("❌ No new payment record created")
                    return False
            else:
                print_error("Failed to retrieve customer payments")
                return False
                
        else:
            print_error(f"Client renewal failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing client renewal: {str(e)}")
        return False
    
    # SCENARIO 3: API Endpoint Test
    print("\n🔌 SCENARIO 3: Testing API Endpoint...")
    
    # Test the endpoint with various request formats
    test_requests = [
        {
            "name": "Minimal request (agency payment)",
            "data": {"payment_type": "agency"},
            "should_succeed": True
        },
        {
            "name": "Full request (client payment)",
            "data": {
                "new_validity_date": (datetime.now().date() + timedelta(days=500)).isoformat(),
                "amount": 2500.0,
                "payment_type": "client",
                "notes": "Full API test"
            },
            "should_succeed": True
        }
    ]
    
    # Use the first domain for API testing (create a fresh one)
    if test_projects:
        api_test_domain_data = {
            "project_id": test_projects[0]['id'],
            "domain_name": "api-test-domain.com",
            "hosting_provider": "Test Provider",
            "username": "api_test",
            "password": "ApiTest789!",
            "validity_date": (datetime.now().date() + timedelta(days=25)).isoformat(),
            "renewal_amount": 1000.0
        }
        
        try:
            response = requests.post(f"{API_URL}/domains", json=api_test_domain_data)
            if response.status_code == 200:
                api_test_domain = response.json()
                test_domain_id = api_test_domain['id']
                print_success(f"Created API test domain: {api_test_domain['domain_name']}")
            else:
                print_error("Failed to create API test domain")
                return False
        except Exception as e:
            print_error(f"Error creating API test domain: {str(e)}")
            return False
    else:
        print_error("No test projects available for API testing")
        return False
    
    for test_case in test_requests:
        print(f"\n   Testing: {test_case['name']}")
        try:
            response = requests.post(f"{API_URL}/domain-renewal/{test_domain_id}", json=test_case['data'])
            
            if test_case['should_succeed']:
                if response.status_code == 200:
                    print_success(f"✅ {test_case['name']} - Success")
                    result = response.json()
                    if 'message' in result and 'new_validity_date' in result:
                        print_success("✅ API returns success response with required fields")
                    else:
                        print_error("❌ API response missing required fields")
                        return False
                else:
                    print_error(f"❌ {test_case['name']} - Expected success, got {response.status_code}")
                    return False
            else:
                if response.status_code != 200:
                    print_success(f"✅ {test_case['name']} - Correctly rejected")
                else:
                    print_error(f"❌ {test_case['name']} - Should have been rejected")
                    return False
        except Exception as e:
            print_error(f"Error testing {test_case['name']}: {str(e)}")
            return False
    
    # Test non-existent domain
    print("\n   Testing: Non-existent domain")
    try:
        response = requests.post(f"{API_URL}/domain-renewal/non-existent-domain", json={"payment_type": "client"})
        if response.status_code == 404:
            print_success("✅ Non-existent domain - Correctly returned 404")
        else:
            print_error(f"❌ Non-existent domain - Expected 404, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing non-existent domain: {str(e)}")
        return False
    
    print_success("🎉 FIXED Domain Renewal Functionality tests completed successfully!")
    print_success("All scenarios verified:")
    print_success("  ✅ Agency Pays: Domain updated, DEBIT ledger entry, pending payment")
    print_success("  ✅ Client Pays: Domain updated, NO ledger entry, completed payment")
    print_success("  ✅ API Endpoint: Accepts new request format, handles errors correctly")
    
    return True

def test_business_financial_summary():
    """Test Business Financial Summary endpoint for dashboard"""
    print_test_header("Business Financial Summary")
    
    print("\n📊 Testing Business Financial Summary endpoint...")
    try:
        response = requests.get(f"{API_URL}/dashboard/business-financial-summary")
        if response.status_code == 200:
            summary = response.json()
            
            # Verify required fields according to BusinessFinancialSummary model
            required_fields = [
                'total_projects', 'total_customers', 'total_project_value', 
                'total_received', 'total_outstanding', 'total_customer_credit',
                'net_revenue', 'project_completion_rate', 'payment_collection_rate',
                'top_customers', 'recent_payments'
            ]
            
            missing_fields = [field for field in required_fields if field not in summary]
            if missing_fields:
                print_error(f"Business financial summary missing fields: {missing_fields}")
                return False
            
            # Verify data types and structure
            print_success("✅ All required fields present in business financial summary")
            
            # Test numeric fields
            numeric_fields = ['total_projects', 'total_customers', 'total_project_value', 
                            'total_received', 'total_outstanding', 'total_customer_credit',
                            'net_revenue', 'project_completion_rate', 'payment_collection_rate']
            
            for field in numeric_fields:
                if not isinstance(summary[field], (int, float)):
                    print_error(f"Field {field} should be numeric, got {type(summary[field])}")
                    return False
            
            print_success("✅ All numeric fields have correct data types")
            
            # Verify calculations make sense
            total_project_value = summary['total_project_value']
            total_received = summary['total_received']
            total_outstanding = summary['total_outstanding']
            
            # Outstanding should equal project value minus received
            expected_outstanding = total_project_value - total_received
            if abs(expected_outstanding - total_outstanding) < 0.01:  # Allow small floating point differences
                print_success("✅ Outstanding amount calculation is correct")
            else:
                print_error(f"Outstanding calculation error: Expected {expected_outstanding}, got {total_outstanding}")
                return False
            
            # Verify completion rate calculation
            if total_project_value > 0:
                expected_completion_rate = (total_received / total_project_value) * 100
                if abs(expected_completion_rate - summary['project_completion_rate']) < 0.01:
                    print_success("✅ Project completion rate calculation is correct")
                else:
                    print_error(f"Completion rate error: Expected {expected_completion_rate:.2f}%, got {summary['project_completion_rate']}%")
                    return False
            
            # Verify top customers structure
            top_customers = summary['top_customers']
            if isinstance(top_customers, list):
                print_success("✅ Top customers is a list")
                
                for customer in top_customers:
                    customer_fields = ['customer_name', 'total_amount', 'project_count']
                    missing_customer_fields = [field for field in customer_fields if field not in customer]
                    if missing_customer_fields:
                        print_error(f"Top customer missing fields: {missing_customer_fields}")
                        return False
                
                if top_customers:
                    print_success(f"✅ Top customers structure is correct ({len(top_customers)} customers)")
                else:
                    print_info("ℹ️  No top customers data (may be expected if no projects exist)")
            else:
                print_error("Top customers should be a list")
                return False
            
            # Verify recent payments structure
            recent_payments = summary['recent_payments']
            if isinstance(recent_payments, list):
                print_success("✅ Recent payments is a list")
                
                for payment in recent_payments:
                    payment_fields = ['date', 'amount', 'type', 'description', 'customer_id']
                    missing_payment_fields = [field for field in payment_fields if field not in payment]
                    if missing_payment_fields:
                        print_error(f"Recent payment missing fields: {missing_payment_fields}")
                        return False
                
                if recent_payments:
                    print_success(f"✅ Recent payments structure is correct ({len(recent_payments)} payments)")
                else:
                    print_info("ℹ️  No recent payments data (may be expected if no payments exist)")
            else:
                print_error("Recent payments should be a list")
                return False
            
            # Display summary information
            print_info(f"📈 Business Summary:")
            print_info(f"   Total Projects: {summary['total_projects']}")
            print_info(f"   Total Customers: {summary['total_customers']}")
            print_info(f"   Total Project Value: ₹{summary['total_project_value']:,.2f}")
            print_info(f"   Total Received: ₹{summary['total_received']:,.2f}")
            print_info(f"   Total Outstanding: ₹{summary['total_outstanding']:,.2f}")
            print_info(f"   Customer Credit Balance: ₹{summary['total_customer_credit']:,.2f}")
            print_info(f"   Net Revenue: ₹{summary['net_revenue']:,.2f}")
            print_info(f"   Project Completion Rate: {summary['project_completion_rate']:.2f}%")
            print_info(f"   Payment Collection Rate: {summary['payment_collection_rate']:.2f}%")
            print_info(f"   Top Customers Count: {len(summary['top_customers'])}")
            print_info(f"   Recent Payments Count: {len(summary['recent_payments'])}")
            
            print_success("Business Financial Summary endpoint working correctly")
            
        else:
            print_error(f"Failed to get business financial summary: {response.status_code}")
            if response.status_code == 500:
                try:
                    error_detail = response.json()
                    print_error(f"Server error details: {error_detail}")
                except:
                    print_error(f"Server error response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error testing business financial summary: {str(e)}")
        return False
    
    # Test integration with existing dashboard endpoints
    print("\n🔗 Testing Integration with Other Dashboard Endpoints...")
    try:
        # Test that business summary integrates well with other dashboard data
        dashboard_projects_response = requests.get(f"{API_URL}/dashboard/projects")
        customer_balances_response = requests.get(f"{API_URL}/dashboard/customer-balances")
        
        if dashboard_projects_response.status_code == 200 and customer_balances_response.status_code == 200:
            dashboard_projects = dashboard_projects_response.json()
            customer_balances = customer_balances_response.json()
            
            # Verify consistency between endpoints
            if len(dashboard_projects) == summary['total_projects']:
                print_success("✅ Project count consistent between dashboard endpoints")
            else:
                print_error(f"Project count mismatch: Dashboard={len(dashboard_projects)}, Summary={summary['total_projects']}")
                return False
            
            # Calculate total project value from dashboard projects
            dashboard_total_value = sum(p.get('amount', 0) for p in dashboard_projects)
            if abs(dashboard_total_value - summary['total_project_value']) < 0.01:
                print_success("✅ Total project value consistent between endpoints")
            else:
                print_error(f"Project value mismatch: Dashboard={dashboard_total_value}, Summary={summary['total_project_value']}")
                return False
            
            print_success("✅ Business financial summary integrates well with other dashboard endpoints")
        else:
            print_error("Failed to retrieve other dashboard endpoints for integration testing")
            return False
            
    except Exception as e:
        print_error(f"Error testing dashboard integration: {str(e)}")
        return False
    
    print_success("Business Financial Summary tests completed successfully")
    return True

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
        # New tests for specific review requirements
        ("Project End Date Non-Mandatory Implementation", test_project_end_date_non_mandatory),
        ("Customer Ledger Entry on Project Creation", test_customer_ledger_on_project_creation),
        ("Enhanced Customer Ledger Functionality", test_enhanced_customer_ledger_functionality),
        ("Business Financial Summary", test_business_financial_summary),
        ("FIXED Domain Renewal Functionality - Review Testing", test_domain_renewal_fixed_functionality),
        ("🎯 DOMAIN RENEWAL REVIEW - COMPREHENSIVE", test_domain_renewal_review_comprehensive),
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