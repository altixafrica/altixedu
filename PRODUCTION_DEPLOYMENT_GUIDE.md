# Production Deployment Guide - AltixEdu

**Date:** June 3, 2026  
**Stack:** Django 5.2 + React 19 + PostgreSQL (Supabase) + Render + Vercel

---

## 📋 Pre-Deployment Checklist

- [ ] All environment variables collected in `.env.example`
- [ ] Backend migrations ready (`python manage.py migrate`)
- [ ] Frontend build tested (`npm run build` = 255KB gzipped)
- [ ] Auth flow verified (login endpoint working)
- [ ] Subdomain functionality verified
- [ ] Payment gateway (Flutterwave) configured
- [ ] Email provider (Mailgun/Resend) configured
- [ ] SMS provider (Afrika's Talking/Termii) configured
- [ ] Supabase PostgreSQL created and tested
- [ ] GitHub repos public (altixedu-backend, altixedu-frontend)

---

## 🚀 Deployment Steps

### **Step 1: Prepare Backend Repository**

```bash
cd altixedu-backend
git init
git add .
git commit -m "Initial commit - production ready"
git remote add origin https://github.com/YOUR_USERNAME/altixedu-backend
git push -u origin main
```

**Ensure `.gitignore` has:**
```
.env
.env.local
*.pyc
__pycache__/
*.sqlite3
.venv/
node_modules/
dist/
```

---

### **Step 2: Setup Supabase PostgreSQL**

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Wait 1-2 minutes for database creation
4. Navigate to **Settings → Database**
5. Copy CONNECTION STRING (URI format)
6. Store securely - will be used in Render

---

### **Step 3: Deploy Backend to Render.com**

1. Go to [render.com](https://render.com)
2. Click **New + → Web Service**
3. Connect GitHub: select `altixedu-backend` repo

**Configuration:**

| Setting | Value |
|---------|-------|
| Name | altixedu-api |
| Environment | Python 3.11 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn altixedu.wsgi:application --bind 0.0.0.0:8000` |
| Plan | Free (750 hrs/month) |

**Add Environment Variables:**

Copy from `.env.example`:
```
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<generate-new>
DJANGO_ALLOWED_HOSTS=<your-render-app>.onrender.com,altixedu.com,*.altixedu.com
DJANGO_DB_ENGINE=django.db.backends.postgresql
DJANGO_DB_HOST=db.xxxxx.supabase.co
DJANGO_DB_NAME=postgres
DJANGO_DB_USER=postgres.xxxxxxxxxxxxx
DJANGO_DB_PASSWORD=<from-supabase>
DJANGO_DB_PORT=5432
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_COOKIES=True
ENCRYPTION_KEY=<generate-new>
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:5173,https://<your-vercel-app>.vercel.app
FRONTEND_APP_URL=https://<your-vercel-app>.vercel.app
EMAIL_PROVIDER=mailgun
MAILGUN_API_KEY=<your-key>
MAILGUN_DOMAIN=mg.your-domain.com
SMS_PROVIDER=africas_talking
AFRICAS_TALKING_API_KEY=<your-key>
AFRICAS_TALKING_USERNAME=<your-username>
FLUTTERWAVE_SECRET_KEY=<your-key>
FLUTTERWAVE_PUBLIC_KEY=<your-key>
FLUTTERWAVE_SECRET_HASH=<your-hash>
```

4. Click **Deploy**
5. Wait 3-5 minutes for first deployment
6. Note your API URL: `https://<your-render-app>.onrender.com`

**Post-Deploy (in Render Shell):**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

---

### **Step 4: Prepare Frontend Repository**

```bash
cd frontend
git init
git add .
git commit -m "Production build - S+ dashboard upgrade"
git remote add origin https://github.com/YOUR_USERNAME/altixedu-frontend
git push -u origin main
```

Update `.env.production`:
```
VITE_API_URL=https://<your-render-app>.onrender.com
```

---

### **Step 5: Deploy Frontend to Vercel**

1. Go to [vercel.com](https://vercel.com)
2. Click **Add New Project**
3. Import `altixedu-frontend` from GitHub

**Configuration:**

| Setting | Value |
|---------|-------|
| Framework | Vite |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Environment Variables | See below |

**Environment Variables:**
```
VITE_API_URL=https://<your-render-app>.onrender.com
```

4. Click **Deploy**
5. Wait 2-3 minutes
6. Note your frontend URL: `https://<your-app>.vercel.app`

---

### **Step 6: Update CORS & Allowed Hosts**

Backend needs to allow frontend origin:

**In Render environment variables, update:**
```
DJANGO_CORS_ALLOWED_ORIGINS=https://<your-app>.vercel.app
DJANGO_ALLOWED_HOSTS=<your-render-app>.onrender.com,altixedu.com
```

Redeploy backend in Render dashboard.

---

## 🔒 Production Security Checklist

- [ ] `DJANGO_DEBUG=False`
- [ ] `DJANGO_SECRET_KEY` is random (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] `ENCRYPTION_KEY` generated (generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`)
- [ ] `DJANGO_SECURE_SSL_REDIRECT=True`
- [ ] `DJANGO_SECURE_COOKIES=True`
- [ ] Database password is strong
- [ ] No `.env` files in Git
- [ ] API keys in platform secrets, not code
- [ ] CORS origins whitelist only production domains
- [ ] SSL certificate enabled (Render/Vercel auto-enable)

---

## 📊 Verification Steps

### **1. Test Backend API**
```bash
curl -X POST https://<your-render-app>.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"password"}'
```

Expected: 401 (no user) or 200 (if seeded with data)

### **2. Test Frontend**
```bash
# Visit in browser:
https://<your-app>.vercel.app
```

Should load login page, no CORS errors in console

### **3. Test Login Flow**
1. Open frontend in browser
2. Try login → should hit backend API
3. Check browser Network tab → sees `/api/auth/login/` requests

### **4. Test Subdomain Check**
```bash
curl -X POST https://<your-render-app>.onrender.com/api/platform/check-subdomain/ \
  -H "Content-Type: application/json" \
  -d '{"subdomain":"test"}'
```

Expected: 200 with `{"is_available": true/false, "message": "..."}`

---

## 💰 Estimated Monthly Costs

| Service | Plan | Cost |
|---------|------|------|
| **Render** | Web Service (free tier) | $0 (750 hrs/mo limit) |
| **Supabase** | PostgreSQL free tier | $0 (500MB storage) |
| **Vercel** | React frontend free | $0 |
| **Mailgun** | Email (1000/mo) | $0-1 |
| **Afrika's Talking** | SMS free tier | $0 (100 SMS + $2 credit) |
| **Flutterwave** | Payment processing | 1.4% + ₦100 per transaction |
| **TOTAL (MVP)** | | **~$0-5/month** |

**To scale:**
- Render paid tier: $7/month → more resources
- Supabase paid: $25/month → more storage/bandwidth
- Mailgun paid: $0.50/1000 emails
- Afrika's Talking: $0.05-0.15/SMS

---

## 🐛 Troubleshooting

**Frontend shows "API connection error":**
- Check CORS: Browser console → Network tab → see 403?
- Verify `DJANGO_CORS_ALLOWED_ORIGINS` includes Vercel URL
- Redeploy backend after changing CORS

**Login fails but backend is up:**
- Check database migration: `python manage.py migrate` in Render shell
- Check if users exist: Django admin at `/admin/`
- Verify `ENCRYPTION_KEY` is set

**Render app keeps spinning down:**
- Free tier expected - will wake up in 30 seconds
- Upgrade to paid to prevent spin-down

**Vercel build fails:**
- Check `npm run build` locally first
- All imports must resolve
- Check `.env.production` has valid `VITE_API_URL`

---

## 📈 Next Steps After Launch

1. **Monitor:** Set up Sentry error tracking
2. **Analytics:** Enable Google Analytics on frontend
3. **Backups:** Configure Supabase automated backups
4. **Domain:** Bind custom domain (`altixedu.com` on Render + Vercel)
5. **Email:** Set up transactional email templates
6. **SMS:** Configure delivery receipts
7. **Testing:** Run full feature test suite

---

## 📞 Support

- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs
- **Supabase Docs:** https://supabase.com/docs
- **Django Docs:** https://docs.djangoproject.com
- **React Docs:** https://react.dev

---

**Status:** ✅ Production Ready  
**Last Updated:** June 3, 2026  
**Deployment Estimate:** 30 minutes (end-to-end)
