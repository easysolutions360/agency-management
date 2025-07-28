#!/usr/bin/env python3
"""
Test AMC Payment Flow to verify the bug fix
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
print(f"🔗 Testing AMC Payment Flow at: {API_URL}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_amc_payment_flow():
    """Test the complete AMC payment flow"""
    print("\n" + "="*80)
    print("🧪 TESTING AMC PAYMENT FLOW")
    print("="*80)
    
    # Step 1: Get AMC projects (before payment)
    print("\n📋 Step 1: Getting AMC projects before payment...")
    try:
        response = requests.get(f"{API_URL}/dashboard/amc-projects")
        if response.status_code == 200:
            amc_projects_before = response.json()
            print_success(f"Found {len(amc_projects_before)} AMC projects before payment")
            
            if len(amc_projects_before) == 0:
                print_error("No AMC projects found. Please ensure test data exists.")
                return False
            
            # Show first project details
            first_project = amc_projects_before[0]
            print_info(f"First project: {first_project['project_name']} (AMC: ₹{first_project['amc_amount']})")
            print_info(f"Customer: {first_project['customer_name']}")
            print_info(f"Days until AMC: {first_project['days_until_amc']}")
            print_info(f"Is overdue: {first_project['is_overdue']}")
            
        else:
            print_error(f"Failed to get AMC projects: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting AMC projects: {str(e)}")
        return False
    
    # Step 2: Check customer ledger before payment
    print("\n📋 Step 2: Checking customer ledger before payment...")
    customer_id = first_project['customer_name']
    try:
        # Get customer ID by name (need to find the actual ID)
        customers_response = requests.get(f"{API_URL}/customers")
        if customers_response.status_code == 200:
            customers = customers_response.json()
            target_customer = next((c for c in customers if c['name'] == first_project['customer_name']), None)
            if target_customer:
                customer_id = target_customer['id']
                print_info(f"Customer ID: {customer_id}")
                
                # Get customer ledger
                ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
                if ledger_response.status_code == 200:
                    ledger_before = ledger_response.json()
                    print_success(f"Customer ledger has {len(ledger_before)} entries before payment")
                    
                    # Show recent entries
                    for entry in ledger_before[:3]:  # Show last 3 entries
                        print_info(f"  {entry['transaction_type']}: ₹{entry['amount']} - {entry['description']}")
                else:
                    print_error(f"Failed to get customer ledger: {ledger_response.status_code}")
            else:
                print_error(f"Customer not found: {first_project['customer_name']}")
                return False
        else:
            print_error(f"Failed to get customers: {customers_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error checking customer ledger: {str(e)}")
        return False
    
    # Step 3: Record AMC payment
    print("\n💳 Step 3: Recording AMC payment...")
    project_id = first_project['project_id']
    amc_amount = first_project['amc_amount']
    
    try:
        payment_data = {
            "project_id": project_id,
            "amount": amc_amount,
            "payment_date": datetime.now().isoformat()
        }
        
        response = requests.post(f"{API_URL}/amc-payment/{project_id}", json=payment_data)
        if response.status_code == 200:
            payment_result = response.json()
            print_success(f"AMC payment recorded successfully")
            print_info(f"Response: {payment_result['message']}")
        else:
            print_error(f"Failed to record AMC payment: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error recording AMC payment: {str(e)}")
        return False
    
    # Step 4: Check AMC projects after payment (should be removed)
    print("\n📋 Step 4: Checking AMC projects after payment...")
    try:
        response = requests.get(f"{API_URL}/dashboard/amc-projects")
        if response.status_code == 200:
            amc_projects_after = response.json()
            print_success(f"Found {len(amc_projects_after)} AMC projects after payment")
            
            # Check if the paid project is still in the list
            paid_project_still_exists = any(p['project_id'] == project_id for p in amc_projects_after)
            
            if paid_project_still_exists:
                print_error("❌ BUG CONFIRMED: Paid AMC project still appears in AMC tracker!")
                return False
            else:
                print_success("✅ BUG FIXED: Paid AMC project removed from AMC tracker!")
                
        else:
            print_error(f"Failed to get AMC projects after payment: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting AMC projects after payment: {str(e)}")
        return False
    
    # Step 5: Check customer ledger after payment
    print("\n📋 Step 5: Checking customer ledger after payment...")
    try:
        ledger_response = requests.get(f"{API_URL}/ledger/customer/{customer_id}")
        if ledger_response.status_code == 200:
            ledger_after = ledger_response.json()
            print_success(f"Customer ledger has {len(ledger_after)} entries after payment")
            
            # Look for the AMC payment entry
            amc_payment_entry = next((entry for entry in ledger_after if 
                                    entry['transaction_type'] == 'credit' and 
                                    entry['reference_type'] == 'amc' and
                                    entry['reference_id'] == project_id), None)
            
            if amc_payment_entry:
                print_success(f"✅ AMC payment entry found in customer ledger")
                print_info(f"  Amount: ₹{amc_payment_entry['amount']}")
                print_info(f"  Description: {amc_payment_entry['description']}")
                print_info(f"  Balance: ₹{amc_payment_entry['balance']}")
            else:
                print_error("❌ AMC payment entry not found in customer ledger")
                return False
                
        else:
            print_error(f"Failed to get customer ledger after payment: {ledger_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error checking customer ledger after payment: {str(e)}")
        return False
    
    # Step 6: Verify customer balance
    print("\n💰 Step 6: Verifying customer balance...")
    try:
        balance_response = requests.get(f"{API_URL}/customer-payment-summary/{customer_id}")
        if balance_response.status_code == 200:
            balance_data = balance_response.json()
            print_success(f"Customer balance summary retrieved")
            print_info(f"  Outstanding amount: ₹{balance_data['outstanding_amount']}")
            print_info(f"  Credit balance: ₹{balance_data['credit_balance']}")
            print_info(f"  Total paid: ₹{balance_data['total_paid_amount']}")
        else:
            print_error(f"Failed to get customer balance: {balance_response.status_code}")
    except Exception as e:
        print_error(f"Error checking customer balance: {str(e)}")
    
    print("\n🎉 AMC Payment Flow Test Completed Successfully!")
    return True

if __name__ == "__main__":
    success = test_amc_payment_flow()
    if success:
        print("\n✅ ALL TESTS PASSED - AMC Payment Bug is FIXED!")
    else:
        print("\n❌ TESTS FAILED - AMC Payment Bug still exists!")
    sys.exit(0 if success else 1)