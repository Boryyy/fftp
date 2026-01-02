"""
Status Panel - Handles logging and status display
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit,
    QGroupBox, QTextEdit
)
from PyQt6.QtCore import Qt
from datetime import datetime


class StatusPanel(QWidget):
    """Panel for displaying logs and status information"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Initialize components
        self.message_log = None
        self.log_messages = []

        self.init_ui()

    def init_ui(self):
        """Initialize the status panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Status group
        status_group = QGroupBox("Message Log")
        status_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        status_layout = QVBoxLayout(status_group)
        status_layout.setContentsMargins(8, 8, 8, 8)

        # Message log
        self.message_log = QTextEdit()
        self.message_log.setReadOnly(True)
        self.message_log.setMinimumHeight(120)
        self.message_log.setMaximumHeight(200)
        # QTextEdit doesn't have setMaximumBlockCount, we'll manage history manually
        self.message_log.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                line-height: 1.4;
            }
        """)

        status_layout.addWidget(self.message_log)
        layout.addWidget(status_group)

    def log(self, message, level="info"):
        """Add a message to the log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "info": "[INFO]",
            "warning": "[WARN]",
            "error": "[ERROR]",
            "success": "[OK]",
            "debug": "[DEBUG]"
        }.get(level, "[INFO]")

        # Create HTML-formatted message for better display
        color = {
            "info": "#2c3e50",
            "warning": "#f39c12",
            "error": "#e74c3c",
            "success": "#27ae60",
            "debug": "#9b59b6"
        }.get(level, "#2c3e50")

        html_message = f'<span style="color: {color};">{timestamp} {prefix} {message}</span><br>'

        # Add to internal storage
        log_entry = f"{timestamp} {prefix} {message}"
        self.log_messages.append(log_entry)

        # Keep only last 500 messages
        if len(self.log_messages) > 500:
            self.log_messages = self.log_messages[-500:]

        # Update display
        if self.message_log:
            self.message_log.append(html_message)

            # Auto-scroll to bottom
            scrollbar = self.message_log.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        """Clear the message log"""
        self.log_messages.clear()
        if self.message_log:
            self.message_log.clear()

    def get_log_messages(self):
        """Get all log messages"""
        return self.log_messages.copy()

    def get_recent_messages(self, count=50):
        """Get the most recent log messages"""
        return self.log_messages[-count:] if len(self.log_messages) > count else self.log_messages.copy()

    def search_log(self, search_term):
        """Search log messages for a term"""
        return [msg for msg in self.log_messages if search_term.lower() in msg.lower()]

    def export_log(self, filepath):
        """Export log messages to a file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("Fftp Message Log\n")
                f.write("=" * 50 + "\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for message in self.log_messages:
                    f.write(message + "\n")
            return True
        except Exception as e:
            print(f"Failed to export log: {e}")
            return False