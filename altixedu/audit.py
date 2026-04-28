"""
Audit Logging Integration for capturing all user actions.
This module provides utilities to log all changes to the audit log.
"""

from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from apps.government.models import AuditLog
import json
import logging

logger = logging.getLogger(__name__)


def log_action(
    user,
    action_type,
    action_description,
    content_type,
    object_id,
    object_name=None,
    before_value=None,
    after_value=None,
    changed_fields=None,
    ip_address=None,
    user_agent=None,
    request_id=None,
    request=None
):
    """
    Create an audit log entry for a user action.
    
    Args:
        user: User performing the action
        action_type: Type of action (e.g., 'user_login', 'student_create')
        action_description: Human-readable description
        content_type: Model name (e.g., 'Student', 'Fee')
        object_id: ID of the object being modified
        object_name: Display name of the object
        before_value: State before change
        after_value: State after change
        changed_fields: List of fields that changed
        ip_address: Client IP address
        user_agent: Client user agent
        request_id: Unique request ID
        request: Django request object (alternative to individual params)
    """
    try:
        # Extract data from request if provided
        if request:
            ip_address = getattr(request, 'client_ip', ip_address) or _get_client_ip(request)
            user_agent = getattr(request, 'user_agent', user_agent) or request.META.get('HTTP_USER_AGENT', '')
            request_id = getattr(request, 'request_id', request_id)

        user_agent = user_agent or ''
        request_id = request_id or ''
        
        # Create audit log entry
        audit_log = AuditLog(
            user=user,
            user_email=user.email if user else None,
            user_role=user.role if user else None,
            user_school=user.school if user else None,
            action_type=action_type,
            action_description=action_description,
            content_type=content_type,
            object_id=object_id,
            object_name=object_name,
            before_value=before_value or {},
            after_value=after_value or {},
            changed_fields=changed_fields or [],
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            created_at=timezone.now()
        )
        
        audit_log.save()
        return audit_log
    
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")
        return None


def log_user_action(user, action_type, description, request=None):
    """Log a user action (login, logout, etc.)"""
    log_action(
        user=user,
        action_type=action_type,
        action_description=description,
        content_type='User',
        object_id=user.id if user else 0,
        object_name=f"{user.first_name} {user.last_name}" if user else "Unknown",
        request=request
    )


def log_create_action(user, obj, request=None):
    """Log object creation"""
    model_name = obj.__class__.__name__
    object_name = str(obj)
    
    # Serialize the new object
    after_value = _serialize_object(obj)
    
    log_action(
        user=user,
        action_type=f'{model_name.lower()}_create',
        action_description=f'{model_name} created: {object_name}',
        content_type=model_name,
        object_id=obj.id,
        object_name=object_name,
        after_value=after_value,
        request=request
    )


def log_update_action(user, obj, before_state=None, changed_fields=None, request=None):
    """Log object update"""
    model_name = obj.__class__.__name__
    object_name = str(obj)
    
    before_value = before_state or {}
    after_value = _serialize_object(obj)
    
    log_action(
        user=user,
        action_type=f'{model_name.lower()}_update',
        action_description=f'{model_name} updated: {object_name}',
        content_type=model_name,
        object_id=obj.id,
        object_name=object_name,
        before_value=before_value,
        after_value=after_value,
        changed_fields=changed_fields or [],
        request=request
    )


def log_delete_action(user, obj, before_state=None, request=None):
    """Log object deletion"""
    model_name = obj.__class__.__name__
    object_name = str(obj)
    
    log_action(
        user=user,
        action_type=f'{model_name.lower()}_delete',
        action_description=f'{model_name} deleted: {object_name}',
        content_type=model_name,
        object_id=obj.id,
        object_name=object_name,
        before_value=before_state or _serialize_object(obj),
        request=request
    )


def _serialize_object(obj):
    """Convert Django model instance to dictionary"""
    result = {}
    
    for field in obj._meta.get_fields():
        try:
            if field.name in ['id', 'created_at', 'updated_at']:
                continue
            
            value = getattr(obj, field.name)
            
            # Handle different field types
            if hasattr(value, 'isoformat'):  # datetime/date
                result[field.name] = value.isoformat()
            elif hasattr(value, 'id'):  # ForeignKey
                result[field.name] = value.id
            elif not callable(value):  # Skip methods
                result[field.name] = str(value)
        
        except Exception:
            pass
    
    return result


def _get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def get_audit_logs(user_id=None, action_type=None, object_id=None, limit=100):
    """
    Retrieve audit logs with optional filtering.
    """
    queryset = AuditLog.objects.all()
    
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    
    if action_type:
        queryset = queryset.filter(action_type=action_type)
    
    if object_id:
        queryset = queryset.filter(object_id=object_id)
    
    return queryset.order_by('-created_at')[:limit]
