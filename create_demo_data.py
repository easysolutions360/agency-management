#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, date, timedelta

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

from server import Customer, Project, DomainHosting

async def create_demo_data():
    # MongoDB connection
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    
    print("Creating demo data for domain renewal testing...")
    
    # Create demo customer
    demo_customer = Customer(
        name="John Demo Customer",
        phone="+1234567890",
        email="john@demo.com",
        address="123 Demo Street, Demo City"
    )
    
    # Insert customer
    await db.customers.insert_one(demo_customer.dict())
    print(f"✅ Created customer: {demo_customer.name} (ID: {demo_customer.id})")
    
    # Create demo project
    demo_project = Project(
        customer_id=demo_customer.id,
        type="Website Development",
        name="Demo Website Project",
        amount=50000.0,
        amc_amount=8000.0,
        start_date=date.today() - timedelta(days=180),
        end_date=date.today() - timedelta(days=30)
    )
    
    # Convert dates to strings for MongoDB storage
    project_data = demo_project.dict()
    project_data['start_date'] = project_data['start_date'].isoformat()
    if project_data['end_date']:
        project_data['end_date'] = project_data['end_date'].isoformat()
    
    await db.projects.insert_one(project_data)
    print(f"✅ Created project: {demo_project.name} (ID: {demo_project.id})")
    
    # Create demo domains - some due for renewal
    domains_to_create = [
        {
            "domain_name": "demo-website.com",
            "hosting_provider": "GoDaddy",
            "validity_date": date.today() + timedelta(days=15),  # Due soon
            "renewal_amount": 1500.0
        },
        {
            "domain_name": "demo-expired.com", 
            "hosting_provider": "Hostinger",
            "validity_date": date.today() - timedelta(days=5),  # Already expired
            "renewal_amount": 1200.0
        },
        {
            "domain_name": "demo-future.com",
            "hosting_provider": "Namecheap", 
            "validity_date": date.today() + timedelta(days=60),  # Not due yet
            "renewal_amount": 2000.0
        }
    ]
    
    for domain_info in domains_to_create:
        demo_domain = DomainHosting(
            project_id=demo_project.id,
            domain_name=domain_info["domain_name"],
            hosting_provider=domain_info["hosting_provider"],
            username="demo_user",
            password="demo_password123",
            validity_date=domain_info["validity_date"],
            renewal_amount=domain_info["renewal_amount"]
        )
        
        # Convert date to string for MongoDB storage
        domain_data = demo_domain.dict()
        domain_data['validity_date'] = domain_data['validity_date'].isoformat()
        
        await db.domains.insert_one(domain_data)
        print(f"✅ Created domain: {demo_domain.domain_name} (ID: {demo_domain.id}) - Validity: {domain_info['validity_date']}")
    
    print("\n🎉 Demo data created successfully!")
    print("\nYou can now test the domain renewal functionality in Reports > Domain Renewals")
    print("- demo-website.com: Due in 15 days")
    print("- demo-expired.com: Already expired (5 days ago)")
    print("- demo-future.com: Not due for 60 days (won't appear in renewal list)")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_demo_data())