#!/bin/bash

# 🚀 QUICK DEPLOYMENT REFERENCE
# Copy & paste commands to deploy AltixEdu to Render + Vercel

# =============================================================================
# STEP 1: Push code to GitHub (35 minutes to production)
# =============================================================================

# Backend repository
cd ~/Documents/altixedu-backend
git init
git add .
git commit -m "Production deployment ready - configured for Render + Vercel"
git remote add origin https://github.com/YOUR_USERNAME/altixedu-backend
git push -u origin main

# Frontend repository
cd ~/Documents/altixedu-backend/frontend
git init
git add .
git commit -m "S+ Dashboard - production ready for Vercel"
git push -u origin main

# =============================================================================
# STEP 2: Create Supabase Database
# =============================================================================

# 1. Go to https://supabase.com
# 2. Create project
# 3. Go to Settings → Database → Connection
# 4. Copy Connection String (looks like):
#    postgresql://postgres.xxxxx:PASSWORD@db.xxxxx.supabase.co:5432/postgres
# 5. SAVE THIS URL - you'll need it in 5 minutes

# =============================================================================
# STEP 3: Generate Secure Keys
# =============================================================================

# Generate DJANGO_SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# SAVE BOTH KEYS SECURELY

# =============================================================================
# STEP 4: Deploy Backend to Render
# =============================================================================

# 1. Go to https://render.com/dashboard
# 2. Click "New +" → "Web Service"
# 3. Select "Build and deploy from a Git repository"
# 4. Authorize GitHub
# 5. Select "altixedu-backend"
# 6. Fill in:
#    Name: altixedu-api
#    Environment: Python 3
#    Region: Oregon (or your choice)
#    Build Command:
#      pip install -r requirements.txt && \
#      python altixedu/manage.py migrate --noinput && \
#      python altixedu/manage.py collectstatic --noinput --clear
#    Start Command:
#      gunicorn altixedu.wsgi:application \
#        --bind 0.0.0.0:$PORT \
#        --workers 3 \
#        --timeout 120 \
#        --access-logfile -

# 7. Add ALL environment variables (see COMPLETE_DEPLOYMENT_GUIDE.md)
# 8. Click "Create Web Service"
# 9. WAIT 5-10 MINUTES FOR DEPLOYMENT

# 10. Once deployed, note your URL (e.g., https://altixedu-api.onrender.com)
# 11. Go to Shell tab and run:
#     cd altixedu
#     python manage.py migrate --noinput
#     python manage.py collectstatic --noinput

# =============================================================================
# STEP 5: Deploy Frontend to Vercel
# =============================================================================

# 1. Go to https://vercel.com/dashboard
# 2. Click "Add New" → "Project"
# 3. Select "altixedu-frontend" repository
# 4. Fill in:
#    Framework: Vite
#    Root Directory: ./
#    Build Command: npm run build
#    Output Directory: dist
# 5. Add environment variable:
#    VITE_API_URL=https://altixedu-api.onrender.com
#    (Replace with YOUR Render URL from Step 4)
# 6. Click "Deploy"
# 7. WAIT 2-3 MINUTES FOR DEPLOYMENT

# 8. Note your URL (e.g., https://altixedu-frontend.vercel.app)

# =============================================================================
# STEP 6: Update Backend CORS
# =============================================================================

# 1. Go to Render dashboard
# 2. Click "altixedu-api" service
# 3. Go to Environment tab
# 4. Update these variables:
#    DJANGO_CORS_ALLOWED_ORIGINS=https://altixedu-frontend.vercel.app
#    FRONTEND_APP_URL=https://altixedu-frontend.vercel.app
# 5. Click Save
# 6. Wait 1-2 minutes for auto-redeploy

# =============================================================================
# STEP 7: Verify Deployment
# =============================================================================

# Test backend health
curl https://altixedu-api.onrender.com/health/
# Expected: 200 OK

# Test API endpoint
curl -X POST https://altixedu-api.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}'
# Expected: 200 (with user) or 401 (invalid credentials)

# Open frontend in browser
open https://altixedu-frontend.vercel.app
# Expected: Login page loads without errors

# =============================================================================
# STEP 8: Test Core Features
# =============================================================================

# 1. Try login (should show auth errors for test credentials)
# 2. Open browser DevTools → Console
# 3. Should see NO CORS errors
# 4. Open Network tab during login attempt
# 5. Should see POST /api/auth/login/ request

# =============================================================================
# 📊 TOTAL TIME: ~35 minutes
# =============================================================================

# Timeline:
# - Minutes 0-2: Push to GitHub
# - Minutes 2-7: Create Supabase
# - Minutes 7-8: Generate keys
# - Minutes 8-18: Deploy backend (10 min build)
# - Minutes 18-23: Deploy frontend (5 min build)
# - Minutes 23-25: Update CORS + redeploy
# - Minutes 25-35: Verify + test

# =============================================================================
# 💰 COSTS
# =============================================================================

# Render backend: FREE ($0/month - 750 hours included)
# Vercel frontend: FREE ($0/month)
# Supabase database: FREE ($0/month - 500MB included)
# Total: $0/month for MVP

# Scales to paid as needed (never pay upfront)

# =============================================================================
# 📋 IMPORTANT REMINDERS
# =============================================================================

# ✅ BEFORE deploying:
#    - Verify .env is in .gitignore (NOT committed)
#    - Verify DJANGO_DEBUG=False in Render env vars
#    - Verify SSL/TLS enabled (auto on both platforms)
#    - Generate new SECRET_KEY and ENCRYPTION_KEY

# ✅ DURING deployment:
#    - Save both URLs (Render + Vercel)
#    - Keep credentials secure (never share in chat)
#    - Use Render/Vercel environment variables, NOT .env files

# ✅ AFTER deployment:
#    - Test all core features
#    - Check browser console for errors
#    - Monitor Render/Vercel logs
#    - Document any issues

# =============================================================================
# 📚 DOCUMENTATION
# =============================================================================

# Full deployment guide: COMPLETE_DEPLOYMENT_GUIDE.md
# Printable checklist: DEPLOYMENT_CHECKLIST.md
# Environment variables: ENV_VARS_CHECKLIST.md
# File organization: DEPLOYMENT_FILES_SUMMARY.md
# Production readiness: PRODUCTION_READY_SUMMARY.md

# =============================================================================
# ✨ YOU'RE DONE!
# =============================================================================

# Your AltixEdu SaaS is now LIVE on production! 🎉
# - Multi-tenant subdomains ready
# - 7 role-based dashboards
# - Real-time features enabled
# - Payment processing active
# - Zero monthly cost (MVP)

# Next steps:
# 1. Seed initial test data (admin user, sample school)
# 2. Share frontend URL with stakeholders
# 3. Monitor for issues
# 4. Collect user feedback
# 5. Plan future improvements

# =============================================================================
