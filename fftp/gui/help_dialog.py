"""
Help and About Dialog
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QPushButton, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from pathlib import Path


class HelpDialog(QDialog):
    """Help and About dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help - Fftp")
        self.setGeometry(300, 300, 700, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.setSpacing(20)
        
        logo_path = Path(__file__).parent.parent / "logo.png"
        if logo_path.exists():
            logo_label = QLabel()
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            about_layout.addWidget(logo_label)
        
        title_label = QLabel("Fftp")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(title_label)
        
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(version_label)
        
        desc_label = QLabel(
            "A modern, cross-platform FTP/SFTP client\n"
            "Built with Python and PyQt6"
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        about_layout.addWidget(desc_label)
        
        about_layout.addStretch()
        
        copyright_label = QLabel("© 2024 Fftp. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(copyright_label)
        
        tabs.addTab(about_tab, "About")
        
        help_tab = QWidget()
        help_layout = QVBoxLayout(help_tab)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>Getting Started</h2>
        <h3>Quick Connect</h3>
        <p>Use the toolbar to quickly connect to a server:</p>
        <ul>
            <li>Enter the hostname or IP address</li>
            <li>Enter your username and password</li>
            <li>Set the port (22 for SFTP, 21 for FTP)</li>
            <li>Click "Connect"</li>
        </ul>
        
        <h3>Site Manager</h3>
        <p>Save and manage multiple connections:</p>
        <ul>
            <li>Click "Site Manager" in the toolbar</li>
            <li>Click "New Site" to create a connection</li>
            <li>Fill in connection details</li>
            <li>Click "Save" to save (master password required)</li>
            <li>Click "Connect" to connect to selected server</li>
        </ul>
        
        <h2>File Operations</h2>
        <h3>Upload Files</h3>
        <ul>
            <li>Right-click a local file → "Upload"</li>
            <li>Or drag and drop files to remote panel</li>
        </ul>
        
        <h3>Download Files</h3>
        <ul>
            <li>Right-click a remote file → "Download"</li>
            <li>Files are saved to current local directory</li>
        </ul>
        
        <h3>Delete Files</h3>
        <ul>
            <li>Right-click a remote file → "Delete"</li>
            <li>Confirm deletion in the dialog</li>
        </ul>
        
        <h3>Create Directory</h3>
        <ul>
            <li>Right-click in remote panel → "Create Directory"</li>
            <li>Enter directory name</li>
        </ul>
        
        <h2>Navigation</h2>
        <ul>
            <li>Double-click folders to open them</li>
            <li>Click "↑" button to go to parent directory</li>
            <li>Type path in path bar and press Enter</li>
        </ul>
        
        <h2>Security</h2>
        <h3>Master Password</h3>
        <p>When saving connections, you'll be prompted for a master password:</p>
        <ul>
            <li>First time: Create a master password (min 8 characters)</li>
            <li>Subsequent saves: Enter your master password</li>
            <li>All saved connections are encrypted</li>
        </ul>
        
        <h2>Keyboard Shortcuts</h2>
        <ul>
            <li><b>F5</b> - Refresh file lists</li>
            <li><b>Ctrl+O</b> - Open Site Manager</li>
            <li><b>Ctrl+S</b> - Settings</li>
            <li><b>F1</b> - Help</li>
        </ul>
        """)
        help_layout.addWidget(help_text)
        
        tabs.addTab(help_tab, "Help")
        
        layout.addWidget(tabs)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
