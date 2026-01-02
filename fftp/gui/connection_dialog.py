"""
Connection Manager Dialog
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QWidget,
    QLabel, QListWidget, QPushButton, QLineEdit, QSpinBox,
    QComboBox, QCheckBox, QFormLayout, QMessageBox, QTreeWidget,
    QTreeWidgetItem, QTabWidget, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ..models import ConnectionConfig


class ConnectionManagerDialog(QDialog):
    """Connection manager dialog"""
    def __init__(self, parent=None, connections=None, master_password=None, encryption_manager=None):
        super().__init__(parent)
        self.connections = connections or []
        self.master_password = master_password
        self.encryption_manager = encryption_manager
        self.selected_config = None
        self.setWindowTitle("Site Manager - Fftp")
        self.setGeometry(200, 200, 600, 500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Sites and Bookmarks:"))

        self.site_tree = QTreeWidget()
        self.site_tree.setHeaderHidden(True)
        self.site_tree.setRootIsDecorated(True)
        self.site_tree.setAnimated(True)
        self.site_tree.setIndentation(15)

        # Add root items
        self.sites_root = QTreeWidgetItem(self.site_tree)
        self.sites_root.setText(0, "My Sites")
        self.sites_root.setIcon(0, QIcon("folder.png"))

        self.bookmarks_root = QTreeWidgetItem(self.site_tree)
        self.bookmarks_root.setText(0, "Global Bookmarks")
        self.bookmarks_root.setIcon(0, QIcon("folder.png"))

        # Populate sites
        for conn in self.connections:
            if isinstance(conn, dict):
                name = conn.get('name', 'Unnamed')
            else:
                name = getattr(conn, 'name', 'Unnamed')

            site_item = QTreeWidgetItem(self.sites_root)
            site_item.setText(0, name)
            site_item.setIcon(0, QIcon("server.png"))
            site_item.setData(0, Qt.ItemDataRole.UserRole, conn)

        self.site_tree.expandAll()
        self.site_tree.currentItemChanged.connect(self.on_site_selected)
        left_layout.addWidget(self.site_tree)
        
        btn_layout = QHBoxLayout()
        self.new_site_btn = QPushButton("New Site")
        self.new_site_btn.clicked.connect(self.new_site)
        self.new_folder_btn = QPushButton("New Folder")
        self.new_folder_btn.clicked.connect(self.new_folder)
        self.rename_btn = QPushButton("Rename")
        self.rename_btn.clicked.connect(self.rename_item)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_site)

        btn_layout.addWidget(self.new_site_btn)
        btn_layout.addWidget(self.new_folder_btn)
        btn_layout.addWidget(self.rename_btn)
        btn_layout.addWidget(self.delete_btn)
        left_layout.addLayout(btn_layout)
        
        splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Settings tabs like FileZilla
        self.settings_tabs = QTabWidget()

        # General tab
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)

        self.name_input = QLineEdit()
        self.host_input = QLineEdit()
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(22)
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["SFTP", "FTP", "FTPS"])
        self.protocol_combo.currentTextChanged.connect(self.on_protocol_changed)
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        general_layout.addRow("Site Name:", self.name_input)
        general_layout.addRow("Host:", self.host_input)
        general_layout.addRow("Port:", self.port_input)
        general_layout.addRow("Protocol:", self.protocol_combo)
        general_layout.addRow("User:", self.user_input)
        general_layout.addRow("Password:", self.pass_input)

        self.settings_tabs.addTab(general_tab, "General")

        # Advanced tab
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)

        # Connection settings
        conn_group = QGroupBox("Connection")
        conn_form = QFormLayout(conn_group)

        self.passive_check = QCheckBox("Passive mode")
        self.passive_check.setChecked(True)
        conn_form.addRow(self.passive_check)

        self.limit_connections_check = QCheckBox("Limit number of simultaneous connections")
        self.limit_connections_spin = QSpinBox()
        self.limit_connections_spin.setRange(1, 10)
        self.limit_connections_spin.setValue(2)
        self.limit_connections_spin.setEnabled(False)
        self.limit_connections_check.toggled.connect(self.limit_connections_spin.setEnabled)

        conn_form.addRow(self.limit_connections_check)
        conn_form.addRow("Maximum connections:", self.limit_connections_spin)

        advanced_layout.addWidget(conn_group)

        # Transfer settings
        transfer_group = QGroupBox("Transfer Settings")
        transfer_form = QFormLayout(transfer_group)

        self.preserve_timestamp_check = QCheckBox("Preserve timestamps of transferred files")
        self.preserve_timestamp_check.setChecked(True)
        transfer_form.addRow(self.preserve_timestamp_check)

        advanced_layout.addWidget(transfer_group)

        # Encryption settings (for FTP/FTPS)
        encryption_group = QGroupBox("Encryption")
        encryption_form = QFormLayout(encryption_group)

        self.ssl_check = QCheckBox("Use explicit FTP over TLS if available")
        self.ssl_check.setChecked(False)
        encryption_form.addRow(self.ssl_check)

        self.ssl_implicit_check = QCheckBox("Implicit FTP over TLS")
        self.ssl_implicit_check.setChecked(False)
        self.ssl_implicit_check.setEnabled(False)
        self.ssl_check.toggled.connect(lambda checked: self.ssl_implicit_check.setEnabled(checked))
        encryption_form.addRow(self.ssl_implicit_check)

        advanced_layout.addWidget(encryption_group)

        advanced_layout.addStretch()
        self.settings_tabs.addTab(advanced_tab, "Advanced")

        right_layout.addWidget(self.settings_tabs)
        
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        btn_box = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_current_connection)
        btn_box.addWidget(self.save_btn)
        
        btn_box.addStretch()
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(self.connect_btn)
        btn_box.addWidget(self.cancel_btn)
        layout.addLayout(btn_box)
    
    def save_current_connection(self):
        """Save current connection settings"""
        if not all([self.name_input.text(), self.host_input.text(), 
                   self.user_input.text(), self.pass_input.text()]):
            QMessageBox.warning(self, "Error", "Please fill in all required fields")
            return
        
        config = self.get_config()
        if config:
            current = self.site_tree.currentItem()
            if current and current.data(0, Qt.ItemDataRole.UserRole):
                # Update existing site
                current.setText(0, config.name)
                current.setData(0, Qt.ItemDataRole.UserRole, {
                    'name': config.name,
                    'host': config.host,
                    'port': config.port,
                    'username': config.username,
                    'password': config.password,
                    'protocol': config.protocol,
                    'use_passive': config.use_passive,
                    'use_ssl': getattr(config, 'use_ssl', False),
                    'ssl_implicit': getattr(config, 'ssl_implicit', False)
                })
                # Update in connections list
                for i, conn in enumerate(self.connections):
                    if conn == self.selected_config:
                        self.connections[i] = current.data(0, Qt.ItemDataRole.UserRole)
                        break
            else:
                # Add new site
                self.add_connection_to_tree(config)

            QMessageBox.information(self, "Success", "Connection saved successfully")
            self.save_connections()

    def add_connection_to_tree(self, config):
        """Add a new connection to the tree"""
        site_item = QTreeWidgetItem(self.sites_root)
        site_item.setText(0, config.name)
        site_item.setIcon(0, QIcon("server.png"))
        site_item.setData(0, Qt.ItemDataRole.UserRole, {
            'name': config.name,
            'host': config.host,
            'port': config.port,
            'username': config.username,
            'password': config.password,
            'protocol': config.protocol,
            'use_passive': config.use_passive,
            'use_ssl': getattr(config, 'use_ssl', False),
            'ssl_implicit': getattr(config, 'ssl_implicit', False)
        })
        self.sites_root.setExpanded(True)
        self.site_tree.setCurrentItem(site_item)
    
    def on_protocol_changed(self, text):
        if text == "SFTP":
            self.port_input.setValue(22)
            self.ssl_check.setEnabled(False)
            self.ssl_check.setChecked(False)
        elif text == "FTPS":
            self.port_input.setValue(990)
            self.ssl_check.setEnabled(True)
            self.ssl_check.setChecked(True)
        else:
            self.port_input.setValue(21)
            self.ssl_check.setEnabled(True)
            self.ssl_check.setChecked(False)
    
    def on_site_selected(self, current, previous):
        """Handle site selection in tree"""
        if current:
            data = current.data(0, Qt.ItemDataRole.UserRole)
            if data:  # It's a site item
                self.selected_config = data
                self.load_connection_details(data)
            else:  # It's a folder or root item
                self.selected_config = None
                self.clear_connection_details()

    def load_connection_details(self, conn):
        """Load connection details into the form"""
        if isinstance(conn, dict):
            self.name_input.setText(conn.get('name', ''))
            self.host_input.setText(conn.get('host', ''))
            self.port_input.setValue(conn.get('port', 22))
            protocol = conn.get('protocol', 'sftp').upper()
            if protocol == 'ftps':
                self.protocol_combo.setCurrentText("FTPS")
            elif protocol == 'sftp':
                self.protocol_combo.setCurrentText("SFTP")
            else:
                self.protocol_combo.setCurrentText("FTP")
            self.user_input.setText(conn.get('username', ''))
            self.pass_input.setText(conn.get('password', ''))
            self.passive_check.setChecked(conn.get('use_passive', True))
            self.ssl_check.setChecked(conn.get('use_ssl', False))
            self.ssl_implicit_check.setChecked(conn.get('ssl_implicit', False))
        else:
            # Handle ConnectionConfig object
            self.name_input.setText(getattr(conn, 'name', ''))
            self.host_input.setText(getattr(conn, 'host', ''))
            self.port_input.setValue(getattr(conn, 'port', 22))
            protocol = getattr(conn, 'protocol', 'sftp').upper()
            if protocol == 'FTPS':
                self.protocol_combo.setCurrentText("FTPS")
            elif protocol == 'SFTP':
                self.protocol_combo.setCurrentText("SFTP")
            else:
                self.protocol_combo.setCurrentText("FTP")
            self.user_input.setText(getattr(conn, 'username', ''))
            self.pass_input.setText(getattr(conn, 'password', ''))
            self.passive_check.setChecked(getattr(conn, 'use_passive', True))
            self.ssl_check.setChecked(getattr(conn, 'use_ssl', False))
            self.ssl_implicit_check.setChecked(getattr(conn, 'ssl_implicit', False))

    def clear_connection_details(self):
        """Clear all connection detail fields"""
        self.name_input.clear()
        self.host_input.clear()
        self.port_input.setValue(22)
        self.protocol_combo.setCurrentText("SFTP")
        self.user_input.clear()
        self.pass_input.clear()
        self.passive_check.setChecked(True)
        self.ssl_check.setChecked(False)
        self.ssl_implicit_check.setChecked(False)

    def new_folder(self):
        """Create a new folder in the site tree"""
        current = self.site_tree.currentItem()
        if current:
            folder_name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
            if ok and folder_name:
                folder_item = QTreeWidgetItem(current)
                folder_item.setText(0, folder_name)
                folder_item.setIcon(0, QIcon("folder.png"))
                current.setExpanded(True)

    def rename_item(self):
        """Rename selected item"""
        current = self.site_tree.currentItem()
        if current and current != self.sites_root and current != self.bookmarks_root:
            old_name = current.text(0)
            new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=old_name)
            if ok and new_name and new_name != old_name:
                current.setText(0, new_name)
                # Update the connection data if it's a site
                if current.data(0, Qt.ItemDataRole.UserRole):
                    if isinstance(current.data(0, Qt.ItemDataRole.UserRole), dict):
                        current.data(0, Qt.ItemDataRole.UserRole)['name'] = new_name
                    else:
                        current.data(0, Qt.ItemDataRole.UserRole).name = new_name

    def new_site(self):
        """Create a new site"""
        # Clear the form for new site
        self.clear_connection_details()
        self.selected_config = None

        # Set focus to name field
        self.name_input.setFocus()
    
    def edit_site(self):
        pass
    
    def delete_site(self):
        row = self.conn_list.currentRow()
        if row >= 0:
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete this connection?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                current = self.site_tree.currentItem()
                if current and current.parent():  # Not a root item
                    # Remove from tree
                    parent = current.parent()
                    parent.removeChild(current)

                    # Remove from connections list
                    data = current.data(0, Qt.ItemDataRole.UserRole)
                    if data in self.connections:
                        self.connections.remove(data)
                        self.save_connections()
    
    def save_connections(self):
        """Save connections with encryption"""
        from .password_dialog import MasterPasswordDialog
        
        password = self.master_password
        if not password:
            if not self.encryption_manager.has_master_password():
                dialog = MasterPasswordDialog(self.parent(), is_setup=True)
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    QMessageBox.warning(self, "Error", "Master password is required to save connections")
                    return
                password = dialog.get_password()
                if password:
                    if self.encryption_manager.set_master_password(password):
                        self.master_password = password
                        if hasattr(self.parent(), 'master_password'):
                            self.parent().master_password = password
                    else:
                        QMessageBox.critical(self, "Error", "Failed to set master password")
                        return
                else:
                    return
            else:
                dialog = MasterPasswordDialog(self.parent(), is_setup=False)
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    QMessageBox.warning(self, "Error", "Master password is required to save connections")
                    return
                password = dialog.get_password()
                if password and self.encryption_manager.verify_master_password(password):
                    self.master_password = password
                    if hasattr(self.parent(), 'master_password'):
                        self.parent().master_password = password
                else:
                    QMessageBox.warning(self, "Error", "Incorrect master password")
                    return
        
        if self.encryption_manager and password:
            conn_dicts = []
            for conn in self.connections:
                if isinstance(conn, dict):
                    conn_dicts.append(conn)
                else:
                    conn_dicts.append({
                        'name': getattr(conn, 'name', ''),
                        'host': getattr(conn, 'host', ''),
                        'port': getattr(conn, 'port', 22),
                        'username': getattr(conn, 'username', ''),
                        'password': getattr(conn, 'password', ''),
                        'protocol': getattr(conn, 'protocol', 'sftp'),
                        'use_passive': getattr(conn, 'use_passive', True),
                        'use_ssl': getattr(conn, 'use_ssl', False),
                        'ssl_implicit': getattr(conn, 'ssl_implicit', False)
                    })
            
            if self.encryption_manager.encrypt_connections(conn_dicts, password):
                QMessageBox.information(self, "Success", "Connections saved and encrypted successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to save connections")
    
    def add_connection(self, config: ConnectionConfig):
        """Add a new connection"""
        conn_dict = {
            'name': config.name,
            'host': config.host,
            'port': config.port,
            'username': config.username,
            'password': config.password,
            'protocol': config.protocol,
            'use_passive': config.use_passive,
            'use_ssl': getattr(config, 'use_ssl', False),
            'ssl_implicit': getattr(config, 'ssl_implicit', False)
        }
        self.connections.append(conn_dict)
        # Add to tree instead of list
        self.add_connection_to_tree(config)
        self.save_connections()
    
    def get_config(self) -> Optional[ConnectionConfig]:
        """Get connection config from dialog"""
        if not all([self.name_input.text(), self.host_input.text(), 
                   self.user_input.text(), self.pass_input.text()]):
            return None
        
        protocol = self.protocol_combo.currentText().lower()
        use_ssl = self.ssl_check.isChecked() or protocol == "ftps"
        return ConnectionConfig(
            name=self.name_input.text(),
            host=self.host_input.text(),
            port=self.port_input.value(),
            username=self.user_input.text(),
            password=self.pass_input.text(),
            protocol=protocol,
            use_passive=self.passive_check.isChecked(),
            use_ssl=use_ssl,
            ssl_implicit=self.ssl_implicit_check.isChecked()
        )
