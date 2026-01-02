from PyQt6.QtWidgets import QToolBar, QLabel, QPushButton, QLineEdit, QSpinBox, QWidget
from PyQt6.QtCore import Qt

class ToolbarManager:
    """Manages the main window toolbar and quick connect bar"""
    def __init__(self, parent_window):
        self.parent = parent_window
        self.toolbar = None
        self.site_manager_btn = None
        self.quick_host = None
        self.quick_user = None
        self.quick_pass = None
        self.quick_port = None
        self.connect_btn = None
        self.disconnect_btn = None
        self.refresh_btn = None
    
    def create_toolbar(self):
        """Create and setup the toolbar"""
        self.toolbar = QToolBar("Main Toolbar", self.parent)
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.toolbar.setStyleSheet("") # Managed by ThemeManager
        self.parent.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        # Icon Manager
        from ..icon_themes import get_icon_theme_manager
        icons = get_icon_theme_manager()

        # Site Manager
        self.site_manager_btn = QPushButton("Site Manager")
        self.site_manager_btn.setMinimumHeight(24)
        self.site_manager_btn.setIcon(icons.get_icon("site_manager"))
        self.site_manager_btn.setToolTip("Open Site Manager")
        self.site_manager_btn.clicked.connect(self.parent.show_site_manager)
        self.toolbar.addWidget(self.site_manager_btn)

        self.toolbar.addSeparator()

        # Quick Connect Bar
        # Quick Connect Bar
        host_label = QLabel("Host:")
        self.toolbar.addWidget(host_label)

        self.quick_host = QLineEdit()
        self.quick_host.setMinimumWidth(100)
        self.quick_host.setMaximumWidth(140)
        self.quick_host.setMinimumHeight(22)
        self.quick_host.setPlaceholderText("Host")
        self.quick_host.returnPressed.connect(self.parent.quick_connect)
        self.toolbar.addWidget(self.quick_host)

        user_label = QLabel("User:")
        self.toolbar.addWidget(user_label)

        self.quick_user = QLineEdit()
        self.quick_user.setMinimumWidth(70)
        self.quick_user.setMaximumWidth(90)
        self.quick_user.setMinimumHeight(22)
        self.quick_user.setPlaceholderText("User")
        self.toolbar.addWidget(self.quick_user)

        pass_label = QLabel("Pass:")
        self.toolbar.addWidget(pass_label)

        self.quick_pass = QLineEdit()
        self.quick_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.quick_pass.setMinimumWidth(70)
        self.quick_pass.setMaximumWidth(90)
        self.quick_pass.setMinimumHeight(22)
        self.quick_pass.setPlaceholderText("Pass")
        self.toolbar.addWidget(self.quick_pass)

        port_label = QLabel("Port:")
        self.toolbar.addWidget(port_label)

        self.quick_port = QSpinBox()
        self.quick_port.setRange(1, 65535)
        self.quick_port.setValue(21)
        self.quick_port.setMinimumWidth(60) # Increased for better button spacing
        self.quick_port.setMinimumHeight(24)
        self.toolbar.addWidget(self.quick_port)

        self.connect_btn = QPushButton("Quickconnect")
        self.connect_btn.setMinimumHeight(24)
        self.connect_btn.setIcon(icons.get_icon("connect"))
        self.connect_btn.setToolTip("Quick Connect")
        self.connect_btn.clicked.connect(self.parent.quick_connect)
        self.toolbar.addWidget(self.connect_btn)
        
        self.toolbar.addSeparator()

        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setMinimumHeight(24)
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.setIcon(icons.get_icon("disconnect"))
        self.disconnect_btn.setToolTip("Disconnect")
        self.disconnect_btn.clicked.connect(self.parent.disconnect)
        self.toolbar.addWidget(self.disconnect_btn)

        # Refresh
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setMinimumHeight(24)
        self.refresh_btn.setIcon(icons.get_icon("refresh"))
        self.refresh_btn.setToolTip("Refresh")
        self.refresh_btn.clicked.connect(self.parent.refresh_files)
        self.toolbar.addWidget(self.refresh_btn)

        # spacer
        empty = QWidget()
        empty.setMinimumWidth(10)
        self.toolbar.addWidget(empty)
