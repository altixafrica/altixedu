"""
Encryption Utilities for AltixEdu Backend
- Database field-level encryption
- Secure key management
- Transparent encryption/decryption for sensitive fields
"""

from cryptography.fernet import Fernet
from django.conf import settings
import os
import base64
from django.db import models


class EncryptedField(models.Field):
    """
    A Django field that automatically encrypts/decrypts data.
    Used for SSN, health info, and other sensitive data.
    """
    description = "Encrypted field for storing sensitive information"
    
    def get_internal_type(self):
        return "TextField"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cipher = self._get_cipher()
    
    def _get_cipher(self):
        """Get Fernet cipher instance from settings"""
        encryption_key = getattr(settings, 'ENCRYPTION_KEY', None)
        if not encryption_key:
            # Generate a default key if not set (for development)
            encryption_key = Fernet.generate_key().decode()
        
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
        
        return Fernet(encryption_key)
    
    def get_prep_value(self, value):
        """Encrypt value before saving to database"""
        if value is None or value == '':
            return value
        
        if isinstance(value, str):
            value = value.encode()
        
        encrypted = self._cipher.encrypt(value)
        return encrypted.decode()
    
    def from_db_value(self, value, expression, connection):
        """Decrypt value retrieved from database"""
        if value is None or value == '':
            return value
        
        if isinstance(value, str):
            value = value.encode()
        
        try:
            decrypted = self._cipher.decrypt(value)
            return decrypted.decode()
        except Exception as e:
            # Log decryption errors but don't crash
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Decryption error: {str(e)}")
            return "[DECRYPTION_ERROR]"
    
    def to_python(self, value):
        """Convert database value to Python"""
        if value is None or value == '':
            return value
        return self.from_db_value(value, None, None)


class EncryptedCharField(EncryptedField):
    """CharField variant of EncryptedField"""
    def get_internal_type(self):
        return "CharField"


class EncryptedEmailField(EncryptedField):
    """EmailField variant of EncryptedField"""
    def get_internal_type(self):
        return "EmailField"


def setup_encryption_key():
    """
    Setup or retrieve encryption key.
    Run this in settings.py or during app initialization.
    """
    encryption_key_path = os.path.join(
        settings.BASE_DIR,
        '.encryption_key'
    )
    
    if os.path.exists(encryption_key_path):
        with open(encryption_key_path, 'r') as f:
            key = f.read()
    else:
        # Generate new key
        key = Fernet.generate_key().decode()
        
        # Save key to file (with restricted permissions)
        with open(encryption_key_path, 'w') as f:
            f.write(key)
        
        # Set file permissions to 600 (read/write for owner only)
        os.chmod(encryption_key_path, 0o600)
    
    return key


def encrypt_value(value, key=None):
    """
    Encrypt a single value using the master key.
    """
    if key is None:
        key = getattr(settings, 'ENCRYPTION_KEY', None)
    
    if isinstance(key, str):
        key = key.encode()
    
    cipher = Fernet(key)
    
    if isinstance(value, str):
        value = value.encode()
    
    return cipher.encrypt(value).decode()


def decrypt_value(encrypted_value, key=None):
    """
    Decrypt a single value using the master key.
    """
    if key is None:
        key = getattr(settings, 'ENCRYPTION_KEY', None)
    
    if isinstance(key, str):
        key = key.encode()
    
    cipher = Fernet(key)
    
    if isinstance(encrypted_value, str):
        encrypted_value = encrypted_value.encode()
    
    try:
        return cipher.decrypt(encrypted_value).decode()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Decryption error: {str(e)}")
        return None
