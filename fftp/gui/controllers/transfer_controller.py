"""
Transfer Controller - Manages file transfer operations and queue
Extracted from main_window.py as part of Phase 13 refactoring
"""

from typing import Optional, Callable, List
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

from ...managers import SFTPManager, FTPManager
from ..transfer_engine import TransferEngine


class TransferItem:
    """Represents a single transfer operation"""
    
    def __init__(self, local_path: Path, remote_path: str, direction: str, size: int = 0):
        self.local_path = local_path
        self.remote_path = remote_path
        self.direction = direction  # 'upload' or 'download'
        self.size = size
        self.progress = 0
        self.status = 'queued'  # queued, active, completed, failed
        self.error_message = None
        self.speed = 0
        self.eta = 0


class TransferController(QObject):
    """Handles all file transfer operations"""
    
    # Signals
    transfer_started = pyqtSignal(object)  # Emits TransferItem
    transfer_progress = pyqtSignal(object, int, int)  # item, current, total
    transfer_completed = pyqtSignal(object)  # Emits TransferItem
    transfer_failed = pyqtSignal(object, str)  # item, error_message
    queue_updated = pyqtSignal()
    
    def __init__(self, parent=None, max_concurrent: int = 10):
        super().__init__(parent)
        self.max_concurrent_transfers = max_concurrent
        self.transfer_queue: List[TransferItem] = []
        self.active_transfers: List[TransferEngine] = []
        self.completed_transfers: List[TransferItem] = []
        self.failed_transfers: List[TransferItem] = []
        
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
    
    def add_upload(self, manager, local_path: Path, remote_path: str) -> TransferItem:
        """
        Add upload to queue
        
        Args:
            manager: FTP/SFTP manager
            local_path: Local file path
            remote_path: Remote destination path
            
        Returns:
            TransferItem representing this transfer
        """
        size = local_path.stat().st_size if local_path.exists() else 0
        item = TransferItem(local_path, remote_path, 'upload', size)
        self.transfer_queue.append(item)
        
        self._log(f"Added to upload queue: {local_path.name}")
        self.queue_updated.emit()
        self._process_queue(manager)
        
        return item
    
    def add_download(self, manager, remote_path: str, local_path: Path, size: int = 0) -> TransferItem:
        """
        Add download to queue
        
        Args:
            manager: FTP/SFTP manager
            remote_path: Remote file path
            local_path: Local destination path
            size: File size (if known)
            
        Returns:
            TransferItem representing this transfer
        """
        item = TransferItem(local_path, remote_path, 'download', size)
        self.transfer_queue.append(item)
        
        self._log(f"Added to download queue: {Path(remote_path).name}")
        self.queue_updated.emit()
        self._process_queue(manager)
        
        return item
    
    def _process_queue(self, manager):
        """Process queued transfers up to max concurrent limit"""
        while (len(self.active_transfers) < self.max_concurrent_transfers and 
               len(self.transfer_queue) > 0):
            
            item = self.transfer_queue.pop(0)
            self._start_transfer(manager, item)
    
    def _start_transfer(self, manager, item: TransferItem):
        """Start a single transfer"""
        item.status = 'active'
        self.transfer_started.emit(item)
        
        # Create transfer engine
        engine = TransferEngine(
            manager=manager,
            local_path=str(item.local_path),
            remote_path=item.remote_path,
            direction=item.direction,
            parent=self
        )
        
        # Connect signals
        engine.progress_updated.connect(
            lambda current, total: self._on_progress(item, current, total)
        )
        engine.transfer_completed.connect(
            lambda: self._on_completed(item, engine, manager)
        )
        engine.transfer_failed.connect(
            lambda error: self._on_failed(item, engine, error, manager)
        )
        
        self.active_transfers.append(engine)
        engine.start()
        
        self._log(f"Started {item.direction}: {item.local_path.name}")
    
    def _on_progress(self, item: TransferItem, current: int, total: int):
        """Handle transfer progress update"""
        item.progress = int((current / total * 100)) if total > 0 else 0
        self.transfer_progress.emit(item, current, total)
    
    def _on_completed(self, item: TransferItem, engine: TransferEngine, manager):
        """Handle transfer completion"""
        item.status = 'completed'
        item.progress = 100
        
        if engine in self.active_transfers:
            self.active_transfers.remove(engine)
        
        self.completed_transfers.append(item)
        self.transfer_completed.emit(item)
        
        self._log(f"Completed {item.direction}: {item.local_path.name}")
        self._status(f"Transfer completed: {item.local_path.name}")
        
        # Process next in queue
        self._process_queue(manager)
    
    def _on_failed(self, item: TransferItem, engine: TransferEngine, error: str, manager):
        """Handle transfer failure"""
        item.status = 'failed'
        item.error_message = error
        
        if engine in self.active_transfers:
            self.active_transfers.remove(engine)
        
        self.failed_transfers.append(item)
        self.transfer_failed.emit(item, error)
        
        self._log(f"Failed {item.direction}: {item.local_path.name} - {error}")
        self._status(f"Transfer failed: {item.local_path.name}")
        
        # Process next in queue
        self._process_queue(manager)
    
    def cancel_transfer(self, item: TransferItem):
        """Cancel a specific transfer"""
        if item.status == 'queued' and item in self.transfer_queue:
            self.transfer_queue.remove(item)
            self._log(f"Cancelled queued transfer: {item.local_path.name}")
            self.queue_updated.emit()
    
    def clear_completed(self):
        """Clear completed transfers list"""
        self.completed_transfers.clear()
        self.queue_updated.emit()
    
    def clear_failed(self):
        """Clear failed transfers list"""
        self.failed_transfers.clear()
        self.queue_updated.emit()
    
    def get_queue_status(self) -> dict:
        """Get current queue statistics"""
        return {
            'queued': len(self.transfer_queue),
            'active': len(self.active_transfers),
            'completed': len(self.completed_transfers),
            'failed': len(self.failed_transfers)
        }
    
    def set_max_concurrent(self, max_concurrent: int):
        """Update maximum concurrent transfers"""
        self.max_concurrent_transfers = max_concurrent
        self._log(f"Max concurrent transfers set to {max_concurrent}")
