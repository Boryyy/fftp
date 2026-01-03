"""
Navigation Controller - Manages local and remote directory navigation
Extracted from main_window.py as part of Phase 13 refactoring
"""

from typing import Optional, Callable, List
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

from ...managers import SFTPManager, FTPManager
from ...models import RemoteFile


class NavigationController(QObject):
    """Handles directory navigation for both local and remote"""
    
    # Signals
    local_path_changed = pyqtSignal(str)  # Emits new path
    remote_path_changed = pyqtSignal(str)  # Emits new path
    local_files_loaded = pyqtSignal(list)  # Emits file list
    remote_files_loaded = pyqtSignal(list)  # Emits file list
    navigation_error = pyqtSignal(str)  # Emits error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_local_path = str(Path.home())
        self.current_remote_path = "/"
        self.local_history: List[str] = []
        self.remote_history: List[str] = []
        
        self._log_callback: Optional[Callable[[str], None]] = None
    
    def set_log_callback(self, callback: Callable[[str], None]):
        """Set callback for logging messages"""
        self._log_callback = callback
    
    def _log(self, message: str):
        """Internal logging helper"""
        if self._log_callback:
            self._log_callback(message)
    
    # Local Navigation
    
    def navigate_local(self, path: str) -> bool:
        """
        Navigate to local directory
        
        Args:
            path: Directory path to navigate to
            
        Returns:
            True if navigation successful
        """
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                self._log(f"Path does not exist: {path}")
                self.navigation_error.emit(f"Path does not exist: {path}")
                return False
            
            if not path_obj.is_dir():
                self._log(f"Not a directory: {path}")
                self.navigation_error.emit(f"Not a directory: {path}")
                return False
            
            # Add to history
            if self.current_local_path != path:
                self.local_history.append(self.current_local_path)
            
            self.current_local_path = str(path_obj)
            self.local_path_changed.emit(self.current_local_path)
            self._log(f"Navigated to: {self.current_local_path}")
            
            return True
            
        except Exception as e:
            self._log(f"Error navigating to {path}: {str(e)}")
            self.navigation_error.emit(str(e))
            return False
    
    def local_up(self) -> bool:
        """Navigate up one directory in local filesystem"""
        parent = Path(self.current_local_path).parent
        return self.navigate_local(str(parent))
    
    def local_back(self) -> bool:
        """Navigate back in local history"""
        if not self.local_history:
            return False
        
        previous_path = self.local_history.pop()
        self.current_local_path = previous_path
        self.local_path_changed.emit(self.current_local_path)
        return True
    
    def get_local_path(self) -> str:
        """Get current local path"""
        return self.current_local_path
    
    # Remote Navigation
    
    def navigate_remote(self, manager, path: str) -> bool:
        """
        Navigate to remote directory
        
        Args:
            manager: FTP/SFTP manager
            path: Directory path to navigate to
            
        Returns:
            True if navigation successful
        """
        if not manager:
            self._log("Not connected to server")
            self.navigation_error.emit("Not connected to server")
            return False
        
        try:
            # Try to list files in the path to verify it exists
            files = manager.list_files(path)
            
            # Add to history
            if self.current_remote_path != path:
                self.remote_history.append(self.current_remote_path)
            
            self.current_remote_path = path
            self.remote_path_changed.emit(self.current_remote_path)
            self._log(f"Navigated to remote: {self.current_remote_path}")
            
            return True
            
        except Exception as e:
            self._log(f"Error navigating to remote {path}: {str(e)}")
            self.navigation_error.emit(str(e))
            return False
    
    def remote_up(self, manager) -> bool:
        """Navigate up one directory in remote filesystem"""
        if not manager:
            return False
        
        # Handle root directory
        if self.current_remote_path in ['/', '.']:
            return False
        
        # Get parent directory
        parts = self.current_remote_path.rstrip('/').split('/')
        if len(parts) > 1:
            parent = '/'.join(parts[:-1]) or '/'
        else:
            parent = '/'
        
        return self.navigate_remote(manager, parent)
    
    def remote_back(self, manager) -> bool:
        """Navigate back in remote history"""
        if not self.remote_history:
            return False
        
        previous_path = self.remote_history.pop()
        return self.navigate_remote(manager, previous_path)
    
    def get_remote_path(self) -> str:
        """Get current remote path"""
        return self.current_remote_path
    
    # File Listing
    
    def load_local_files(self) -> List[Path]:
        """
        Load files from current local directory
        
        Returns:
            List of Path objects
        """
        try:
            path = Path(self.current_local_path)
            files = list(path.iterdir())
            self.local_files_loaded.emit(files)
            return files
        except Exception as e:
            self._log(f"Error loading local files: {str(e)}")
            self.navigation_error.emit(str(e))
            return []
    
    def load_remote_files(self, manager) -> List[RemoteFile]:
        """
        Load files from current remote directory
        
        Args:
            manager: FTP/SFTP manager
            
        Returns:
            List of RemoteFile objects
        """
        if not manager:
            return []
        
        try:
            files = manager.list_files(self.current_remote_path)
            self.remote_files_loaded.emit(files)
            return files
        except Exception as e:
            self._log(f"Error loading remote files: {str(e)}")
            self.navigation_error.emit(str(e))
            return []
    
    # Synchronized Browsing
    
    def sync_local_to_remote(self, manager, local_path: str) -> bool:
        """
        Synchronize remote path based on local path change
        
        Args:
            manager: FTP/SFTP manager
            local_path: New local path
            
        Returns:
            True if sync successful
        """
        # This is a simplified version - can be enhanced with path mapping
        return self.navigate_remote(manager, self.current_remote_path)
    
    def sync_remote_to_local(self, remote_path: str) -> bool:
        """
        Synchronize local path based on remote path change
        
        Args:
            remote_path: New remote path
            
        Returns:
            True if sync successful
        """
        # This is a simplified version - can be enhanced with path mapping
        return self.navigate_local(self.current_local_path)
