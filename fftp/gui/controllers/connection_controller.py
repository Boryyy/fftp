"""
Connection Controller - Manages FTP/SFTP connection lifecycle
Extracted from main_window.py as part of Phase 13 refactoring
"""

from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from ...models import ConnectionConfig
from ...managers import SFTPManager, FTPManager
from ..connection_worker import ConnectionWorker


class ConnectionController(QObject):
    """Handles all connection-related operations"""
    
    # Signals
    connection_started = pyqtSignal()
    connection_established = pyqtSignal(object)  # Emits manager
    connection_failed = pyqtSignal(str)  # Emits error message
    connection_closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager: Optional[SFTPManager | FTPManager] = None
        self.config: Optional[ConnectionConfig] = None
        self.connection_worker: Optional[ConnectionWorker] = None
        self._log_callback: Optional[Callable[[str], None]] = None
        self._status_callback: Optional[Callable[[str], None]] = None
    
    def set_log_callback(self, callback: Callable[[str], None]):
        """Set callback for logging messages"""
        self._log_callback = callback
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback for status updates"""
        self._status_callback = callback
    
    def _log(self, message: str):
        """Internal logging helper"""
        if self._log_callback:
            self._log_callback(message)
    
    def _status(self, message: str):
        """Internal status update helper"""
        if self._status_callback:
            self._status_callback(message)
    
    def connect(self, config: ConnectionConfig) -> bool:
        """
        Initiate connection to server
        
        Args:
            config: Connection configuration
            
        Returns:
            True if connection initiated successfully
        """
        if self.is_connected():
            self._log("Already connected. Disconnect first.")
            return False
        
        self.config = config
        self._log(f"Connecting to {config.host}:{config.port}...")
        self._status("Connecting...")
        
        # Create and start connection worker
        self.connection_worker = ConnectionWorker(config)
        self.connection_worker.connection_established.connect(self._on_connection_established)
        self.connection_worker.connection_failed.connect(self._on_connection_failed)
        
        self.connection_started.emit()
        self.connection_worker.start()
        
        return True
    
    def _on_connection_established(self, manager):
        """Handle successful connection"""
        self.manager = manager
        self._log(f"Connected to {self.config.host}")
        self._status(f"Connected to {self.config.host}")
        self.connection_established.emit(manager)
    
    def _on_connection_failed(self, error_message: str):
        """Handle connection failure"""
        self._log(f"Connection failed: {error_message}")
        self._status("Connection failed")
        self.connection_failed.emit(error_message)
        self.manager = None
        self.config = None
    
    def disconnect(self) -> bool:
        """
        Disconnect from current server
        
        Returns:
            True if disconnected successfully
        """
        if not self.is_connected():
            self._log("Not connected")
            return False
        
        try:
            if self.manager:
                self.manager.disconnect()
                self._log(f"Disconnected from {self.config.host if self.config else 'server'}")
                self._status("Disconnected")
            
            self.manager = None
            self.config = None
            self.connection_closed.emit()
            return True
            
        except Exception as e:
            self._log(f"Error during disconnect: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """Check if currently connected to a server"""
        return self.manager is not None and hasattr(self.manager, 'is_connected') and self.manager.is_connected()
    
    def get_manager(self) -> Optional[SFTPManager | FTPManager]:
        """Get current connection manager"""
        return self.manager
    
    def get_config(self) -> Optional[ConnectionConfig]:
        """Get current connection configuration"""
        return self.config
    
    def reconnect(self) -> bool:
        """
        Reconnect to the last server
        
        Returns:
            True if reconnection initiated successfully
        """
        if not self.config:
            self._log("No previous connection to reconnect to")
            return False
        
        self._log("Reconnecting...")
        self.disconnect()
        return self.connect(self.config)
