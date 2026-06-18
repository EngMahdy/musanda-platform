"""Services endpoints — detailed info for each service"""
from fastapi import APIRouter, HTTPException

router = APIRouter()


SERVICE_DETAILS = {
    "trade_license": {
        "name_ar": "استخراج الرخص التجارية",
        "description": "استخراج جميع أنواع الرخص التجارية من دائرة التنمية الاقتصادية في أبوظبي",
        "steps": [
            "حجز الاسم التجاري",
            "تجهيز عقد التأسيس",
            "الموافقات الأولية",
            "إصدار الرخصة",
            "غرفة التجارة والتسجيل"
        ],
        "timeline": "7-14 يوم عمل",
        "price_range": "AED 3,000 - 15,000",
        "documents_required": [
            "جواز سفر الشركاء",
            "رخصة شركة الأم (إن وجدت)",
            "صورة عن الإمارات ID",
            "اختيار النشاط من جدول ISIC"
        ]
    },
    "classification": {
        "name_ar": "تصنيف الشركات",
        "description": "تصنيف شركات المقاولات والاستشارات الهندسية في جميع الدرجات",
        "steps": [
            "تقييم الكوادر الفنية",
            "إعداد الملف المالي",
            "تجهيز المشاريع المنجزة",
            "تقديم الطلب للجهة المعنية",
            "متابعة التصنيف"
        ],
        "timeline": "30-60 يوم",
        "price_range": "AED 8,000 - 50,000 حسب الدرجة"
    },
    "feasibility": {
        "name_ar": "دراسات الجدوى الاقتصادية",
        "description": "دراسات جدوى احترافية بتحليل NPV, IRR, Payback مع توصيات استثمارية",
        "steps": [
            "تحليل السوق والمنافسين",
            "التحليل الفني والهندسي",
            "النموذج المالي (25 سنة)",
            "تحليل الحساسية",
            "التقرير النهائي"
        ],
        "timeline": "15-30 يوم",
        "price_range": "AED 15,000 - 100,000 حسب حجم المشروع"
    }
}


@router.get("/{service_id}")
async def get_service_details(service_id: str):
    """تفاصيل خدمة محددة"""
    if service_id not in SERVICE_DETAILS:
        raise HTTPException(status_code=404, detail="Service not found")
    return SERVICE_DETAILS[service_id]
