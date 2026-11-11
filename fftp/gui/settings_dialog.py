"""
Settings Dialog
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QPushButton, QLineEdit, QSpinBox, QCheckBox,
    QFormLayout, QGroupBox, QComboBox, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from pathlib import Path


class SettingsDialog(QDialog):
    """Application settings dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - Fftp")
        self.setMinimumSize(600, 550)
        # No hardcoded stylesheet - ThemeManager handles it
        self.settings = self.load_settings()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        tabs = QTabWidget()

        # === General Tab ===
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.setSpacing(12)

        paths_group = QGroupBox("Default Paths")
        paths_layout = QFormLayout()
        self.local_path_edit = QLineEdit()
        self.local_path_edit.setText(self.settings.get('default_local_path', str(Path.home())))
        browse_local_btn = QPushButton("Browse...")
        browse_local_btn.clicked.connect(lambda: self.browse_path(self.local_path_edit))
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.local_path_edit)
        path_layout.addWidget(browse_local_btn)
        paths_layout.addRow("Default Local Path:", path_layout)
        paths_group.setLayout(paths_layout)
        general_layout.addWidget(paths_group)

        conn_group = QGroupBox("Connection Settings")
        conn_layout = QFormLayout()
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(self.settings.get('connection_timeout', 30))
        self.timeout_spin.setSuffix(" seconds")
        conn_layout.addRow("Connection Timeout:", self.timeout_spin)

        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(0, 10)
        self.retry_spin.setValue(self.settings.get('retry_count', 3))
        conn_layout.addRow("Retry Count:", self.retry_spin)

        self.passive_check = QCheckBox("Use Passive Mode by Default")
        self.passive_check.setChecked(self.settings.get('default_passive', True))
        conn_layout.addRow(self.passive_check)
        conn_group.setLayout(conn_layout)
        general_layout.addWidget(conn_group)

        interface_group = QGroupBox("Interface")
        interface_layout = QFormLayout()
        self.show_toolbar_check = QCheckBox("Show Toolbar")
        self.show_toolbar_check.setChecked(self.settings.get('show_toolbar', True))
        interface_layout.addRow(self.show_toolbar_check)
        self.show_statusbar_check = QCheckBox("Show Status Bar")
        self.show_statusbar_check.setChecked(self.settings.get('show_statusbar', True))
        interface_layout.addRow(self.show_statusbar_check)
        self.show_log_panel_check = QCheckBox("Show Activity Log Panel")
        self.show_log_panel_check.setChecked(self.settings.get('show_log_panel', True))
        interface_layout.addRow(self.show_log_panel_check)
        self.show_queue_panel_check = QCheckBox("Show Transfer Queue Panel")
        self.show_queue_panel_check.setChecked(self.settings.get('show_queue_panel', True))
        interface_layout.addRow(self.show_queue_panel_check)
        self.table_alternating_check = QCheckBox("Alternating Row Colors")
        self.table_alternating_check.setChecked(self.settings.get('table_alternating', True))
        interface_layout.addRow(self.table_alternating_check)
        interface_group.setLayout(interface_layout)
        general_layout.addWidget(interface_group)

        general_layout.addStretch()
        tabs.addTab(general_tab, "General")

        # === Appearance Tab ===
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        appearance_layout.setSpacing(12)

        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText(self.settings.get('theme', 'Dark'))
        theme_layout.addRow("Theme:", self.theme_combo)

        self.auto_theme_check = QCheckBox("Auto-detect System Theme")
        self.auto_theme_check.setChecked(self.settings.get('auto_theme', False))
        theme_layout.addRow(self.auto_theme_check)
        theme_group.setLayout(theme_layout)
        appearance_layout.addWidget(theme_group)

        font_group = QGroupBox("Font")
        font_layout = QFormLayout()
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        self.font_size_spin.setValue(self.settings.get('font_size', 12))
        font_layout.addRow("Font Size:", self.font_size_spin)
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["System Default", "Segoe UI", "Inter", "Arial", "Consolas"])
        font_family = self.settings.get('font_family', 'System Default')
        if font_family in [self.font_family_combo.itemText(i) for i in range(self.font_family_combo.count())]:
            self.font_family_combo.setCurrentText(font_family)
        font_layout.addRow("Font Family:", self.font_family_combo)
        font_group.setLayout(font_layout)
        appearance_layout.addWidget(font_group)

        table_group = QGroupBox("Table Display")
        table_layout = QFormLayout()
        self.table_row_height_spin = QSpinBox()
        self.table_row_height_spin.setRange(20, 50)
        self.table_row_height_spin.setValue(self.settings.get('table_row_height', 24))
        table_layout.addRow("Row Height:", self.table_row_height_spin)
        self.show_file_icons_check = QCheckBox("Show File Type Icons")
        self.show_file_icons_check.setChecked(self.settings.get('show_file_icons', True))
        table_layout.addRow(self.show_file_icons_check)
        table_group.setLayout(table_layout)
        appearance_layout.addWidget(table_group)

        appearance_layout.addStretch()
        tabs.addTab(appearance_tab, "Appearance")

        # === Security Tab ===
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)
        security_layout.setSpacing(12)

        security_group = QGroupBox("Security")
        security_form = QFormLayout()
        self.auto_lock_check = QCheckBox("Auto-lock after inactivity")
        self.auto_lock_check.setChecked(self.settings.get('auto_lock', False))
        security_form.addRow(self.auto_lock_check)
        self.lock_timeout_spin = QSpinBox()
        self.lock_timeout_spin.setRange(1, 60)
        self.lock_timeout_spin.setValue(self.settings.get('lock_timeout', 15))
        self.lock_timeout_spin.setSuffix(" minutes")
        security_form.addRow("Lock Timeout:", self.lock_timeout_spin)
        self.clear_password_on_disconnect_check = QCheckBox("Clear Password on Disconnect")
        self.clear_password_on_disconnect_check.setChecked(self.settings.get('clear_password_on_disconnect', True))
        security_form.addRow(self.clear_password_on_disconnect_check)
        self.remember_master_password_check = QCheckBox("Remember Master Password (Session Only)")
        self.remember_master_password_check.setChecked(self.settings.get('remember_master_password', False))
        security_form.addRow(self.remember_master_password_check)
        security_group.setLayout(security_form)
        security_layout.addWidget(security_group)
        security_layout.addStretch()
        tabs.addTab(security_tab, "Security")

        # === Advanced Tab ===
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_layout.setSpacing(12)

        connection_advanced_group = QGroupBox("Advanced Connection")
        connection_advanced_form = QFormLayout()
        self.keep_alive_check = QCheckBox("Enable Keep-Alive")
        self.keep_alive_check.setChecked(self.settings.get('keep_alive', True))
        connection_advanced_form.addRow(self.keep_alive_check)
        self.keep_alive_interval_spin = QSpinBox()
        self.keep_alive_interval_spin.setRange(10, 300)
        self.keep_alive_interval_spin.setValue(self.settings.get('keep_alive_interval', 30))
        self.keep_alive_interval_spin.setSuffix(" seconds")
        connection_advanced_form.addRow("Keep-Alive Interval:", self.keep_alive_interval_spin)
        self.compression_check = QCheckBox("Enable Compression (SFTP)")
        self.compression_check.setChecked(self.settings.get('compression', False))
        connection_advanced_form.addRow(self.compression_check)
        connection_advanced_group.setLayout(connection_advanced_form)
        advanced_layout.addWidget(connection_advanced_group)

        perf_group = QGroupBox("Transfer & Performance")
        perf_form = QFormLayout()
        self.max_concurrent_transfers_spin = QSpinBox()
        self.max_concurrent_transfers_spin.setRange(1, 100)
        self.max_concurrent_transfers_spin.setValue(self.settings.get('max_concurrent_transfers', 10))
        perf_form.addRow("Max Concurrent Transfers:", self.max_concurrent_transfers_spin)

        self.speed_limit_check = QCheckBox("Enable Speed Limit")
        self.speed_limit_check.setChecked(self.settings.get('speed_limit_enabled', False))
        perf_form.addRow(self.speed_limit_check)
        self.speed_limit_spin = QSpinBox()
        self.speed_limit_spin.setRange(1, 100000)
        self.speed_limit_spin.setValue(self.settings.get('speed_limit', 1000))
        self.speed_limit_spin.setSuffix(" KB/s")
        self.speed_limit_spin.setEnabled(self.speed_limit_check.isChecked())
        self.speed_limit_check.toggled.connect(self.speed_limit_spin.setEnabled)
        perf_form.addRow("Speed Limit:", self.speed_limit_spin)

        self.buffer_size_spin = QSpinBox()
        self.buffer_size_spin.setRange(8192, 10485760)
        self.buffer_size_spin.setValue(self.settings.get('buffer_size', 65536))
        self.buffer_size_spin.setSuffix(" bytes")
        perf_form.addRow("Buffer Size:", self.buffer_size_spin)

        self.prefetch_check = QCheckBox("Prefetch Directory Listings")
        self.prefetch_check.setChecked(self.settings.get('prefetch', True))
        perf_form.addRow(self.prefetch_check)

        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setValue(self.settings.get('cache_size', 100))
        self.cache_size_spin.setSuffix(" items")
        perf_form.addRow("Directory Cache Size:", self.cache_size_spin)

        self.auto_resume_transfers_check = QCheckBox("Auto-resume interrupted transfers")
        self.auto_resume_transfers_check.setChecked(self.settings.get('auto_resume_transfers', True))
        perf_form.addRow(self.auto_resume_transfers_check)

        perf_group.setLayout(perf_form)
        advanced_layout.addWidget(perf_group)

        advanced_layout.addStretch()
        tabs.addTab(advanced_tab, "Advanced")

        layout.addWidget(tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("Save")
        ok_btn.setProperty("primary", True)
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def browse_path(self, line_edit):
        """Browse for directory"""
        path = QFileDialog.getExistingDirectory(self, "Select Directory", line_edit.text())
        if path:
            line_edit.setText(path)

    def load_settings(self) -> dict:
        """Load settings from file"""
        settings_file = Path.home() / ".fftp" / "settings.json"
        if settings_file.exists():
            try:
                import json
                with open(settings_file) as f:
                    return json.load(f)
            except:
                pass
        return {}

    def get_settings(self) -> dict:
        """Get current settings"""
        return {
            'default_local_path': self.local_path_edit.text(),
            'connection_timeout': self.timeout_spin.value(),
            'retry_count': self.retry_spin.value(),
            'default_passive': self.passive_check.isChecked(),
            'buffer_size': self.buffer_size_spin.value(),
            'max_concurrent_transfers': self.max_concurrent_transfers_spin.value(),
            'show_toolbar': self.show_toolbar_check.isChecked(),
            'show_statusbar': self.show_statusbar_check.isChecked(),
            'show_log_panel': self.show_log_panel_check.isChecked(),
            'show_queue_panel': self.show_queue_panel_check.isChecked(),
            'table_alternating': self.table_alternating_check.isChecked(),
            'theme': self.theme_combo.currentText(),
            'auto_theme': self.auto_theme_check.isChecked(),
            'font_size': self.font_size_spin.value(),
            'font_family': self.font_family_combo.currentText(),
            'table_row_height': self.table_row_height_spin.value(),
            'show_file_icons': self.show_file_icons_check.isChecked(),
            'auto_lock': self.auto_lock_check.isChecked(),
            'lock_timeout': self.lock_timeout_spin.value(),
            'clear_password_on_disconnect': self.clear_password_on_disconnect_check.isChecked(),
            'remember_master_password': self.remember_master_password_check.isChecked(),
            'keep_alive': self.keep_alive_check.isChecked(),
            'keep_alive_interval': self.keep_alive_interval_spin.value(),
            'compression': self.compression_check.isChecked(),
            'prefetch': self.prefetch_check.isChecked(),
            'cache_size': self.cache_size_spin.value(),
            'speed_limit_enabled': self.speed_limit_check.isChecked(),
            'speed_limit': self.speed_limit_spin.value(),
            'auto_resume_transfers': self.auto_resume_transfers_check.isChecked(),
        }

    def save_settings(self):
        """Save settings to file"""
        settings_file = Path.home() / ".fftp" / "settings.json"
        settings_file.parent.mkdir(exist_ok=True)
        settings = self.get_settings()
        try:
            import json
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
            return False

    def accept(self):
        """Save settings and close"""
        if self.save_settings():
            super().accept()
