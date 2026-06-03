# DEPLOYMENT CHECKLIST - Print & Check Off ✓

**Date:** ____________  
**Deployed by:** ____________  
**Status:** [ ] NOT STARTED  [ ] IN PROGRESS  [ ] COMPLETE

---

## PHASE 1: PREPARATION ✓

### Prerequisites
- [ ] GitHub account created
- [ ] Supabase account created
- [ ] Mailgun account created (or Resend/SMTP)
- [ ] Afrika's Talking account created (or Termii/AWS SNS)
- [ ] Flutterwave account created & verified

### Repository Setup
- [ ] Backend code pushed to GitHub (altixedu-backend)
- [ ] Frontend code pushed to GitHub (altixedu-frontend)
- [ ] `.env` file is in `.gitignore` (NOT committed)
- [ ] `Procfile` exists in backend root
- [ ] `runtime.txt` exists in backend root
- [ ] `vercel.json` exists in frontend root
- [ ] `render.yaml` exists in backend root

---

## PHASE 2: DATABASE ✓

### Supabase Setup
- [ ] Supabase project created
- [ ] Database initialized
- [ ] Connection URL obtained
  ```
  Format: postgresql://postgres.xxxxx:PASSWORD@db.xxxxx.supabase.co:5432/postgres
  ```
- [ ] Database URL saved securely

### Generate Secure Keys
- [ ] DJANGO_SECRET_KEY generated
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- [ ] ENCRYPTION_KEY generated
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
- [ ] Both keys saved securely

---

## PHASE 3: RENDER BACKEND DEPLOYMENT ✓

### Step 1: Create Render Web Service
- [ ] Render account created
- [ ] GitHub account connected to Render
- [ ] `altixedu-backend` repository selected
- [ ] Web Service created

### Step 2: Configure Deployment
- [ ] Service name: `altixedu-api`
- [ ] Environment: Python 3
- [ ] Build Command configured ✓
- [ ] Start Command configured ✓
- [ ] Instance Type: Free (750 hrs/month)
- [ ] Region selected

### Step 3: Environment Variables Added
**Django Core:**
- [ ] DJANGO_DEBUG = False
- [ ] DJANGO_SECRET_KEY = __________ (generated key)
- [ ] DJANGO_ALLOWED_HOSTS = *.onrender.com,.altixedu.com
- [ ] DJANGO_LANGUAGE_CODE = en-us
- [ ] DJANGO_TIME_ZONE = Africa/Lagos
- [ ] DJANGO_SECURE_SSL_REDIRECT = True
- [ ] DJANGO_SECURE_COOKIES = True

**Database:**
- [ ] DJANGO_DB_ENGINE = django.db.backends.postgresql
- [ ] DJANGO_DB_HOST = db.xxxxx.supabase.co
- [ ] DJANGO_DB_NAME = postgres
- [ ] DJANGO_DB_USER = postgres.xxxxxxxxxxxxx
- [ ] DJANGO_DB_PASSWORD = __________ (Supabase password)
- [ ] DJANGO_DB_PORT = 5432

**Security:**
- [ ] ENCRYPTION_KEY = __________ (generated key)

**Email:**
- [ ] EMAIL_PROVIDER = mailgun (or resend/smtp)
- [ ] MAILGUN_API_KEY = __________ (or RESEND_API_KEY)
- [ ] MAILGUN_DOMAIN = mg.yourdomain.com
- [ ] MAILGUN_SENDER_EMAIL = noreply@yourdomain.com

**SMS:**
- [ ] SMS_PROVIDER = africas_talking (or termii/aws_sns)
- [ ] AFRICAS_TALKING_API_KEY = __________
- [ ] AFRICAS_TALKING_USERNAME = __________
- [ ] AFRICAS_TALKING_SENDER_ID = AltixEdu

**Payment:**
- [ ] FLUTTERWAVE_SECRET_KEY = __________
- [ ] FLUTTERWAVE_PUBLIC_KEY = __________
- [ ] FLUTTERWAVE_SECRET_HASH = __________

### Step 4: Deploy
- [ ] Service deployed to Render
- [ ] Build completed successfully
- [ ] Service is running (green status)
- [ ] Render URL noted: https://__________.onrender.com

### Step 5: Post-Deploy Setup
- [ ] Opened Render Shell (dashboard → Shell tab)
- [ ] Ran: `cd altixedu && python manage.py migrate --noinput`
- [ ] Ran: `python manage.py collectstatic --noinput`
- [ ] Migrations completed successfully

### Verification
- [ ] Backend URL accessible (no 500 errors)
- [ ] Health endpoint responds: https://<render-url>/health/
- [ ] API responds: https://<render-url>/api/auth/login/

---

## PHASE 4: VERCEL FRONTEND DEPLOYMENT ✓

### Step 1: Create Vercel Project
- [ ] Vercel account created
- [ ] GitHub account connected to Vercel
- [ ] `altixedu-frontend` repository selected
- [ ] Project created

### Step 2: Configure Settings
- [ ] Project name: `altixedu-frontend`
- [ ] Framework: Vite
- [ ] Root directory: ./
- [ ] Build command: npm run build
- [ ] Output directory: dist

### Step 3: Environment Variables
- [ ] VITE_API_URL = https://<your-render-app>.onrender.com

### Step 4: Deploy
- [ ] Project deployed to Vercel
- [ ] Build completed successfully (2-3 minutes)
- [ ] Deployment is ready
- [ ] Vercel URL noted: https://<your-project>.vercel.app

### Verification
- [ ] Frontend loads in browser
- [ ] Login page appears
- [ ] No JavaScript errors in console

---

## PHASE 5: CONNECT & TEST ✓

### Update CORS
- [ ] Went to Render dashboard
- [ ] Selected `altixedu-api` service
- [ ] Updated environment variables:
  ```
  DJANGO_CORS_ALLOWED_ORIGINS=https://<vercel-url>.vercel.app
  FRONTEND_APP_URL=https://<vercel-url>.vercel.app
  ```
- [ ] Saved changes
- [ ] Backend redeployed (wait 1-2 minutes)

### Functional Tests
- [ ] Frontend loads without CORS errors
- [ ] Login form appears
- [ ] API requests show in Network tab
- [ ] Subdomain validation works
- [ ] No errors in browser console
- [ ] Responsive design works (mobile/tablet)

---

## PHASE 6: FINAL VERIFICATION ✓

### Backend Health
```bash
curl https://<render-url>/health/
# Expected: 200 OK
```
- [ ] Endpoint responds

### Test Auth Endpoint
```bash
curl -X POST https://<render-url>/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}'
# Expected: 200 (with user) or 401 (invalid credentials)
```
- [ ] Endpoint responds

### Test Subdomain Check
```bash
curl -X POST https://<render-url>/api/platform/check-subdomain/ \
  -H "Content-Type: application/json" \
  -d '{"subdomain":"test"}'
# Expected: 200 with is_available field
```
- [ ] Endpoint responds

### Browser Tests
1. [ ] Visit https://<vercel-url>.vercel.app
2. [ ] Page loads (no CORS errors)
3. [ ] Try clicking login button
4. [ ] Shows validation errors (email required)
5. [ ] Enter email/password
6. [ ] Attempt login
7. [ ] Shows error message (credentials error expected if no users)
8. [ ] No errors in console

---

## PHASE 7: PRODUCTION READINESS ✓

### Performance
- [ ] Frontend build size acceptable (~250KB gzipped)
- [ ] Page load time < 3 seconds
- [ ] API responses < 500ms
- [ ] No console warnings

### Security
- [ ] SSL enabled on both services (auto)
- [ ] No HTTP (only HTTPS)
- [ ] Secrets not in code (all env vars)
- [ ] `.env` not committed to Git
- [ ] CORS properly restricted

### Monitoring
- [ ] Render logs accessible
- [ ] Vercel logs accessible
- [ ] Can view deployment history

### Documentation
- [ ] Deployment URLs documented
- [ ] Environment variables documented
- [ ] Credentials stored securely
- [ ] Runbook created for future deployments

---

## GOING LIVE ✓

### Before Launch
- [ ] All tests passing
- [ ] No known issues
- [ ] Team notified
- [ ] Backup plan ready

### Launch
- [ ] Share frontend URL with stakeholders
- [ ] Monitor Render/Vercel logs
- [ ] Monitor error tracking (if enabled)
- [ ] Collect user feedback

### Post-Launch
- [ ] Watch for errors in first hour
- [ ] Respond to user issues quickly
- [ ] Document any problems
- [ ] Plan fixes/improvements

---

## 📊 DEPLOYMENT SUMMARY

**Backend (Render):**
- URL: https://________________________.onrender.com
- API Status: [ ] ✅ Working  [ ] ⚠️ Needs fixing

**Frontend (Vercel):**
- URL: https://________________________.vercel.app
- Status: [ ] ✅ Working  [ ] ⚠️ Needs fixing

**Database (Supabase):**
- Host: db.________________________.supabase.co
- Status: [ ] ✅ Connected  [ ] ⚠️ Connection issues

**Current Issues:** ___________________________________________________________

**Next Steps:** _______________________________________________________________

---

## ✅ DEPLOYMENT COMPLETE!

**Deployment Date:** ____________  
**Deployment Time:** ____________ minutes  
**Deployed By:** ________________________  
**Verified By:** ________________________  

**Notes:**
```
________________________________________________________________________

________________________________________________________________________

________________________________________________________________________
```

---

**🎉 Your AltixEdu SaaS is now LIVE on production!**

Keep this checklist for future deployments and maintenance reference.
