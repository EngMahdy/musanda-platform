"""👤 Client Portal Router"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import shutil

from app.models.database import get_db, User, Project, Document, ProjectUpdate, ProjectStatus
from app.routers.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

UPLOAD_DIR = Path("/tmp/musanada_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class ProjectCreate(BaseModel):
    title: str
    service_type: str
    description: Optional[str] = None


@router.get("/dashboard")
async def get_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """لوحة العميل الرئيسية"""
    projects = db.query(Project).filter(Project.client_id == user.id).all()
    
    # Stats
    stats = {
        "total_projects": len(projects),
        "active": sum(1 for p in projects if p.status in [ProjectStatus.IN_PROGRESS, ProjectStatus.UNDER_REVIEW]),
        "completed": sum(1 for p in projects if p.status == ProjectStatus.COMPLETED),
        "pending": sum(1 for p in projects if p.status in [ProjectStatus.NEW, ProjectStatus.PENDING_DOCS]),
    }
    
    return {
        "user": {
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
            "company": user.company,
        },
        "stats": stats,
        "recent_projects": [
            {
                "id": p.id,
                "title": p.title,
                "service_type": p.service_type,
                "status": p.status.value if p.status else "new",
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects[:5]
        ]
    }


@router.get("/projects")
async def list_my_projects(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """قائمة مشاريعي"""
    projects = db.query(Project).filter(Project.client_id == user.id).all()
    return {
        "projects": [
            {
                "id": p.id,
                "title": p.title,
                "service_type": p.service_type,
                "description": p.description,
                "status": p.status.value if p.status else "new",
                "estimated_cost": p.estimated_cost,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "deadline": p.deadline.isoformat() if p.deadline else None,
            }
            for p in projects
        ]
    }


@router.post("/projects")
async def create_project(
    data: ProjectCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """إنشاء مشروع جديد"""
    project = Project(
        title=data.title,
        service_type=data.service_type,
        description=data.description,
        client_id=user.id,
        status=ProjectStatus.NEW,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Add initial update
    update = ProjectUpdate(
        project_id=project.id,
        user_id=user.id,
        message="تم إنشاء المشروع",
        status_change="new",
    )
    db.add(update)
    db.commit()
    
    return {"id": project.id, "title": project.title, "status": "created"}


@router.get("/projects/{project_id}")
async def get_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """تفاصيل مشروع"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.client_id == user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    documents = db.query(Document).filter(Document.project_id == project_id).all()
    updates = db.query(ProjectUpdate).filter(ProjectUpdate.project_id == project_id).order_by(ProjectUpdate.created_at.desc()).all()
    
    return {
        "id": project.id,
        "title": project.title,
        "service_type": project.service_type,
        "description": project.description,
        "status": project.status.value if project.status else "new",
        "estimated_cost": project.estimated_cost,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "documents": [
            {
                "id": d.id,
                "filename": d.filename,
                "size_kb": d.file_size_kb,
                "category": d.category,
                "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
            }
            for d in documents
        ],
        "updates": [
            {
                "id": u.id,
                "message": u.message,
                "status_change": u.status_change,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in updates
        ]
    }


@router.post("/projects/{project_id}/upload")
async def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    category: str = Form("general"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """رفع مستند للمشروع"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.client_id == user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Save file
    project_dir = UPLOAD_DIR / f"project_{project_id}"
    project_dir.mkdir(exist_ok=True)
    
    file_path = project_dir / file.filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Save to DB
    doc = Document(
        project_id=project_id,
        filename=file.filename,
        file_path=str(file_path),
        file_size_kb=len(content) / 1024,
        uploaded_by_id=user.id,
        category=category,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    return {
        "id": doc.id,
        "filename": doc.filename,
        "size_kb": doc.file_size_kb,
        "message": "تم الرفع بنجاح"
    }
