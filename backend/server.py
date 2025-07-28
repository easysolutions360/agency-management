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
from datetime import datetime, date

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
    start_date: date
    end_date: date
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectCreate(BaseModel):
    customer_id: str
    type: str
    name: str
    amount: float
    start_date: date
    end_date: date

class ProjectUpdate(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    amount: Optional[float] = None
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
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DomainHostingCreate(BaseModel):
    project_id: str
    domain_name: str
    hosting_provider: str
    username: str
    password: str
    validity_date: date

class DomainHostingUpdate(BaseModel):
    domain_name: Optional[str] = None
    hosting_provider: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    validity_date: Optional[date] = None

class ProjectWithDetails(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    type: str
    name: str
    amount: float
    start_date: date
    end_date: date
    domains: List[DomainHosting]
    created_at: datetime

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
    project_data['end_date'] = project_data['end_date'].isoformat()
    
    await db.projects.insert_one(project_data)
    return project_obj

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects = await db.projects.find().to_list(1000)
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project)

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project_update: ProjectUpdate):
    update_dict = {k: v for k, v in project_update.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.projects.update_one(
        {"id": project_id}, 
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_project = await db.projects.find_one({"id": project_id})
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
    await db.domains.insert_one(domain_obj.dict())
    return domain_obj

@api_router.get("/domains", response_model=List[DomainHosting])
async def get_domains():
    domains = await db.domains.find().to_list(1000)
    return [DomainHosting(**domain) for domain in domains]

@api_router.get("/domains/project/{project_id}", response_model=List[DomainHosting])
async def get_domains_by_project(project_id: str):
    domains = await db.domains.find({"project_id": project_id}).to_list(1000)
    return [DomainHosting(**domain) for domain in domains]

@api_router.get("/domains/{domain_id}", response_model=DomainHosting)
async def get_domain(domain_id: str):
    domain = await db.domains.find_one({"id": domain_id})
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DomainHosting(**domain)

@api_router.put("/domains/{domain_id}", response_model=DomainHosting)
async def update_domain_hosting(domain_id: str, domain_update: DomainHostingUpdate):
    update_dict = {k: v for k, v in domain_update.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.domains.update_one(
        {"id": domain_id}, 
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    updated_domain = await db.domains.find_one({"id": domain_id})
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
        # Get customer details
        customer = await db.customers.find_one({"id": project["customer_id"]})
        
        # Get domains for this project
        domains = await db.domains.find({"project_id": project["id"]}).to_list(1000)
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
                start_date=project["start_date"],
                end_date=project["end_date"],
                domains=domain_objects,
                created_at=project["created_at"]
            )
            project_details.append(project_detail)
    
    return project_details

@api_router.get("/dashboard/expiring-domains")
async def get_expiring_domains():
    from datetime import timedelta
    
    # Get domains expiring in the next 30 days
    thirty_days_from_now = datetime.now().date() + timedelta(days=30)
    domains = await db.domains.find({
        "validity_date": {"$lte": thirty_days_from_now}
    }).to_list(1000)
    
    expiring_domains = []
    for domain in domains:
        # Get project and customer details
        project = await db.projects.find_one({"id": domain["project_id"]})
        if project:
            customer = await db.customers.find_one({"id": project["customer_id"]})
            if customer:
                expiring_domains.append({
                    "domain_name": domain["domain_name"],
                    "hosting_provider": domain["hosting_provider"],
                    "validity_date": domain["validity_date"],
                    "project_name": project["name"],
                    "customer_name": customer["name"],
                    "customer_email": customer["email"],
                    "days_remaining": (domain["validity_date"] - datetime.now().date()).days
                })
    
    return expiring_domains

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