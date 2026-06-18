"""
مساندة 2.0 — Main FastAPI Application
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware


# ===== Settings (inline to avoid import issues) =====
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
FRONTEND_DIR_STR = os.getenv("FRONTEND_DIR", str(Path(__file__).parent.parent.parent / "frontend" / "public"))
FRONTEND_DIR = Path(FRONTEND_DIR_STR)


# ===== Lifespan =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Musanada 2.0 starting...")
    print(f"📍 Environment: {ENVIRONMENT}")
    print(f"🌐 Frontend dir: {FRONTEND_DIR}")
    print(f"🌐 Frontend exists: {FRONTEND_DIR.exists()}")
    
    # Init DB
    try:
        from app.models.database import init_db
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database init error: {e}")
    
    yield
    print("👋 Shutting down...")


# ===== App =====
app = FastAPI(
    title="مساندة | Musanada Engineering Consultancy",
    description="منصة موحّدة للاستشارات الهندسية والتراخيص في أبوظبي",
    version="2.0.1",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS - allow all
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Include Routers (with try/except for each) =====
def safe_include(router_path, prefix, tags):
    """Include router safely - skip if fails"""
    try:
        module_parts = router_path.split('.')
        module = __import__(router_path, fromlist=[module_parts[-1]])
        app.include_router(module.router, prefix=prefix, tags=tags)
        print(f"  ✅ {prefix}")
    except Exception as e:
        print(f"  ❌ {prefix}: {e}")


print("📡 Loading routers...")
safe_include("app.routers.public", "/api/public", ["Public"])
safe_include("app.routers.calculators", "/api/calculators", ["Calculators"])
safe_include("app.routers.services_router", "/api/services", ["Services"])
safe_include("app.routers.auth", "/api/auth", ["Auth"])
safe_include("app.routers.client_portal", "/api/portal", ["Portal"])
safe_include("app.routers.admin", "/api/admin", ["Admin"])
safe_include("app.routers.ai_tenders", "/api/tenders", ["AI Tenders"])


@app.get("/healthz")
async def health_check():
    return {
        "status": "ok",
        "service": "musanada-platform",
        "version": "2.0.1",
        "environment": ENVIRONMENT,
        "routes_count": len(app.routes),
    }


# ===== Static Files =====
if FRONTEND_DIR.exists() and (FRONTEND_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
    print(f"✅ Static files mounted from {FRONTEND_DIR}/static")


# ===== Frontend SPA =====
@app.get("/{full_path:path}")
async def serve_frontend(request: Request, full_path: str):
    # API & static handled separately
    if full_path.startswith("api/") or full_path.startswith("static/"):
        return JSONResponse({"error": "Not found"}, status_code=404)
    
    # If no frontend dir, return JSON
    if not FRONTEND_DIR.exists():
        return JSONResponse({
            "message": "Musanada 2.0 API",
            "version": "2.0.1",
            "docs": "/api/docs",
            "health": "/healthz",
        })
    
    # Specific HTML pages
    if full_path in ["portal", "admin", "login", "register"]:
        specific = FRONTEND_DIR / f"{full_path}.html"
        if specific.exists():
            return FileResponse(specific)
    
    # Default to index.html
    file_path = FRONTEND_DIR / (full_path if full_path else "index.html")
    
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # Fallback to index
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    return JSONResponse({"error": "Not found"}, status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )
