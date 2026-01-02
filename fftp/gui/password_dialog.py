"""
Password dialogs for master password
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt


class MasterPasswordDialog(QDialog):
    """Dialog for entering master password"""
    def __init__(self, parent=None, is_setup=False):
        super().__init__(parent)
        self.is_setup = is_setup
        self.password = None
        
        if is_setup:
            self.setWindowTitle("Set Master Password - Fftp")
        else:
            self.setWindowTitle("Enter Master Password - Fftp")
        
        self.setGeometry(300, 300, 400, 200)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        if self.is_setup:
            info_text = (
                "Set a master password to encrypt your saved connections.\n\n"
                "This password will be required to access saved connections.\n"
                "Make sure to remember it - it cannot be recovered!"
            )
        else:
            info_text = "Enter your master password to access saved connections."
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        password_layout = QVBoxLayout()
        password_layout.addWidget(QLabel("Master Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(30)
        self.password_input.returnPressed.connect(self.accept_password)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        if self.is_setup:
            confirm_layout = QVBoxLayout()
            confirm_layout.addWidget(QLabel("Confirm Password:"))
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_input.setMinimumHeight(30)
            self.confirm_input.returnPressed.connect(self.accept_password)
            confirm_layout.addWidget(self.confirm_input)
            layout.addLayout(confirm_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        if not self.is_setup:
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(self.reject)
            btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK" if not self.is_setup else "Set Password")
        ok_btn.clicked.connect(self.accept_password)
        ok_btn.setDefault(True)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
        self.password_input.setFocus()
    
    def accept_password(self):
        """Validate and accept password"""
        password = self.password_input.text()
        
        if not password:
            QMessageBox.warning(self, "Error", "Password cannot be empty")
            return
        
        if len(password) < 8:
            QMessageBox.warning(
                self, "Error",
                "Password must be at least 8 characters long"
            )
            return
        
        if self.is_setup:
            confirm = self.confirm_input.text()
            if password != confirm:
                QMessageBox.warning(
                    self, "Error",
                    "Passwords do not match"
                )
                return
        
        self.password = password
        self.accept()
    
    def get_password(self) -> str:
        """Get entered password"""
        return self.password
