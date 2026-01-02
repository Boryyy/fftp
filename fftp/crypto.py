"""
Encryption module for secure connection storage
Uses PBKDF2 for key derivation and Fernet for symmetric encryption
"""

import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class EncryptionManager:
    """Manages encryption/decryption of connection data"""
    
    def __init__(self, config_dir: Path = None):
        if config_dir is None:
            config_dir = Path.home() / ".fftp"
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        self.salt_file = self.config_dir / "salt.dat"
        self.connections_file = self.config_dir / "connections.encrypted"
        self.master_hash_file = self.config_dir / "master.hash"
    
    def _get_salt(self) -> bytes:
        """Get or create salt for key derivation"""
        if self.salt_file.exists():
            with open(self.salt_file, 'rb') as f:
                return f.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            return salt
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # High iteration count for security
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _get_fernet(self, password: str) -> Fernet:
        """Get Fernet cipher instance"""
        salt = self._get_salt()
        key = self._derive_key(password, salt)
        return Fernet(key)
    
    def set_master_password(self, password: str) -> bool:
        """Set master password (creates verification token using same key derivation as encryption)"""
        try:
            # Use the same key derivation as encryption
            salt = self._get_salt()
            key = self._derive_key(password, salt)

            # Create a verification token by encrypting a known value
            fernet = Fernet(key)
            verification_token = fernet.encrypt(b"VERIFIED")

            with open(self.master_hash_file, 'wb') as f:
                f.write(verification_token)

            return True
        except Exception as e:
            return False
    
    def verify_master_password(self, password: str) -> bool:
        """Verify master password using same key derivation as encryption"""
        if not self.master_hash_file.exists():
            return False

        try:
            # Use the same key derivation as encryption
            salt = self._get_salt()
            key = self._derive_key(password, salt)

            fernet = Fernet(key)

            with open(self.master_hash_file, 'rb') as f:
                stored_token = f.read()

            # Try to decrypt the verification token
            decrypted = fernet.decrypt(stored_token)
            result = decrypted == b"VERIFIED"

            return result
        except Exception as e:
            return False
    
    def has_master_password(self) -> bool:
        """Check if master password is set"""
        return self.master_hash_file.exists()
    
    def encrypt_connections(self, connections: list, password: str) -> bool:
        """Encrypt and save connections"""
        try:
            fernet = self._get_fernet(password)
            
            import json
            data = json.dumps(connections).encode()
            
            encrypted_data = fernet.encrypt(data)
            
            with open(self.connections_file, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            return False
    
    def decrypt_connections(self, password: str) -> list:
        """Decrypt and load connections"""
        if not self.connections_file.exists():
            return []

        try:
            fernet = self._get_fernet(password)

            with open(self.connections_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = fernet.decrypt(encrypted_data)

            import json
            connections = json.loads(decrypted_data.decode())

            return connections
        except Exception as e:
            return []
    
    def migrate_legacy_password(self) -> bool:
        """Check if using old SHA256-based password system"""
        if not self.master_hash_file.exists():
            return False  # No password to migrate

        try:
            # Check if it's an old-style hash (32 bytes for SHA256) vs new-style token (longer)
            with open(self.master_hash_file, 'rb') as f:
                data = f.read()

            # Old SHA256 hash is 32 bytes, new encrypted token is much longer
            return len(data) != 32
        except Exception as e:
            return False

    def clear_encrypted_data(self):
        """Clear all encrypted data (for testing/reset)"""
        if self.connections_file.exists():
            self.connections_file.unlink()
        if self.master_hash_file.exists():
            self.master_hash_file.unlink()
        if self.salt_file.exists():
            self.salt_file.unlink()  # Also remove salt for fresh start
