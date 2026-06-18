"""
إعدادات التطبيق
"""
import os
from pathlib import Path
from typing import List


class Settings:
    # ===== Environment =====
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # ===== Paths =====
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent
    FRONTEND_DIR: str = os.getenv(
        "FRONTEND_DIR",
        str(BASE_DIR / "frontend" / "public")
    )
    UPLOADS_DIR: str = os.getenv("UPLOADS_DIR", "/tmp/musanda_uploads")
    OUTPUTS_DIR: str = os.getenv("OUTPUTS_DIR", "/tmp/musanda_outputs")
    
    # ===== Database =====
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./musanada.db"  # Default to SQLite for dev
    )
    
    # ===== Security =====
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-please-please")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # ===== CORS =====
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://musanda.ae",
        "https://www.musanda.ae",
        "https://musanada.onrender.com",
        "https://musanda-platform.onrender.com",
    ]
    
    # ===== Email (SMTP) =====
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "info@musanda.ae")
    
    # ===== Storage =====
    STORAGE_BACKEND: str = os.getenv("STORAGE_BACKEND", "local")  # local, s3, b2
    S3_BUCKET: str = os.getenv("S3_BUCKET", "musanda-files")
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "")
    
    # ===== Company Info =====
    COMPANY_NAME_AR: str = "مساندة للاستشارات الهندسية ودراسات الجدوى"
    COMPANY_NAME_EN: str = "Musanada Engineering Consultancy"
    LICENSE_NO: str = "CN-6295947"
    LICENSE_EXPIRY: str = "2027-02-17"
    PHONE: str = "+971 56 966 4664"
    EMAIL: str = "info@musanda.ae"
    WEBSITE: str = "www.musanda.ae"
    ADDRESS: str = "خليفة سيتي — أبوظبي، الإمارات"


settings = Settings()
