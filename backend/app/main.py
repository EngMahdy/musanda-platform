"""
مساندة 2.0 — Main FastAPI Application
=====================================
تطبيق موحّد بيخدم:
1. الموقع العام (Public Website)
2. حاسبات BOQ + Feasibility
3. Client Portal
4. Admin Panel + CRM
5. AI Engine للمناقصات

Author: Musanada Engineering Consultancy
License: Proprietary
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from app.core.config import settings
from app.routers import (
    public,
    calculators,
    services_router,
    auth,
    client_portal,
    admin,
    ai_tenders,
)


# ===== Lifespan Management =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & Shutdown events."""
    print("🚀 مساندة 2.0 — Starting up...")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🌐 Frontend dir: {settings.FRONTEND_DIR}")
    yield
    print("👋 Shutting down...")


# ===== FastAPI App =====
app = FastAPI(
    title="مساندة | Musanada Engineering Consultancy",
    description="منصة موحّدة للاستشارات الهندسية والتراخيص في أبوظبي",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Routers (API) =====
app.include_router(public.router, prefix="/api/public", tags=["Public"])
app.include_router(calculators.router, prefix="/api/calculators", tags=["Calculators"])
app.include_router(services_router.router, prefix="/api/services", tags=["Services"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(client_portal.router, prefix="/api/portal", tags=["Client Portal"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(ai_tenders.router, prefix="/api/tenders", tags=["AI Tenders"])


# ===== Health Check =====
@app.get("/healthz")
async def health_check():
    return {
        "status": "ok",
        "service": "musanada-platform",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
    }


# ===== Static Files (Frontend) =====
FRONTEND_DIR = Path(settings.FRONTEND_DIR)
if FRONTEND_DIR.exists():
    # Static assets (CSS, JS, images, fonts)
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
    
    # Serve frontend for any non-API route (SPA fallback)
    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        # Don't catch API routes
        if full_path.startswith("api/") or full_path.startswith("static/"):
            return JSONResponse({"error": "Not found"}, status_code=404)
        
        # Map specific routes
        route_map = {
            "": "index.html",
            "portal": "portal.html",
            "admin": "admin.html",
            "login": "login.html",
            "services": "services.html",
            "projects": "projects.html",
            "calculators": "calculators.html",
            "contact": "contact.html",
        }
        
        # Default to index.html (SPA)
        filename = route_map.get(full_path.rstrip("/"), "index.html")
        file_path = FRONTEND_DIR / filename
        
        if file_path.exists():
            return FileResponse(file_path)
        
        # Fallback to index.html for unknown routes
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        
        return JSONResponse({"error": "Frontend not built"}, status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=settings.DEBUG,
    )
