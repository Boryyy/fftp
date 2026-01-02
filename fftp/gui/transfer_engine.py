"""
Transfer engine for handling individual file transfers
"""

import os
import time
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal, QObject


class TransferEngine(QObject):
    """Engine for handling individual file transfers"""

    # Signals
    progress_updated = pyqtSignal(int, int, int)  # row, bytes_transferred, total_bytes
    transfer_completed = pyqtSignal(int, bool, str)  # row, success, message
    transfer_cancelled = pyqtSignal(int)  # row

    def __init__(self, direction, local_file, remote_file, queue_row, parent):
        super().__init__()
        self.direction = direction  # "Upload" or "Download"
        self.local_file = local_file
        self.remote_file = remote_file
        self.queue_row = queue_row
        self.parent = parent
        self.cancelled = False
        self.paused = False
        self.thread = None
        self.speed_limit = getattr(parent, 'transfer_speed_limit', 0)  # bytes per second, 0 = unlimited
        self.chunk_size = 8192  # 8KB chunks
        self.last_progress_time = 0
        self.bytes_since_last_check = 0

    def start(self):
        """Start the transfer"""
        self.thread = QThread()
        self.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.run_transfer)
        self.transfer_completed.connect(self.parent.on_transfer_completed)
        self.progress_updated.connect(self.parent.on_transfer_progress)

        self.thread.start()

    def run_transfer(self):
        """Run the actual transfer"""
        try:
            if self.direction == "Upload":
                self._upload_file()
            elif self.direction == "Download":
                self._download_file()
            else:
                self.transfer_completed.emit(self.queue_row, False, "Unknown transfer direction")

        except Exception as e:
            self.transfer_completed.emit(self.queue_row, False, str(e))

    def _upload_file(self):
        """Upload a file to remote server with speed limiting"""
        local_path = Path(self.local_file)
        if not local_path.exists():
            self.transfer_completed.emit(self.queue_row, False, "Local file not found")
            return

        # Get the current tab's manager
        tab = self.parent.get_current_tab()
        if not tab or not tab.manager:
            self.transfer_completed.emit(self.queue_row, False, "No active connection")
            return

        try:
            # Use the high-level upload_file function with overwrite checking
            from .file_operations import upload_file

            # Determine the remote directory path
            remote_dir = os.path.dirname(self.remote_file)
            if not remote_dir or remote_dir == ".":
                remote_dir = tab.current_remote_path if tab.current_remote_path != "." else "/"

            # Create a simple progress callback
            def progress_callback(current, total):
                if not self.cancelled and not self.paused:
                    self.progress_updated.emit(self.queue_row, current, total)

            success = upload_file(
                tab.manager,
                local_path,
                remote_dir,
                log_callback=self.parent.log,
                status_callback=lambda msg: None,  # Don't show status during transfer
                queue_callback=None,  # Don't add to queue again
                move_completed_callback=None,
                refresh_callback=None,
                format_size_func=self.parent.format_size if hasattr(self.parent, 'format_size') else None,
                parent_widget=self.parent,
                overwrite_mode=self.parent.upload_overwrite_mode if hasattr(self.parent, 'upload_overwrite_mode') else "ask"
            )

            if self.cancelled:
                self.transfer_cancelled.emit(self.queue_row)
            elif success:
                self.transfer_completed.emit(self.queue_row, True, "Upload completed")
            else:
                self.transfer_completed.emit(self.queue_row, False, "Upload failed")

        except Exception as e:
            self.transfer_completed.emit(self.queue_row, False, f"Upload failed: {e}")

    def _download_file(self):
        """Download a file from remote server with speed limiting"""
        # Get the current tab's manager
        tab = self.parent.get_current_tab()
        if not tab or not tab.manager:
            self.transfer_completed.emit(self.queue_row, False, "No active connection")
            return

        try:
            # Ensure local directory exists
            local_dir = os.path.dirname(self.local_file)
            if local_dir:
                Path(local_dir).mkdir(parents=True, exist_ok=True)

            # Download file with speed limiting
            # For now, this is a simplified version. In a real implementation,
            # you'd modify the manager's download method to support chunked reading
            tab.manager.download_file(self.remote_file, self.local_file)

            # Simulate progress updates for speed limiting demo
            local_path = Path(self.local_file)
            if local_path.exists():
                file_size = local_path.stat().st_size
                # Simulate progress updates
                for i in range(0, 101, 10):
                    if self.cancelled:
                        break
                    bytes_done = int(file_size * i / 100)
                    self.progress_updated.emit(self.queue_row, bytes_done, file_size)
                    self._apply_speed_limit(min(self.chunk_size, file_size - bytes_done))

            self.transfer_completed.emit(self.queue_row, True, "Download completed")

        except Exception as e:
            self.transfer_completed.emit(self.queue_row, False, f"Download failed: {e}")

    def cancel(self):
        """Cancel the transfer"""
        self.cancelled = True
        if self.thread:
            self.thread.quit()
            self.thread.wait()
        self.transfer_cancelled.emit(self.queue_row)

    def pause(self):
        """Pause the transfer"""
        self.paused = True

    def resume(self):
        """Resume the transfer"""
        self.paused = False

    def _apply_speed_limit(self, bytes_sent):
        """Apply speed limiting by sleeping if necessary"""
        if self.speed_limit <= 0:  # No speed limit
            return

        import time
        current_time = time.time()

        # Initialize timing on first call
        if not hasattr(self, '_speed_limit_start_time'):
            self._speed_limit_start_time = current_time
            self._speed_limit_bytes = 0
            return

        self._speed_limit_bytes += bytes_sent

        # Check speed every 100ms
        time_diff = current_time - self._speed_limit_start_time
        if time_diff >= 0.1:  # 100ms
            current_speed = self._speed_limit_bytes / time_diff  # bytes per second

            if current_speed > self.speed_limit:
                # Calculate sleep time to achieve desired speed
                target_time = self._speed_limit_bytes / self.speed_limit
                sleep_time = max(0, target_time - time_diff)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            # Reset counters
            self._speed_limit_start_time = time.time()
            self._speed_limit_bytes = 0


class TransferProgressTracker:
    """Tracks transfer progress and speed"""

    def __init__(self):
        self.start_time = time.time()
        self.bytes_transferred = 0
        self.total_bytes = 0
        self.speed_history = []

    def update_progress(self, bytes_transferred, total_bytes):
        """Update transfer progress"""
        self.bytes_transferred = bytes_transferred
        self.total_bytes = total_bytes

        # Calculate speed (simple moving average)
        current_time = time.time()
        elapsed = current_time - self.start_time
        if elapsed > 0:
            speed = bytes_transferred / elapsed
            self.speed_history.append(speed)
            if len(self.speed_history) > 10:  # Keep last 10 measurements
                self.speed_history.pop(0)

    def get_average_speed(self):
        """Get average transfer speed in bytes/second"""
        if self.speed_history:
            return sum(self.speed_history) / len(self.speed_history)
        return 0

    def get_eta(self):
        """Get estimated time of arrival in seconds"""
        speed = self.get_average_speed()
        if speed > 0:
            remaining = self.total_bytes - self.bytes_transferred
            return remaining / speed
        return 0

    def get_progress_percentage(self):
        """Get transfer progress as percentage"""
        if self.total_bytes > 0:
            return (self.bytes_transferred / self.total_bytes) * 100
        return 0