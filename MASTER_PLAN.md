# 🏆 مُساندة 2.0 — الخطة الرئيسية

## ✅ مرحلة التنفيذ — الترتيب الذكي

### **Sprint 1 — Foundation (اليوم)**
الهدف: نقل الموقع الجديد كأساس + ربطه بالـAI Engine الموجود.

#### المهام:
1. ✅ تنزيل كل ملفات الموقع الجديد (HTML + CSS + JS + Images)
2. ✅ إنشاء repo جديد على GitHub: `musanda-platform`
3. ✅ هيكل المشروع:
   ```
   musanda-platform/
   ├── frontend/          # الموقع الراقي
   │   ├── public/
   │   │   ├── index.html
   │   │   └── static/
   │   ├── services/      # 9 خدمات
   │   ├── calculators/   # BOQ + Feasibility
   │   └── portal/        # Client Portal (قادم)
   │
   ├── backend/           # FastAPI
   │   ├── app/
   │   │   ├── api/
   │   │   ├── core/
   │   │   ├── ai_engine/  # من التطبيق القديم
   │   │   └── db/
   │   └── requirements.txt
   │
   └── README.md
   ```

### **Sprint 2 — AI Engine Integration**
- نقل محرك المناقصات من musanada-app
- تطبيق هوية مساندة الحقيقية
- ربطه بـAdmin Panel

### **Sprint 3 — Client Portal**
- Authentication
- Dashboard
- File Upload/Download

### **Sprint 4 — Admin Panel**
- CRM
- Project Tracking
- Reports

---

## 🎯 الـUser Flows

### **العميل الجديد:**
1. يدخل musanda.ae
2. يشوف الخدمات → يستخدم الحاسبات
3. يقدّم طلب خدمة (Form)
4. يستلم Email + Account Activation
5. يدخل Client Portal → يرفع المستندات
6. يتابع المعاملة

### **الموظف:**
1. يدخل Admin Panel
2. يشوف Leads الجديدة
3. يحوّلهم لـClients
4. يستخدم AI Engine للمناقصات
5. يولّد الفورمات → يبعتها للعميل
6. يحدّث Status

---

## 🛠️ التقنيات النهائية

| الطبقة | التقنية | لماذا |
|---|---|---|
| Frontend | HTML + Tailwind + Chart.js | السرعة + اللي عملته بالفعل |
| Backend | FastAPI | اللي مستخدمه في AI Engine |
| Database | PostgreSQL | للـCRM والـUsers |
| Auth | JWT + bcrypt | بسيط وآمن |
| Storage | Backblaze B2 | رخيص + S3-compatible |
| Hosting Backend | Render | اللي شغّال عليه |
| Hosting Frontend | Cloudflare Pages | مجاني + CDN قوي |
| Domain | musanda.ae | الموجود |

---

## 📦 المتطلبات منك

1. ✅ **Domain** musanda.ae — هل عندك access للـDNS؟
2. ✅ **Render** — عندي API key
3. ✅ **GitHub** — عندي PAT
4. ⏳ **PostgreSQL Database** — هنستخدم Render's free tier
5. ⏳ **Email SMTP** — Gmail SMTP أو SendGrid (مجاني)
6. ⏳ **Cloudflare** account — لو عندك

---

## ⏱️ التايملاين الحقيقي

- **Sprint 1** (Foundation): **3-4 ساعات** ✅ يبدأ الآن
- **Sprint 2** (AI Integration): **4-6 ساعات**
- **Sprint 3** (Client Portal): **6-8 ساعات**
- **Sprint 4** (Admin Panel): **8-12 ساعة**

**Total**: 21-30 ساعة شغل ≈ **3-5 أيام** بشغل متواصل
