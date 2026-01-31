"""
FastAPI Main Application

Entry point for the Orion AI API service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os

# Import routers
from api.health import router as health_router
from api.connectors.routes import router as connectors_router
from api.webhooks.handler import router as webhooks_router

# Create FastAPI app
app = FastAPI(
    title="Orion AI API",
    description="Backend API for Orion AI Integration Platform",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
)

# ====================
# MIDDLEWARE
# ====================

# CORS Configuration
allowed_origins_str = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8000"
)
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted host (production only)
if os.getenv("ENVIRONMENT") == "production":
    trusted_hosts = os.getenv("TRUSTED_HOSTS", "api-prod.railway.app").split(",")
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts
    )

# ====================
# ROUTERS
# ====================

# Health checks (no prefix, at root level)
app.include_router(health_router, tags=["Health"])

# API routes
app.include_router(
    connectors_router,
    prefix="/api/v1/connectors",
    tags=["Connectors"]
)

app.include_router(
    webhooks_router,
    prefix="/api/v1/webhooks",
    tags=["Webhooks"]
)

# ====================
# ROOT ENDPOINT
# ====================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Orion AI API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs" if os.getenv("ENVIRONMENT") != "production" else "disabled",
        "health": "/health"
    }


# ====================
# STARTUP/SHUTDOWN
# ====================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Orion AI API starting up...")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"CORS Allowed Origins: {allowed_origins}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Orion AI API shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development"
    )
