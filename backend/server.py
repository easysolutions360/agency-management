from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, date, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: str
    email: str
    address: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: str
    address: str

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    type: str
    name: str
    amount: float
    paid_amount: float = 0.0
    amc_amount: float = 0.0
    start_date: date
    end_date: Optional[date] = None
    payment_status: str = "pending"  # pending, partial, paid
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectCreate(BaseModel):
    customer_id: str
    type: str
    name: str
    amount: float
    amc_amount: float = 0.0
    start_date: date
    end_date: Optional[date] = None

class ProjectUpdate(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    amount: Optional[float] = None
    amc_amount: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class DomainHosting(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    domain_name: str
    hosting_provider: str
    username: str
    password: str
    validity_date: date
    renewal_amount: float = 0.0
    renewal_status: str = "active"  # active, due, renewed
    payment_type: str = "client"  # client, agency
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DomainHostingCreate(BaseModel):
    project_id: str
    domain_name: str
    hosting_provider: str
    username: str
    password: str
    validity_date: date
    renewal_amount: float = 0.0

class DomainHostingUpdate(BaseModel):
    domain_name: Optional[str] = None
    hosting_provider: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    validity_date: Optional[date] = None
    renewal_amount: Optional[float] = None
    renewal_status: Optional[str] = None
    payment_type: Optional[str] = None

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    type: str  # project_advance, domain_renewal, amc_payment, credit_payment
    reference_id: str  # project_id, domain_id, or amc_id
    amount: float
    description: str
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "completed"  # completed, pending, failed

class PaymentCreate(BaseModel):
    customer_id: str
    type: str
    reference_id: str
    amount: float
    description: str

class CustomerLedger(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    transaction_type: str  # debit, credit
    amount: float
    description: str
    reference_type: str  # project, domain, amc
    reference_id: str
    date: datetime = Field(default_factory=datetime.utcnow)
    balance: float = 0.0

class CustomerLedgerCreate(BaseModel):
    customer_id: str
    transaction_type: str
    amount: float
    description: str
    reference_type: str
    reference_id: str

class ProjectWithDetails(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    type: str
    name: str
    amount: float
    amc_amount: float
    start_date: date
    end_date: Optional[date] = None
    domains: List[DomainHosting]
    created_at: datetime

# New models for enhanced payment functionality
class DomainRenewalRequest(BaseModel):
    domain_id: str
    payment_type: str  # "client" or "agency"
    notes: str = ""

class AMCPaymentRequest(BaseModel):
    project_id: str
    amount: float
    payment_date: datetime = Field(default_factory=datetime.utcnow)

class PaymentStatus(BaseModel):
    project_id: str
    total_amount: float
    paid_amount: float
    remaining_amount: float
    payment_status: str
    amc_amount: float
    amc_due_date: Optional[date] = None
    amc_paid: bool = False

class CustomerPaymentSummary(BaseModel):
    customer_id: str
    customer_name: str
    total_projects: int
    total_project_amount: float
    total_paid_amount: float
    outstanding_amount: float
    credit_balance: float
    recent_payments: List[dict]

# Customer Routes
@api_router.post("/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate):
    customer_dict = customer.dict()
    customer_obj = Customer(**customer_dict)
    await db.customers.insert_one(customer_obj.dict())
    return customer_obj

@api_router.get("/customers", response_model=List[Customer])
async def get_customers():
    customers = await db.customers.find().to_list(1000)
    return [Customer(**customer) for customer in customers]

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return Customer(**customer)

@api_router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, customer_update: CustomerUpdate):
    update_dict = {k: v for k, v in customer_update.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.customers.update_one(
        {"id": customer_id}, 
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    updated_customer = await db.customers.find_one({"id": customer_id})
    return Customer(**updated_customer)

@api_router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str):
    result = await db.customers.delete_one({"id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}

# Project Routes
@api_router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate):
    # Check if customer exists
    customer = await db.customers.find_one({"id": project.customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    project_dict = project.dict()
    project_obj = Project(**project_dict)
    
    # Convert date objects to strings for MongoDB storage
    project_data = project_obj.dict()
    project_data['start_date'] = project_data['start_date'].isoformat()
    if project_data['end_date']:
        project_data['end_date'] = project_data['end_date'].isoformat()
    else:
        project_data['end_date'] = None
    
    await db.projects.insert_one(project_data)
    
    # Create customer ledger entry for project creation (DEBIT - customer owes money)
    # Get current balance before adding this transaction
    current_balance = await get_customer_balance(project.customer_id)
    
    ledger_entry = CustomerLedger(
        customer_id=project.customer_id,
        transaction_type="debit",
        amount=project.amount,
        description=f"Project created: {project.name}",
        reference_type="project",
        reference_id=project_obj.id,
        balance=current_balance - project.amount  # New balance after this debit
    )
    
    await db.ledger.insert_one(ledger_entry.dict())
    
    return project_obj

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects = await db.projects.find().to_list(1000)
    # Convert string dates back to date objects
    for project in projects:
        if isinstance(project.get('start_date'), str):
            project['start_date'] = datetime.fromisoformat(project['start_date']).date()
        if isinstance(project.get('end_date'), str) and project.get('end_date'):
            project['end_date'] = datetime.fromisoformat(project['end_date']).date()
        elif project.get('end_date') is None:
            project['end_date'] = None
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Convert string dates back to date objects
    if isinstance(project.get('start_date'), str):
        project['start_date'] = datetime.fromisoformat(project['start_date']).date()
    if isinstance(project.get('end_date'), str) and project.get('end_date'):
        project['end_date'] = datetime.fromisoformat(project['end_date']).date()
    elif project.get('end_date') is None:
        project['end_date'] = None
    return Project(**project)

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project_update: ProjectUpdate):
    # Allow None values for end_date to make it optional
    update_dict = {}
    for k, v in project_update.dict().items():
        if v is not None or k == 'end_date':
            update_dict[k] = v
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Convert date objects to strings for MongoDB storage
    if 'start_date' in update_dict and update_dict['start_date']:
        update_dict['start_date'] = update_dict['start_date'].isoformat()
    if 'end_date' in update_dict:
        if update_dict['end_date']:
            update_dict['end_date'] = update_dict['end_date'].isoformat()
        else:
            update_dict['end_date'] = None
    
    result = await db.projects.update_one(
        {"id": project_id}, 
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_project = await db.projects.find_one({"id": project_id})
    # Convert string dates back to date objects
    if isinstance(updated_project.get('start_date'), str):
        updated_project['start_date'] = datetime.fromisoformat(updated_project['start_date']).date()
    if isinstance(updated_project.get('end_date'), str) and updated_project.get('end_date'):
        updated_project['end_date'] = datetime.fromisoformat(updated_project['end_date']).date()
    elif updated_project.get('end_date') is None:
        updated_project['end_date'] = None
    return Project(**updated_project)

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

# Domain/Hosting Routes
@api_router.post("/domains", response_model=DomainHosting)
async def create_domain_hosting(domain: DomainHostingCreate):
    # Check if project exists
    project = await db.projects.find_one({"id": domain.project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    domain_dict = domain.dict()
    domain_obj = DomainHosting(**domain_dict)
    
    # Convert date objects to strings for MongoDB storage
    domain_data = domain_obj.dict()
    domain_data['validity_date'] = domain_data['validity_date'].isoformat()
    
    await db.domains.insert_one(domain_data)
    return domain_obj

@api_router.get("/domains", response_model=List[DomainHosting])
async def get_domains():
    domains = await db.domains.find().to_list(1000)
    # Convert string dates back to date objects
    for domain in domains:
        if isinstance(domain.get('validity_date'), str):
            domain['validity_date'] = datetime.fromisoformat(domain['validity_date']).date()
    return [DomainHosting(**domain) for domain in domains]

@api_router.get("/domains/project/{project_id}", response_model=List[DomainHosting])
async def get_domains_by_project(project_id: str):
    domains = await db.domains.find({"project_id": project_id}).to_list(1000)
    # Convert string dates back to date objects
    for domain in domains:
        if isinstance(domain.get('validity_date'), str):
            domain['validity_date'] = datetime.fromisoformat(domain['validity_date']).date()
    return [DomainHosting(**domain) for domain in domains]

@api_router.get("/domains/{domain_id}", response_model=DomainHosting)
async def get_domain(domain_id: str):
    domain = await db.domains.find_one({"id": domain_id})
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    # Convert string dates back to date objects
    if isinstance(domain.get('validity_date'), str):
        domain['validity_date'] = datetime.fromisoformat(domain['validity_date']).date()
    return DomainHosting(**domain)

@api_router.put("/domains/{domain_id}", response_model=DomainHosting)
async def update_domain_hosting(domain_id: str, domain_update: DomainHostingUpdate):
    update_dict = {k: v for k, v in domain_update.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Convert date objects to strings for MongoDB storage if needed
    if 'validity_date' in update_dict and isinstance(update_dict['validity_date'], date):
        update_dict['validity_date'] = update_dict['validity_date'].isoformat()
    
    result = await db.domains.update_one(
        {"id": domain_id}, 
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    updated_domain = await db.domains.find_one({"id": domain_id})
    # Convert string dates back to date objects
    if isinstance(updated_domain.get('validity_date'), str):
        updated_domain['validity_date'] = datetime.fromisoformat(updated_domain['validity_date']).date()
    return DomainHosting(**updated_domain)

@api_router.delete("/domains/{domain_id}")
async def delete_domain_hosting(domain_id: str):
    result = await db.domains.delete_one({"id": domain_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Domain not found")
    return {"message": "Domain deleted successfully"}

# Dashboard Routes
@api_router.get("/dashboard/projects", response_model=List[ProjectWithDetails])
async def get_dashboard_projects():
    projects = await db.projects.find().to_list(1000)
    project_details = []
    
    for project in projects:
        # Convert string dates back to date objects for projects
        if isinstance(project.get('start_date'), str):
            project['start_date'] = datetime.fromisoformat(project['start_date']).date()
        if isinstance(project.get('end_date'), str):
            project['end_date'] = datetime.fromisoformat(project['end_date']).date()
            
        # Get customer details
        customer = await db.customers.find_one({"id": project["customer_id"]})
        
        # Get domains for this project
        domains = await db.domains.find({"project_id": project["id"]}).to_list(1000)
        # Convert string dates back to date objects for domains
        for domain in domains:
            if isinstance(domain.get('validity_date'), str):
                domain['validity_date'] = datetime.fromisoformat(domain['validity_date']).date()
        domain_objects = [DomainHosting(**domain) for domain in domains]
        
        if customer:
            project_detail = ProjectWithDetails(
                id=project["id"],
                customer_id=project["customer_id"],
                customer_name=customer["name"],
                customer_email=customer["email"],
                customer_phone=customer["phone"],
                type=project["type"],
                name=project["name"],
                amount=project["amount"],
                amc_amount=project.get("amc_amount", 0.0),
                start_date=project["start_date"],
                end_date=project["end_date"],
                domains=domain_objects,
                created_at=project["created_at"]
            )
            project_details.append(project_detail)
    
    return project_details

@api_router.get("/dashboard/amc-projects")
async def get_amc_projects():
    """Get projects that are due for AMC (Annual Maintenance Contract) - 1 year after project completion"""
    from datetime import datetime, timedelta
    
    # Get all projects that have an end_date
    projects = await db.projects.find({"end_date": {"$exists": True, "$ne": None}}).to_list(1000)
    
    amc_projects = []
    current_date = datetime.now().date()
    
    for project in projects:
        # Convert string dates back to date objects if needed
        if isinstance(project.get('end_date'), str):
            project_end_date = datetime.fromisoformat(project['end_date']).date()
        else:
            project_end_date = project['end_date']
        
        # Calculate AMC due date (1 year after project completion)
        amc_due_date = project_end_date + timedelta(days=365)
        
        # Check if AMC is due (within next 30 days or already due)
        days_until_amc = (amc_due_date - current_date).days
        if days_until_amc <= 30:  # AMC due within 30 days
            # Get customer details
            customer = await db.customers.find_one({"id": project["customer_id"]})
            
            if customer:
                amc_projects.append({
                    "project_id": project["id"],
                    "project_name": project["name"],
                    "project_type": project["type"],
                    "project_amount": project["amount"],
                    "project_end_date": project_end_date.isoformat(),
                    "amc_due_date": amc_due_date.isoformat(),
                    "days_until_amc": days_until_amc,
                    "customer_name": customer["name"],
                    "customer_email": customer["email"],
                    "customer_phone": customer["phone"],
                    "is_overdue": days_until_amc < 0
                })
    
    # Sort by days_until_amc (most urgent first)
    amc_projects.sort(key=lambda x: x["days_until_amc"])
    
    return amc_projects

@api_router.get("/dashboard/expiring-domains")
async def get_expiring_domains():
    from datetime import timedelta
    
    # Get domains expiring in the next 30 days
    thirty_days_from_now = datetime.now().date() + timedelta(days=30)
    thirty_days_str = thirty_days_from_now.isoformat()
    
    domains = await db.domains.find({
        "validity_date": {"$lte": thirty_days_str}
    }).to_list(1000)
    
    expiring_domains = []
    for domain in domains:
        # Get project and customer details
        project = await db.projects.find_one({"id": domain["project_id"]})
        if project:
            customer = await db.customers.find_one({"id": project["customer_id"]})
            if customer:
                from datetime import datetime as dt
                validity_date = dt.fromisoformat(domain["validity_date"]).date()
                days_remaining = (validity_date - datetime.now().date()).days
                
                expiring_domains.append({
                    "domain_name": domain["domain_name"],
                    "hosting_provider": domain["hosting_provider"],
                    "validity_date": domain["validity_date"],
                    "project_name": project["name"],
                    "customer_name": customer["name"],
                    "customer_email": customer["email"],
                    "days_remaining": days_remaining
                })
    
    return expiring_domains

# Payment Routes
@api_router.post("/payments", response_model=Payment)
async def create_payment(payment: PaymentCreate):
    # Create payment record
    payment_dict = payment.dict()
    payment_obj = Payment(**payment_dict)
    await db.payments.insert_one(payment_obj.dict())
    
    # Create ledger entry (CREDIT - customer pays money)
    # Get current balance before adding this transaction
    current_balance = await get_customer_balance(payment.customer_id)
    
    ledger_entry = CustomerLedger(
        customer_id=payment.customer_id,
        transaction_type="credit",
        amount=payment.amount,
        description=payment.description,
        reference_type=payment.type,
        reference_id=payment.reference_id,
        balance=current_balance + payment.amount  # New balance after this credit
    )
    
    await db.ledger.insert_one(ledger_entry.dict())
    
    # Update payment status in respective modules
    if payment.type == "project_advance":
        await update_project_payment(payment.reference_id, payment.amount)
    elif payment.type == "amc_payment":
        await update_amc_payment(payment.reference_id)
    
    return payment_obj

@api_router.get("/payments/customer/{customer_id}", response_model=List[Payment])
async def get_customer_payments(customer_id: str):
    payments = await db.payments.find({"customer_id": customer_id}).to_list(1000)
    return [Payment(**payment) for payment in payments]

@api_router.get("/ledger/customer/{customer_id}", response_model=List[CustomerLedger])
async def get_customer_ledger(customer_id: str):
    ledger = await db.ledger.find({"customer_id": customer_id}).sort("date", -1).to_list(1000)
    return [CustomerLedger(**entry) for entry in ledger]

@api_router.post("/domain-renewal/{domain_id}")
async def renew_domain(domain_id: str, renewal_request: DomainRenewalRequest):
    domain = await db.domains.find_one({"id": domain_id})
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    # Get project and customer info
    project = await db.projects.find_one({"id": domain["project_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Calculate new validity date (extend by 1 year)
    current_validity = datetime.fromisoformat(domain["validity_date"]).date()
    new_validity = current_validity + timedelta(days=365)
    
    # Update domain
    await db.domains.update_one(
        {"id": domain_id},
        {"$set": {
            "validity_date": new_validity.isoformat(),
            "renewal_status": "renewed",
            "payment_type": renewal_request.payment_type
        }}
    )
    
    # Handle payment based on who pays
    if renewal_request.payment_type == "agency":
        # Agency pays - create debit entry in customer ledger (customer owes money)
        # Get current balance before adding this transaction
        current_balance = await get_customer_balance(project["customer_id"])
        
        ledger_entry = CustomerLedger(
            customer_id=project["customer_id"],
            transaction_type="debit",
            amount=domain["renewal_amount"],
            description=f"Domain renewal for {domain['domain_name']} (Agency paid)",
            reference_type="domain_renewal",
            reference_id=domain_id,
            balance=current_balance - domain["renewal_amount"]  # New balance after this debit
        )
        
        await db.ledger.insert_one(ledger_entry.dict())
        
        # Create a payment record for agency payment
        payment_obj = Payment(
            customer_id=project["customer_id"],
            type="domain_renewal_agency",
            reference_id=domain_id,
            amount=domain["renewal_amount"],
            description=f"Domain renewal for {domain['domain_name']} (Agency paid - awaiting client payment)",
            status="pending"
        )
        await db.payments.insert_one(payment_obj.dict())
    
    return {"message": "Domain renewed successfully", "new_validity_date": new_validity.isoformat()}

@api_router.post("/domain-renewal-payment/{domain_id}")
async def record_domain_renewal_payment(domain_id: str, payment_data: dict):
    """Record payment received from client for agency-paid domain renewal"""
    domain = await db.domains.find_one({"id": domain_id})
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    project = await db.projects.find_one({"id": domain["project_id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create credit entry in customer ledger
    ledger_entry = CustomerLedger(
        customer_id=project["customer_id"],
        transaction_type="credit",
        amount=payment_data["amount"],
        description=f"Payment received for domain renewal: {domain['domain_name']}",
        reference_type="domain_renewal_payment",
        reference_id=domain_id
    )
    
    # Calculate balance
    customer_balance = await get_customer_balance(project["customer_id"])
    ledger_entry.balance = customer_balance + payment_data["amount"]
    
    await db.ledger.insert_one(ledger_entry.dict())
    
    # Update the pending payment status
    await db.payments.update_one(
        {"reference_id": domain_id, "type": "domain_renewal_agency"},
        {"$set": {"status": "completed"}}
    )
    
    return {"message": "Domain renewal payment recorded successfully"}

async def get_customer_balance(customer_id: str):
    """Calculate customer balance from ledger"""
    ledger_entries = await db.ledger.find({"customer_id": customer_id}).to_list(1000)
    balance = 0.0
    for entry in ledger_entries:
        if entry["transaction_type"] == "credit":
            balance += entry["amount"]
        else:
            balance -= entry["amount"]
    return balance

async def update_project_payment(project_id: str, amount: float):
    """Update project payment status"""
    project = await db.projects.find_one({"id": project_id})
    if project:
        new_paid_amount = project.get("paid_amount", 0) + amount
        total_amount = project["amount"]
        
        if new_paid_amount >= total_amount:
            payment_status = "paid"
        elif new_paid_amount > 0:
            payment_status = "partial"
        else:
            payment_status = "pending"
        
        await db.projects.update_one(
            {"id": project_id},
            {"$set": {
                "paid_amount": new_paid_amount,
                "payment_status": payment_status
            }}
        )

async def update_amc_payment(project_id: str):
    """Update AMC payment and extend for next year"""
    project = await db.projects.find_one({"id": project_id})
    if not project:
        return
    
    # Calculate new AMC due date (1 year from payment date)
    current_date = datetime.utcnow().date()
    new_amc_due_date = current_date + timedelta(days=365)
    
    # Update project with AMC payment status
    await db.projects.update_one(
        {"id": project_id},
        {"$set": {
            "amc_paid_until": new_amc_due_date.isoformat(),
            "last_amc_payment_date": current_date.isoformat()
        }}
    )
    
    return {"message": "AMC renewed for one year", "new_due_date": new_amc_due_date.isoformat()}

# Enhanced Payment Endpoints
@api_router.post("/amc-payment/{project_id}")
async def record_amc_payment(project_id: str, payment_request: AMCPaymentRequest):
    """Record AMC payment and renew for next year"""
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create payment record
    payment_obj = Payment(
        customer_id=project["customer_id"],
        type="amc_payment",
        reference_id=project_id,
        amount=payment_request.amount,
        description=f"AMC payment for project: {project['name']}",
        payment_date=payment_request.payment_date
    )
    await db.payments.insert_one(payment_obj.dict())
    
    # Create ledger entry
    ledger_entry = CustomerLedger(
        customer_id=project["customer_id"],
        transaction_type="credit",
        amount=payment_request.amount,
        description=f"AMC payment received for: {project['name']}",
        reference_type="amc",
        reference_id=project_id
    )
    
    # Calculate balance
    customer_balance = await get_customer_balance(project["customer_id"])
    ledger_entry.balance = customer_balance + payment_request.amount
    
    await db.ledger.insert_one(ledger_entry.dict())
    
    # Update AMC status
    await update_amc_payment(project_id)
    
    return {"message": "AMC payment recorded and renewed successfully"}

@api_router.get("/payment-status/{project_id}", response_model=PaymentStatus)
async def get_payment_status(project_id: str):
    """Get comprehensive payment status for a project"""
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Calculate AMC due date if project is completed
    amc_due_date = None
    amc_paid = False
    
    if project.get("end_date"):
        end_date = datetime.fromisoformat(project["end_date"]).date()
        amc_due_date = end_date + timedelta(days=365)
        
        # Check if AMC is paid
        if project.get("amc_paid_until"):
            amc_paid_until = datetime.fromisoformat(project["amc_paid_until"]).date()
            amc_paid = amc_paid_until > datetime.utcnow().date()
    
    return PaymentStatus(
        project_id=project_id,
        total_amount=project["amount"],
        paid_amount=project.get("paid_amount", 0),
        remaining_amount=project["amount"] - project.get("paid_amount", 0),
        payment_status=project.get("payment_status", "pending"),
        amc_amount=project.get("amc_amount", 0),
        amc_due_date=amc_due_date,
        amc_paid=amc_paid
    )

@api_router.get("/customer-payment-summary/{customer_id}", response_model=CustomerPaymentSummary)
async def get_customer_payment_summary(customer_id: str):
    """Get comprehensive payment summary for a customer"""
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get all customer projects
    projects = await db.projects.find({"customer_id": customer_id}).to_list(1000)
    
    total_project_amount = sum(p.get("amount", 0) for p in projects)
    total_paid_amount = sum(p.get("paid_amount", 0) for p in projects)
    outstanding_amount = total_project_amount - total_paid_amount
    
    # Get customer balance
    credit_balance = await get_customer_balance(customer_id)
    
    # Get recent payments (last 10)
    payments = await db.payments.find({"customer_id": customer_id}).sort("payment_date", -1).limit(10).to_list(10)
    recent_payments = [
        {
            "date": p["payment_date"],
            "amount": p["amount"],
            "type": p["type"],
            "description": p["description"]
        }
        for p in payments
    ]
    
    return CustomerPaymentSummary(
        customer_id=customer_id,
        customer_name=customer["name"],
        total_projects=len(projects),
        total_project_amount=total_project_amount,
        total_paid_amount=total_paid_amount,
        outstanding_amount=outstanding_amount,
        credit_balance=credit_balance,
        recent_payments=recent_payments
    )

@api_router.get("/domains-due-renewal")
async def get_domains_due_renewal():
    """Get domains that are due for renewal in next 30 days"""
    current_date = datetime.utcnow().date()
    domains = await db.domains.find().to_list(1000)
    
    due_domains = []
    for domain in domains:
        validity_date = datetime.fromisoformat(domain["validity_date"]).date()
        days_until_expiry = (validity_date - current_date).days
        
        if days_until_expiry <= 30:  # Due within 30 days
            # Get project and customer info
            project = await db.projects.find_one({"id": domain["project_id"]})
            customer = await db.customers.find_one({"id": project["customer_id"]}) if project else None
            
            due_domains.append({
                "domain_id": domain["id"],
                "domain_name": domain["domain_name"],
                "hosting_provider": domain["hosting_provider"],
                "validity_date": domain["validity_date"],
                "days_until_expiry": days_until_expiry,
                "renewal_amount": domain.get("renewal_amount", 0),
                "project_name": project["name"] if project else "Unknown",
                "customer_name": customer["name"] if customer else "Unknown",
                "customer_id": project["customer_id"] if project else None,
                "is_expired": days_until_expiry < 0
            })
    
    # Sort by days until expiry (most urgent first)
    due_domains.sort(key=lambda x: x["days_until_expiry"])
    
    return due_domains

@api_router.get("/dashboard/customer-balances")
async def get_all_customer_balances():
    """Get balance summary for all customers"""
    customers = await db.customers.find().to_list(1000)
    balances = []
    
    for customer in customers:
        balance = await get_customer_balance(customer["id"])
        balances.append({
            "customer_id": customer["id"],
            "customer_name": customer["name"],
            "balance": balance
        })
    
    return balances

@api_router.get("/")
async def root():
    return {"message": "Agency Management System API"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()