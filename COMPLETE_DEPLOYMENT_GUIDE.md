# Complete Deployment Guide - Render + Vercel

**Status:** Production Ready  
**Date:** June 3, 2026

---

## 📋 Files Configured for Deployment

### Backend (Django + Render)
- ✅ `Procfile` - Gunicorn configuration
- ✅ `render.yaml` - Render deployment config
- ✅ `runtime.txt` - Python 3.11.8
- ✅ `requirements.txt` - All dependencies including WhiteNoise
- ✅ `settings.py` - WhiteNoise middleware + static files
- ✅ `render-build.sh` - Automated setup script
- ✅ `.env.example` - All environment variables documented

### Frontend (React + Vercel)
- ✅ `vercel.json` - Vercel deployment config
- ✅ `.env.production` - Production environment
- ✅ `package.json` - Node 20 engine specified
- ✅ `vite.config.js` - Optimized for production

---

## 🚀 STEP-BY-STEP DEPLOYMENT

### PHASE 1: PREPARE REPOSITORIES (5 minutes)

#### Backend Repository

```bash
cd altixedu-backend
git init
git add .
git commit -m "Production deployment ready"
git remote add origin https://github.com/YOUR_USERNAME/altixedu-backend
git push -u origin main
```

**Verify pushed files:**
- ✅ `Procfile` exists
- ✅ `runtime.txt` exists
- ✅ `render.yaml` exists
- ✅ `requirements.txt` has gunicorn + whitenoise
- ✅ `.env.example` is NOT in git
- ✅ `.gitignore` has `.env`

#### Frontend Repository

```bash
cd frontend
git init
git add .
git commit -m "Production deployment - S+ dashboard"
git push -u origin main
```

**Verify pushed files:**
- ✅ `vercel.json` exists
- ✅ `.env.production` exists (safe to commit)
- ✅ `package.json` specifies Node 20
- ✅ `dist/` is in `.gitignore`

---

### PHASE 2: SETUP SUPABASE DATABASE (5 minutes)

1. Go to https://supabase.com
2. Create new project
3. Wait 1-2 minutes for database creation
4. Navigate to **Settings → Database → Connection**
5. Copy **Connection String (URI)**
   - Format: `postgresql://postgres.xxxxx:PASSWORD@db.xxxxx.supabase.co:5432/postgres`
6. **SAVE** this URL - you'll need it in 10 minutes

---

### PHASE 3: DEPLOY BACKEND TO RENDER (10 minutes)

#### Step 1: Connect GitHub to Render

1. Go to https://render.com
2. Click **Dashboard** (top right)
3. Click **New +** → **Web Service**
4. Select **Build and deploy from a Git repository**
5. Click **Connect account** → Authorize GitHub
6. Find & select `altixedu-backend` repository
7. Click **Connect**

#### Step 2: Configure Deployment

Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `altixedu-api` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && python altixedu/manage.py migrate --noinput && python altixedu/manage.py collectstatic --noinput --clear` |
| **Start Command** | `gunicorn altixedu.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --access-logfile -` |
| **Instance Type** | `Free (750 hours/month)` |
| **Region** | `Oregon` (or your preferred region) |

#### Step 3: Add Environment Variables

Copy ALL of these into Render's environment variables section:

```
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<GENERATE NEW - see below>
DJANGO_ALLOWED_HOSTS=<your-render-app>.onrender.com,.altixedu.com,*.altixedu.com
DJANGO_LANGUAGE_CODE=en-us
DJANGO_TIME_ZONE=Africa/Lagos
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_COOKIES=True
ENCRYPTION_KEY=<GENERATE NEW - see below>
DJANGO_DB_ENGINE=django.db.backends.postgresql
DJANGO_DB_HOST=db.xxxxx.supabase.co
DJANGO_DB_NAME=postgres
DJANGO_DB_USER=postgres.xxxxxxxxxxxxx
DJANGO_DB_PASSWORD=<YOUR_SUPABASE_PASSWORD>
DJANGO_DB_PORT=5432
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:5173,https://<will-update-after-vercel>
FRONTEND_APP_URL=https://<will-update-after-vercel>
EMAIL_PROVIDER=mailgun
MAILGUN_API_KEY=<your-mailgun-key>
MAILGUN_DOMAIN=mg.yourdomain.com
MAILGUN_SENDER_EMAIL=noreply@yourdomain.com
SMS_PROVIDER=africas_talking
AFRICAS_TALKING_API_KEY=<your-africas-talking-key>
AFRICAS_TALKING_USERNAME=<your-username>
AFRICAS_TALKING_SENDER_ID=AltixEdu
FLUTTERWAVE_BASE_URL=https://api.flutterwave.com/v3
FLUTTERWAVE_SECRET_KEY=<your-flutterwave-key>
FLUTTERWAVE_PUBLIC_KEY=<your-flutterwave-public-key>
FLUTTERWAVE_SECRET_HASH=<your-flutterwave-hash>
```

**Generate missing keys:**
```bash
# DJANGO_SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

#### Step 4: Deploy

1. Click **Create Web Service**
2. **Wait 5-10 minutes** for deployment
3. Once deployed, note your URL: `https://<render-app-name>.onrender.com`
4. Visit the URL - should show Django 404 (that's OK, no static files yet)

#### Step 5: Run Post-Deploy Setup

In Render dashboard:
1. Click your web service
2. Go to **Shell** tab
3. Run:
```bash
cd altixedu
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

✅ **Backend deployed!** Save your URL: `https://<your-render-app>.onrender.com`

---

### PHASE 4: DEPLOY FRONTEND TO VERCEL (5 minutes)

#### Step 1: Connect GitHub to Vercel

1. Go to https://vercel.com
2. Click **Dashboard**
3. Click **Add New... → Project**
4. Click **Continue with GitHub**
5. Select `altixedu-frontend` repository
6. Click **Import**

#### Step 2: Configure Project

Fill in these fields:

| Field | Value |
|-------|-------|
| **Project Name** | `altixedu-frontend` |
| **Framework Preset** | `Vite` |
| **Root Directory** | `./` (or `frontend/` if nested) |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

#### Step 3: Add Environment Variables

Add this variable:

```
VITE_API_URL=https://<your-render-app>.onrender.com
```

Replace `<your-render-app>` with your actual Render URL from Phase 3.

#### Step 4: Deploy

1. Click **Deploy**
2. **Wait 2-3 minutes** for deployment
3. Once done, note your URL: `https://<your-vercel-app>.vercel.app`

✅ **Frontend deployed!** Save your URL: `https://<your-vercel-app>.vercel.app`

---

### PHASE 5: UPDATE CORS & RECONNECT (5 minutes)

Now that you have both URLs, update the backend CORS:

1. Go to Render dashboard
2. Click `altixedu-api` service
3. Go to **Environment** tab
4. Update these variables:
   ```
   DJANGO_CORS_ALLOWED_ORIGINS=https://<your-vercel-app>.vercel.app
   FRONTEND_APP_URL=https://<your-vercel-app>.vercel.app
   ```
5. Click **Save**
6. Redeploy backend (it will auto-redeploy in 1-2 minutes)

---

## ✅ VERIFICATION TESTS

### Test 1: Backend Health

```bash
curl https://<your-render-app>.onrender.com/health/
```

Expected: 200 OK (or 404 if health endpoint not configured)

### Test 2: Frontend Loads

Open in browser:
```
https://<your-vercel-app>.vercel.app
```

Expected: Login page appears

### Test 3: API Connection

1. Open frontend in browser
2. Open **Developer Tools → Console**
3. Enter email, click login
4. Check **Network tab**
5. Should see `POST /api/auth/login/` request

Expected: No CORS errors in console

### Test 4: Subdomain Validation

```bash
curl -X POST https://<your-render-app>.onrender.com/api/platform/check-subdomain/ \
  -H "Content-Type: application/json" \
  -d '{"subdomain":"test"}'
```

Expected: 200 with JSON response

---

## 🔧 TROUBLESHOOTING

### Render build fails

**Problem:** Build command fails  
**Solution:**
1. Check Render logs: Dashboard → Service → Logs
2. Run `python manage.py migrate --noinput` locally first
3. Ensure `requirements.txt` has all dependencies

### CORS errors in frontend

**Problem:** Console shows CORS errors  
**Solution:**
1. Verify `DJANGO_CORS_ALLOWED_ORIGINS` has correct Vercel URL
2. Redeploy backend (might take 1-2 minutes)
3. Check capitalization - must match exactly

### Frontend can't reach API

**Problem:** Network requests fail  
**Solution:**
1. Verify `VITE_API_URL` is correct in Vercel env vars
2. Redeploy frontend
3. Check that Render URL is accessible (no 500 errors)

### Static files return 404

**Problem:** CSS/JS not loading  
**Solution:**
1. WhiteNoise should serve them automatically
2. If still failing, run in Render shell:
   ```bash
   cd altixedu
   python manage.py collectstatic --noinput --clear
   ```

---

## 📊 WHAT'S NOW RUNNING

**Backend (Render):**
- Django 5.2.12
- PostgreSQL via Supabase
- 13 apps (accounts, schools, finance, etc.)
- Auth endpoints working
- Subdomain validation working
- Email/SMS/Payment integration ready

**Frontend (Vercel):**
- React 19 + Vite
- S+ Dashboard (charts, insights, skeletons)
- 7 role-based dashboards
- Real-time WebSocket ready
- TailwindCSS + responsive design

**Infrastructure:**
- Auto-deploys on GitHub push
- SSL/TLS enabled automatically
- Free tier (can scale to paid)
- Database backups enabled (Supabase)

---

## 💰 COSTS

| Service | Tier | Cost/Month |
|---------|------|-----------|
| Render | Free (750 hrs) | $0 |
| Vercel | Free | $0 |
| Supabase | Free (500MB) | $0 |
| Mailgun | Free (1000/mo) | $0 |
| Afrika's Talking | Free tier | $0 |
| **TOTAL** | | **$0** |

---

## 🎓 NEXT STEPS

1. **Seed Data** (optional): Populate database with test schools/users
2. **Enable SSL** (auto): Already enabled on Render + Vercel
3. **Monitor**: Set up error tracking (Sentry - optional)
4. **Backup**: Supabase auto-backups enabled
5. **Scale**: Upgrade plans when traffic grows

---

## 📞 QUICK LINKS

- [Render Dashboard](https://dashboard.render.com)
- [Vercel Dashboard](https://vercel.com/dashboard)
- [Supabase Dashboard](https://supabase.com/dashboard)
- [Your Backend URL](https://<your-render-app>.onrender.com)
- [Your Frontend URL](https://<your-vercel-app>.vercel.app)

---

**Status:** ✅ **LIVE & PRODUCTION READY**

Your AltixEdu SaaS is now live with:
- Multi-tenant subdomains
- 7 role-based dashboards
- Real-time features
- Payment processing
- Email & SMS
- Zero monthly cost (MVP phase)

🎉 **Congratulations - You're deployed!**
