# Production Environment Variables - Collection Checklist

**Status:** Ready to Deploy  
**Date:** June 3, 2026

---

## ✅ Environment Variables Checklist

Use this to collect all required values before deployment.

### **SECTION 1: Django Core (Required)**

**Generate New Secure Keys:**
```bash
# SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# ENCRYPTION_KEY  
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

| Variable | Value | Source | Status |
|----------|-------|--------|--------|
| `DJANGO_DEBUG` | `False` | Hardcoded | ✅ |
| `DJANGO_SECRET_KEY` | __________ | Generate above | ⏳ |
| `DJANGO_ALLOWED_HOSTS` | `*.render.com,altixedu.com` | Hardcoded | ✅ |
| `DJANGO_LANGUAGE_CODE` | `en-us` | Hardcoded | ✅ |
| `DJANGO_TIME_ZONE` | `Africa/Lagos` | Hardcoded | ✅ |

---

### **SECTION 2: Database (Required)**

**Get from Supabase:**
1. Go to [supabase.com](https://supabase.com) → Your Project
2. Settings → Database → Connection string
3. Copy the URI (looks like: `postgresql://postgres:...@db.xxxxx.supabase.co:5432/postgres`)

| Variable | Value | Source | Status |
|----------|-------|--------|--------|
| `DJANGO_DB_ENGINE` | `django.db.backends.postgresql` | Hardcoded | ✅ |
| `DJANGO_DB_HOST` | `db.xxxxx.supabase.co` | Supabase | ⏳ |
| `DJANGO_DB_NAME` | `postgres` | Supabase | ✅ |
| `DJANGO_DB_USER` | `postgres.xxxxxxxxxxxxx` | Supabase | ⏳ |
| `DJANGO_DB_PASSWORD` | __________ | Supabase | ⏳ |
| `DJANGO_DB_PORT` | `5432` | Supabase | ✅ |

---

### **SECTION 3: Security (Required)**

| Variable | Value | Source | Status |
|----------|-------|--------|--------|
| `DJANGO_SECURE_SSL_REDIRECT` | `True` | Hardcoded | ✅ |
| `DJANGO_SECURE_COOKIES` | `True` | Hardcoded | ✅ |
| `ENCRYPTION_KEY` | __________ | Generate above | ⏳ |

---

### **SECTION 4: CORS & Frontend (Required)**

**Get Vercel URL after deploying frontend:**

| Variable | Value | Source | Status |
|----------|-------|--------|--------|
| `DJANGO_CORS_ALLOWED_ORIGINS` | `https://yourapp.vercel.app` | Vercel | ⏳ |
| `FRONTEND_APP_URL` | `https://yourapp.vercel.app` | Vercel | ⏳ |

---

### **SECTION 5: Email Provider (Required - Choose ONE)**

**Option A: Mailgun** (Recommended)
- Create account: https://www.mailgun.com
- Get API key: Dashboard → API Keys
- Verify domain: Add DNS records

| Variable | Value | Source | Status |
|----------|-------|--------|--------|
| `EMAIL_PROVIDER` | `mailgun` | Hardcoded | ✅ |
| `MAILGUN_API_KEY` | `key-__________` | Mailgun | ⏳ |
| `MAILGUN_DOMAIN` | `mg.yourdomain.com` | Mailgun | ⏳ |
| `MAILGUN_SENDER_EMAIL` | `noreply@yourdomain.com` | Mailgun | ⏳ |

**Option B: Resend** (Free tier: 50/day)
- Create account: https://resend.com
- Get API key: Settings → API Keys

| Variable | Value | Source | Status |
|----------|-------|--------|--------|
| `EMAIL_PROVIDER` | `resend` | Hardcoded | ✅ |
| `RESEND_API_KEY` | `re___________` | Resend | ⏳ |
| `RESEND_SENDER_EMAIL` | `noreply@yourdomain.com` | Resend | ⏳ |

---

### **SECTION 6: SMS Provider (Required - Choose ONE)**

**Option A: Afrika's Talking** (Best for Africa)
- Create account: https://africastalking.com
- Free tier: 100 SMS + $2 credit
- Get credentials: Dashboard → Settings

| Variable | Value | Source | Status |
|----------|-------|--------|--------|
| `SMS_PROVIDER` | `africas_talking` | Hardcoded | ✅ |
| `AFRICAS_TALKING_API_KEY` | `__________` | Afrika's Talking | ⏳ |
| `AFRICAS_TALKING_USERNAME` | `__________` | Afrika's Talking | ⏳ |
| `AFRICAS_TALKING_SENDER_ID` | `AltixEdu` | Hardcoded | ✅ |

**Option B: Termii** (Cheapest for Nigeria)
- Create account: https://www.termii.com
- Get API key: Dashboard → Settings

| Variable | Value | Source | Status |
|----------|-------|--------|--------|
| `SMS_PROVIDER` | `termii` | Hardcoded | ✅ |
| `TERMII_API_KEY` | `__________` | Termii | ⏳ |
| `TERMII_SENDER_ID` | `AltixEdu` | Hardcoded | ✅ |

---

### **SECTION 7: Payment Gateway - Flutterwave (Required)**

- Create account: https://dashboard.flutterwave.com
- Complete KYC verification
- Get credentials: Settings → API Keys

| Variable | Value | Source | Status |
|----------|-------|--------|--------|
| `FLUTTERWAVE_BASE_URL` | `https://api.flutterwave.com/v3` | Hardcoded | ✅ |
| `FLUTTERWAVE_SECRET_KEY` | `__________` | Flutterwave | ⏳ |
| `FLUTTERWAVE_PUBLIC_KEY` | `__________` | Flutterwave | ⏳ |
| `FLUTTERWAVE_SECRET_HASH` | `__________` | Flutterwave (webhook) | ⏳ |

---

### **SECTION 8: Redis/Celery (Optional but Recommended)**

If using Render, add Redis add-on and get URL.

| Variable | Value | Source | Status |
|----------|-------|--------|--------|
| `CELERY_BROKER_URL` | `redis://...` | Render Redis | ⏳ |
| `CELERY_RESULT_BACKEND` | `redis://...` | Render Redis | ⏳ |
| `REDIS_URL` | `redis://...` | Render Redis | ⏳ |
| `AUTO_SEND_ANNOUNCEMENTS` | `True` | Hardcoded | ✅ |
| `AUTO_SEND_MESSAGE_NOTIFICATIONS` | `True` | Hardcoded | ✅ |

---

## 📋 Data Collection Form

**Print and fill out with your details:**

```
DJANGO CORE:
SECRET_KEY: _________________________________________________________
ENCRYPTION_KEY: _____________________________________________________

DATABASE (Supabase):
Host: _________________________________________________________________
User: _________________________________________________________________
Password: _____________________________________________________________

EMAIL (Choose: Mailgun / Resend / SMTP):
Provider: _____________________________________________________________
API Key: ______________________________________________________________
Domain/Details: _______________________________________________________

SMS (Choose: Afrika's Talking / Termii / AWS):
Provider: _____________________________________________________________
API Key: ______________________________________________________________
Username/ID: __________________________________________________________

PAYMENT (Flutterwave):
Secret Key: ___________________________________________________________
Public Key: ___________________________________________________________
Webhook Hash: _________________________________________________________

URLS:
Render Backend URL: ___________________________________________________
Vercel Frontend URL: __________________________________________________
```

---

## 🚀 Deployment Sequence

**Step 1:** Fill out Database section (Supabase)  
**Step 2:** Fill out Security section (generate keys)  
**Step 3:** Deploy Backend to Render (use filled vars)  
**Step 4:** Get Render URL → Fill CORS section  
**Step 5:** Deploy Frontend to Vercel  
**Step 6:** Get Vercel URL → Update Render CORS + redeploy  
**Step 7:** Fill Email provider section → add to Render  
**Step 8:** Fill SMS provider section → add to Render  
**Step 9:** Fill Payment section → add to Render  
**Step 10:** Redeploy backend → Done!

---

## ✅ Final Verification

Before going live, verify in production:

```bash
# 1. Check backend health
curl https://<your-render-app>.onrender.com/health/

# 2. Test login endpoint
curl -X POST https://<your-render-app>.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}'

# 3. Check subdomain validation
curl -X POST https://<your-render-app>.onrender.com/api/platform/check-subdomain/ \
  -H "Content-Type: application/json" \
  -d '{"subdomain":"test"}'

# 4. Frontend loads without CORS errors
open https://<your-app>.vercel.app
# Check browser console for CORS errors
```

---

**Status:** Ready to Deploy  
**Time to Deploy:** ~30 minutes  
**Support:** See PRODUCTION_DEPLOYMENT_GUIDE.md
