"""
Data models for FTP/SFTP client
"""

from dataclasses import dataclass


@dataclass
class ConnectionConfig:
    """Store connection settings"""
    name: str
    host: str
    port: int
    username: str
    password: str
    protocol: str  # 'ftp', 'ftps', 'sftp'
    use_passive: bool = True
    use_key_file: bool = False
    key_path: str = ""
    use_ssl: bool = False
    ssl_implicit: bool = False


@dataclass
class RemoteFile:
    """Represent remote file/folder"""
    name: str
    path: str
    is_dir: bool
    size: int
    modified: str
