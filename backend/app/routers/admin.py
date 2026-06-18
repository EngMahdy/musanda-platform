"""👔 Admin Panel + CRM"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.models.database import (
    get_db, User, UserRole, Project, ProjectStatus, 
    Document, Lead, ProjectUpdate
)
from app.routers.auth import require_admin

router = APIRouter()


@router.get("/dashboard")
async def admin_dashboard(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """لوحة الإدارة الرئيسية"""
    total_users = db.query(User).filter(User.role == UserRole.CLIENT).count()
    total_projects = db.query(Project).count()
    new_leads = db.query(Lead).filter(Lead.status == "new").count()
    
    # Project status breakdown
    status_counts = {}
    for status in ProjectStatus:
        count = db.query(Project).filter(Project.status == status).count()
        status_counts[status.value] = count
    
    # Recent activity
    recent_projects = db.query(Project).order_by(desc(Project.created_at)).limit(10).all()
    recent_leads = db.query(Lead).order_by(desc(Lead.created_at)).limit(10).all()
    
    return {
        "admin": {
            "name": admin.full_name,
            "email": admin.email,
            "role": admin.role.value,
        },
        "stats": {
            "total_clients": total_users,
            "total_projects": total_projects,
            "new_leads": new_leads,
            "projects_by_status": status_counts,
        },
        "recent_projects": [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status.value if p.status else "new",
                "client_id": p.client_id,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in recent_projects
        ],
        "recent_leads": [
            {
                "id": l.id,
                "name": l.name,
                "email": l.email,
                "phone": l.phone,
                "service_interest": l.service_interest,
                "status": l.status,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in recent_leads
        ]
    }


@router.get("/leads")
async def list_leads(
    status: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """قائمة الـLeads"""
    query = db.query(Lead).order_by(desc(Lead.created_at))
    if status:
        query = query.filter(Lead.status == status)
    
    leads = query.all()
    return {
        "total": len(leads),
        "leads": [
            {
                "id": l.id,
                "name": l.name,
                "email": l.email,
                "phone": l.phone,
                "company": l.company,
                "service_interest": l.service_interest,
                "message": l.message,
                "source": l.source,
                "status": l.status,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in leads
        ]
    }


class LeadUpdate(BaseModel):
    status: str  # contacted, qualified, converted, lost


@router.patch("/leads/{lead_id}")
async def update_lead(
    lead_id: int,
    data: LeadUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """تحديث حالة Lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.status = data.status
    db.commit()
    return {"status": "updated", "lead_id": lead_id, "new_status": data.status}


@router.get("/clients")
async def list_clients(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """قائمة العملاء"""
    clients = db.query(User).filter(User.role == UserRole.CLIENT).order_by(desc(User.created_at)).all()
    
    return {
        "total": len(clients),
        "clients": [
            {
                "id": c.id,
                "email": c.email,
                "full_name": c.full_name,
                "phone": c.phone,
                "company": c.company,
                "is_active": c.is_active,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "projects_count": db.query(Project).filter(Project.client_id == c.id).count(),
            }
            for c in clients
        ]
    }


@router.get("/clients/{client_id}")
async def get_client_details(
    client_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """تفاصيل عميل + مشاريعه"""
    client = db.query(User).filter(User.id == client_id, User.role == UserRole.CLIENT).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    projects = db.query(Project).filter(Project.client_id == client_id).all()
    
    return {
        "client": {
            "id": client.id,
            "email": client.email,
            "full_name": client.full_name,
            "phone": client.phone,
            "company": client.company,
            "created_at": client.created_at.isoformat() if client.created_at else None,
        },
        "projects": [
            {
                "id": p.id,
                "title": p.title,
                "service_type": p.service_type,
                "status": p.status.value if p.status else "new",
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects
        ]
    }


@router.get("/projects")
async def list_all_projects(
    status: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """قائمة كل المشاريع"""
    query = db.query(Project).order_by(desc(Project.created_at))
    if status:
        query = query.filter(Project.status == status)
    
    projects = query.all()
    return {
        "total": len(projects),
        "projects": [
            {
                "id": p.id,
                "title": p.title,
                "service_type": p.service_type,
                "status": p.status.value if p.status else "new",
                "client_id": p.client_id,
                "estimated_cost": p.estimated_cost,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "deadline": p.deadline.isoformat() if p.deadline else None,
            }
            for p in projects
        ]
    }


class ProjectStatusUpdate(BaseModel):
    status: str  # ProjectStatus value
    message: Optional[str] = None


@router.patch("/projects/{project_id}/status")
async def update_project_status(
    project_id: int,
    data: ProjectStatusUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """تحديث حالة مشروع"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    old_status = project.status
    project.status = ProjectStatus(data.status)
    project.updated_at = datetime.utcnow()
    
    if data.status == "completed":
        project.completed_at = datetime.utcnow()
    
    # Log update
    update = ProjectUpdate(
        project_id=project_id,
        user_id=admin.id,
        message=data.message or f"تم تحديث الحالة من {old_status.value if old_status else 'new'} إلى {data.status}",
        status_change=data.status,
    )
    db.add(update)
    db.commit()
    
    return {"status": "updated", "project_id": project_id, "new_status": data.status}
