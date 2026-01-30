from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import db
from app.routers import (
    official_contractor_chat,
    auth, 
    community, 
    users, 
    projects, 
    dashboard, 
    schemes, 
    proposals, 
    complaints,
)
import pymongo

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Create Indexes for Performance ---
    print("⚡ Creating Database Indexes...")
    
    try:
        # Unique Constraints
        await db.villagers.create_index([("phone_number", pymongo.ASCENDING)], unique=True)
        await db.contractors.create_index([("contractor_id", pymongo.ASCENDING)], unique=True)
        await db.government_officials.create_index([("government_id", pymongo.ASCENDING)], unique=True)
        await db.schemes.create_index([("scheme_id", pymongo.ASCENDING)], unique=True)
        
        # Rapid Feed Fetching (Descending Order on Time)
        await db.discussions.create_index([("created_at", pymongo.DESCENDING)])
        print("✅ Database indexes verified/created.")
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        
    yield

app = FastAPI(
    title="Gram-Sahayak API", 
    version="1.0.0", 
    lifespan=lifespan
)

# --- CORS CONFIGURATION ---
# Note: You cannot use "*" with allow_credentials=True.
# You must list your actual domains here.
origins = [
    "http://localhost:5173",            # Local Development
    "http://localhost:3000",            # Alternative Local Port
    "https://gram-sahayak.vercel.app",  # Your Production Vercel URL
    # Add any other specific Vercel preview URLs here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTER ROUTERS ---
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(community.router, prefix="/api/community", tags=["Community"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(schemes.router, prefix="/api/schemes", tags=["Schemes"])
app.include_router(proposals.router, prefix="/api/proposals", tags=["Proposals"])
app.include_router(complaints.router, prefix="/api/complaints", tags=["Complaints"])
app.include_router(official_contractor_chat.router, prefix="/api/chat", tags=["Chat"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Gram-Sahayak Backend Intelligence",
        "status": "Online",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    try:
        # Check database connectivity
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
