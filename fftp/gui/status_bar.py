"""
Enhanced status bar for Fftp with file counts, selection info, and connection status
"""

from PyQt6.QtWidgets import QStatusBar, QLabel, QProgressBar, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path


class FftpStatusBar(QStatusBar):
    """Enhanced status bar with detailed file and connection information"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize status components
        self.connection_status = QLabel("Not connected")
        self.connection_status.setMinimumWidth(150)

        self.current_directory = QLabel("No directory selected")
        self.current_directory.setMinimumWidth(200)

        self.file_info = QLabel("No files")
        self.file_info.setMinimumWidth(150)

        self.selection_info = QLabel("No selection")
        self.selection_info.setMinimumWidth(150)

        self.transfer_progress = QProgressBar()
        self.transfer_progress.setVisible(False)
        self.transfer_progress.setMaximumWidth(200)
        self.transfer_progress.setMaximumHeight(16)

        # Add permanent widgets
        self.addPermanentWidget(self.connection_status)
        self.addPermanentWidget(self.current_directory)
        self.addPermanentWidget(self.file_info)
        self.addPermanentWidget(self.selection_info)
        self.addPermanentWidget(self.transfer_progress)

        # Set initial styles
        self._apply_styles()

        # Initialize data
        self.local_file_count = 0
        self.local_folder_count = 0
        self.local_total_size = 0
        self.remote_file_count = 0
        self.remote_folder_count = 0
        self.remote_total_size = 0

    def _apply_styles(self):
        """Apply simple styling to status bar components"""
        base_style = """
            QLabel {
                font-size: 10px;
                padding: 2px 8px;
                border-left: 1px solid #cccccc;
            }
        """

        self.connection_status.setStyleSheet(base_style + """
            QLabel {
                font-weight: bold;
            }
        """)

        self.current_directory.setStyleSheet(base_style)
        self.file_info.setStyleSheet(base_style)
        self.selection_info.setStyleSheet(base_style)

        self.transfer_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 2px;
                text-align: center;
                font-size: 9px;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
            }
        """)

    def update_connection_status(self, status: str, connected: bool = False):
        """Update connection status display"""
        self.connection_status.setText(status)
        if connected:
            self.connection_status.setStyleSheet("""
                QLabel {
                    color: #27ae60;
                    font-weight: 600;
                    font-size: 11px;
                    padding: 2px 6px;
                    border-left: 1px solid #bdc3c7;
                }
            """)
        else:
            self.connection_status.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-weight: 600;
                    font-size: 11px;
                    padding: 2px 6px;
                    border-left: 1px solid #bdc3c7;
                }
            """)

    def update_local_directory_info(self, path: str, files_data: list):
        """Update local directory information"""
        self.current_directory.setText(f"Local: {path}")

        # Count files and folders
        file_count = sum(1 for f in files_data if not f.get('is_dir', False))
        folder_count = sum(1 for f in files_data if f.get('is_dir', False))
        total_size = sum(f.get('size', 0) for f in files_data if not f.get('is_dir', False))

        self.local_file_count = file_count
        self.local_folder_count = folder_count
        self.local_total_size = total_size

        self._update_file_info_display()

    def update_remote_directory_info(self, path: str, files_data: list):
        """Update remote directory information"""
        # Count files and folders
        file_count = sum(1 for f in files_data if not getattr(f, 'is_dir', False))
        folder_count = sum(1 for f in files_data if getattr(f, 'is_dir', False))
        total_size = sum(getattr(f, 'size', 0) for f in files_data if not getattr(f, 'is_dir', False))

        self.remote_file_count = file_count
        self.remote_folder_count = folder_count
        self.remote_total_size = total_size

        self._update_file_info_display()

    def _update_file_info_display(self):
        """Update the file information display"""
        # Show local info by default, remote when connected
        if self.remote_file_count > 0 or self.remote_folder_count > 0:
            files = self.remote_file_count
            folders = self.remote_folder_count
            total_size = self.remote_total_size
            prefix = "Remote:"
        else:
            files = self.local_file_count
            folders = self.local_folder_count
            total_size = self.local_total_size
            prefix = "Local:"

        size_str = self._format_size(total_size)
        self.file_info.setText(f"{prefix} {files} files, {folders} folders ({size_str})")

    def update_selection_info(self, selected_files: list, is_local: bool = True):
        """Update selection information"""
        if not selected_files:
            self.selection_info.setText("No selection")
            return

        count = len(selected_files)
        total_size = sum(f.get('size', 0) if isinstance(f, dict) else getattr(f, 'size', 0)
                        for f in selected_files)

        size_str = self._format_size(total_size)
        location = "Local" if is_local else "Remote"
        self.selection_info.setText(f"{location}: {count} selected ({size_str})")

    def show_transfer_progress(self, current: int, total: int, filename: str = ""):
        """Show transfer progress in status bar"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.transfer_progress.setValue(percentage)
            self.transfer_progress.setFormat(f"{filename} ({percentage}%)")
            self.transfer_progress.setVisible(True)
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
                return ".1f"
            size /= 1024.0
        return ".1f"

    def show_message(self, message: str, timeout: int = 0):
        """Show a temporary message in the status bar"""
        super().showMessage(message, timeout)

    def clear_message(self):
        """Clear any temporary message"""
        super().clearMessage()