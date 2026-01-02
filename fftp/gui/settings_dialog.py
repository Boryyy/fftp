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
        self.setGeometry(300, 300, 700, 650)
        self.settings = self.load_settings()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.setSpacing(15)
        
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
        
        transfer_group = QGroupBox("Transfer Settings")
        # The 'Transfer Settings' group from the General tab is being removed
        # as its contents are now managed in the 'Advanced' tab under 'Transfer & Performance'.
        # This ensures consistency and avoids duplication of settings.
        # The following lines are commented out to remove the group from the General tab.
        # transfer_group = QGroupBox("Transfer Settings")
        # transfer_layout = QFormLayout()
        
        # self.buffer_size_spin = QSpinBox()
        # self.buffer_size_spin.setRange(1024, 10485760)
        # self.buffer_size_spin.setValue(self.settings.get('buffer_size', 8192))
        # self.buffer_size_spin.setSuffix(" bytes")
        # transfer_layout.addRow("Buffer Size:", self.buffer_size_spin)
        
        # self.max_concurrent_spin = QSpinBox()
        # self.max_concurrent_spin.setRange(1, 10)
        # self.max_concurrent_spin.setValue(self.settings.get('max_concurrent_transfers', 3))
        # transfer_layout.addRow("Max Concurrent Transfers:", self.max_concurrent_spin)
        
        # self.auto_retry_check = QCheckBox("Auto-retry Failed Transfers")
        # self.auto_retry_check.setChecked(self.settings.get('auto_retry', True))
        # transfer_layout.addRow(self.auto_retry_check)
        
        # self.show_progress_check = QCheckBox("Show Transfer Progress")
        # self.show_progress_check.setChecked(self.settings.get('show_progress', True))
        # transfer_layout.addRow(self.show_progress_check)
        
        # self.drag_drop_check = QCheckBox("Enable Drag-and-Drop from File System")
        # self.drag_drop_check.setChecked(self.settings.get('enable_drag_drop', True))
        # transfer_layout.addRow(self.drag_drop_check)
        
        # self.confirm_delete_check = QCheckBox("Confirm Before Deleting Files")
        # self.confirm_delete_check.setChecked(self.settings.get('confirm_delete', True))
        # transfer_layout.addRow(self.confirm_delete_check)
        
        # transfer_group.setLayout(transfer_layout)
        # general_layout.addWidget(transfer_group) # Removed duplicated transfer group from General tab
        
        interface_group = QGroupBox("Interface Settings")
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
        
        self.table_alternating_check = QCheckBox("Alternating Row Colors in Tables")
        self.table_alternating_check.setChecked(self.settings.get('table_alternating', True))
        interface_layout.addRow(self.table_alternating_check)
        
        interface_group.setLayout(interface_layout)
        general_layout.addWidget(interface_group)
        
        general_layout.addStretch()
        tabs.addTab(general_tab, "General")
        
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        appearance_layout.setSpacing(15)
        
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light"]) # Removed Dark and System for a clean look
        self.theme_combo.setCurrentText("Light")
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
        self.font_size_spin.setValue(self.settings.get('font_size', 10))
        font_layout.addRow("Font Size:", self.font_size_spin)
        
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["System Default", "Arial", "Segoe UI", "Consolas", "Courier New"])
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

        self.icon_theme_combo = QComboBox()
        from .icon_themes import get_icon_theme_manager
        icon_theme_manager = get_icon_theme_manager()
        self.icon_theme_combo.addItems(icon_theme_manager.get_available_themes())
        current_theme = self.settings.get('icon_theme', 'Default')
        if current_theme in icon_theme_manager.get_available_themes():
            self.icon_theme_combo.setCurrentText(current_theme)
        table_layout.addRow("Icon Theme:", self.icon_theme_combo)
        
        table_group.setLayout(table_layout)
        appearance_layout.addWidget(table_group)
        
        appearance_layout.addStretch()
        tabs.addTab(appearance_tab, "Appearance")
        
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)
        security_layout.setSpacing(15)
        
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
        
        # Logging settings removed - logging is always enabled
        
        security_layout.addStretch()
        tabs.addTab(security_tab, "Security")
        
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_layout.setSpacing(15)
        
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
        
        performance_group = QGroupBox("Performance")
        performance_form = QFormLayout()
        
        self.prefetch_check = QCheckBox("Prefetch Directory Listings")
        self.prefetch_check.setChecked(self.settings.get('prefetch', True))
        performance_form.addRow(self.prefetch_check)
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setValue(self.settings.get('cache_size', 100))
        self.cache_size_spin.setSuffix(" items")
        performance_form.addRow("Directory Cache Size:", self.cache_size_spin)
        
        performance_group.setLayout(performance_form)
        advanced_layout.addWidget(performance_group)

        perf_transfer_group = QGroupBox("Transfer & Performance")
        perf_transfer_form = QFormLayout()

        self.max_concurrent_transfers_spin = QSpinBox()
        self.max_concurrent_transfers_spin.setRange(1, 100)
        self.max_concurrent_transfers_spin.setValue(self.settings.get('max_concurrent_transfers', 10))
        perf_transfer_form.addRow("Max Concurrent Transfers:", self.max_concurrent_transfers_spin)

        self.speed_limit_check = QCheckBox("Enable Speed Limit")
        self.speed_limit_check.setChecked(self.settings.get('speed_limit_enabled', False))
        perf_transfer_form.addRow(self.speed_limit_check)

        self.speed_limit_spin = QSpinBox()
        self.speed_limit_spin.setRange(1, 100000)
        self.speed_limit_spin.setValue(self.settings.get('speed_limit', 1000))
        self.speed_limit_spin.setSuffix(" KB/s")
        self.speed_limit_spin.setEnabled(self.speed_limit_check.isChecked())
        self.speed_limit_check.toggled.connect(self.speed_limit_spin.setEnabled)
        perf_transfer_form.addRow("Speed Limit:", self.speed_limit_spin)

        self.buffer_size_spin = QSpinBox()
        self.buffer_size_spin.setRange(8192, 10485760)
        self.buffer_size_spin.setValue(self.settings.get('buffer_size', 65536))
        self.buffer_size_spin.setSuffix(" bytes")
        perf_transfer_form.addRow("Buffer Size:", self.buffer_size_spin)

        self.auto_resume_transfers_check = QCheckBox("Auto-resume interrupted transfers")
        self.auto_resume_transfers_check.setChecked(self.settings.get('auto_resume_transfers', True))
        perf_transfer_form.addRow(self.auto_resume_transfers_check)

        perf_transfer_group.setLayout(perf_transfer_form)
        advanced_layout.addWidget(perf_transfer_group)

        advanced_layout.addStretch()
        tabs.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(tabs)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
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
    
    def save_settings(self):
        """Save settings to file"""
        settings_file = Path.home() / ".fftp" / "settings.json"
        settings_file.parent.mkdir(exist_ok=True)
        
        settings = {
            'default_local_path': self.local_path_edit.text(),
            'connection_timeout': self.timeout_spin.value(),
            'retry_count': self.retry_spin.value(),
            'default_passive': self.passive_check.isChecked(),
            'buffer_size': self.buffer_size_spin.value(),
            'max_concurrent_transfers': self.max_concurrent_transfers_spin.value(),
            'auto_retry': self.auto_retry_check.isChecked() if hasattr(self, 'auto_retry_check') else True,
            'show_progress': self.show_progress_check.isChecked() if hasattr(self, 'show_progress_check') else True,
            'enable_drag_drop': self.drag_drop_check.isChecked() if hasattr(self, 'drag_drop_check') else True,
            'confirm_delete': self.confirm_delete_check.isChecked() if hasattr(self, 'confirm_delete_check') else True,
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
            'auto_resume_transfers': self.auto_resume_transfers_check.isChecked()
        }

        try:
            import json
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
            return False
    
    def get_settings(self) -> dict:
        """Get current settings"""
        return {
            'icon_theme': self.icon_theme_combo.currentText(),
            'default_local_path': self.local_path_edit.text(),
            'connection_timeout': self.timeout_spin.value(),
            'retry_count': self.retry_spin.value(),
            'default_passive': self.passive_check.isChecked(),
            'buffer_size': self.buffer_size_spin.value(),
            'max_concurrent_transfers': self.max_concurrent_transfers_spin.value(),
            'auto_retry': self.auto_retry_check.isChecked() if hasattr(self, 'auto_retry_check') else True,
            'show_progress': self.show_progress_check.isChecked() if hasattr(self, 'show_progress_check') else True,
            'enable_drag_drop': self.drag_drop_check.isChecked() if hasattr(self, 'drag_drop_check') else True,
            'confirm_delete': self.confirm_delete_check.isChecked() if hasattr(self, 'confirm_delete_check') else True,
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
            'auto_resume_transfers': self.auto_resume_transfers_check.isChecked()
        }
    
    def accept(self):
        """Save settings and close"""
        if self.save_settings():
            super().accept()
