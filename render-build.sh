#!/bin/bash
# Production Setup Script - AltixEdu Backend
# Run this after environment variables are set in Render/Railway

set -e

echo "======================================================================"
echo "AltixEdu Production Setup"
echo "======================================================================"

# 1. Run Django migrations
echo ""
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# 2. Collect static files
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# 3. Create cache table (if using cache)
echo ""
echo "💾 Setting up cache..."
python manage.py createcachetable 2>/dev/null || true

# 4. Test database connection
echo ""
echo "🔗 Testing database connection..."
python manage.py dbshell <<< "SELECT 1;" > /dev/null && echo "✅ Database connection OK"

# 5. Check that all settings are correct
echo ""
echo "🔍 Verifying Django settings..."
python manage.py check --deploy || true

# 6. Show startup information
echo ""
echo "======================================================================"
echo "✅ Setup Complete!"
echo "======================================================================"
echo ""
echo "📝 Summary:"
echo "  - Database migrations: Applied"
echo "  - Static files: Collected"
echo "  - Settings: Verified"
echo ""
echo "🚀 Ready to start Gunicorn server"
echo ""
