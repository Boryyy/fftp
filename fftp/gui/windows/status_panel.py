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
        """Initialize the status panel UI - Reconstructed for Minimalism"""
        # Status area layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Message log - Using QTextEdit for HTML color support
        self.message_log = QTextEdit()
        self.message_log.setReadOnly(True)
        self.message_log.setAcceptRichText(True)
        
        self.message_log.setStyleSheet(f"""
            QTextEdit {{
                background-color: #fcfcfc;
                border: none;
                border-bottom: 1px solid #d1d1d1;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                color: #202124;
                padding: 4px;
            }}
        """)
        
        layout.addWidget(self.message_log)

    def log(self, message, level="info"):
        """Add a message to the log display"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{level.upper()}]"
        
        color = {
            "info": "#202124",
            "error": "#d93025",
            "success": "#1e8e3e",
            "debug": "#5f6368"
        }.get(level, "#202124")

        html_message = f'<span style="color: {color};">{timestamp} {prefix} {message}</span>'

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
            QMessageBox.critical(parent, "Export Error", f"Failed to export log: {str(e)}")
            return False