# 🏛️ مُساندة 2.0 — منصة متكاملة

> منصة موحّدة للاستشارات الهندسية والتراخيص في أبوظبي  
> Musanada Engineering Consultancy Platform

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Status: Active](https://img.shields.io/badge/Status-Active-green.svg)]()

---

## 🎯 الرؤية

منصة واحدة بتجمع:
- 🌐 **موقع تسويقي راقي** (Public Website)
- 🧮 **حاسبات ذكية** (BOQ + Feasibility Study)
- 🔐 **بوابة العملاء** (Client Portal)
- 👔 **لوحة إدارة** (Admin + CRM)
- 🤖 **محرك AI للمناقصات** (DMT + ADIO)

---

## 🏗️ المعمارية

```
musanda-platform/
│
├── frontend/                # الواجهة (HTML + Tailwind + Chart.js)
│   └── public/
│       ├── index.html       # الصفحة الرئيسية
│       └── static/
│           ├── imgs/        # الصور والشعار
│           ├── fonts/       # خطوط Cairo
│           └── *.css, *.js
│
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py          # نقطة الدخول
│   │   ├── core/            # الإعدادات
│   │   ├── routers/         # API endpoints
│   │   │   ├── public.py    # Contact, Service Request
│   │   │   ├── calculators.py  # BOQ + Feasibility
│   │   │   ├── auth.py      # تسجيل دخول
│   │   │   ├── client_portal.py
│   │   │   ├── admin.py     # CRM
│   │   │   └── ai_tenders.py
│   │   ├── ai_engine/       # محرك المناقصات (من v1)
│   │   ├── db/              # قواعد البيانات
│   │   ├── models/          # SQLAlchemy models
│   │   └── services/        # Business logic
│   └── requirements.txt
│
├── render.yaml              # Deploy config
└── README.md
```

---

## 🚀 التشغيل المحلي

### Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Visit:
- 🌐 Website: http://localhost:8000
- 📚 API Docs: http://localhost:8000/api/docs
- ❤️ Health: http://localhost:8000/healthz

---

## 🌐 النشر (Render)

التطبيق بيتنشر تلقائياً على Render عند كل push للـmain branch.

**URL Production**: https://musanda-platform.onrender.com  
**Domain**: musanda.ae (مرتبط بالـRender)

---

## 📋 API Endpoints

### Public APIs:
- `POST /api/public/contact` - نموذج تواصل
- `POST /api/public/service-request` - طلب خدمة
- `GET /api/public/services` - قائمة الخدمات

### Calculators:
- `POST /api/calculators/boq` - حاسبة جدول الكميات
- `POST /api/calculators/feasibility` - دراسة جدوى

### Services:
- `GET /api/services/{service_id}` - تفاصيل خدمة

### Auth (Coming Soon):
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`

### Client Portal (Coming Soon):
- `GET /api/portal/projects`
- `POST /api/portal/upload`
- `GET /api/portal/invoices`

### Admin Panel (Coming Soon):
- `GET /api/admin/leads`
- `GET /api/admin/clients`
- `POST /api/admin/project`

### AI Tenders (Coming Soon):
- `POST /api/tenders/upload`
- `GET /api/tenders/{job_id}/status`
- `GET /api/tenders/{job_id}/download`

---

## 📞 معلومات الشركة

| البند | القيمة |
|---|---|
| **الاسم** | مساندة للاستشارات الهندسية ودراسات الجدوى |
| **الترخيص** | CN-6295947 |
| **سارية حتى** | 17/02/2027 |
| **الهاتف** | +971 56 966 4664 |
| **الإيميل** | info@musanda.ae |
| **الموقع** | خليفة سيتي، أبوظبي |
| **المدير** | م. محمود مهدي أبوشعيشع |

---

## 📅 خارطة الطريق

### ✅ Sprint 1: Foundation (مكتمل)
- [x] هيكل المشروع
- [x] الواجهة العامة
- [x] حاسبات BOQ + Feasibility
- [x] نموذج تواصل

### 🔄 Sprint 2: AI Engine Integration
- [ ] نقل محرك المناقصات من v1
- [ ] تطبيق هوية مساندة
- [ ] ربط بقاعدة البيانات

### ⏳ Sprint 3: Client Portal
- [ ] نظام تسجيل دخول (JWT)
- [ ] Dashboard العميل
- [ ] رفع/تحميل المستندات
- [ ] تتبع المعاملات

### ⏳ Sprint 4: Admin Panel + CRM
- [ ] إدارة Leads
- [ ] إدارة Clients
- [ ] Project Tracking
- [ ] Financial Reports

---

## 📄 الترخيص

© 2025 Musanada Engineering Consultancy. All rights reserved.
