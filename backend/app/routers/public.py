"""Public API — Contact forms, service requests, leads"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from app.models.database import get_db, Lead

router = APIRouter()


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=8)
    email: EmailStr
    message: str = Field(..., min_length=10)


class ServiceRequest(BaseModel):
    name: str
    phone: str
    email: EmailStr
    company: Optional[str] = None
    service_type: str
    project_details: Optional[str] = None
    budget_range: Optional[str] = None


@router.post("/contact")
async def submit_contact(req: ContactRequest, db: Session = Depends(get_db)):
    """نموذج التواصل العام"""
    lead = Lead(
        name=req.name,
        email=req.email,
        phone=req.phone,
        message=req.message,
        source="website_contact",
        status="new",
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    return {
        "status": "received",
        "message": "شكراً لتواصلك! سيتم الرد عليك خلال 24 ساعة.",
        "ticket_id": f"CONTACT-{lead.id}"
    }


@router.post("/service-request")
async def submit_service_request(req: ServiceRequest, db: Session = Depends(get_db)):
    """طلب خدمة محددة"""
    lead = Lead(
        name=req.name,
        email=req.email,
        phone=req.phone,
        company=req.company,
        service_interest=req.service_type,
        message=req.project_details or "",
        source="website_service_request",
        status="new",
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    return {
        "status": "received",
        "message": "تم استلام طلبك! فريقنا سيتواصل معك خلال 24 ساعة.",
        "request_id": f"REQ-{lead.id}"
    }


@router.get("/services")
async def list_services():
    """قائمة الخدمات التسع"""
    return {
        "services": [
            {"id": "trade_license", "name_ar": "استخراج الرخص التجارية", "name_en": "Trade License", "icon": "fa-id-card"},
            {"id": "industrial_license", "name_ar": "الرخص الصناعية", "name_en": "Industrial License", "icon": "fa-industry"},
            {"id": "engineering_license", "name_ar": "تراخيص الهندسة", "name_en": "Engineering License", "icon": "fa-drafting-compass"},
            {"id": "classification", "name_ar": "تصنيف الشركات", "name_en": "Company Classification", "icon": "fa-award"},
            {"id": "feasibility", "name_ar": "دراسات الجدوى", "name_en": "Feasibility Studies", "icon": "fa-chart-line"},
            {"id": "building_permits", "name_ar": "تراخيص البناء", "name_en": "Building Permits", "icon": "fa-building"},
            {"id": "land_allocation", "name_ar": "تخصيص الأراضي", "name_en": "Land Allocation", "icon": "fa-map-marked-alt"},
            {"id": "adio_services", "name_ar": "خدمات ADIO", "name_en": "ADIO Services", "icon": "fa-handshake"},
            {"id": "ports_services", "name_ar": "خدمات الموانئ", "name_en": "Ports Services", "icon": "fa-anchor"},
        ]
    }
