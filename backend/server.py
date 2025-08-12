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
    company_name: str = ""
    gst_no: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: str
    address: str
    company_name: str = ""
    gst_no: str = ""

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    company_name: Optional[str] = None
    gst_no: Optional[str] = None

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

# Product Master Models
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_name: str
    hsn_code: str
    tax_group: str  # GST0, GST5, GST12, GST18, GST28
    tax_percentage: float  # Will be set based on tax_group
    sale_price: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    product_name: str
    hsn_code: str
    tax_group: str  # GST0, GST5, GST12, GST18, GST28
    sale_price: float

class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    hsn_code: Optional[str] = None
    tax_group: Optional[str] = None
    sale_price: Optional[float] = None

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
    new_validity_date: Optional[str] = None  # Allow custom validity date
    amount: Optional[float] = None  # Allow custom renewal amount
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

class BusinessFinancialSummary(BaseModel):
    total_projects: int
    total_customers: int
    total_project_value: float
    total_received: float
    total_outstanding: float
    total_customer_credit: float
    net_revenue: float
    project_completion_rate: float
    payment_collection_rate: float
    top_customers: List[dict]
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
        
        # Check if AMC has already been paid
        amc_paid_until = project.get('amc_paid_until')
        if amc_paid_until:
            # Convert to date if string
            if isinstance(amc_paid_until, str):
                amc_paid_until_date = datetime.fromisoformat(amc_paid_until).date()
            else:
                amc_paid_until_date = amc_paid_until
            
            # If AMC is paid until a future date, skip this project
            if amc_paid_until_date > current_date:
                continue
        
        # Check if AMC is due (within next 30 days or already due)
        days_until_amc = (amc_due_date - current_date).days
        if days_until_amc <= 30:  # AMC due within 30 days
            # Get customer details
            customer = await db.customers.find_one({"id": project["customer_id"]})
            
            if customer:
                # Check if AMC debt entry already exists in ledger
                amc_debt_exists = await db.ledger.find_one({
                    "customer_id": project["customer_id"],
                    "reference_type": "amc_due",
                    "reference_id": project["id"]
                })
                
                # If AMC is overdue and no debt entry exists, create it
                if days_until_amc < 0 and not amc_debt_exists and project.get("amc_amount", 0) > 0:
                    # Get current balance before adding this transaction
                    current_balance = await get_customer_balance(project["customer_id"])
                    
                    # Create AMC debt entry
                    ledger_entry = CustomerLedger(
                        customer_id=project["customer_id"],
                        transaction_type="debit",
                        amount=project.get("amc_amount", 0),
                        description=f"AMC due for project: {project['name']}",
                        reference_type="amc_due",
                        reference_id=project["id"],
                        balance=current_balance - project.get("amc_amount", 0)
                    )
                    
                    await db.ledger.insert_one(ledger_entry.dict())
                
                amc_projects.append({
                    "project_id": project["id"],
                    "project_name": project["name"],
                    "project_type": project["type"],
                    "project_amount": project["amount"],
                    "amc_amount": project.get("amc_amount", 0.0),
                    "project_end_date": project_end_date.isoformat(),
                    "amc_due_date": amc_due_date.isoformat(),
                    "days_until_amc": days_until_amc,
                    "customer_name": customer["name"],
                    "customer_email": customer["email"],
                    "customer_phone": customer["phone"],
                    "is_overdue": days_until_amc < 0,
                    "amc_paid_until": amc_paid_until
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
    
    # Use custom validity date if provided, otherwise extend by 1 year
    if renewal_request.new_validity_date:
        new_validity = datetime.fromisoformat(renewal_request.new_validity_date).date()
    else:
        current_validity = datetime.fromisoformat(domain["validity_date"]).date()
        new_validity = current_validity + timedelta(days=365)
    
    # Use custom amount if provided, otherwise use existing renewal_amount
    renewal_amount = renewal_request.amount if renewal_request.amount else domain.get("renewal_amount", 0)
    
    # Update domain
    await db.domains.update_one(
        {"id": domain_id},
        {"$set": {
            "validity_date": new_validity.isoformat(),
            "renewal_amount": renewal_amount,  # Update renewal amount
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
            amount=renewal_amount,
            description=f"Domain renewal for {domain['domain_name']} (Agency paid)",
            reference_type="domain_renewal",
            reference_id=domain_id,
            balance=current_balance - renewal_amount  # New balance after this debit
        )
        
        await db.ledger.insert_one(ledger_entry.dict())
        
        # Create a payment record for agency payment
        payment_obj = Payment(
            customer_id=project["customer_id"],
            type="domain_renewal_agency",
            reference_id=domain_id,
            amount=renewal_amount,
            description=f"Domain renewal for {domain['domain_name']} (Agency paid - awaiting client payment)",
            status="pending"
        )
        await db.payments.insert_one(payment_obj.dict())
    
    elif renewal_request.payment_type == "client":
        # Client pays directly - create payment record as completed
        payment_obj = Payment(
            customer_id=project["customer_id"],
            type="domain_renewal_client",
            reference_id=domain_id,
            amount=renewal_amount,
            description=f"Domain renewal for {domain['domain_name']} (Client paid directly)",
            status="completed"
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
    
    # Create credit entry in customer ledger (customer pays money)
    # Get current balance before adding this transaction
    current_balance = await get_customer_balance(project["customer_id"])
    
    ledger_entry = CustomerLedger(
        customer_id=project["customer_id"],
        transaction_type="credit",
        amount=payment_data["amount"],
        description=f"Payment received for domain renewal: {domain['domain_name']}",
        reference_type="domain_renewal_payment",
        reference_id=domain_id,
        balance=current_balance + payment_data["amount"]  # New balance after this credit
    )
    
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
    
    # Create ledger entry (customer pays AMC)
    # Get current balance before adding this transaction
    current_balance = await get_customer_balance(project["customer_id"])
    
    ledger_entry = CustomerLedger(
        customer_id=project["customer_id"],
        transaction_type="credit",
        amount=payment_request.amount,
        description=f"AMC payment received for: {project['name']}",
        reference_type="amc",
        reference_id=project_id,
        balance=current_balance + payment_request.amount  # New balance after this credit
    )
    
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

@api_router.get("/dashboard/business-financial-summary", response_model=BusinessFinancialSummary)
async def get_business_financial_summary():
    """Get comprehensive business financial summary for dashboard"""
    
    # Get all projects and customers
    projects = await db.projects.find().to_list(1000)
    customers = await db.customers.find().to_list(1000)
    payments = await db.payments.find().sort("payment_date", -1).to_list(1000)
    
    # Calculate project totals
    total_projects = len(projects)
    total_customers = len(customers)
    total_project_value = sum(p.get("amount", 0) for p in projects)
    total_received = sum(p.get("paid_amount", 0) for p in projects)
    total_outstanding = total_project_value - total_received
    
    # Calculate customer credit balances
    total_customer_credit = 0
    customer_credits = []
    for customer in customers:
        balance = await get_customer_balance(customer["id"])
        total_customer_credit += balance
        if balance > 0:  # Only customers with positive credit
            customer_credits.append({
                "customer_name": customer["name"],
                "credit_balance": balance
            })
    
    # Calculate rates
    project_completion_rate = (total_received / total_project_value * 100) if total_project_value > 0 else 0
    payment_collection_rate = project_completion_rate  # Same calculation for now
    net_revenue = total_received + total_customer_credit
    
    # Get top customers by project value
    customer_totals = {}
    for project in projects:
        customer_id = project.get("customer_id")
        amount = project.get("amount", 0)
        if customer_id in customer_totals:
            customer_totals[customer_id]["total_amount"] += amount
            customer_totals[customer_id]["project_count"] += 1
        else:
            # Find customer name
            customer = next((c for c in customers if c["id"] == customer_id), None)
            customer_totals[customer_id] = {
                "customer_name": customer["name"] if customer else "Unknown",
                "total_amount": amount,
                "project_count": 1
            }
    
    # Sort and get top 5 customers
    top_customers = sorted(
        customer_totals.values(), 
        key=lambda x: x["total_amount"], 
        reverse=True
    )[:5]
    
    # Get recent payments (last 10)
    recent_payments = [
        {
            "date": p.get("payment_date"),
            "amount": p.get("amount", 0),
            "type": p.get("type", ""),
            "description": p.get("description", ""),
            "customer_id": p.get("customer_id", "")
        }
        for p in payments[:10]
    ]
    
    return BusinessFinancialSummary(
        total_projects=total_projects,
        total_customers=total_customers,
        total_project_value=total_project_value,
        total_received=total_received,
        total_outstanding=total_outstanding,
        total_customer_credit=total_customer_credit,
        net_revenue=net_revenue,
        project_completion_rate=round(project_completion_rate, 2),
        payment_collection_rate=round(payment_collection_rate, 2),
        top_customers=top_customers,
        recent_payments=recent_payments
    )

# Helper function to get tax percentage from tax group
def get_tax_percentage(tax_group: str) -> float:
    tax_mapping = {
        "GST0": 0.0,
        "GST5": 5.0,
        "GST12": 12.0,
        "GST18": 18.0,
        "GST28": 28.0
    }
    return tax_mapping.get(tax_group, 0.0)

# Product Master Routes
@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate):
    product_dict = product.dict()
    # Set tax_percentage based on tax_group
    product_dict["tax_percentage"] = get_tax_percentage(product.tax_group)
    product_obj = Product(**product_dict)
    await db.products.insert_one(product_obj.dict())
    return product_obj

@api_router.get("/products", response_model=List[Product])
async def get_products():
    products = await db.products.find().to_list(1000)
    return [Product(**product) for product in products]

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

@api_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate):
    update_dict = {k: v for k, v in product_update.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Update tax_percentage if tax_group is being updated
    if "tax_group" in update_dict:
        update_dict["tax_percentage"] = get_tax_percentage(update_dict["tax_group"])
    
    result = await db.products.update_one(
        {"id": product_id}, 
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    updated_product = await db.products.find_one({"id": product_id})
    return Product(**updated_product)

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# Get available tax groups for dropdown
@api_router.get("/tax-groups")
async def get_tax_groups():
    return [
        {"value": "GST0", "label": "GST0 [0%]", "percentage": 0.0},
        {"value": "GST5", "label": "GST5 [5%]", "percentage": 5.0},
        {"value": "GST12", "label": "GST12 [12%]", "percentage": 12.0},
        {"value": "GST18", "label": "GST18 [18%]", "percentage": 18.0},
        {"value": "GST28", "label": "GST28 [28%]", "percentage": 28.0}
    ]

# Estimate Models
class EstimateLineItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: Optional[str] = None
    product_name: str = ""
    description: str = ""
    quantity: float = 1.0
    rate: float = 0.0
    discount: float = 0.0  # percentage
    tax_group: str = "GST0"
    tax_percentage: float = 0.0
    amount: float = 0.0  # calculated field

class EstimateLineItemCreate(BaseModel):
    product_id: Optional[str] = None
    product_name: str = ""
    description: str = ""
    quantity: float = 1.0
    rate: float = 0.0
    discount: float = 0.0  # percentage
    tax_group: str = "GST0"

class Estimate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    estimate_number: str = ""  # EST-0001, EST-0002, etc.
    customer_id: str
    reference_number: str = ""
    estimate_date: date = Field(default_factory=lambda: datetime.utcnow().date())
    expiry_date: date = Field(default_factory=lambda: (datetime.utcnow() + timedelta(days=30)).date())
    salesperson: str = ""
    project_id: Optional[str] = None
    line_items: List[EstimateLineItem] = []
    subtotal: float = 0.0
    total_tax: float = 0.0
    adjustment: float = 0.0
    total_amount: float = 0.0
    customer_notes: str = ""
    status: str = "draft"  # draft, sent, accepted, declined
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EstimateCreate(BaseModel):
    customer_id: str
    reference_number: str = ""
    estimate_date: date = Field(default_factory=lambda: datetime.utcnow().date())
    expiry_date: date = Field(default_factory=lambda: (datetime.utcnow() + timedelta(days=30)).date())
    salesperson: str = ""
    project_id: Optional[str] = None
    line_items: List[EstimateLineItemCreate] = []
    adjustment: float = 0.0
    customer_notes: str = ""

class EstimateUpdate(BaseModel):
    customer_id: Optional[str] = None
    reference_number: Optional[str] = None
    estimate_date: Optional[date] = None
    expiry_date: Optional[date] = None
    salesperson: Optional[str] = None
    project_id: Optional[str] = None
    line_items: Optional[List[EstimateLineItemCreate]] = None
    adjustment: Optional[float] = None
    customer_notes: Optional[str] = None
    status: Optional[str] = None

# Helper function to generate next estimate number
async def generate_estimate_number():
    # Find the latest estimate number
    latest_estimate = await db.estimates.find().sort("estimate_number", -1).limit(1).to_list(1)
    
    if not latest_estimate:
        return "EST-0001"
    
    latest_number = latest_estimate[0].get("estimate_number", "EST-0000")
    # Extract the number part and increment
    try:
        number_part = int(latest_number.split("-")[1])
        new_number = number_part + 1
        return f"EST-{new_number:04d}"
    except (IndexError, ValueError):
        return "EST-0001"

# Helper function to calculate line item amounts and taxes
def calculate_line_item_totals(line_items) -> tuple:
    processed_items = []
    subtotal = 0.0
    total_tax = 0.0
    
    for item in line_items:
        # Handle both EstimateLineItemCreate objects and dictionaries
        if isinstance(item, dict):
            quantity = item.get('quantity', 1.0)
            rate = item.get('rate', 0.0)
            discount = item.get('discount', 0.0)
            tax_group = item.get('tax_group', 'GST0')
            product_id = item.get('product_id')
            product_name = item.get('product_name', '')
            description = item.get('description', '')
        else:
            quantity = item.quantity
            rate = item.rate
            discount = item.discount
            tax_group = item.tax_group
            product_id = item.product_id
            product_name = item.product_name
            description = item.description
        
        # Calculate line amount after discount
        line_subtotal = quantity * rate
        discount_amount = line_subtotal * (discount / 100)
        line_amount_after_discount = line_subtotal - discount_amount
        
        # Get tax percentage and calculate tax
        tax_percentage = get_tax_percentage(tax_group)
        tax_amount = line_amount_after_discount * (tax_percentage / 100)
        total_line_amount = line_amount_after_discount + tax_amount
        
        # Create processed line item
        processed_item = EstimateLineItem(
            product_id=product_id,
            product_name=product_name,
            description=description,
            quantity=quantity,
            rate=rate,
            discount=discount,
            tax_group=tax_group,
            tax_percentage=tax_percentage,
            amount=total_line_amount
        )
        
        processed_items.append(processed_item)
        subtotal += line_amount_after_discount
        total_tax += tax_amount
    
    return processed_items, subtotal, total_tax

# Estimate CRUD Routes
@api_router.post("/estimates", response_model=Estimate)
async def create_estimate(estimate: EstimateCreate):
    # Check if customer exists
    customer = await db.customers.find_one({"id": estimate.customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Generate estimate number
    estimate_number = await generate_estimate_number()
    
    # Calculate line item totals
    processed_items, subtotal, total_tax = calculate_line_item_totals(estimate.line_items)
    
    # Calculate final total
    final_total = subtotal + total_tax + estimate.adjustment
    
    # Create estimate object
    estimate_dict = estimate.dict()
    estimate_dict["estimate_number"] = estimate_number
    estimate_dict["line_items"] = [item.dict() for item in processed_items]
    estimate_dict["subtotal"] = subtotal
    estimate_dict["total_tax"] = total_tax
    estimate_dict["total_amount"] = final_total
    
    estimate_obj = Estimate(**estimate_dict)
    
    # Convert date objects to strings for MongoDB storage
    estimate_data = estimate_obj.dict()
    estimate_data['estimate_date'] = estimate_data['estimate_date'].isoformat()
    estimate_data['expiry_date'] = estimate_data['expiry_date'].isoformat()
    
    await db.estimates.insert_one(estimate_data)
    return estimate_obj

@api_router.get("/estimates", response_model=List[Estimate])
async def get_estimates():
    estimates = await db.estimates.find().sort("created_at", -1).to_list(1000)
    # Convert string dates back to date objects
    for estimate in estimates:
        if isinstance(estimate.get('estimate_date'), str):
            estimate['estimate_date'] = datetime.fromisoformat(estimate['estimate_date']).date()
        if isinstance(estimate.get('expiry_date'), str):
            estimate['expiry_date'] = datetime.fromisoformat(estimate['expiry_date']).date()
    return [Estimate(**estimate) for estimate in estimates]

@api_router.get("/estimates/{estimate_id}", response_model=Estimate)
async def get_estimate(estimate_id: str):
    estimate = await db.estimates.find_one({"id": estimate_id})
    if not estimate:
        raise HTTPException(status_code=404, detail="Estimate not found")
    # Convert string dates back to date objects
    if isinstance(estimate.get('estimate_date'), str):
        estimate['estimate_date'] = datetime.fromisoformat(estimate['estimate_date']).date()
    if isinstance(estimate.get('expiry_date'), str):
        estimate['expiry_date'] = datetime.fromisoformat(estimate['expiry_date']).date()
    return Estimate(**estimate)

@api_router.put("/estimates/{estimate_id}", response_model=Estimate)
async def update_estimate(estimate_id: str, estimate_update: EstimateUpdate):
    # Get existing estimate
    existing_estimate = await db.estimates.find_one({"id": estimate_id})
    if not existing_estimate:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    update_dict = {k: v for k, v in estimate_update.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Recalculate totals if line items are being updated
    if "line_items" in update_dict:
        processed_items, subtotal, total_tax = calculate_line_item_totals(update_dict["line_items"])
        adjustment = update_dict.get("adjustment", existing_estimate.get("adjustment", 0))
        final_total = subtotal + total_tax + adjustment
        
        update_dict["line_items"] = [item.dict() for item in processed_items]
        update_dict["subtotal"] = subtotal
        update_dict["total_tax"] = total_tax
        update_dict["total_amount"] = final_total
    
    # Convert date objects to strings for MongoDB storage
    if 'estimate_date' in update_dict and isinstance(update_dict['estimate_date'], date):
        update_dict['estimate_date'] = update_dict['estimate_date'].isoformat()
    if 'expiry_date' in update_dict and isinstance(update_dict['expiry_date'], date):
        update_dict['expiry_date'] = update_dict['expiry_date'].isoformat()
    
    result = await db.estimates.update_one(
        {"id": estimate_id}, 
        {"$set": update_dict}
    )
    
    updated_estimate = await db.estimates.find_one({"id": estimate_id})
    # Convert string dates back to date objects
    if isinstance(updated_estimate.get('estimate_date'), str):
        updated_estimate['estimate_date'] = datetime.fromisoformat(updated_estimate['estimate_date']).date()
    if isinstance(updated_estimate.get('expiry_date'), str):
        updated_estimate['expiry_date'] = datetime.fromisoformat(updated_estimate['expiry_date']).date()
    return Estimate(**updated_estimate)

@api_router.delete("/estimates/{estimate_id}")
async def delete_estimate(estimate_id: str):
    result = await db.estimates.delete_one({"id": estimate_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Estimate not found")
    return {"message": "Estimate deleted successfully"}

# Update estimate status (draft -> sent -> accepted/declined)
@api_router.put("/estimates/{estimate_id}/status")
async def update_estimate_status(estimate_id: str, status: dict):
    if "status" not in status or status["status"] not in ["draft", "sent", "accepted", "declined"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    result = await db.estimates.update_one(
        {"id": estimate_id}, 
        {"$set": {"status": status["status"]}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    return {"message": f"Estimate status updated to {status['status']}"}

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