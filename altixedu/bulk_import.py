"""
Bulk User Import from CSV
Allows admins to import users in batch using CSV files
"""

import csv
import io
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.schools.models import School
from audit import log_action
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class BulkUserImportError(Exception):
    """Exception raised during bulk user import"""
    pass


class BulkUserImporter:
    """
    Import users from CSV file.
    
    CSV Format:
    username,email,password,first_name,last_name,role,school_id
    
    Example:
    john_smith,john@school.com,Password123!,John,Smith,teacher,1
    sarah_jones,sarah@school.com,Password123!,Sarah,Jones,student,1
    """
    
    VALID_ROLES = ['superadmin', 'admin', 'teacher', 'student', 'parent', 'bursar']
    REQUIRED_FIELDS = ['username', 'email', 'password', 'first_name', 'last_name', 'role']
    
    def __init__(self, school=None, created_by=None):
        """
        Initialize the importer.
        
        Args:
            school: School instance (optional, defaults to all schools)
            created_by: User creating the import (for audit logging)
        """
        self.school = school
        self.created_by = created_by
        self.results = {
            'successful': [],
            'failed': [],
            'total': 0
        }
    
    def import_from_csv_content(self, csv_content, file_encoding='utf-8'):
        """
        Import users from CSV content (string or bytes).
        
        Args:
            csv_content: CSV file content as string or bytes
            file_encoding: Encoding of the CSV file
        
        Returns:
            dict with 'successful', 'failed', and 'total' counts
        """
        if isinstance(csv_content, bytes):
            csv_content = csv_content.decode(file_encoding)
        
        csv_file = io.StringIO(csv_content)
        return self.import_from_file(csv_file)
    
    def import_from_file(self, csv_file):
        """
        Import users from CSV file object.
        
        Args:
            csv_file: File object or file-like object
        
        Returns:
            dict with 'successful', 'failed', and 'total' counts
        """
        reader = csv.DictReader(csv_file)
        
        if reader.fieldnames is None:
            raise BulkUserImportError("CSV file is empty")
        
        # Validate headers
        self._validate_headers(reader.fieldnames)
        
        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):  # Start from 2 (header is 1)
                try:
                    self._process_row(row, row_num)
                except Exception as e:
                    error_msg = str(e)
                    self.results['failed'].append({
                        'row': row_num,
                        'error': error_msg,
                        'data': row
                    })
                    logger.warning(f"Row {row_num} import failed: {error_msg}")
        
        self.results['total'] = len(self.results['successful']) + len(self.results['failed'])
        return self.results
    
    def _validate_headers(self, fieldnames):
        """Validate CSV headers"""
        for required_field in self.REQUIRED_FIELDS:
            if required_field not in fieldnames:
                raise BulkUserImportError(
                    f"Missing required column: {required_field}"
                )
    
    def _process_row(self, row, row_num):
        """Process a single CSV row"""
        # Clean whitespace
        row = {k: v.strip() if v else v for k, v in row.items()}
        
        # Validate required fields
        for field in self.REQUIRED_FIELDS:
            if not row.get(field):
                raise BulkUserImportError(f"Missing {field}")
        
        username = row['username']
        email = row['email']
        password = row['password']
        first_name = row['first_name']
        last_name = row['last_name']
        role = row['role']
        school_id = row.get('school_id')
        
        # Validate role
        if role not in self.VALID_ROLES:
            raise BulkUserImportError(
                f"Invalid role '{role}'. Must be one of: {', '.join(self.VALID_ROLES)}"
            )
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            raise BulkUserImportError(f"Username '{username}' already exists")
        
        if User.objects.filter(email=email).exists():
            raise BulkUserImportError(f"Email '{email}' already exists")
        
        # Get school
        school = None
        if school_id:
            try:
                school = School.objects.get(id=school_id)
            except School.DoesNotExist:
                raise BulkUserImportError(f"School with ID {school_id} does not exist")
        elif self.school:
            school = self.school
        
        # Validate password strength
        if len(password) < 8:
            raise BulkUserImportError(
                f"Password for {username} must be at least 8 characters"
            )
        
        # Validate email format
        if '@' not in email or '.' not in email.split('@')[1]:
            raise BulkUserImportError(f"Invalid email format: {email}")
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            school=school
        )
        
        # Log the action
        if self.created_by:
            log_action(
                user=self.created_by,
                action_type='user_bulk_import',
                action_description=f'User imported via CSV: {username} ({email})',
                content_type='User',
                object_id=user.id,
                object_name=f"{first_name} {last_name}"
            )
        
        self.results['successful'].append({
            'username': username,
            'email': email,
            'user_id': user.id
        })
        
        logger.info(f"Successfully created user: {username}")


def validate_csv_format(csv_file):
    """
    Validate CSV format without importing.
    Returns validation errors if any.
    """
    errors = []
    
    try:
        csv_file.seek(0)
        reader = csv.DictReader(csv_file)
        
        if reader.fieldnames is None:
            return ['CSV file is empty']
        
        # Check headers
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if field not in reader.fieldnames:
                errors.append(f"Missing required column: {field}")
        
        if errors:
            return errors
        
        # Check rows
        for row_num, row in enumerate(reader, start=2):
            for field in required_fields:
                if not row.get(field, '').strip():
                    errors.append(f"Row {row_num}: Missing {field}")
            
            role = row.get('role', '').strip()
            if role and role not in ['superadmin', 'admin', 'teacher', 'student', 'parent', 'bursar']:
                errors.append(f"Row {row_num}: Invalid role '{role}'")
        
        return errors
    
    except Exception as e:
        return [f"Error reading CSV: {str(e)}"]


def get_csv_template():
    """Return a CSV template for user import"""
    return """username,email,password,first_name,last_name,role,school_id
john_doe,john@school.com,SecurePass123!,John,Doe,teacher,1
jane_smith,jane@school.com,SecurePass123!,Jane,Smith,student,1
admin_user,admin@school.com,SecurePass123!,Admin,User,admin,1"""
