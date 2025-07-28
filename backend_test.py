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
        ("Expiring Domains Functionality", test_expiring_domains)
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