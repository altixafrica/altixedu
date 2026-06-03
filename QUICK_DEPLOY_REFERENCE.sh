#!/bin/bash
# Quick Deployment Reference - Copy & Paste Commands

echo "=========================================="
echo "AltixEdu Production Deployment Commands"
echo "=========================================="
echo ""

# Step 1: Generate secure keys
echo "1️⃣  Generate Django Secret Key:"
echo "python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
echo ""

echo "2️⃣  Generate Encryption Key:"
echo "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
echo ""

# Step 2: Git push
echo "3️⃣  Push to GitHub:"
echo "cd altixedu-backend"
echo "git add ."
echo "git commit -m 'Production deployment'"
echo "git push origin main"
echo ""

# Step 3: Render environment variables (copy all at once)
cat << 'EOF'
4️⃣  Environment Variables for Render (copy entire block to Render dashboard):

DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<GENERATED_KEY>
DJANGO_ALLOWED_HOSTS=<your-render-app>.onrender.com,altixedu.com,*.altixedu.com
DJANGO_LANGUAGE_CODE=en-us
DJANGO_TIME_ZONE=Africa/Lagos
DJANGO_DB_ENGINE=django.db.backends.postgresql
DJANGO_DB_HOST=db.xxxxx.supabase.co
DJANGO_DB_NAME=postgres
DJANGO_DB_USER=postgres.xxxxxxxxxxxxx
DJANGO_DB_PASSWORD=<SUPABASE_PASSWORD>
DJANGO_DB_PORT=5432
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_COOKIES=True
ENCRYPTION_KEY=<GENERATED_KEY>
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:5173,https://<vercel-url>.vercel.app
FRONTEND_APP_URL=https://<vercel-url>.vercel.app
EMAIL_PROVIDER=mailgun
MAILGUN_API_KEY=<your-key>
MAILGUN_DOMAIN=mg.yourdomain.com
MAILGUN_SENDER_EMAIL=noreply@yourdomain.com
SMS_PROVIDER=africas_talking
AFRICAS_TALKING_API_KEY=<your-key>
AFRICAS_TALKING_USERNAME=<your-username>
AFRICAS_TALKING_SENDER_ID=AltixEdu
FLUTTERWAVE_BASE_URL=https://api.flutterwave.com/v3
FLUTTERWAVE_SECRET_KEY=<your-key>
FLUTTERWAVE_PUBLIC_KEY=<your-key>
FLUTTERWAVE_SECRET_HASH=<your-hash>

EOF

echo ""
echo "5️⃣  Render Deployment Configuration:"
echo "   Name: altixedu-api"
echo "   Environment: Python 3.11"
echo "   Build Command: pip install -r requirements.txt"
echo "   Start Command: gunicorn altixedu.wsgi:application --bind 0.0.0.0:8000"
echo ""

echo "6️⃣  After Render deploys, run in Shell tab:"
echo "   python manage.py migrate"
echo "   python manage.py collectstatic --noinput"
echo ""

echo "7️⃣  Frontend deployment (Vercel):"
echo "   Env Var: VITE_API_URL=https://<your-render-app>.onrender.com"
echo ""

echo "=========================================="
echo "✅ Ready to deploy!"
echo "=========================================="
echo ""
echo "Full guide: See PRODUCTION_DEPLOYMENT_GUIDE.md"
echo "Checklist: See ENV_VARS_CHECKLIST.md"
echo ""
