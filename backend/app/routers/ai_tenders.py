"""
🤖 AI Tenders Router
====================
محرك تحليل المناقصات الذكي:
- Upload tender file (PDF/ZIP/RAR)
- Extract requirements (technical + financial)
- Authority detection (DMT/ADIO)
- Generate analysis report
- Calculate IRR/NPV/Payback
- Provide strategic recommendation
"""

import os
import uuid
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

router = APIRouter()

# ===== Job storage (in-memory for now) =====
JOBS = {}

# ===== Paths =====
UPLOAD_DIR = Path("/tmp/musanda_tenders/uploads")
OUTPUT_DIR = Path("/tmp/musanda_tenders/outputs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/status")
async def status():
    return {
        "router": "ai_tenders",
        "status": "active",
        "active_jobs": len(JOBS),
        "engine_version": "2.0"
    }


@router.post("/analyze")
async def analyze_tender(
    bg: BackgroundTasks,
    tender_file: UploadFile = File(...),
    company_name: str = Form("Musanada Engineering"),
    user_rent_per_sqm: Optional[float] = Form(None),
):
    """
    تحليل مناقصة كاملة:
    1. استخراج النص من الملف
    2. كشف الجهة (DMT/ADIO)
    3. تحليل تقني + مالي + سوق + استراتيجي
    4. إرجاع تقرير شامل
    """
    # Generate job ID
    job_id = uuid.uuid4().hex[:12]
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    # Save file
    file_path = job_dir / tender_file.filename
    content = await tender_file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Initial job state
    JOBS[job_id] = {
        "job_id": job_id,
        "status": "processing",
        "stage": "تم رفع الملف، جاري التحليل...",
        "progress": 10,
        "created_at": datetime.now().isoformat(),
        "filename": tender_file.filename,
        "file_size_kb": len(content) / 1024,
        "company_name": company_name,
        "result": None,
        "error": None,
    }
    
    # Run analysis in background
    bg.add_task(_run_analysis, job_id, str(file_path), company_name, user_rent_per_sqm)
    
    return {
        "job_id": job_id,
        "status": "accepted",
        "message": "تم رفع الملف بنجاح، التحليل جاري...",
        "status_url": f"/api/tenders/jobs/{job_id}",
        "estimated_time_seconds": 30,
    }


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """متابعة حالة التحليل"""
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return JOBS[job_id]


@router.get("/jobs")
async def list_recent_jobs(limit: int = 10):
    """قائمة آخر التحليلات"""
    jobs = sorted(JOBS.values(), key=lambda j: j["created_at"], reverse=True)
    return {
        "total": len(jobs),
        "jobs": jobs[:limit]
    }


def _run_analysis(job_id: str, file_path: str, company_name: str, user_rent: Optional[float]):
    """تشغيل التحليل في الـbackground"""
    try:
        JOBS[job_id]["stage"] = "قراءة محتوى الملف..."
        JOBS[job_id]["progress"] = 20
        
        # Extract text from file
        tender_text = _extract_text(file_path)
        
        if not tender_text or len(tender_text) < 100:
            JOBS[job_id]["status"] = "failed"
            JOBS[job_id]["error"] = "لم يتمكن النظام من قراءة محتوى الملف. تأكد من أن الملف PDF أو نص قابل للقراءة."
            return
        
        JOBS[job_id]["stage"] = "تحليل المناقصة (تقني + مالي + سوق)..."
        JOBS[job_id]["progress"] = 50
        
        # Try to import and run the intelligence engine
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from app.ai_engine_core import run_full_intelligence
            
            # Extract tender name from filename
            tender_name = Path(file_path).stem
            
            # Detect area from text (simple)
            area_name = _detect_area(tender_text)
            
            intel = run_full_intelligence(
                tender_name=tender_name,
                auction_text=tender_text,
                area_name=area_name,
                company_name=company_name,
                user_rent_per_sqm_per_year=user_rent,
            )
            
            JOBS[job_id]["progress"] = 90
            JOBS[job_id]["stage"] = "تجهيز التقرير النهائي..."
            
            # Build simplified result
            h = intel.get("financial", {}).get("headline", {})
            a = intel.get("financial", {}).get("assumptions", {})
            strat = intel.get("strategic", {})
            
            result = {
                "tender_name": tender_name,
                "area": area_name,
                "project_type": intel.get("project_type", "unknown"),
                "authority": "DMT" if "DMT" in tender_text.upper() or "بلدية" in tender_text else "ADIO",
                "financial": {
                    "capex_aed": h.get("capex", 0),
                    "annual_revenue_stabilized": h.get("annual_revenue_stabilized", 0),
                    "annual_opex_stabilized": h.get("annual_opex_stabilized", 0),
                    "annual_ebitda": h.get("annual_ebitda_stabilized", 0),
                    "irr_pct": h.get("irr_pct", 0),
                    "payback_years": h.get("payback_years", 0),
                    "npv_aed": h.get("npv_aed", 0),
                    "total_net_profit_lease": h.get("total_net_profit_lease", 0),
                },
                "assumptions": {
                    "plot_area_sqm": a.get("plot_area_sqm", 0),
                    "rent_per_sqm_per_year": a.get("rent_per_sqm_per_year", 0),
                    "rent_source": a.get("rent_source", "unknown"),
                    "lease_years": a.get("lease_years", 25),
                    "capex_per_sqm": a.get("capex_per_sqm", 0),
                },
                "strategic": {
                    "decision": strat.get("decision", "CONDITIONAL"),
                    "signal": strat.get("signal", "🟡"),
                    "strengths": strat.get("swot", {}).get("strengths", []),
                    "weaknesses": strat.get("swot", {}).get("weaknesses", []),
                    "risks": [r.get("title", "") for r in strat.get("risks", [])],
                    "opportunities": strat.get("swot", {}).get("opportunities", []),
                },
                "executive_summary": intel.get("executive_summary", {}).get("one_liner", ""),
                "pricing_recommendation": intel.get("executive_summary", {}).get("pricing_recommendation", ""),
            }
            
            JOBS[job_id]["status"] = "completed"
            JOBS[job_id]["stage"] = "✅ التحليل اكتمل!"
            JOBS[job_id]["progress"] = 100
            JOBS[job_id]["result"] = result
            JOBS[job_id]["completed_at"] = datetime.now().isoformat()
            
        except ImportError as ie:
            # Engine not available - return basic analysis
            JOBS[job_id]["status"] = "completed"
            JOBS[job_id]["stage"] = "✅ تحليل أولي (محرك الذكاء الاصطناعي غير متاح)"
            JOBS[job_id]["progress"] = 100
            JOBS[job_id]["result"] = _basic_analysis(tender_text)
            JOBS[job_id]["completed_at"] = datetime.now().isoformat()
            
    except Exception as e:
        import traceback
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = f"خطأ: {str(e)}"
        JOBS[job_id]["traceback"] = traceback.format_exc()


def _extract_text(file_path: str) -> str:
    """استخراج النص من PDF أو text"""
    path = Path(file_path)
    
    if path.suffix.lower() == ".pdf":
        try:
            import pdfplumber
            text = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages[:50]:  # max 50 pages
                    t = page.extract_text()
                    if t:
                        text.append(t)
            return "\n".join(text)
        except ImportError:
            # Try pypdf
            try:
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                text = []
                for page in reader.pages[:50]:
                    text.append(page.extract_text())
                return "\n".join(text)
            except ImportError:
                return path.read_text(errors='ignore')
    
    elif path.suffix.lower() in [".txt", ".md"]:
        return path.read_text(errors='ignore')
    
    else:
        # Try as text
        try:
            return path.read_text(errors='ignore')
        except:
            return ""


def _detect_area(text: str) -> str:
    """كشف المنطقة من النص"""
    areas = [
        "الشهامة", "Al Shahamah", "الوثبة", "Al Wathba",
        "خليفة سيتي", "Khalifa City", "الريم", "Al Reem",
        "ياس", "Yas", "صير بني ياس", "Saadiyat", "السعديات",
        "أبوظبي", "Abu Dhabi", "العين", "Al Ain",
        "دلما", "Delma", "غياثي", "Ghayathi"
    ]
    
    for area in areas:
        if area in text:
            return area
    
    return "أبوظبي"


def _basic_analysis(text: str) -> dict:
    """تحليل أساسي بدون AI engine"""
    return {
        "tender_name": "تحليل أولي",
        "area": _detect_area(text),
        "text_length": len(text),
        "word_count": len(text.split()),
        "preview": text[:500] + "..." if len(text) > 500 else text,
        "note": "النتائج أساسية فقط. محرك الذكاء الاصطناعي الكامل سيتم تفعيله قريباً.",
    }


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """حذف تحليل"""
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete files
    job_dir = UPLOAD_DIR / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir)
    
    del JOBS[job_id]
    return {"status": "deleted", "job_id": job_id}
