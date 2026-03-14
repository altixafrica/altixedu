"""
Multi-tenant middleware that extracts subdomain and attaches school to request.

This middleware:
1. Extracts subdomain from request hostname
2. Loads the School object from the subdomain
3. Attaches school_id and school object to the request
4. Filters subsequent querysets by school_id
5. Allows superadmin (school_id=NULL) to see all schools
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from apps.schools.models import School


class SubdomainTenantMiddleware(MiddlewareMixin):
    """
    Middleware to handle multi-tenant routing via subdomains.
    
    For requests to muse.altixedu.com:
    - Extracts 'muse' from hostname
    - Loads School with subdomain='muse'
    - Attaches request.school_id and request.school
    
    For requests to altixedu.com (no subdomain):
    - Sets request.school_id = None (superadmin)
    - Sets request.school = None
    """
    
    # Hostnames that should not be treated as subdomains
    RESERVED_SUBDOMAINS = [
        'api',
        'admin',
        'www',
        'localhost',
        'staging',
        'production',
        'development',
    ]
    
    def process_request(self, request):
        """
        Extract subdomain from hostname and attach school to request.
        """
        host = request.get_host().lower()
        
        # Remove port number if present
        if ':' in host:
            host = host.split(':')[0]
        
        # Extract subdomain
        subdomain = self._extract_subdomain(host)
        
        # Initialize request attributes
        request.school_id = None
        request.school = None
        request.is_superadmin = False
        
        # If subdomain exists and is not reserved, try to load school
        if subdomain and subdomain not in self.RESERVED_SUBDOMAINS:
            try:
                school = School.objects.get(
                    subdomain=subdomain,
                    is_active=True
                )
                request.school_id = school.id
                request.school = school
                request.is_superadmin = False
                
            except School.DoesNotExist:
                # Subdomain doesn't exist or school is inactive
                return JsonResponse(
                    {
                        'error': 'School not found',
                        'subdomain': subdomain,
                        'message': f'No active school with subdomain "{subdomain}"'
                    },
                    status=404
                )
            except School.MultipleObjectsReturned:
                # Should not happen due to unique constraint, but handle it
                return JsonResponse(
                    {'error': 'Multiple schools found with same subdomain'},
                    status=500
                )
        else:
            # No subdomain or reserved subdomain - superadmin access
            request.is_superadmin = True
        
        return None
    
    @staticmethod
    def _extract_subdomain(host):
        """
        Extract subdomain from hostname.
        
        Examples:
        - 'muse.altixedu.com' -> 'muse'
        - 'api.altixedu.com' -> 'api'
        - 'altixedu.com' -> None
        - 'localhost' -> None
        - 'localhost:8000' -> None
        """
        parts = host.split('.')
        
        # If only one part (localhost) or two parts (example.com), no subdomain
        if len(parts) <= 2:
            return None
        
        # Return the first part (subdomain)
        return parts[0].lower()
