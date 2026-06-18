# 🌐 ربط دومين musanada.ae بالمنصة

## الخطوات (5 دقائق)

### 1. اذهب إلى لوحة تحكم المسجّل (Domain Registrar)
الدومين `musanda.ae` غالباً مسجّل في إحدى الجهات التالية:
- **AE Domain Authority** (للدومينات .ae)
- **GoDaddy** / **Namecheap** / **Etisalat Business**

### 2. إعدادات DNS المطلوبة

افتح **DNS Management** وأضف هذه الـRecords:

```
Type    Name    Value                              TTL
─────────────────────────────────────────────────────────
CNAME   www     musanda-platform.onrender.com      3600
A       @       216.24.57.1                        3600
A       @       216.24.57.4                        3600
```

**أو بدلاً من A Records، استخدم ALIAS/ANAME**:
```
ALIAS   @       musanda-platform.onrender.com      3600
```

### 3. أضف الدومين في Render

1. افتح https://dashboard.render.com/web/srv-d8pq4o37uimc73aeflf0
2. اختر **Settings**
3. تحت **Custom Domains**، اضغط **+ Add Custom Domain**
4. أدخل: `musanda.ae`
5. كرّر للـsubdomain: `www.musanda.ae`
6. **Render** سيُعطيك SSL certificate تلقائياً (مجاناً)

### 4. انتظر DNS Propagation

- **عادة**: 15 دقيقة - ساعة
- **أحياناً**: حتى 24 ساعة
- تحقق من: https://dnschecker.org

### 5. الاختبار

```bash
# تحقق من DNS
nslookup musanda.ae
dig musanda.ae

# تحقق من SSL
curl -I https://musanda.ae
```

---

## ✅ النتيجة النهائية

| النطاق | المسار |
|---|---|
| 🌐 **الموقع الرئيسي** | https://musanda.ae |
| 🔐 **تسجيل الدخول** | https://musanda.ae/login |
| 👤 **بوابة العميل** | https://musanda.ae/portal |
| 👔 **لوحة الإدارة** | https://musanda.ae/admin |
| 📚 **API Docs** | https://musanda.ae/api/docs |

---

## 🆘 المساعدة

لو لقيت أي مشكلة، شارك:
1. **اسم المسجّل** (Domain Registrar)
2. **لقطة من DNS settings الحالية**
3. **رسالة الخطأ** (لو في)

وأنا هساعدك خطوة بخطوة! 🔧
