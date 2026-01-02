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
        """Set master password (creates hash for verification)"""
        try:
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest.update(password.encode())
            password_hash = digest.finalize()
            
            with open(self.master_hash_file, 'wb') as f:
                f.write(password_hash)
            
            return True
        except Exception as e:
            return False
    
    def verify_master_password(self, password: str) -> bool:
        """Verify master password"""
        if not self.master_hash_file.exists():
            return False
        
        try:
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest.update(password.encode())
            provided_hash = digest.finalize()
            
            with open(self.master_hash_file, 'rb') as f:
                stored_hash = f.read()
            
            return provided_hash == stored_hash
        except Exception:
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
    
    def clear_encrypted_data(self):
        """Clear all encrypted data (for testing/reset)"""
        if self.connections_file.exists():
            self.connections_file.unlink()
        if self.master_hash_file.exists():
            self.master_hash_file.unlink()
