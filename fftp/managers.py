"""
FTP and SFTP connection managers
"""

from typing import List
from datetime import datetime
from pathlib import Path
import paramiko
import ftplib
import os
from .models import ConnectionConfig, RemoteFile


class HostKeyPolicy(paramiko.MissingHostKeyPolicy):
    """Custom host key policy that stores known hosts"""
    def __init__(self, known_hosts_file):
        self.known_hosts_file = known_hosts_file
        self.known_hosts = {}
        self._load_known_hosts()
    
    def _load_known_hosts(self):
        """Load known hosts from file"""
        if self.known_hosts_file.exists():
            try:
                with open(self.known_hosts_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split()
                            if len(parts) >= 2:
                                hostname = parts[0]
                                key_type = parts[1]
                                if len(parts) >= 3:
                                    key_data = parts[2]
                                    self.known_hosts[hostname] = (key_type, key_data)
            except Exception:
                pass
    
    def _save_known_hosts(self):
        """Save known hosts to file"""
        try:
            self.known_hosts_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.known_hosts_file, 'w') as f:
                for hostname, (key_type, key_data) in self.known_hosts.items():
                    f.write(f"{hostname} {key_type} {key_data}\n")
        except Exception:
            pass
    
    def missing_host_key(self, client, hostname, key):
        """Handle missing host key"""
        key_type = key.get_name()
        
        if hostname in self.known_hosts:
            stored_type, stored_data = self.known_hosts[hostname]
            if stored_type == key_type and stored_data == key.get_base64():
                return
        
        self.known_hosts[hostname] = (key_type, key.get_base64())
        self._save_known_hosts()


class SFTPManager:
    """Handle SFTP connections via paramiko"""
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.client = None
        self.sftp = None
        known_hosts_path = Path.home() / ".fftp" / "known_hosts"
        self.host_key_policy = HostKeyPolicy(known_hosts_path)
    
    def connect(self):
        """Establish SFTP connection"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(self.host_key_policy)
            
            connect_params = {
                'hostname': self.config.host,
                'port': self.config.port,
                'username': self.config.username,
                'timeout': 30,
                'allow_agent': False,
                'look_for_keys': False
            }
            
            if self.config.use_key_file and self.config.key_path:
                connect_params['key_filename'] = self.config.key_path
                self.client.connect(**connect_params)
            else:
                if not self.config.password:
                    return False, "SFTP Error: Password required for password authentication"
                connect_params['password'] = self.config.password
                self.client.connect(**connect_params)
            
            self.sftp = self.client.open_sftp()
            return True, "SFTP connected"
        except paramiko.AuthenticationException:
            return False, "SFTP Authentication failed. Check username and password."
        except paramiko.SSHException as e:
            return False, f"SFTP SSH Error: {str(e)}"
        except ConnectionRefusedError:
            return False, f"Connection refused. Check host and port."
        except TimeoutError:
            return False, f"Connection timeout. Check host and port."
        except Exception as e:
            return False, f"SFTP Error: {str(e)}"
    
    def get_current_directory(self) -> str:
        """Get current working directory"""
        try:
            return self.sftp.normalize(".")
        except:
            try:
                return self.sftp.getcwd()
            except:
                return "."
    
    def is_connected(self) -> bool:
        """Check if connection is still alive"""
        try:
            if not self.sftp or not self.client:
                return False
            self.sftp.listdir(".")
            return True
        except:
            return False
    
    def list_files(self, path: str = ".") -> List[RemoteFile]:
        """List remote directory"""
        try:
            files = []
            
            if path == "." or path == "":
                try:
                    items = self.sftp.listdir_attr(".")
                except:
                    try:
                        current_dir = self.sftp.getcwd()
                        if current_dir:
                            items = self.sftp.listdir_attr(current_dir)
                            path = current_dir
                        else:
                            items = self.sftp.listdir_attr(".")
                    except:
                        items = self.sftp.listdir_attr(".")
            else:
                try:
                    items = self.sftp.listdir_attr(path)
                except Exception as e:
                    error_str = str(e).lower()
                    if "no such file" in error_str or "not found" in error_str:
                        try:
                            items = self.sftp.listdir_attr(".")
                            path = "."
                        except:
                            items = []
                    else:
                        raise
            
            for item in items:
                try:
                    is_dir = paramiko.stat.S_ISDIR(item.st_mode)
                    if path == "." or path == "":
                        file_path = item.filename
                    else:
                        file_path = f"{path.rstrip('/')}/{item.filename}"
                    
                    files.append(RemoteFile(
                        name=item.filename,
                        path=file_path,
                        is_dir=is_dir,
                        size=item.st_size if not is_dir else 0,
                        modified=datetime.fromtimestamp(item.st_mtime).strftime("%Y-%m-%d %H:%M") if hasattr(item, 'st_mtime') else ""
                    ))
                except Exception as e:
                    continue
            
            return sorted(files, key=lambda x: (not x.is_dir, x.name.lower()))
        except Exception as e:
            raise Exception(f"List error: {str(e)}")
    
    def download_file(self, remote_path: str, local_path: str):
        """Download file from remote"""
        self.sftp.get(remote_path, local_path)
    
    def upload_file(self, local_path: str, remote_path: str):
        """Upload file to remote"""
        try:
            remote_dir = '/'.join(remote_path.split('/')[:-1]) if '/' in remote_path else None
            remote_filename = remote_path.split('/')[-1] if '/' in remote_path else remote_path
            
            if remote_dir and remote_dir != '.':
                try:
                    self.sftp.chdir(remote_dir)
                    final_path = remote_filename
                except:
                    final_path = remote_path
            else:
                final_path = remote_path
            
            self.sftp.put(local_path, final_path)
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")
    
    def delete_file(self, remote_path: str):
        """Delete remote file"""
        self.sftp.remove(remote_path)
    
    def delete_folder(self, remote_path: str):
        """Delete remote folder recursively"""
        self.sftp.rmdir(remote_path)
    
    def create_folder(self, remote_path: str):
        """Create remote folder"""
        self.sftp.mkdir(remote_path)
    
    def rename_file(self, old_path: str, new_path: str):
        """Rename remote file or folder"""
        self.sftp.rename(old_path, new_path)
    
    def disconnect(self):
        """Close SFTP connection"""
        if self.sftp:
            try:
                self.sftp.close()
            except:
                pass
        if self.client:
            try:
                self.client.close()
            except:
                pass


class FTPManager:
    """Handle FTP and FTPS connections"""
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.ftp = None
    
    def connect(self):
        """Establish FTP or FTPS connection"""
        try:
            if self.config.protocol == "ftps" or self.config.use_ssl:
                self.ftp = ftplib.FTP_TLS()
                self.ftp.connect(self.config.host, self.config.port, timeout=30)
                if self.config.ssl_implicit:
                    self.ftp.auth()
                else:
                    self.ftp.prot_p()
            else:
                self.ftp = ftplib.FTP()
                self.ftp.connect(self.config.host, self.config.port, timeout=30)
            
            # Try different authentication approaches
            if self.config.username == "anonymous" or not self.config.password:
                try:
                    self.ftp.login(self.config.username or "anonymous", self.config.password or "")
                except ftplib.error_perm:
                    # Some servers require empty password for anonymous
                    self.ftp.login("anonymous", "")
            else:
                # Try with provided credentials
                try:
                    self.ftp.login(self.config.username, self.config.password)
                except ftplib.error_perm as auth_error:
                    # Try alternative: some servers are case-sensitive
                    try:
                        # Try lowercase username
                        self.ftp.login(self.config.username.lower(), self.config.password)
                    except ftplib.error_perm:
                        # Try uppercase username
                        try:
                            self.ftp.login(self.config.username.upper(), self.config.password)
                        except ftplib.error_perm:
                            # Re-raise original error
                            raise auth_error
            
            if self.config.use_passive:
                self.ftp.set_pasv(True)
            
            protocol_name = "FTPS" if (self.config.protocol == "ftps" or self.config.use_ssl) else "FTP"
            return True, f"{protocol_name} connected"
        except ftplib.error_perm as e:
            error_msg = str(e).strip()
            if not error_msg:
                error_msg = "Authentication failed - check username and password"
            return False, f"FTP Authentication Error: {error_msg}"
        except ftplib.error_temp as e:
            error_msg = str(e).strip()
            if not error_msg:
                error_msg = "Temporary server error - try again later"
            return False, f"FTP Temporary Error: {error_msg}"
        except ConnectionRefusedError as e:
            return False, f"Connection refused by {self.config.host}:{self.config.port}. Check if server is running and firewall settings."
        except TimeoutError as e:
            return False, f"Connection timeout to {self.config.host}:{self.config.port}. Check network connectivity and server response time."
        except OSError as e:
            # Socket errors, DNS resolution, etc.
            error_code = getattr(e, 'errno', None)
            if error_code == 11001:  # Windows DNS error
                return False, f"DNS resolution failed for {self.config.host}. Check hostname spelling."
            elif error_code == 10061:  # Windows connection refused
                return False, f"Connection refused by {self.config.host}:{self.config.port}. Server may be down or blocking connections."
            elif error_code == 10060:  # Windows timeout
                return False, f"Connection timeout to {self.config.host}:{self.config.port}. Network may be slow or server unresponsive."
            else:
                return False, f"Network error connecting to {self.config.host}:{self.config.port}: {str(e)}"
        except Exception as e:
            error_msg = str(e).strip()
            if not error_msg:
                error_msg = "Unknown connection error"
            return False, f"FTP Error: {error_msg} (Host: {self.config.host}:{self.config.port})"
    
    def get_current_directory(self) -> str:
        """Get current working directory"""
        try:
            return self.ftp.pwd()
        except:
            return "."
    
    def is_connected(self) -> bool:
        """Check if connection is still alive"""
        try:
            if not self.ftp:
                return False
            self.ftp.voidcmd("NOOP")
            return True
        except:
            return False
    
    def list_files(self, path: str = ".") -> List[RemoteFile]:
        """List remote directory"""
        try:
            files = []
            
            if path == "." or path == "":
                try:
                    current_dir = self.ftp.pwd()
                    if current_dir:
                        path = current_dir
                    else:
                        path = "/"
                except:
                    path = "/"
            
            try:
                self.ftp.cwd(path)
            except:
                try:
                    self.ftp.cwd("/")
                    path = "/"
                except:
                    pass
            
            self.ftp.dir(lambda line: self._parse_ftp_line(line, files, path))
            return sorted(files, key=lambda x: (not x.is_dir, x.name.lower()))
        except Exception as e:
            raise Exception(f"List error: {str(e)}")
    
    def _parse_ftp_line(self, line: str, files: list, current_path: str = "."):
        """Parse FTP LIST output"""
        try:
            parts = line.split()
            if len(parts) >= 9:
                is_dir = line.startswith('d')
                name = ' '.join(parts[8:])
                if name in ['.', '..']:
                    return
                
                try:
                    size = int(parts[4]) if not is_dir else 0
                except:
                    size = 0
                
                if current_path == "." or current_path == "/":
                    file_path = name
                else:
                    file_path = f"{current_path.rstrip('/')}/{name}"
                
                files.append(RemoteFile(
                    name=name,
                    path=file_path,
                    is_dir=is_dir,
                    size=size,
                    modified=f"{parts[5]} {parts[6]} {parts[7]}" if len(parts) >= 8 else ""
                ))
        except Exception:
            pass
    
    def download_file(self, remote_path: str, local_path: str):
        """Download file"""
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, 'wb') as f:
                self.ftp.retrbinary(f'RETR {remote_path}', f.write)
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")
    
    def upload_file(self, local_path: str, remote_path: str):
        """Upload file"""
        try:
            remote_dir = '/'.join(remote_path.split('/')[:-1]) if '/' in remote_path else '.'
            remote_filename = remote_path.split('/')[-1] if '/' in remote_path else remote_path
            
            if remote_dir and remote_dir != '.':
                try:
                    self.ftp.cwd(remote_dir)
                except:
                    pass
            
            with open(local_path, 'rb') as f:
                self.ftp.storbinary(f'STOR {remote_filename}', f)
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")
    
    def delete_file(self, remote_path: str):
        """Delete file"""
        self.ftp.delete(remote_path)
    
    def delete_folder(self, remote_path: str):
        """Delete folder"""
        self.ftp.rmd(remote_path)
    
    def create_folder(self, remote_path: str):
        """Create folder"""
        self.ftp.mkd(remote_path)
    
    def rename_file(self, old_path: str, new_path: str):
        """Rename remote file or folder"""
        self.ftp.rename(old_path, new_path)
    
    def disconnect(self):
        """Close connection"""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                try:
                    self.ftp.close()
                except:
                    pass
