# Render Web Service Configuration
# Runs Django with Gunicorn ASGI server
web: gunicorn altixedu.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --worker-class sync --timeout 120 --access-logfile - --error-logfile - --log-level info
