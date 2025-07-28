#!/usr/bin/env python3
"""
Create comprehensive test data to verify all functionality
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys

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
print(f"🔗 Creating test data via API at: {API_URL}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def create_test_data():
    """Create comprehensive test data"""
    print("📝 Creating comprehensive test data...")
    
    # Test customers
    customers_data = [
        {
            "name": "Tech Startup Inc",
            "phone": "+1-555-0101",
            "email": "contact@techstartup.com",
            "address": "123 Innovation Drive, Tech City, TC 12345"
        },
        {
            "name": "Digital Agency Co",
            "phone": "+1-555-0102",
            "email": "info@digitalagency.com",
            "address": "456 Creative Street, Design City, DC 67890"
        }
    ]
    
    created_customers = []
    for customer_data in customers_data:
        try:
            response = requests.post(f"{API_URL}/customers", json=customer_data)
            if response.status_code == 200:
                customer = response.json()
                created_customers.append(customer)
                print_success(f"Created customer: {customer['name']}")
            else:
                print_error(f"Failed to create customer: {response.status_code}")
        except Exception as e:
            print_error(f"Error creating customer: {str(e)}")
    
    # Test projects with AMC amounts
    current_date = datetime.now().date()
    end_date_past = current_date - timedelta(days=30)  # 30 days ago
    end_date_future = current_date + timedelta(days=90)  # 90 days from now
    
    projects_data = [
        {
            "customer_id": created_customers[0]["id"],
            "name": "E-commerce Website",
            "type": "Web Development",
            "amount": 50000.0,
            "amc_amount": 8000.0,
            "start_date": (current_date - timedelta(days=180)).isoformat(),
            "end_date": end_date_past.isoformat()
        },
        {
            "customer_id": created_customers[1]["id"],
            "name": "Mobile App Development",
            "type": "Mobile Development",
            "amount": 75000.0,
            "amc_amount": 12000.0,
            "start_date": (current_date - timedelta(days=120)).isoformat(),
            "end_date": end_date_future.isoformat()
        },
        {
            "customer_id": created_customers[0]["id"],
            "name": "Digital Marketing Campaign",
            "type": "Marketing",
            "amount": 25000.0,
            "amc_amount": 5000.0,
            "start_date": (current_date - timedelta(days=90)).isoformat(),
            "end_date": (current_date - timedelta(days=10)).isoformat()
        }
    ]
    
    created_projects = []
    for project_data in projects_data:
        try:
            response = requests.post(f"{API_URL}/projects", json=project_data)
            if response.status_code == 200:
                project = response.json()
                created_projects.append(project)
                print_success(f"Created project: {project['name']} (AMC: ₹{project['amc_amount']})")
            else:
                print_error(f"Failed to create project: {response.status_code}")
        except Exception as e:
            print_error(f"Error creating project: {str(e)}")
    
    # Test domains with different expiry dates
    expired_date = current_date - timedelta(days=10)  # Expired 10 days ago
    due_soon_date = current_date + timedelta(days=15)  # Due in 15 days
    due_later_date = current_date + timedelta(days=200)  # Due in 200 days
    
    domains_data = [
        {
            "project_id": created_projects[0]["id"],
            "domain_name": "techstartup.com",
            "hosting_provider": "AWS",
            "username": "admin",
            "password": "secure123",
            "validity_date": expired_date.isoformat(),
            "renewal_amount": 1500.0
        },
        {
            "project_id": created_projects[1]["id"],
            "domain_name": "digitalagency.com",
            "hosting_provider": "GoDaddy",
            "username": "webmaster",
            "password": "password123",
            "validity_date": due_soon_date.isoformat(),
            "renewal_amount": 2000.0
        },
        {
            "project_id": created_projects[2]["id"],
            "domain_name": "marketing-pro.com",
            "hosting_provider": "Bluehost",
            "username": "marketing",
            "password": "marketing456",
            "validity_date": due_later_date.isoformat(),
            "renewal_amount": 1200.0
        }
    ]
    
    created_domains = []
    for domain_data in domains_data:
        try:
            response = requests.post(f"{API_URL}/domains", json=domain_data)
            if response.status_code == 200:
                domain = response.json()
                created_domains.append(domain)
                print_success(f"Created domain: {domain['domain_name']} (Expires: {domain['validity_date']}, Renewal: ₹{domain['renewal_amount']})")
            else:
                print_error(f"Failed to create domain: {response.status_code}")
        except Exception as e:
            print_error(f"Error creating domain: {str(e)}")
    
    print(f"\n🎉 Test data creation complete!")
    print(f"📊 Created: {len(created_customers)} customers, {len(created_projects)} projects, {len(created_domains)} domains")
    print(f"📅 Domain expiry dates: {expired_date} (expired), {due_soon_date} (due soon), {due_later_date} (due later)")

if __name__ == "__main__":
    create_test_data()