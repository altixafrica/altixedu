"""
Security Middleware for AltixEdu Backend
- Rate Limiting (Login attempts, API requests)
- DDoS Protection
- Brute Force Detection
"""

import time
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
from rest_framework.status import HTTP_429_TOO_MANY_REQUESTS


class RateLimitingMiddleware:
    """
    Implements rate limiting for API requests.
    - Login endpoint: 5 attempts per minute
    - General API: 100 requests per hour per user
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Configuration
        self.LOGIN_ATTEMPTS_LIMIT = getattr(settings, 'LOGIN_ATTEMPTS_LIMIT', 5)
        self.LOGIN_ATTEMPTS_WINDOW = getattr(settings, 'LOGIN_ATTEMPTS_WINDOW', 60)  # seconds
        self.API_REQUESTS_LIMIT = getattr(settings, 'API_REQUESTS_LIMIT', 100)
        self.API_REQUESTS_WINDOW = getattr(settings, 'API_REQUESTS_WINDOW', 3600)  # 1 hour
        
    def __call__(self, request):
        # Get client identifier (user_id or IP)
        client_identifier = self._get_client_identifier(request)
        
        # Check login endpoint rate limiting
        if request.path == '/api/auth/login/' and request.method == 'POST':
            if not self._check_login_rate_limit(client_identifier):
                return JsonResponse(
                    {'error': 'Too many login attempts. Please try again later.'},
                    status=HTTP_429_TOO_MANY_REQUESTS
                )
        
        # Check general API rate limiting (only for authenticated requests)
        elif request.path.startswith('/api/') and request.user.is_authenticated:
            if not self._check_api_rate_limit(client_identifier):
                return JsonResponse(
                    {'error': 'API rate limit exceeded. Max 100 requests per hour.'},
                    status=HTTP_429_TOO_MANY_REQUESTS
                )
        
        response = self.get_response(request)
        return response
    
    def _get_client_identifier(self, request):
        """Get a unique identifier for the client"""
        if request.user.is_authenticated:
            return f"user_{request.user.id}"
        else:
            # Use IP address for unauthenticated requests
            return f"ip_{self._get_client_ip(request)}"
    
    def _get_client_ip(self, request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
    
    def _check_login_rate_limit(self, client_identifier):
        """Check if login attempt is within rate limit"""
        cache_key = f"login_attempts:{client_identifier}"
        attempt_count = cache.get(cache_key, 0)
        
        if attempt_count >= self.LOGIN_ATTEMPTS_LIMIT:
            return False
        
        cache.set(
            cache_key,
            attempt_count + 1,
            self.LOGIN_ATTEMPTS_WINDOW
        )
        return True
    
    def _check_api_rate_limit(self, client_identifier):
        """Check if API request is within rate limit"""
        cache_key = f"api_requests:{client_identifier}"
        request_count = cache.get(cache_key, 0)
        
        if request_count >= self.API_REQUESTS_LIMIT:
            return False
        
        cache.set(
            cache_key,
            request_count + 1,
            self.API_REQUESTS_WINDOW
        )
        return True


class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class AuditLoggingMiddleware:
    """
    Middleware to capture request metadata for audit logging.
    Stores client IP and user agent in request for views to use.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Store IP and User-Agent for audit logging
        request.client_ip = self._get_client_ip(request)
        request.user_agent = request.META.get('HTTP_USER_AGENT', '')
        request.request_id = self._get_or_create_request_id()
        
        response = self.get_response(request)
        return response
    
    def _get_client_ip(self, request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
    
    def _get_or_create_request_id(self):
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())
