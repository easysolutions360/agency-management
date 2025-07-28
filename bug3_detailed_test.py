#!/usr/bin/env python3
"""
Detailed test for Bug 3: Domains due for renewal not showing all expired/about to expire
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys

# Get backend URL
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
API_URL = f"{BASE_URL}/api"

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_domains_due_renewal_detailed():
    """Detailed test of domains due for renewal logic"""
    print("🔍 DETAILED TEST: Domains Due for Renewal Logic")
    print("="*80)
    
    # Get current date
    current_date = datetime.now().date()
    print_info(f"Current date: {current_date}")
    
    # Calculate test dates
    expired_date = current_date - timedelta(days=10)  # 10 days ago (expired)
    due_soon_date = current_date + timedelta(days=15)  # 15 days from now (due soon)
    due_later_date = current_date + timedelta(days=45)  # 45 days from now (not due)
    
    print_info(f"Test dates:")
    print_info(f"  Expired: {expired_date}")
    print_info(f"  Due soon: {due_soon_date}")
    print_info(f"  Due later: {due_later_date}")
    
    # Get existing customers and projects
    customers_response = requests.get(f"{API_URL}/customers")
    projects_response = requests.get(f"{API_URL}/projects")
    
    if customers_response.status_code != 200 or projects_response.status_code != 200:
        print_error("Failed to get existing customers or projects")
        return False
    
    customers = customers_response.json()
    projects = projects_response.json()
    
    if not customers or not projects:
        print_error("No existing customers or projects found")
        return False
    
    customer_id = customers[0]['id']
    project_id = projects[0]['id']
    
    # Create test domains with specific dates
    test_domains = [
        {
            "project_id": project_id,
            "domain_name": "test-expired.com",
            "hosting_provider": "Test Provider",
            "username": "test_user",
            "password": "test_pass",
            "validity_date": expired_date.isoformat(),
            "renewal_amount": 1000.0
        },
        {
            "project_id": project_id,
            "domain_name": "test-due-soon.com",
            "hosting_provider": "Test Provider",
            "username": "test_user",
            "password": "test_pass",
            "validity_date": due_soon_date.isoformat(),
            "renewal_amount": 1500.0
        },
        {
            "project_id": project_id,
            "domain_name": "test-due-later.com",
            "hosting_provider": "Test Provider",
            "username": "test_user",
            "password": "test_pass",
            "validity_date": due_later_date.isoformat(),
            "renewal_amount": 2000.0
        }
    ]
    
    created_domains = []
    
    # Create test domains
    print("\n📝 Creating test domains...")
    for domain_data in test_domains:
        try:
            response = requests.post(f"{API_URL}/domains", json=domain_data)
            if response.status_code == 200:
                domain = response.json()
                created_domains.append(domain)
                print_success(f"Created domain: {domain['domain_name']} (Expires: {domain['validity_date']})")
            else:
                print_error(f"Failed to create domain {domain_data['domain_name']}: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating domain: {str(e)}")
            return False
    
    # Test the domains-due-renewal endpoint
    print("\n🔍 Testing domains-due-renewal endpoint...")
    try:
        response = requests.get(f"{API_URL}/domains-due-renewal")
        if response.status_code == 200:
            due_domains = response.json()
            print_success(f"Retrieved {len(due_domains)} domains due for renewal")
            
            # Check which of our test domains are included
            found_expired = False
            found_due_soon = False
            found_due_later = False
            
            for domain in due_domains:
                domain_name = domain.get('domain_name')
                days_until_expiry = domain.get('days_until_expiry')
                is_expired = domain.get('is_expired')
                
                print_info(f"Domain: {domain_name} | Days: {days_until_expiry} | Expired: {is_expired}")
                
                if domain_name == "test-expired.com":
                    found_expired = True
                    if days_until_expiry < 0 and is_expired:
                        print_success("✅ Expired domain correctly identified")
                    else:
                        print_error(f"❌ Expired domain logic error: days={days_until_expiry}, expired={is_expired}")
                        return False
                
                elif domain_name == "test-due-soon.com":
                    found_due_soon = True
                    if 0 <= days_until_expiry <= 30 and not is_expired:
                        print_success("✅ Due soon domain correctly identified")
                    else:
                        print_error(f"❌ Due soon domain logic error: days={days_until_expiry}, expired={is_expired}")
                        return False
                
                elif domain_name == "test-due-later.com":
                    found_due_later = True
                    print_error("❌ Domain due later should NOT be in the list")
                    return False
            
            # Check results
            if not found_expired:
                print_error("❌ BUG CONFIRMED: Expired domain not found in due for renewal list")
                return False
            
            if not found_due_soon:
                print_error("❌ BUG CONFIRMED: Due soon domain not found in due for renewal list")
                return False
            
            if found_due_later:
                print_error("❌ BUG CONFIRMED: Domain due later incorrectly included")
                return False
            
            print_success("✅ Domains due for renewal logic is working correctly")
            return True
            
        else:
            print_error(f"❌ Failed to get domains due for renewal: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"❌ Exception testing domains due for renewal: {str(e)}")
        return False
    
    finally:
        # Clean up test domains
        print("\n🧹 Cleaning up test domains...")
        for domain in created_domains:
            try:
                requests.delete(f"{API_URL}/domains/{domain['id']}")
                print_info(f"Deleted test domain: {domain['domain_name']}")
            except:
                pass

if __name__ == "__main__":
    success = test_domains_due_renewal_detailed()
    sys.exit(0 if success else 1)