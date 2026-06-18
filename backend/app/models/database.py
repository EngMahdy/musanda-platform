"""Database models using SQLAlchemy"""
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, 
    Boolean, Text, Float, ForeignKey, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
import os

DB_PATH = os.getenv("DATABASE_URL", "sqlite:////tmp/musanada.db")
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False} if "sqlite" in DB_PATH else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserRole(str, enum.Enum):
    CLIENT = "client"
    STAFF = "staff"
    ADMIN = "admin"


class ProjectStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PENDING_DOCS = "pending_docs"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    company = Column(String)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Explicitly specify which FK for each relationship
    projects = relationship(
        "Project", 
        back_populates="client", 
        foreign_keys="Project.client_id"
    )
    assigned_projects = relationship(
        "Project",
        back_populates="assigned_to",
        foreign_keys="Project.assigned_to_id"
    )


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    service_type = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.NEW)
    
    client_id = Column(Integer, ForeignKey("users.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deadline = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    client = relationship("User", back_populates="projects", foreign_keys=[client_id])
    assigned_to = relationship("User", back_populates="assigned_projects", foreign_keys=[assigned_to_id])
    documents = relationship("Document", back_populates="project")
    updates = relationship("ProjectUpdate", back_populates="project")


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size_kb = Column(Float)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    category = Column(String)
    
    project = relationship("Project", back_populates="documents")


class ProjectUpdate(Base):
    __tablename__ = "project_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    status_change = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="updates")


class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    company = Column(String)
    service_interest = Column(String)
    message = Column(Text)
    source = Column(String, default="website")
    status = Column(String, default="new")
    converted_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
