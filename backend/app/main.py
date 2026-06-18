"""
مساندة 2.0 — Main FastAPI Application
=====================================
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
from app.models.database import init_db
from app.routers import (
    public,
    calculators,
    services_router,
    auth,
    client_portal,
    admin,
    ai_tenders,
)


# ===== Lifespan =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 مساندة 2.0 — Starting up...")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🌐 Frontend dir: {settings.FRONTEND_DIR}")
    
    # Initialize database
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database init warning: {e}")
    
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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS + ["*"],  # Allow all in dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(public.router, prefix="/api/public", tags=["Public"])
app.include_router(calculators.router, prefix="/api/calculators", tags=["Calculators"])
app.include_router(services_router.router, prefix="/api/services", tags=["Services"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(client_portal.router, prefix="/api/portal", tags=["Client Portal"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(ai_tenders.router, prefix="/api/tenders", tags=["AI Tenders"])


@app.get("/healthz")
async def health_check():
    return {
        "status": "ok",
        "service": "musanada-platform",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "features": {
            "calculators": True,
            "auth": True,
            "client_portal": True,
            "admin_panel": True,
            "ai_tenders": True,
        }
    }


# ===== Static Files =====
FRONTEND_DIR = Path(settings.FRONTEND_DIR)
if FRONTEND_DIR.exists() and (FRONTEND_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")


# Serve frontend
@app.get("/{full_path:path}")
async def serve_frontend(request: Request, full_path: str):
    if full_path.startswith("api/") or full_path.startswith("static/"):
        return JSONResponse({"error": "Not found"}, status_code=404)
    
    if not FRONTEND_DIR.exists():
        return JSONResponse({
            "message": "مساندة 2.0 Backend",
            "api_docs": "/api/docs",
            "health": "/healthz"
        })
    
    # Check for specific HTML files
    if full_path in ["portal", "admin", "login", "register"]:
        specific = FRONTEND_DIR / f"{full_path}.html"
        if specific.exists():
            return FileResponse(specific)
    
    # Default to index.html
    file_path = FRONTEND_DIR / (full_path if full_path else "index.html")
    
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # Fallback
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    return JSONResponse({"error": "Page not found"}, status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=settings.DEBUG,
    )
