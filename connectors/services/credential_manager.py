"""
Credential Manager Service

Handles encryption/decryption of API credentials.
Uses Fernet symmetric encryption (cryptography library).
"""

import os
from typing import Optional
from cryptography.fernet import Fernet
from datetime import datetime


class CredentialManager:
    """
    Manages secure storage of API credentials.
    
    Uses Fernet (symmetric encryption) for API keys.
    Key should be stored in environment variable.
    
    Usage:
        manager = CredentialManager(encryption_key)
        encrypted = manager.encrypt("sk_test_123")
        decrypted = manager.decrypt(encrypted)
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize manager with encryption key.
        
        Args:
            encryption_key: Base64-encoded Fernet key.
                           If None, reads from ENCRYPTION_KEY env var.
        
        Raises:
            ValueError: If no key provided
        """
        key = encryption_key or os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError(
                "Encryption key required. "
                "Set ENCRYPTION_KEY environment variable or pass key."
            )
        
        try:
            self.cipher = Fernet(key.encode())
        except Exception as e:
            raise ValueError(
                f"Invalid encryption key: {str(e)}"
            )
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a credential.
        
        Args:
            plaintext: Raw API key or token
        
        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            raise ValueError("Cannot encrypt empty string")
        
        encrypted_bytes = self.cipher.encrypt(plaintext.encode())
        return encrypted_bytes.decode()
    
    def decrypt(self, encrypted: str) -> str:
        """
        Decrypt a credential.
        
        Args:
            encrypted: Base64-encoded encrypted string
        
        Returns:
            Original plaintext credential
        
        Raises:
            ValueError: If decryption fails
        """
        if not encrypted:
            raise ValueError("Cannot decrypt empty string")
        
        try:
            decrypted_bytes = self.cipher.decrypt(encrypted.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            raise ValueError(
                f"Decryption failed: {str(e)}"
            )
    
    def rotate_key(
        self,
        old_key: str,
        new_key: str,
        encrypted_value: str
    ) -> str:
        """
        Re-encrypt credential with new key.
        
        Used for key rotation.
        
        Args:
            old_key: Current encryption key
            new_key: New encryption key
            encrypted_value: Value encrypted with old key
        
        Returns:
            Value encrypted with new key
        """
        # Decrypt with old key
        old_manager = CredentialManager(old_key)
        plaintext = old_manager.decrypt(encrypted_value)
        
        # Encrypt with new key
        new_manager = CredentialManager(new_key)
        return new_manager.encrypt(plaintext)
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet encryption key.
        
        Returns:
            Base64-encoded key (store securely!)
        """
        key = Fernet.generate_key()
        return key.decode()
    
    def is_expired(self, expires_at: Optional[datetime]) -> bool:
        """
        Check if credential has expired.
        
        Args:
            expires_at: Expiration timestamp
        
        Returns:
            True if expired or no expiration set
        """
        if not expires_at:
            return False
        
        return datetime.utcnow() > expires_at


# Credential type helpers
class CredentialType:
    """Supported credential types"""
    API_KEY = "api_key"
    OAUTH_TOKEN = "oauth_token"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"


class CredentialValidator:
    """Validates credentials before encryption"""
    
    @staticmethod
    def validate_api_key(key: str) -> bool:
        """Basic API key validation"""
        if not key or len(key) < 10:
            return False
        return True
    
    @staticmethod
    def validate_oauth_token(token: str) -> bool:
        """Basic OAuth token validation"""
        if not token or len(token) < 20:
            return False
        return True
