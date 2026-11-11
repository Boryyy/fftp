"""
Enhanced status bar for Fftp with file counts, selection info, and connection status
"""

from PyQt6.QtWidgets import QStatusBar, QLabel, QProgressBar
from PyQt6.QtCore import Qt


class FftpStatusBar(QStatusBar):
    """Enhanced status bar with detailed file and connection information"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.connection_status = QLabel("Not connected")
        self.connection_status.setMinimumWidth(150)

        self.current_directory = QLabel("")
        self.current_directory.setMinimumWidth(200)

        self.file_info = QLabel("")
        self.file_info.setMinimumWidth(150)

        self.selection_info = QLabel("")
        self.selection_info.setMinimumWidth(150)

        self.transfer_progress = QProgressBar()
        self.transfer_progress.setVisible(False)
        self.transfer_progress.setMaximumWidth(200)
        self.transfer_progress.setMaximumHeight(16)

        self.addPermanentWidget(self.connection_status)
        self.addPermanentWidget(self.current_directory)
        self.addPermanentWidget(self.file_info)
        self.addPermanentWidget(self.selection_info)
        self.addPermanentWidget(self.transfer_progress)

        # No hardcoded styles - ThemeManager handles everything

        self.local_file_count = 0
        self.local_folder_count = 0
        self.local_total_size = 0
        self.remote_file_count = 0
        self.remote_folder_count = 0
        self.remote_total_size = 0

    def update_connection_status(self, status: str, connected: bool = False):
        """Update connection status display"""
        from .theme_manager import ThemeManager
        c = ThemeManager.COLORS
        color = c["success"] if connected else c["text_secondary"]
        self.connection_status.setText(status)
        self.connection_status.setStyleSheet(f"QLabel {{ color: {color}; font-weight: 600; font-size: 11px; }}")

    def update_local_directory_info(self, path: str, files_data: list):
        """Update local directory information"""
        self.current_directory.setText(path)

        file_count = sum(1 for f in files_data if not f.get('is_dir', False))
        folder_count = sum(1 for f in files_data if f.get('is_dir', False))
        total_size = sum(f.get('size', 0) for f in files_data if not f.get('is_dir', False))

        self.local_file_count = file_count
        self.local_folder_count = folder_count
        self.local_total_size = total_size

        self.file_info.setText(
            f"{file_count} files, {folder_count} dirs ({self._format_size(total_size)})"
        )

    def update_remote_directory_info(self, path: str, files_data: list):
        """Update remote directory information"""
        file_count = sum(1 for f in files_data if not f.get('is_dir', False))
        folder_count = sum(1 for f in files_data if f.get('is_dir', False))
        total_size = sum(f.get('size', 0) for f in files_data if not f.get('is_dir', False))

        self.remote_file_count = file_count
        self.remote_folder_count = folder_count
        self.remote_total_size = total_size

    def update_selection_info(self, selected_items, is_local=True):
        """Update selection information"""
        if not selected_items:
            self.selection_info.setText("")
            return

        count = len(selected_items)
        total_size = 0
        for item in selected_items:
            if hasattr(item, 'size'):
                total_size += item.size
            elif isinstance(item, dict):
                total_size += item.get('size', 0)

        if count == 1:
            name = ""
            if hasattr(selected_items[0], 'name'):
                name = selected_items[0].name
            elif isinstance(selected_items[0], dict):
                name = selected_items[0].get('name', '')
            self.selection_info.setText(f"Selected: {name} ({self._format_size(total_size)})")
        else:
            self.selection_info.setText(f"{count} items selected ({self._format_size(total_size)})")

    def update_transfer_progress(self, current: int, total: int, speed: str = ""):
        """Update transfer progress bar"""
        if total > 0:
            self.transfer_progress.setVisible(True)
            self.transfer_progress.setRange(0, total)
            self.transfer_progress.setValue(current)
            if speed:
                self.transfer_progress.setFormat(f"{speed} - %p%")
            else:
                self.transfer_progress.setFormat("%p%")
        else:
            self.transfer_progress.setVisible(False)

    def hide_transfer_progress(self):
        """Hide transfer progress"""
        self.transfer_progress.setVisible(False)

    def _format_size(self, size: int) -> str:
        """Format file size in human readable format"""
        if size == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def show_message(self, message: str, timeout: int = 0):
        """Show a temporary message in the status bar"""
        super().showMessage(message, timeout)

    def clear_message(self):
        """Clear any temporary message"""
        super().clearMessage()
