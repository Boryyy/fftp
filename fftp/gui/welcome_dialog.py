"""
Welcome dialog and first-time setup for Fftp
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWizard, QWizardPage, QLineEdit, QTextEdit, QCheckBox,
    QGroupBox, QRadioButton, QButtonGroup, QMessageBox,
    QFileDialog, QProgressBar, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont


class WelcomeWizard(QWizard):
    """Welcome wizard for first-time Fftp users"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Fftp - FTP/SFTP Client")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setOption(QWizard.WizardOption.NoCancelButton, False)
        self.setOption(QWizard.WizardOption.NoDefaultButton, False)

        # Set up pages
        self.addPage(WelcomePage())
        self.addPage(SetupPage())
        self.addPage(ThemePage())
        self.addPage(FeaturesPage())
        self.addPage(CompletePage())

        # Set window properties
        self.setFixedSize(600, 500)
        self.setPixmap(QWizard.WizardPixmap.LogoPixmap, QPixmap())  # Could add logo here

    def accept(self):
        """Called when wizard is completed"""
        # Save first-time setup completion
        settings_file = Path.home() / ".fftp" / "settings.json"
        settings_file.parent.mkdir(exist_ok=True)

        # Load existing settings
        settings = {}
        if settings_file.exists():
            try:
                import json
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            except:
                pass

        # Mark setup as completed
        settings['first_time_setup_completed'] = True

        # Save setup choices
        setup_page = self.page(1)  # SetupPage
        if hasattr(setup_page, 'get_settings'):
            setup_settings = setup_page.get_settings()
            settings.update(setup_settings)

        theme_page = self.page(2)  # ThemePage
        if hasattr(theme_page, 'get_settings'):
            theme_settings = theme_page.get_settings()
            settings.update(theme_settings)

        # Save settings
        try:
            import json
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Settings Error",
                              f"Failed to save settings: {e}")

        super().accept()


class WelcomePage(QWizardPage):
    """Welcome page with introduction"""

    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to Fftp!")
        self.setSubTitle("Your professional FTP/SFTP client is ready to use")

        layout = QVBoxLayout(self)

        # Welcome message
        welcome_label = QLabel("Welcome to Fftp!")
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)

        # Logo or icon (placeholder)
        logo_label = QLabel("🚀")
        logo_label.setFont(QFont("Arial", 48))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("color: #3498db; margin: 20px;")
        layout.addWidget(logo_label)

        # Description
        desc_label = QLabel(
            "Fftp is a powerful and secure FTP/SFTP client designed for professionals. "
            "This setup wizard will help you configure the application for your needs."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        # Features list
        features_group = QGroupBox("Key Features")
        features_layout = QVBoxLayout()

        features = [
            "✓ Dual-pane file management",
            "✓ Secure FTP/SFTP connections",
            "✓ Drag & drop file transfers",
            "✓ Advanced search and filtering",
            "✓ Directory comparison",
            "✓ Bookmarks and quick access",
            "✓ Remote file editing",
            "✓ Transfer queue management"
        ]

        for feature in features:
            feature_label = QLabel(feature)
            features_layout.addWidget(feature_label)

        features_group.setLayout(features_layout)
        layout.addWidget(features_group)

        layout.addStretch()


class SetupPage(QWizardPage):
    """Setup page for basic configuration"""

    def __init__(self):
        super().__init__()
        self.setTitle("Basic Setup")
        self.setSubTitle("Configure your default settings")

        layout = QVBoxLayout(self)

        # Default local directory
        local_group = QGroupBox("Default Local Directory")
        local_layout = QVBoxLayout()

        self.local_path_edit = QLineEdit()
        self.local_path_edit.setText(str(Path.home()))
        self.local_path_edit.setPlaceholderText("Enter default local directory path")
        local_layout.addWidget(self.local_path_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_local_path)
        local_layout.addWidget(browse_btn)

        local_group.setLayout(local_layout)
        layout.addWidget(local_group)

        # Connection settings
        conn_group = QGroupBox("Connection Preferences")
        conn_layout = QVBoxLayout()

        self.passive_mode_check = QCheckBox("Use passive mode for FTP connections")
        self.passive_mode_check.setChecked(True)
        self.passive_mode_check.setToolTip("Passive mode is recommended for most networks")
        conn_layout.addWidget(self.passive_mode_check)

        self.auto_reconnect_check = QCheckBox("Automatically reconnect on connection loss")
        self.auto_reconnect_check.setChecked(True)
        conn_layout.addWidget(self.auto_reconnect_check)

        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # Transfer settings
        transfer_group = QGroupBox("Transfer Settings")
        transfer_layout = QVBoxLayout()

        self.confirm_delete_check = QCheckBox("Confirm before deleting files")
        self.confirm_delete_check.setChecked(True)
        transfer_layout.addWidget(self.confirm_delete_check)

        self.show_progress_check = QCheckBox("Show transfer progress")
        self.show_progress_check.setChecked(True)
        transfer_layout.addWidget(self.show_progress_check)

        transfer_group.setLayout(transfer_layout)
        layout.addWidget(transfer_group)

        layout.addStretch()

    def browse_local_path(self):
        """Browse for local directory"""
        path = QFileDialog.getExistingDirectory(self, "Select Default Local Directory",
                                              self.local_path_edit.text())
        if path:
            self.local_path_edit.setText(path)

    def get_settings(self):
        """Get settings from this page"""
        return {
            'default_local_path': self.local_path_edit.text(),
            'default_passive': self.passive_mode_check.isChecked(),
            'auto_reconnect': self.auto_reconnect_check.isChecked(),
            'confirm_delete': self.confirm_delete_check.isChecked(),
            'show_progress': self.show_progress_check.isChecked(),
        }


class ThemePage(QWizardPage):
    """Theme selection page"""

    def __init__(self):
        super().__init__()
        self.setTitle("Choose Your Theme")
        self.setSubTitle("Select the visual appearance of Fftp")

        layout = QVBoxLayout(self)

        # Theme description
        theme_desc = QLabel(
            "Choose a theme that suits your preference. You can change this later in Settings."
        )
        theme_desc.setWordWrap(True)
        layout.addWidget(theme_desc)

        # Theme selection
        theme_group = QGroupBox("Application Theme")
        theme_layout = QVBoxLayout()

        self.theme_group = QButtonGroup(self)

        # Light theme
        light_radio = QRadioButton("Light Theme - Clean and bright interface")
        light_radio.setChecked(True)
        self.theme_group.addButton(light_radio, 0)
        theme_layout.addWidget(light_radio)

        # Dark theme
        dark_radio = QRadioButton("Dark Theme - Easy on the eyes in low light")
        self.theme_group.addButton(dark_radio, 1)
        theme_layout.addWidget(dark_radio)

        # System theme
        system_radio = QRadioButton("System Theme - Follow your system settings")
        self.theme_group.addButton(system_radio, 2)
        theme_layout.addWidget(system_radio)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Icon theme
        icon_group = QGroupBox("Icon Theme")
        icon_layout = QVBoxLayout()

        icon_desc = QLabel("Choose how file type icons are displayed:")
        icon_layout.addWidget(icon_desc)

        self.icon_theme_combo = QComboBox()
        from .icon_themes import get_icon_theme_manager
        icon_theme_manager = get_icon_theme_manager()
        self.icon_theme_combo.addItems(icon_theme_manager.get_available_themes())
        self.icon_theme_combo.setCurrentText("Default")
        icon_layout.addWidget(self.icon_theme_combo)

        icon_group.setLayout(icon_layout)
        layout.addWidget(icon_group)

        layout.addStretch()

    def get_settings(self):
        """Get theme settings"""
        theme_map = {0: "Light", 1: "Dark", 2: "System"}
        selected_theme = theme_map.get(self.theme_group.checkedId(), "Light")

        return {
            'theme': selected_theme,
            'icon_theme': self.icon_theme_combo.currentText(),
            'auto_theme': (self.theme_group.checkedId() == 2)
        }


class FeaturesPage(QWizardPage):
    """Features introduction page"""

    def __init__(self):
        super().__init__()
        self.setTitle("Discover Fftp Features")
        self.setSubTitle("Learn about the powerful features available to you")

        layout = QVBoxLayout(self)

        # Feature overview
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setPlainText("""
Fftp offers a comprehensive set of features for professional file management:

🔐 SECURITY
• Master password protection for saved connections
• Encrypted storage of sensitive data
• Secure FTP/SFTP protocol support

📁 FILE MANAGEMENT
• Dual-pane interface for easy file comparison
• Drag & drop between local and remote systems
• Advanced search and filtering capabilities
• Remote file editing with built-in text editor

⚡ PERFORMANCE
• Multi-threaded file transfers
• Transfer speed limiting and queue management
• Connection health monitoring and auto-reconnect
• Directory synchronization and comparison

🎨 CUSTOMIZATION
• Multiple themes and icon sets
• Customizable keyboard shortcuts
• Bookmarks for quick directory access
• Extensive settings for personalization

🛠️ ADVANCED FEATURES
• Directory comparison and synchronization
• Transfer queue with priority management
• Comprehensive logging and error reporting
• Plugin-ready architecture for extensions

Get started by connecting to your first server using the Site Manager!
        """)

        features_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f9f9f9;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                line-height: 1.4;
            }
        """)

        layout.addWidget(features_text)

        # Quick start tips
        tips_group = QGroupBox("Quick Start Tips")
        tips_layout = QVBoxLayout()

        tips = [
            "• Use Ctrl+T to open a new connection tab",
            "• Press F5 to refresh file listings",
            "• Use Ctrl+F to search for files",
            "• Drag files between panes for quick transfers",
            "• Right-click files for context menu options"
        ]

        for tip in tips:
            tip_label = QLabel(tip)
            tip_label.setStyleSheet("font-size: 11px;")
            tips_layout.addWidget(tip_label)

        tips_group.setLayout(tips_layout)
        layout.addWidget(tips_group)


class CompletePage(QWizardPage):
    """Setup completion page"""

    def __init__(self):
        super().__init__()
        self.setTitle("Setup Complete!")
        self.setSubTitle("You're all set to start using Fftp")

        layout = QVBoxLayout(self)

        # Success message
        success_label = QLabel("✅ Setup Complete!")
        success_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_label.setStyleSheet("color: #27ae60; margin: 20px;")
        layout.addWidget(success_label)

        # Completion message
        complete_text = QLabel(
            "Fftp has been configured with your preferences. You can now start transferring files!\n\n"
            "To get started:\n"
            "1. Click 'Site Manager' to add your first FTP/SFTP server\n"
            "2. Use the quick connect fields for immediate connections\n"
            "3. Explore the menus for advanced features\n\n"
            "Need help? Press F1 or visit the Help menu."
        )
        complete_text.setWordWrap(True)
        complete_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(complete_text)

        # Launch options
        launch_group = QGroupBox("Launch Options")
        launch_layout = QVBoxLayout()

        self.site_manager_check = QCheckBox("Open Site Manager after setup")
        self.site_manager_check.setChecked(True)
        launch_layout.addWidget(self.site_manager_check)

        self.show_shortcuts_check = QCheckBox("Show keyboard shortcuts reference")
        launch_layout.addWidget(self.show_shortcuts_check)

        launch_group.setLayout(launch_layout)
        layout.addWidget(launch_group)

        layout.addStretch()

    def get_settings(self):
        """Get completion settings"""
        return {
            'open_site_manager': self.site_manager_check.isChecked(),
            'show_shortcuts': self.show_shortcuts_check.isChecked(),
        }


def show_welcome_dialog_if_needed(parent):
    """Show welcome dialog if this is the first time running Fftp"""
    settings_file = Path.home() / ".fftp" / "settings.json"

    # Check if setup has been completed
    if settings_file.exists():
        try:
            import json
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                if settings.get('first_time_setup_completed', False):
                    return  # Setup already completed
        except:
            pass  # If we can't read settings, show setup anyway

    # Show welcome wizard
    wizard = WelcomeWizard(parent)
    result = wizard.exec()

    if result == QDialog.DialogCode.Accepted:
        # Setup completed successfully
        completion_settings = wizard.page(4).get_settings()  # CompletePage

        # Handle launch options
        if completion_settings.get('open_site_manager', True):
            QTimer.singleShot(100, lambda: parent.show_site_manager())

        if completion_settings.get('show_shortcuts', False):
            QTimer.singleShot(200, lambda: parent.show_keyboard_shortcuts())

        QMessageBox.information(
            parent, "Welcome to Fftp!",
            "Setup completed successfully! Fftp is ready to use.\n\n"
            "Use the Site Manager to add your FTP/SFTP servers and start transferring files."
        )


def show_welcome_dialog(parent):
    """Show welcome dialog regardless of setup status"""
    wizard = WelcomeWizard(parent)
    return wizard.exec()