"""
Connection worker thread for non-blocking connections
"""

from PyQt6.QtCore import QThread, pyqtSignal
from ..models import ConnectionConfig


class ConnectionWorker(QThread):
    """Worker thread for connection operations"""
    finished = pyqtSignal(bool, str)
    status_update = pyqtSignal(str)
    log_message = pyqtSignal(str, str)
    
    def __init__(self, config: ConnectionConfig, manager_class):
        super().__init__()
        self.config = config
        self.manager_class = manager_class
        self.manager = None
    
    def run(self):
        """Run connection in background thread"""
        try:
            self.log_message.emit(f"Initializing {self.config.protocol.upper()} connection...", "info")
            self.status_update.emit(f"Initializing {self.config.protocol.upper()} connection...")
            self.manager = self.manager_class(self.config)
            
            self.log_message.emit(f"Connecting to {self.config.host}:{self.config.port} using {self.config.protocol.upper()}...", "info")
            self.status_update.emit(f"Connecting to {self.config.host}:{self.config.port}...")
            success, msg = self.manager.connect()
            
            if success:
                self.log_message.emit(f"Successfully connected to {self.config.host}:{self.config.port}", "success")
                self.status_update.emit(f"Successfully connected to {self.config.host}")
            else:
                self.log_message.emit(f"Connection failed: {msg}", "error")
                self.status_update.emit(f"Connection failed: {msg}")
            
            self.finished.emit(success, msg)
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            self.log_message.emit(error_msg, "error")
            self.status_update.emit(error_msg)
            self.finished.emit(False, str(e))
