"""🔐 Authentication Router"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from app.models.database import get_db, User, UserRole
from app.core.security import (
    hash_password, verify_password, 
    create_access_token, decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()


# ===== Schemas =====
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    phone: Optional[str] = None
    company: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    company: Optional[str] = None


# ===== Dependency: Get current user from token =====
def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ===== Endpoints =====
@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister, db: Session = Depends(get_db)):
    """تسجيل عميل جديد"""
    # Check if email exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="هذا البريد الإلكتروني مسجل بالفعل")
    
    # Create user
    user = User(
        email=data.email,
        full_name=data.full_name,
        phone=data.phone,
        company=data.company,
        hashed_password=hash_password(data.password),
        role=UserRole.CLIENT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate token
    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "company": user.company,
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """تسجيل دخول"""
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="بيانات الدخول غير صحيحة")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="الحساب غير مفعل")
    
    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "company": user.company,
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """جلب بيانات المستخدم الحالي"""
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        company=user.company,
    )


@router.post("/init-admin")
async def init_admin(db: Session = Depends(get_db)):
    """إنشاء حساب admin أولي (للتهيئة الأولى فقط)"""
    # Check if any admin exists
    admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if admin_exists:
        return {"status": "admin_exists", "message": "Admin already exists"}
    
    # Create default admin
    admin = User(
        email="mahmoud@mahdy.ae",
        full_name="م. محمود مهدي أبوشعيشع",
        phone="+971 56 966 4664",
        company="مساندة للاستشارات الهندسية",
        hashed_password=hash_password("Musanada@2025"),
        role=UserRole.ADMIN,
    )
    db.add(admin)
    db.commit()
    
    return {
        "status": "created",
        "message": "Admin account created",
        "email": admin.email,
        "default_password": "Musanada@2025",
        "warning": "⚠️ غيّر كلمة السر فوراً بعد أول تسجيل دخول"
    }
