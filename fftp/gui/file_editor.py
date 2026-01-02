"""
Remote file editor for Fftp - allows viewing and editing remote text files
"""

from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QMessageBox, QProgressBar, QFileDialog, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor


class FileDownloadWorker(QThread):
    """Worker thread for downloading files"""
    finished = pyqtSignal(str, bool, str)  # content, success, error_message
    progress = pyqtSignal(int)  # progress percentage

    def __init__(self, manager, remote_path: str):
        super().__init__()
        self.manager = manager
        self.remote_path = remote_path

    def run(self):
        try:
            # Create a temporary local file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as temp_file:
                temp_path = temp_file.name

            # Download the file
            success, message = self.manager.download_file(self.remote_path, temp_path)

            if success:
                # Read the content
                try:
                    with open(temp_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    self.finished.emit(content, True, "")
                except UnicodeDecodeError:
                    # Try binary mode for non-text files
                    try:
                        with open(temp_path, 'rb') as f:
                            content = f.read().decode('latin-1', errors='replace')
                        self.finished.emit(content, True, "")
                    except Exception as e:
                        self.finished.emit("", False, f"Cannot display file as text: {e}")
                finally:
                    # Clean up temp file
                    try:
                        Path(temp_path).unlink()
                    except:
                        pass
            else:
                self.finished.emit("", False, message)

        except Exception as e:
            self.finished.emit("", False, str(e))


class FileUploadWorker(QThread):
    """Worker thread for uploading edited files"""
    finished = pyqtSignal(bool, str)  # success, error_message

    def __init__(self, manager, remote_path: str, content: str):
        super().__init__()
        self.manager = manager
        self.remote_path = remote_path
        self.content = content

    def run(self):
        try:
            import tempfile

            # Create a temporary local file with the content
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp_file:
                temp_file.write(self.content)
                temp_path = temp_file.name

            try:
                # Upload the file
                success, message = self.manager.upload_file(temp_path, self.remote_path)
                self.finished.emit(success, message if not success else "")
            finally:
                # Clean up temp file
                try:
                    Path(temp_path).unlink()
                except:
                    pass

        except Exception as e:
            self.finished.emit(False, str(e))


class RemoteFileEditor(QDialog):
    """Dialog for editing remote text files"""

    def __init__(self, manager, remote_path: str, file_name: str, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.remote_path = remote_path
        self.file_name = file_name
        self.original_content = ""
        self.is_modified = False

        self.setWindowTitle(f"Edit Remote File - {file_name}")
        self.setGeometry(200, 200, 800, 600)
        self.init_ui()

        # Start downloading the file
        self.download_file()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # File info
        info_layout = QHBoxLayout()
        info_label = QLabel(f"Editing: {self.remote_path}")
        info_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        info_layout.addWidget(info_label)

        info_layout.addStretch()

        # Character/Line count
        self.stats_label = QLabel("Lines: 0 | Characters: 0")
        info_layout.addWidget(self.stats_label)

        layout.addLayout(info_layout)

        # Text editor
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_edit.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.text_edit)

        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_file)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)

        self.save_as_btn = QPushButton("Save As...")
        self.save_as_btn.clicked.connect(self.save_as)
        button_layout.addWidget(self.save_as_btn)

        button_layout.addStretch()

        self.reload_btn = QPushButton("Reload")
        self.reload_btn.clicked.connect(self.reload_file)
        button_layout.addWidget(self.reload_btn)

        cancel_btn = QPushButton("Close")
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Set up syntax highlighting for common file types
        self.setup_syntax_highlighting()

    def setup_syntax_highlighting(self):
        """Set up basic syntax highlighting based on file extension"""
        ext = Path(self.file_name).suffix.lower()

        if ext in ['.py', '.js', '.java', '.cpp', '.c', '.h', '.php']:
            # Basic code highlighting
            self.text_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #f8f8f8;
                    color: #2c3e50;
                    selection-background-color: #3498db;
                }
            """)
        elif ext in ['.txt', '.md', '.log']:
            # Plain text
            self.text_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #ffffff;
                    color: #2c3e50;
                    selection-background-color: #3498db;
                }
            """)
        elif ext in ['.xml', '.html', '.css', '.json']:
            # Markup/Web files
            self.text_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #f9f9f9;
                    color: #2c3e50;
                    selection-background-color: #3498db;
                }
            """)

    def download_file(self):
        """Download the remote file"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.text_edit.setEnabled(False)
        self.save_btn.setEnabled(False)

        self.download_worker = FileDownloadWorker(self.manager, self.remote_path)
        self.download_worker.finished.connect(self.on_download_finished)
        self.download_worker.progress.connect(self.progress_bar.setValue)
        self.download_worker.start()

    def on_download_finished(self, content: str, success: bool, error: str):
        """Handle download completion"""
        self.progress_bar.setVisible(False)
        self.text_edit.setEnabled(True)

        if success:
            self.original_content = content
            self.text_edit.setPlainText(content)
            self.is_modified = False
            self.update_stats()
            self.save_btn.setEnabled(False)
        else:
            QMessageBox.critical(self, "Download Error",
                               f"Failed to download file:\n{error}")
            self.reject()

    def on_text_changed(self):
        """Handle text changes"""
        self.is_modified = self.text_edit.toPlainText() != self.original_content
        self.save_btn.setEnabled(self.is_modified)
        self.update_stats()

    def update_stats(self):
        """Update line and character count"""
        text = self.text_edit.toPlainText()
        lines = text.count('\n') + 1
        chars = len(text)
        self.stats_label.setText(f"Lines: {lines} | Characters: {chars}")

    def save_file(self):
        """Save the file back to the remote server"""
        if not self.is_modified:
            return

        content = self.text_edit.toPlainText()

        # Confirm save
        reply = QMessageBox.question(
            self, "Confirm Save",
            "Save changes to remote file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.text_edit.setEnabled(False)
        self.save_btn.setEnabled(False)

        self.upload_worker = FileUploadWorker(self.manager, self.remote_path, content)
        self.upload_worker.finished.connect(self.on_upload_finished)
        self.upload_worker.start()

    def on_upload_finished(self, success: bool, error: str):
        """Handle upload completion"""
        self.progress_bar.setVisible(False)
        self.text_edit.setEnabled(True)

        if success:
            self.original_content = self.text_edit.toPlainText()
            self.is_modified = False
            self.save_btn.setEnabled(False)
            QMessageBox.information(self, "Success", "File saved successfully!")
        else:
            QMessageBox.critical(self, "Upload Error", f"Failed to save file:\n{error}")
            self.save_btn.setEnabled(True)

    def save_as(self):
        """Save the file with a different name"""
        new_name, ok = QFileDialog.getSaveFileName(
            self, "Save As", self.file_name,
            "All Files (*.*)"
        )

        if ok and new_name:
            content = self.text_edit.toPlainText()

            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)

            self.upload_worker = FileUploadWorker(self.manager, new_name, content)
            self.upload_worker.finished.connect(self.on_save_as_finished)
            self.upload_worker.start()

    def on_save_as_finished(self, success: bool, error: str):
        """Handle save as completion"""
        self.progress_bar.setVisible(False)

        if success:
            QMessageBox.information(self, "Success", f"File saved as {self.file_name}!")
        else:
            QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{error}")

    def reload_file(self):
        """Reload the file from server"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Reload anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.download_file()

    def closeEvent(self, event):
        """Handle dialog close"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Close without saving?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                self.save_file()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def edit_remote_file(manager, remote_path: str, file_name: str, parent=None) -> bool:
    """
    Open a remote file for editing

    Args:
        manager: FTP/SFTP manager instance
        remote_path: Path to the remote file
        file_name: Display name for the file
        parent: Parent widget

    Returns:
        bool: True if file was opened for editing
    """
    # Check if it's a text file (by extension)
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.java', '.cpp', '.c', '.h', '.php',
        '.html', '.css', '.xml', '.json', '.yaml', '.yml', '.ini', '.cfg',
        '.conf', '.log', '.sh', '.bat', '.ps1', '.sql', '.csv'
    }

    file_ext = Path(file_name).suffix.lower()

    if file_ext in text_extensions or not file_ext:
        # Open in editor
        editor = RemoteFileEditor(manager, remote_path, file_name, parent)
        editor.exec()
        return True
    else:
        # Show message for non-text files
        QMessageBox.information(
            parent, "File Type Not Supported",
            f"Cannot edit binary file: {file_name}\n\n"
            "Only text files can be edited remotely."
        )
        return False