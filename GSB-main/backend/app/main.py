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
import os

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
# IMPORTANT: When allow_credentials=True, allow_origins CANNOT be ["*"]
# The browser will block requests if the origin isn't explicitly listed.
origins = [
    "http://localhost:5173",            # Local Vite Dev
    "http://localhost:3000",            # Alternative Local Dev
    "https://gram-sahayak.vercel.app",  # Your main Vercel URL
]

# Optional: Add any Vercel Preview deployment URLs dynamically if needed
# origins.append("https://your-preview-url.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTER ROUTERS ---
# Using /api prefix to ensure clear separation from frontend routing
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
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    try:
        # Pings the database to ensure connection is live
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Use environment port if available (standard for cloud deployments)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
