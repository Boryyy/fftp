"""
Main application window
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QComboBox, QSpinBox, QMessageBox, QMenu, QInputDialog,
    QToolBar, QStatusBar, QDialog, QMenuBar, QTabWidget, QTextEdit,
    QPlainTextEdit, QCheckBox, QTreeView, QFormLayout
)
from PyQt6.QtCore import Qt, QSize, QUrl, QThread, pyqtSignal, QDir, QTimer
from PyQt6.QtGui import QAction, QIcon, QPixmap, QFileSystemModel, QColor

from ..models import ConnectionConfig
from ..managers import SFTPManager, FTPManager
from ..crypto import EncryptionManager
from .connection_dialog import ConnectionManagerDialog
from .password_dialog import MasterPasswordDialog
from .settings_dialog import SettingsDialog
from .help_dialog import HelpDialog
from .themes import PREMIUM_LIGHT_THEME, PREMIUM_DARK_THEME
from .connection_worker import ConnectionWorker
from .logger import setup_file_logging
from .table_managers import load_local_files_to_table, load_remote_files_to_table, format_size, NumericTableWidgetItem
from .file_operations import (
    upload_file, download_file, delete_remote_file, create_remote_folder,
    rename_remote_file, delete_local_file, open_local_file
)
from .connection_handler import connect_to_server, handle_connection_finished, disconnect as disconnect_handler
from .context_menus import ContextMenuManager
from .status_bar import FftpStatusBar
from .bookmarks import BookmarkManager, show_bookmark_dialog
from .file_editor import edit_remote_file
from .icon_themes import get_icon_theme_manager
from .keyboard_shortcuts import KeyboardShortcutsManager
from .welcome_dialog import show_welcome_dialog_if_needed
from .drag_drop_table import DragDropTableWidget
from .connection_tab import ConnectionTab
from .transfer_engine import TransferEngine
from .search_dialog import SearchDialog
from .filter_manager import FilterManager
from .comparison import ComparisonManager


class FTPClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fftp - FTP/SFTP Client")
        self.setGeometry(100, 100, 1400, 900)
        
        self.set_window_icon()
        
        self.manager = None
        self.current_remote_path = "."
        self.current_local_path = str(Path.home())
        self.config = None
        self.transfer_queue = []
        self.connection_worker = None
        
        self.encryption_manager = EncryptionManager()
        self.master_password = None
        
        self.connections = []
        self.log_messages = []
        self.settings = self.load_settings()
        self.connection_tabs = {}
        self.active_tab_id = None

        # Transfer engine system
        self.transfer_engines = []  # List of active transfer engines
        self.max_concurrent_transfers = 2  # Default concurrent transfers
        self.auto_process_queue = True  # Auto-start transfers
        self.transfer_speed_limit = 0  # 0 = unlimited

        # Filter system
        self.filter_manager = FilterManager()
        self.filter_manager.create_default_filters()

        # Comparison system
        self.comparison_manager = ComparisonManager(self)

        # Synchronized browsing
        self.synchronized_browsing = False

        # Context menu manager
        self.context_menu_manager = ContextMenuManager(self)

        # Bookmark manager
        self.bookmark_manager = BookmarkManager()

        # Keyboard shortcuts manager
        self.keyboard_shortcuts = KeyboardShortcutsManager(self)

        # Icon theme manager (lazy initialized)
        self.icon_theme_manager = get_icon_theme_manager()

        self.setup_file_logging()

        self.init_ui()

        # Show welcome dialog for first-time users
        QTimer.singleShot(500, lambda: show_welcome_dialog_if_needed(self))
        self.create_menu_bar()
        # Load and apply theme from settings
        settings = self.load_settings()
        theme = settings.get('theme', 'Light')
        auto_theme = settings.get('auto_theme', False)

        if auto_theme:
            # Try to detect system theme
            try:
                import darkdetect
                if darkdetect.isDark():
                    theme = 'Dark'
                else:
                    theme = 'Light'
            except ImportError:
                # darkdetect not available, use saved theme
                pass

        self.apply_theme(theme)
        self.apply_global_theme()
        
        if hasattr(self, 'log_text'):
            self.log("Application started")
    
    def setup_file_logging(self):
        """Setup persistent file logging to ~/.fftp/logs/"""
        self.file_logger = setup_file_logging()
    
    def set_window_icon(self):
        """Set window icon from logo"""
        logo_path = Path(__file__).parent.parent / "logo.png"
        if logo_path.exists():
            icon = QIcon(str(logo_path))
            self.setWindowIcon(icon)
            try:
                import ctypes
                myappid = 'fftp.ftp.client.1.0'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except:
                pass
    
    def init_ui(self):
        """Build GUI layout"""
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        
        site_manager_btn = QPushButton("Site Manager")
        site_manager_btn.setMinimumHeight(34)
        site_manager_btn.setMinimumWidth(130)
        site_manager_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                font-weight: 600;
                padding: 8px 18px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
                border-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #bdc3c7;
            }
        """)
        site_manager_btn.clicked.connect(self.show_site_manager)
        toolbar.addWidget(site_manager_btn)
        
        toolbar.addSeparator()
        
        connect_widget = QWidget()
        connect_layout = QHBoxLayout(connect_widget)
        connect_layout.setContentsMargins(0, 0, 0, 0)
        connect_layout.setSpacing(5)
        
        host_label = QLabel("Host:")
        host_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 12px; padding: 0px 4px;")
        connect_layout.addWidget(host_label)
        self.quick_connect_combo = QComboBox()
        self.quick_connect_combo.setEditable(True)
        self.quick_connect_combo.setMinimumWidth(200)
        self.quick_connect_combo.setMinimumHeight(34)
        self.quick_connect_combo.lineEdit().setPlaceholderText("Enter hostname")
        self.quick_connect_combo.lineEdit().returnPressed.connect(self.quick_connect)
        # Ensure consistent styling and text visibility
        self.quick_connect_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 2px 8px;
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #2c3e50;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #bdc3c7;
                selection-background-color: #3498db;
                selection-color: #ffffff;
                background-color: #ffffff;
                color: #2c3e50;
            }
        """)
        connect_layout.addWidget(self.quick_connect_combo)

        user_label = QLabel("User:")
        user_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 12px; padding: 0px 4px;")
        connect_layout.addWidget(user_label)
        self.quick_user = QLineEdit()
        self.quick_user.setPlaceholderText("Username")
        self.quick_user.setMinimumWidth(120)
        self.quick_user.setMinimumHeight(34)
        connect_layout.addWidget(self.quick_user)

        pass_label = QLabel("Pass:")
        pass_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 12px; padding: 0px 4px;")
        connect_layout.addWidget(pass_label)
        self.quick_pass = QLineEdit()
        self.quick_pass.setPlaceholderText("Password")
        self.quick_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.quick_pass.setMinimumWidth(120)
        self.quick_pass.setMinimumHeight(34)
        connect_layout.addWidget(self.quick_pass)

        port_label = QLabel("Port:")
        port_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 12px; padding: 0px 4px;")
        connect_layout.addWidget(port_label)
        self.quick_port = QSpinBox()
        self.quick_port.setRange(1, 65535)
        self.quick_port.setValue(21)
        self.quick_port.setMinimumWidth(80)
        self.quick_port.setMinimumHeight(34)
        # Hide the spin box buttons to make it look cleaner
        self.quick_port.setStyleSheet("""
            QSpinBox {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 2px 8px;
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 12px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0px;
                border: none;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                width: 0px;
                height: 0px;
                border: none;
            }
        """)
        connect_layout.addWidget(self.quick_port)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setMinimumHeight(34)
        self.connect_btn.setMinimumWidth(110)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                font-weight: 600;
                padding: 9px 20px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.connect_btn.clicked.connect(self.quick_connect)
        connect_layout.addWidget(self.connect_btn)
        
        toolbar.addWidget(connect_widget)
        
        toolbar.addSeparator()
        
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setMinimumHeight(34)
        self.disconnect_btn.setMinimumWidth(110)
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                font-weight: 600;
                padding: 9px 20px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.disconnect_btn.clicked.connect(self.disconnect)
        toolbar.addWidget(self.disconnect_btn)
        
        toolbar.addSeparator()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setMinimumHeight(34)
        refresh_btn.setMinimumWidth(100)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                font-weight: 600;
                font-size: 12px;
                padding: 9px 18px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
                border-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #bdc3c7;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_files)
        toolbar.addWidget(refresh_btn)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top splitter: Message log from rest of panes
        self.top_splitter = QSplitter(Qt.Orientation.Vertical)

        # Bottom splitter: View splitter from queue
        self.bottom_splitter = QSplitter(Qt.Orientation.Vertical)

        # View splitter: Local pane from remote pane
        self.view_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Queue log splitter: Queue from log (when position 1)
        self.queue_log_splitter = QSplitter(Qt.Orientation.Vertical)

        # Setup splitter hierarchy
        self.top_splitter.addWidget(self.create_log_panel())
        self.top_splitter.addWidget(self.bottom_splitter)

        self.bottom_splitter.addWidget(self.view_splitter)
        self.bottom_splitter.addWidget(self.queue_log_splitter)

        # Create local and remote panes
        self.view_splitter.addWidget(self.create_local_pane())
        self.view_splitter.addWidget(self.create_remote_pane())

        # Create queue and log panels
        self.queue_log_splitter.addWidget(self.create_queue_panel())
        self.queue_log_splitter.addWidget(self.create_log_panel_bottom())

        # Set splitter sizes 
        self.top_splitter.setSizes([150, self.height() - 150])  # Log panel at top
        self.bottom_splitter.setSizes([self.height() - 300, 150])  # Queue at bottom
        self.view_splitter.setSizes([self.width() // 2, self.width() // 2])  # Equal local/remote
        self.queue_log_splitter.setSizes([100, 50])  # Queue larger than log

        main_layout.addWidget(self.top_splitter)

        # Set up custom status bar
        self.status_bar = FftpStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.update_connection_status("Ready")

    def create_log_panel(self):
        """Create the top message log panel"""
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(4, 4, 4, 4)

        # Header with clear button
        log_header = QHBoxLayout()
        log_label = QLabel("Message Log")
        log_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        log_header.addWidget(log_label)

        log_header.addStretch()

        self.log_enabled_check_top = QCheckBox("Enable Logging")
        self.log_enabled_check_top.setChecked(True)
        log_header.addWidget(self.log_enabled_check_top)

        clear_log_btn = QPushButton("Clear")
        clear_log_btn.setMaximumWidth(60)
        clear_log_btn.setMaximumHeight(24)
        clear_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                font-weight: 500;
                font-size: 11px;
                padding: 4px 8px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """)
        clear_log_btn.clicked.connect(self.clear_log)
        log_header.addWidget(clear_log_btn)

        log_layout.addLayout(log_header)

        # Message log text area
        self.message_log_text = QPlainTextEdit()
        self.message_log_text.setReadOnly(True)
        self.message_log_text.setMaximumBlockCount(500)
        self.message_log_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #ffffff;
                color: #2c3e50;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 4px;
            }
        """)
        log_layout.addWidget(self.message_log_text)

        return log_widget

    def create_local_pane(self):
        """Create the local file pane with tree and list"""
        local_widget = QWidget()
        local_layout = QVBoxLayout(local_widget)
        local_layout.setContentsMargins(6, 6, 6, 6)
        local_layout.setSpacing(4)

        # Header with path and controls
        local_header = QHBoxLayout()
        local_label = QLabel("Local site:")
        local_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 11px;")
        local_header.addWidget(local_label)

        self.local_path_edit = QLineEdit()
        self.local_path_edit.setText(self.current_local_path)
        self.local_path_edit.returnPressed.connect(self.navigate_local_path)
        self.local_path_edit.setStyleSheet("""
            QLineEdit {
                font-size: 11px;
                padding: 6px 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        local_header.addWidget(self.local_path_edit)

        # Control buttons
        self.local_up_btn = QPushButton("⬆️")
        self.local_up_btn.setToolTip("Go to parent directory")
        self.local_up_btn.setMaximumWidth(32)
        self.local_up_btn.clicked.connect(self.local_up)
        self.local_up_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 4px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """)
        local_header.addWidget(self.local_up_btn)

        self.local_refresh_btn = QPushButton("🔄")
        self.local_refresh_btn.setToolTip("Refresh local files")
        self.local_refresh_btn.setMaximumWidth(32)
        self.local_refresh_btn.clicked.connect(self.load_local_files)
        self.local_refresh_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 4px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """)
        local_header.addWidget(self.local_refresh_btn)

        self.local_new_folder_btn = QPushButton("📁")
        self.local_new_folder_btn.setToolTip("Create new folder")
        self.local_new_folder_btn.setMaximumWidth(32)
        self.local_new_folder_btn.clicked.connect(self.create_local_folder)
        self.local_new_folder_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 4px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """)
        local_header.addWidget(self.local_new_folder_btn)

        local_layout.addLayout(local_header)

        # Local file browser (tree + list)
        local_browser = QSplitter(Qt.Orientation.Horizontal)

        # Local tree view
        self.local_tree = QTreeView()
        self.local_tree.setHeaderHidden(True)
        self.local_tree.setRootIsDecorated(True)
        self.local_tree.setAnimated(False)
        self.local_tree.setIndentation(15)
        self.local_tree.setStyleSheet("""
            QTreeView {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
                font-size: 10px;
            }
            QTreeView::item {
                padding: 3px;
                border: none;
                color: #2c3e50;
            }
            QTreeView::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QTreeView::item:hover {
                background-color: #ecf0f1;
            }
        """)
        self.local_tree_model = QFileSystemModel()
        self.local_tree_model.setRootPath("")
        self.local_tree_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)
        self.local_tree.setModel(self.local_tree_model)
        self.local_tree.setRootIndex(self.local_tree_model.index(self.current_local_path))
        self.local_tree.clicked.connect(self.on_local_tree_clicked)
        self.local_tree.doubleClicked.connect(self.on_local_tree_double_clicked)
        self.local_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.local_tree.customContextMenuRequested.connect(self.show_local_tree_context_menu)
        local_browser.addWidget(self.local_tree)

        # Local list view
        drag_drop_enabled = True
        self.local_table = DragDropTableWidget(
            parent=self,
            drop_callback=self._handle_local_drop,
            drag_callback=self._handle_local_drag,
            enabled=drag_drop_enabled
        )
        self.local_table.setColumnCount(4)
        self.local_table.setHorizontalHeaderLabels(["Filename", "Filesize", "Filetype", "Last modified"])
        self.local_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.local_table.setAlternatingRowColors(True)
        self.local_table.setSortingEnabled(True)
        self.local_table.doubleClicked.connect(self.on_local_table_double_click)
        self.local_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.local_table.customContextMenuRequested.connect(self._show_local_context_menu)
        self.local_table.itemSelectionChanged.connect(self._on_local_selection_changed)

        # Enable editing for renaming
        self.local_table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked | QTableWidget.EditTrigger.EditKeyPressed)
        self.local_table.itemChanged.connect(self._on_local_item_changed)
        self.local_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 10px;
                gridline-color: #ecf0f1;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QTableWidget::item {
                padding: 4px 6px;
                color: #2c3e50;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 8px 6px;
                border: none;
                border-bottom: 2px solid #bdc3c7;
                border-right: 1px solid #bdc3c7;
                font-weight: 600;
                font-size: 10px;
                color: #2c3e50;
            }
        """)
        self.local_table.setColumnWidth(0, 200)
        self.local_table.setColumnWidth(1, 80)
        self.local_table.setColumnWidth(2, 80)
        self.local_table.setColumnWidth(3, 120)
        local_browser.addWidget(self.local_table)

        local_browser.setSizes([150, 350])
        local_layout.addWidget(local_browser)

        self.load_local_files()
        return local_widget

    def create_remote_pane(self):
        """Create the remote file pane with tabs for multiple connections"""
        remote_widget = QWidget()
        remote_layout = QVBoxLayout(remote_widget)
        remote_layout.setContentsMargins(6, 6, 6, 6)
        remote_layout.setSpacing(4)

        # Remote tabs
        self.remote_tabs = QTabWidget()
        self.remote_tabs.setTabsClosable(True)
        self.remote_tabs.tabCloseRequested.connect(self.close_connection_tab)
        self.remote_tabs.currentChanged.connect(self.on_tab_changed)

        # Add initial "New Connection" tab
        welcome_tab = QWidget()
        welcome_layout = QVBoxLayout(welcome_tab)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_label = QLabel("Welcome to Fftp\n\nQuick Connect:")
        welcome_label.setStyleSheet("font-size: 14px; color: #34495e; text-align: center;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_label)

        # Quick connect form
        quick_form = QWidget()
        quick_form_layout = QFormLayout(quick_form)

        self.quick_host = QLineEdit()
        self.quick_host.setPlaceholderText("hostname or IP address")
        quick_form_layout.addRow("Host:", self.quick_host)

        self.quick_port = QSpinBox()
        self.quick_port.setRange(1, 65535)
        self.quick_port.setValue(21)
        quick_form_layout.addRow("Port:", self.quick_port)

        self.quick_user = QLineEdit()
        self.quick_user.setPlaceholderText("username")
        quick_form_layout.addRow("User:", self.quick_user)

        self.quick_pass = QLineEdit()
        self.quick_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.quick_pass.setPlaceholderText("password")
        quick_form_layout.addRow("Password:", self.quick_pass)

        connect_btn = QPushButton("Quick Connect")
        connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                font-weight: 600;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        connect_btn.clicked.connect(self.quick_connect)

        quick_form_layout.addRow(connect_btn)
        welcome_layout.addWidget(quick_form)

        welcome_layout.addStretch()
        self.remote_tabs.addTab(welcome_tab, "New Connection")

        remote_layout.addWidget(self.remote_tabs)
        return remote_widget

    def create_queue_panel(self):
        """Create the transfer queue panel"""
        queue_widget = QWidget()
        queue_layout = QVBoxLayout(queue_widget)
        queue_layout.setContentsMargins(4, 4, 4, 4)

        # Queue header
        queue_header = QHBoxLayout()
        queue_label = QLabel("Transfer Queue")
        queue_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        queue_header.addWidget(queue_label)

        queue_header.addStretch()

        # Queue control buttons
        process_queue_btn = QPushButton("Process Queue")
        process_queue_btn.setMaximumWidth(100)
        process_queue_btn.setMaximumHeight(24)
        process_queue_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: #ffffff;
                font-weight: 500;
                font-size: 10px;
                padding: 4px 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        process_queue_btn.clicked.connect(self.process_queue_manually)
        queue_header.addWidget(process_queue_btn)

        clear_queue_btn = QPushButton("Clear")
        clear_queue_btn.setMaximumWidth(60)
        clear_queue_btn.setMaximumHeight(24)
        clear_queue_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                font-weight: 500;
                font-size: 10px;
                padding: 4px 8px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """)
        clear_queue_btn.clicked.connect(self.clear_queue)
        queue_header.addWidget(clear_queue_btn)

        queue_layout.addLayout(queue_header)

        # Queue tabs (Active/Completed)
        self.queue_tabs = QTabWidget()

        # Active transfers tab
        active_tab = QWidget()
        active_layout = QVBoxLayout(active_tab)
        self.active_queue_table = QTableWidget()
        self.active_queue_table.setColumnCount(5)
        self.active_queue_table.setHorizontalHeaderLabels(["Direction", "Local File", "Remote File", "Size", "Status"])
        self.active_queue_table.setAlternatingRowColors(True)
        self.active_queue_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                font-size: 10px;
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #bdc3c7;
                font-weight: 600;
                font-size: 10px;
            }
        """)
        active_layout.addWidget(self.active_queue_table)
        self.queue_tabs.addTab(active_tab, "Active")

        # Completed transfers tab
        completed_tab = QWidget()
        completed_layout = QVBoxLayout(completed_tab)
        self.completed_queue_table = QTableWidget()
        self.completed_queue_table.setColumnCount(5)
        self.completed_queue_table.setHorizontalHeaderLabels(["Direction", "Local File", "Remote File", "Size", "Time"])
        self.completed_queue_table.setAlternatingRowColors(True)
        self.completed_queue_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                font-size: 10px;
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #bdc3c7;
                font-weight: 600;
                font-size: 10px;
            }
        """)
        completed_layout.addWidget(self.completed_queue_table)
        self.queue_tabs.addTab(completed_tab, "Completed")

        queue_layout.addWidget(self.queue_tabs)

        return queue_widget

    def create_log_panel_bottom(self):
        """Create the bottom log panel (minimal)"""
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(4, 4, 4, 4)

        log_label = QLabel("Activity Log")
        log_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 11px;")
        log_layout.addWidget(log_label)

        self.activity_log_text = QPlainTextEdit()
        self.activity_log_text.setReadOnly(True)
        self.activity_log_text.setMaximumBlockCount(100)
        self.activity_log_text.setMaximumHeight(80)
        self.activity_log_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #ffffff;
                color: #2c3e50;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 2px;
            }
        """)
        log_layout.addWidget(self.activity_log_text)

        return log_widget
        local_group.setStyleSheet("""
            QGroupBox {
                font-weight: 700;
                font-size: 13px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 14px;
                padding-top: 18px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 8px;
                background-color: #ffffff;
                color: #3498db;
            }
        """)
        local_layout = QVBoxLayout(local_group)
        local_layout.setContentsMargins(8, 8, 8, 8)
        local_layout.setSpacing(4)
        
        local_path_layout = QHBoxLayout()
        local_path_layout.setSpacing(6)
        path_label = QLabel("Local site:")
        path_label.setMinimumWidth(85)
        path_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 12px;")
        local_path_layout.addWidget(path_label)
        self.local_path_edit = QLineEdit()
        self.local_path_edit.setText(self.current_local_path)
        self.local_path_edit.returnPressed.connect(self.navigate_local_path)
        self.local_path_edit.setStyleSheet("font-size: 12px; padding: 8px 12px; border: 2px solid #bdc3c7; border-radius: 5px;")
        local_path_layout.addWidget(self.local_path_edit, 1)
        local_layout.addLayout(local_path_layout)
        
        local_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.local_tree = QTreeView()
        self.local_tree.setHeaderHidden(True)
        self.local_tree.setRootIsDecorated(True)
        self.local_tree.setAnimated(False)
        self.local_tree.setIndentation(15)
        self.local_tree.setStyleSheet("""
            QTreeView {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ffffff;
                font-size: 11px;
            }
            QTreeView::item {
                padding: 4px;
                border: none;
                color: #2c3e50;
            }
            QTreeView::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QTreeView::item:hover {
                background-color: #ecf0f1;
            }
        """)
        self.local_tree_model = QFileSystemModel()
        self.local_tree_model.setRootPath("")
        self.local_tree_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)
        self.local_tree.setModel(self.local_tree_model)
        self.local_tree.setRootIndex(self.local_tree_model.index(self.current_local_path))
        self.local_tree.clicked.connect(self.on_local_tree_clicked)
        self.local_tree.doubleClicked.connect(self.on_local_tree_double_clicked)
        self.local_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.local_tree.customContextMenuRequested.connect(self.show_local_tree_context_menu)
        local_splitter.addWidget(self.local_tree)
        
        self.local_table = QTableWidget()
        self.local_table.setColumnCount(4)
        self.local_table.setHorizontalHeaderLabels(["Filename", "Filesize", "Filetype", "Last modified"])
        self.local_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.local_table.setAlternatingRowColors(True)
        self.local_table.setSortingEnabled(True)
        self.local_table.doubleClicked.connect(self.on_local_table_double_click)
        self.local_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.local_table.customContextMenuRequested.connect(self.show_local_context_menu)
        self.local_table.setDragEnabled(True)
        self.local_table.setDragDropMode(QTableWidget.DragDropMode.DragOnly)
        self.local_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 11px;
                gridline-color: #ecf0f1;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QTableWidget::item {
                padding: 5px 8px;
                color: #2c3e50;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid #bdc3c7;
                border-right: 1px solid #bdc3c7;
                font-weight: 700;
                font-size: 11px;
                color: #2c3e50;
            }
        """)
        self.local_table.setColumnWidth(0, 250)
        self.local_table.setColumnWidth(1, 100)
        self.local_table.setColumnWidth(2, 100)
        self.local_table.setColumnWidth(3, 150)
        local_splitter.addWidget(self.local_table)
        local_splitter.setSizes([200, 600])
        
        local_layout.addWidget(local_splitter, 1)
        
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&File")
        
        site_manager_action = QAction("&Site Manager...", self)
        site_manager_action.setShortcut("Ctrl+O")
        site_manager_action.triggered.connect(self.show_site_manager)
        file_menu.addAction(site_manager_action)
        
        file_menu.addSeparator()
        
        disconnect_action = QAction("&Disconnect", self)
        disconnect_action.triggered.connect(self.disconnect)
        disconnect_action.setEnabled(False)
        file_menu.addAction(disconnect_action)
        self.disconnect_action = disconnect_action
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        edit_menu = menubar.addMenu("&Edit")
        
        upload_action = QAction("&Upload", self)
        upload_action.setShortcut("Ctrl+U")
        upload_action.triggered.connect(self.upload_selected_local)
        edit_menu.addAction(upload_action)
        
        download_action = QAction("&Download", self)
        download_action.setShortcut("Ctrl+D")
        download_action.triggered.connect(self.download_selected_remote)
        edit_menu.addAction(download_action)
        
        edit_menu.addSeparator()
        
        delete_action = QAction("&Delete", self)
        delete_action.setShortcut("Del")
        delete_action.triggered.connect(self.delete_selected_remote)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()

        search_action = QAction("&Search...", self)
        search_action.setShortcut("Ctrl+F")
        search_action.triggered.connect(self.show_search_dialog)
        edit_menu.addAction(search_action)

        edit_menu.addSeparator()

        new_folder_action = QAction("New &Folder", self)
        new_folder_action.setShortcut("Ctrl+N")
        new_folder_action.triggered.connect(self.create_remote_folder)
        edit_menu.addAction(new_folder_action)
        
        view_menu = menubar.addMenu("&View")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_files)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        show_toolbar_action = QAction("&Toolbar", self)
        show_toolbar_action.setCheckable(True)
        show_toolbar_action.setChecked(True)
        show_toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(show_toolbar_action)
        
        show_statusbar_action = QAction("&Status Bar", self)
        show_statusbar_action.setCheckable(True)
        show_statusbar_action.setChecked(True)
        show_statusbar_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(show_statusbar_action)

        filters_menu = menubar.addMenu("F&ilters")
        self.filter_toggle_action = QAction("&Enable Filters", self)
        self.filter_toggle_action.setCheckable(True)
        self.filter_toggle_action.setChecked(True)
        self.filter_toggle_action.triggered.connect(self.toggle_filters)
        filters_menu.addAction(self.filter_toggle_action)

        filters_menu.addSeparator()

        manage_filters_action = QAction("&Manage Filters...", self)
        manage_filters_action.triggered.connect(self.show_filter_manager)
        filters_menu.addAction(manage_filters_action)

        # Directory comparison submenu
        comparison_menu = view_menu.addMenu("&Directory Comparison")

        self.compare_dirs_action = QAction("&Compare Directories", self)
        self.compare_dirs_action.setCheckable(True)
        self.compare_dirs_action.triggered.connect(self.toggle_directory_comparison)
        comparison_menu.addAction(self.compare_dirs_action)

        comparison_menu.addSeparator()

        self.hide_identical_action = QAction("&Hide Identical Files", self)
        self.hide_identical_action.setCheckable(True)
        self.hide_identical_action.triggered.connect(self.toggle_hide_identical)
        comparison_menu.addAction(self.hide_identical_action)

        # Comparison method submenu
        compare_method_menu = comparison_menu.addMenu("Compare &By")

        self.compare_size_action = QAction("&Size", self)
        self.compare_size_action.setCheckable(True)
        self.compare_size_action.setChecked(True)
        self.compare_size_action.triggered.connect(lambda: self.set_comparison_method("size"))
        compare_method_menu.addAction(self.compare_size_action)

        self.compare_date_action = QAction("&Date", self)
        self.compare_date_action.setCheckable(True)
        self.compare_date_action.triggered.connect(lambda: self.set_comparison_method("date"))
        compare_method_menu.addAction(self.compare_date_action)

        self.compare_both_action = QAction("&Size and Date", self)
        self.compare_both_action.setCheckable(True)
        self.compare_both_action.triggered.connect(lambda: self.set_comparison_method("both"))
        compare_method_menu.addAction(self.compare_both_action)

        view_menu.addSeparator()

        self.sync_browse_action = QAction("&Synchronized Browsing", self)
        self.sync_browse_action.setCheckable(True)
        self.sync_browse_action.triggered.connect(self.toggle_synchronized_browsing)
        view_menu.addAction(self.sync_browse_action)

        # Bookmarks menu
        from .bookmarks import create_bookmark_menu
        bookmarks_menu = create_bookmark_menu(self.bookmark_manager, self)
        menubar.addMenu(bookmarks_menu)

        settings_menu = menubar.addMenu("&Settings")
        
        preferences_action = QAction("&Preferences...", self)
        preferences_action.setShortcut("Ctrl+S")
        preferences_action.triggered.connect(self.show_settings)
        settings_menu.addAction(preferences_action)
        
        help_menu = menubar.addMenu("&Help")
        
        help_action = QAction("&Help", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setShortcut("Ctrl+?")
        shortcuts_action.triggered.connect(self.show_keyboard_shortcuts)
        help_menu.addAction(shortcuts_action)

        help_menu.addSeparator()

        welcome_action = QAction("&Welcome Wizard", self)
        welcome_action.triggered.connect(self.show_welcome_wizard)
        help_menu.addAction(welcome_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About Fftp", self)
        about_action.triggered.connect(self.show_help)
        help_menu.addAction(about_action)
    
    def toggle_toolbar(self, checked):
        """Toggle toolbar visibility"""
        for toolbar in self.findChildren(QToolBar):
            toolbar.setVisible(checked)
    
    def toggle_statusbar(self, checked):
        """Toggle statusbar visibility"""
        self.statusBar().setVisible(checked)
    
    def reset_connect_button_style(self):
        """Reset connect button to default style"""
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-weight: 600;
                padding: 7px 16px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
        """)
    
    def disconnect(self):
        """Disconnect from server"""
        tab = self.get_current_tab()
        if not tab:
            return
        
        result = disconnect_handler(
            tab.manager, tab.connection_worker, self.disconnect_action,
            tab.remote_table, self.connect_btn,
            log_callback=self.log,
            status_callback=lambda msg: self.statusBar().showMessage(msg),
            disconnect_btn=self.disconnect_btn if hasattr(self, 'disconnect_btn') else None
        )
        if result:
            tab.manager = None
            self.manager = None
            title = tab.get_tab_title()
            index = self.remote_tabs.indexOf(tab)
            if index >= 0:
                self.remote_tabs.setTabText(index, title)
    
    def reset_connect_button_style(self):
        """Reset connect button to default style"""
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-weight: 600;
                padding: 7px 16px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
        """)
    
    def log(self, message, level="info"):
        """Add message to log (both UI and file)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "info": "[INFO]",
            "warning": "[WARN]",
            "error": "[ERROR]",
            "success": "[OK]"
        }.get(level, "[INFO]")
        
        log_entry = f"{timestamp} {prefix} {message}"
        
        if hasattr(self, 'log_messages'):
            self.log_messages.append(log_entry)
        
        # Update message log (top panel)
        if hasattr(self, 'message_log_text') and (not hasattr(self, 'log_enabled_check_top') or self.log_enabled_check_top.isChecked()):
            self.message_log_text.appendPlainText(log_entry)
            scrollbar = self.message_log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

        # Update activity log (bottom panel)
        if hasattr(self, 'activity_log_text'):
            self.activity_log_text.appendPlainText(log_entry)
            scrollbar = self.activity_log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        
        if hasattr(self, 'file_logger'):
            log_level = {
                "info": logging.INFO,
                "warning": logging.WARNING,
                "error": logging.ERROR,
                "success": logging.INFO
            }.get(level, logging.INFO)
            self.file_logger.log(log_level, message)
    
    def clear_log(self):
        """Clear all log panels"""
        if hasattr(self, 'message_log_text'):
            self.message_log_text.clear()
        if hasattr(self, 'activity_log_text'):
            self.activity_log_text.clear()
        if hasattr(self, 'log_messages'):
            self.log_messages.clear()
        self.log("All logs cleared")
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            self.apply_settings(settings)
    
    def apply_settings(self, settings):
        """Apply settings to application"""
        if 'default_local_path' in settings:
            self.current_local_path = settings['default_local_path']
            self.load_local_files()
        
        if 'theme' in settings:
            self.apply_theme(settings.get('theme', 'Light'))

        if 'icon_theme' in settings:
            self.icon_theme_manager.set_theme(settings['icon_theme'])

        if 'max_concurrent_transfers' in settings:
            self.max_concurrent_transfers = settings['max_concurrent_transfers']

        if 'speed_limit_enabled' in settings and settings['speed_limit_enabled']:
            if 'speed_limit' in settings:
                self.transfer_speed_limit = settings['speed_limit'] * 1024  # Convert KB/s to bytes/s
            else:
                self.transfer_speed_limit = 0
        else:
            self.transfer_speed_limit = 0
    
    def show_help(self):
        """Show help dialog"""
        dialog = HelpDialog(self)
        dialog.exec()

    def show_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        from .keyboard_shortcuts import show_keyboard_shortcuts_dialog
        show_keyboard_shortcuts_dialog(self)

    def show_welcome_wizard(self):
        """Show welcome wizard"""
        from .welcome_dialog import show_welcome_dialog
        show_welcome_dialog(self)
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            self.settings = settings
            self.settings.update(settings)
            
            if hasattr(self, 'remote_table') and isinstance(self.remote_table, DragDropTableWidget):
                self.remote_table.set_drag_drop_enabled(settings.get('enable_drag_drop', True))
            
            if 'theme' in settings:
                self.apply_theme(settings.get('theme', 'Light'))
    
    def show_site_manager(self):
        """Show site manager dialog"""
        dialog = ConnectionManagerDialog(self, self.encryption_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = dialog.get_selected_connection()
            if selected:
                if isinstance(selected, dict):
                    self.config = ConnectionConfig(**selected)
                else:
                    self.config = selected
                self.connect_to_server()

    def show_search_dialog(self):
        """Show search dialog"""
        tab = self.get_current_tab()
        manager = tab.manager if tab else None
        dialog = SearchDialog(self, manager)
        dialog.exec()

    def toggle_filters(self):
        """Toggle file filtering on/off"""
        self.filter_manager.toggle_filters()
        self.filter_toggle_action.setChecked(self.filter_manager.filters_enabled)
        # Refresh file lists to apply filter changes
        self.refresh_files()

    def show_filter_manager(self):
        """Show filter management dialog"""
        # For now, just show a simple message
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Filter Manager",
                              "Filter management dialog will be implemented.\n\n"
                              "Current active filters will be shown here, "
                              "and you can create/edit filter sets.")

    def toggle_directory_comparison(self):
        """Toggle directory comparison mode"""
        if self.compare_dirs_action.isChecked():
            self.comparison_manager.start_comparison()
        else:
            self.comparison_manager.stop_comparison()

        # Update menu item states
        self.hide_identical_action.setEnabled(self.compare_dirs_action.isChecked())

    def toggle_hide_identical(self):
        """Toggle hiding of identical files"""
        hide_identical = self.hide_identical_action.isChecked()
        self.comparison_manager.set_comparison_options(hide_identical=hide_identical)

    def set_comparison_method(self, method):
        """Set comparison method (size, date, both)"""
        # Update menu check states
        self.compare_size_action.setChecked(method == "size")
        self.compare_date_action.setChecked(method == "date")
        self.compare_both_action.setChecked(method == "both")

        # Apply comparison method
        self.comparison_manager.set_comparison_options(compare_by=method)

    def toggle_synchronized_browsing(self):
        """Toggle synchronized browsing mode"""
        self.synchronized_browsing = self.sync_browse_action.isChecked()

        if self.synchronized_browsing:
            self.log("Synchronized browsing enabled")
            # When enabling, try to sync current directories
            self.sync_directories_if_possible()
        else:
            self.log("Synchronized browsing disabled")

    def sync_directories_if_possible(self):
        """Try to synchronize directories between local and remote"""
        if not self.synchronized_browsing:
            return

        tab = self.get_current_tab()
        if not tab or not tab.manager:
            return

        # Get relative paths from roots
        local_path = self.current_local_path
        remote_path = tab.current_remote_path

        # For now, just log the attempt - full sync logic would need more complex path mapping
        self.log(f"Synchronized browsing: Local={local_path}, Remote={remote_path}")

    def navigate_local_with_sync(self, new_path):
        """Navigate local directory with synchronization"""
        old_path = self.current_local_path
        self.current_local_path = new_path
        self.load_local_files()

        if self.synchronized_browsing:
            self.sync_remote_to_local_change(old_path, new_path)

    def navigate_remote_with_sync(self, new_path):
        """Navigate remote directory with synchronization"""
        tab = self.get_current_tab()
        if not tab:
            return

        old_path = tab.current_remote_path
        tab.current_remote_path = new_path
        tab.load_remote_files()

        if self.synchronized_browsing:
            self.sync_local_to_remote_change(old_path, new_path)

    def sync_remote_to_local_change(self, old_local, new_local):
        """Sync remote directory when local changes"""
        tab = self.get_current_tab()
        if not tab or not tab.manager:
            return

        try:
            # Calculate relative path change
            if old_local in new_local:
                # Going deeper
                relative_path = new_local[len(old_local):].strip(os.sep)
                if relative_path:
                    new_remote = os.path.join(tab.current_remote_path, relative_path)
                    # Try to navigate to corresponding remote path
                    try:
                        tab.manager.list_files(new_remote)  # Check if path exists
                        tab.current_remote_path = new_remote
                        tab.remote_path_edit.setText(new_remote)
                        tab.load_remote_files()
                        self.log(f"Synchronized: navigated remote to {new_remote}")
                    except:
                        pass  # Path doesn't exist remotely
            elif new_local in old_local:
                # Going up
                levels_up = old_local.count(os.sep) - new_local.count(os.sep)
                current_remote = tab.current_remote_path
                for _ in range(levels_up):
                    current_remote = os.path.dirname(current_remote)
                if current_remote and current_remote != tab.current_remote_path:
                    tab.current_remote_path = current_remote
                    tab.remote_path_edit.setText(current_remote)
                    tab.load_remote_files()
                    self.log(f"Synchronized: navigated remote to {current_remote}")
        except Exception as e:
            self.log(f"Synchronized browsing error: {e}")

    def sync_local_to_remote_change(self, old_remote, new_remote):
        """Sync local directory when remote changes"""
        try:
            # Calculate relative path change
            if old_remote in new_remote:
                # Going deeper
                relative_path = new_remote[len(old_remote):].strip("/")
                if relative_path:
                    new_local = os.path.join(self.current_local_path, relative_path.replace("/", os.sep))
                    # Try to navigate to corresponding local path
                    if os.path.isdir(new_local):
                        self.current_local_path = new_local
                        self.local_path_edit.setText(new_local)
                        self.load_local_files()
                        self.log(f"Synchronized: navigated local to {new_local}")
            elif new_remote in old_remote:
                # Going up
                levels_up = old_remote.count("/") - new_remote.count("/")
                current_local = self.current_local_path
                for _ in range(levels_up):
                    current_local = os.path.dirname(current_local)
                if current_local and current_local != self.current_local_path:
                    self.current_local_path = current_local
                    self.local_path_edit.setText(current_local)
                    self.load_local_files()
                    self.log(f"Synchronized: navigated local to {current_local}")
        except Exception as e:
            self.log(f"Synchronized browsing error: {e}")


    def get_master_password(self, allow_setup=True) -> Optional[str]:
        """Get master password from user"""
        if self.master_password:
            return self.master_password
        
        if not self.encryption_manager.has_master_password():
            if allow_setup:
                dialog = MasterPasswordDialog(self, is_setup=True)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    password = dialog.get_password()
                    if password:
                        if self.encryption_manager.set_master_password(password):
                            self.master_password = password
                            QMessageBox.information(
                                self, "Master Password Set",
                                "Master password has been set successfully.\n"
                                "Your saved connections will be encrypted."
                            )
                            return password
                        else:
                            QMessageBox.critical(
                                self, "Error",
                                "Failed to set master password"
                            )
            return None
        
        dialog = MasterPasswordDialog(self, is_setup=False)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            password = dialog.get_password()
            if password and self.encryption_manager.verify_master_password(password):
                self.master_password = password
                return password
            else:
                QMessageBox.warning(
                    self, "Error",
                    "Incorrect master password"
                )
                return None
        return None
    
    def show_site_manager(self):
        """Show connection manager dialog"""
        connections = []
        password = None
        
        if self.encryption_manager.has_master_password():
            password = self.get_master_password()
            if password:
                connections = self.encryption_manager.decrypt_connections(password)
        else:
            connections = []
        
        dialog = ConnectionManagerDialog(
            self, 
            connections=connections,
            master_password=password,
            encryption_manager=self.encryption_manager
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_config()
            if config:
                self.config = config
                self.connect_to_server()
    
    def quick_connect(self):
        """Quick connect from toolbar"""
        host = self.quick_connect_combo.currentText().strip()
        user = self.quick_user.text().strip()
        password = self.quick_pass.text().strip()
        port = self.quick_port.value()

        if not host:
            QMessageBox.warning(self, "Error", "Please enter a host")
            return

        # Debug logging to help troubleshoot
        # Enhanced debugging
        self.log(f"Quick Connect: Host='{host}', User='{user}' (len={len(user)}), Port={port}, HasPassword={bool(password)}")

        if port == 22:
            protocol = "sftp"
        elif port == 21:
            protocol = "ftp"
        else:
            protocol = "sftp" if port >= 22 and port < 100 else "ftp"

        # Only use anonymous if both user and password are empty
        if not user.strip() and not password.strip():
            user = "anonymous"
            password = ""
            self.log("Using anonymous login (no credentials provided)")
        else:
            self.log(f"Using authenticated login as '{user}' with password")
            # Ensure user is not empty for authentication
            if not user.strip():
                user = "anonymous"
                self.log("Warning: Empty username, using anonymous")

        self.log(f"Quick Connect: Attempting to connect to {host}:{port} as {user or 'anonymous'}")
        
        self.config = ConnectionConfig(
            name="quick_connect",
            host=host,
            port=port,
            username=user or "anonymous",
            password=password,
            protocol=protocol,
            use_passive=True
        )
        
        self.connect_to_server()
    
    def connect_to_server(self):
        """Connect using current config - non-blocking with proper threading"""
        tab = self.get_current_tab()
        if not tab:
            tab = self.create_new_tab(self.config)
        
        if tab.config is None:
            tab.config = self.config
        
        worker = connect_to_server(
            tab.config, tab.manager, tab.connection_worker,
            self.connect_btn,
            status_callback=lambda msg: self.statusBar().showMessage(msg),
            log_callback=self.log
        )
        if worker:
            tab.connection_worker = worker
            self.connection_worker = worker
            self.config = tab.config
            worker.status_update.connect(self.on_connection_status)
            worker.log_message.connect(self.log)
            worker.finished.connect(self.on_connection_finished)
            worker.start()
    
    def on_connection_status(self, message):
        """Update status bar with connection progress"""
        self.statusBar().showMessage(message)
    
    def on_connection_finished(self, success, msg):
        """Handle connection completion"""
        tab = self.get_current_tab()
        if not tab:
            return
        
        manager_ref = [tab.manager]
        path_ref = [tab.current_remote_path]
        
        handle_connection_finished(
            tab.connection_worker, success, msg, tab.config, manager_ref, path_ref,
            self.connect_btn, self.disconnect_action,
            status_callback=lambda m: self.status_bar.show_message(m),
            log_callback=self.log,
            refresh_callback=self.load_remote_files,
            disconnect_btn=self.disconnect_btn if hasattr(self, 'disconnect_btn') else None,
            status_bar=self.status_bar
        )
        
        tab.manager = manager_ref[0]
        tab.current_remote_path = path_ref[0]
        self.manager = tab.manager
        self.current_remote_path = tab.current_remote_path
        tab.connection_worker = None
        self.connection_worker = None
        
        if success:
            title = tab.get_tab_title()
            index = self.remote_tabs.indexOf(tab)
            if index >= 0:
                self.remote_tabs.setTabText(index, title)
    
    def refresh_files(self):
        """Refresh both local and remote file lists"""
        self.load_local_files()
        if self.manager:
            self.load_remote_files()
    
    def load_local_files(self):
        """Load local directory into table"""
        try:
            path = Path(self.current_local_path)
            if not path.exists():
                path = Path.home()
                self.current_local_path = str(path)
            
            if hasattr(self, 'local_tree') and hasattr(self, 'local_tree_model'):
                index = self.local_tree_model.index(self.current_local_path)
                if index.isValid():
                    self.local_tree.setRootIndex(index)
            
            self.local_table.setSortingEnabled(False)
            self.local_table.setRowCount(0)

            # Collect file data for comparison
            local_files_data = []

            if path.parent != path:
                row = self.local_table.rowCount()
                self.local_table.insertRow(row)
                self.local_table.setItem(row, 0, QTableWidgetItem(".."))
                self.local_table.setItem(row, 1, QTableWidgetItem(""))
                self.local_table.setItem(row, 2, QTableWidgetItem("<Parent Directory>"))
                self.local_table.setItem(row, 3, QTableWidgetItem(""))

            for item in sorted(path.iterdir()):
                if item.is_dir():
                    # Create file info for filtering
                    file_info = {
                        'name': item.name,
                        'path': str(path),
                        'full_path': str(item),
                        'size': 0,
                        'modified': datetime.fromtimestamp(item.stat().st_mtime),
                        'is_dir': True
                    }

                    # Check if filtered
                    if self.filter_manager.is_filtered(file_info):
                        continue

                    # Check if should be hidden in comparison mode
                    if self.comparison_manager.comparator.should_hide_file(item.name):
                        continue

                    local_files_data.append(file_info)

                    row = self.local_table.rowCount()
                    self.local_table.insertRow(row)
                    icon = self.icon_theme_manager.get_file_icon(item.name, is_dir=True)
                    name_item = QTableWidgetItem(icon, item.name)
                    self.local_table.setItem(row, 0, name_item)
                    size_item = QTableWidgetItem("")
                    size_item.setData(Qt.ItemDataRole.UserRole, 0)
                    self.local_table.setItem(row, 1, size_item)
                    self.local_table.setItem(row, 2, QTableWidgetItem("<Directory>"))
                    try:
                        mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    except:
                        mtime = ""
                    self.local_table.setItem(row, 3, QTableWidgetItem(mtime))
                    self.local_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(item))

                    # Apply comparison highlighting
                    comparison_result = self.comparison_manager.comparator.get_comparison_result(item.name, True)
                    if comparison_result:
                        color = self.comparison_manager.get_comparison_color(comparison_result)
                        if color:
                            name_item.setBackground(QColor(color))
            
            for item in sorted(path.iterdir()):
                if item.is_file():
                    # Create file info for filtering
                    size = item.stat().st_size
                    file_info = {
                        'name': item.name,
                        'path': str(path),
                        'full_path': str(item),
                        'size': size,
                        'modified': datetime.fromtimestamp(item.stat().st_mtime),
                        'is_dir': False
                    }

                    # Check if filtered
                    if self.filter_manager.is_filtered(file_info):
                        continue

                    # Check if should be hidden in comparison mode
                    if self.comparison_manager.comparator.should_hide_file(item.name):
                        continue

                    local_files_data.append(file_info)

                    row = self.local_table.rowCount()
                    self.local_table.insertRow(row)
                    icon = self.icon_theme_manager.get_file_icon(item.name, is_dir=False)
                    name_item = QTableWidgetItem(icon, item.name)
                    self.local_table.setItem(row, 0, name_item)
                    size_str = self.format_size(size)
                    size_item = QTableWidgetItem(size_str)
                    size_item.setData(Qt.ItemDataRole.UserRole, size)
                    self.local_table.setItem(row, 1, size_item)
                    self.local_table.setItem(row, 2, QTableWidgetItem(item.suffix or "File"))
                    try:
                        mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    except:
                        mtime = ""
                    self.local_table.setItem(row, 3, QTableWidgetItem(mtime))
                    self.local_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(item))

                    # Apply comparison highlighting
                    comparison_result = self.comparison_manager.comparator.get_comparison_result(item.name, True)
                    if comparison_result:
                        color = self.comparison_manager.get_comparison_color(comparison_result)
                        if color:
                            name_item.setBackground(QColor(color))

            # Update comparison manager with local file data
            self.comparison_manager.update_directory_data(True, local_files_data)

            # Update status bar with directory info
            self.status_bar.update_local_directory_info(self.current_local_path, local_files_data)

            self.local_table.setSortingEnabled(True)
            self.local_table.resizeColumnsToContents()
            self.local_path_edit.setText(self.current_local_path)
        except Exception as e:
            self.statusBar().showMessage(f"Error loading local files: {str(e)}")
            self.local_table.setSortingEnabled(True)
    
    def get_current_tab(self) -> Optional[ConnectionTab]:
        """Get the currently active connection tab"""
        if self.active_tab_id and self.active_tab_id in self.connection_tabs:
            return self.connection_tabs[self.active_tab_id]
        return None
    
    def on_tab_changed(self, index):
        """Handle tab change"""
        if index >= 0:
            widget = self.remote_tabs.widget(index)
            if widget:
                tab_id = id(widget)
                self.active_tab_id = tab_id
                tab = self.connection_tabs.get(tab_id)
                if tab:
                    self.manager = tab.manager
                    self.config = tab.config
                    self.current_remote_path = tab.current_remote_path
                    self.connection_worker = tab.connection_worker
                    
                    if tab.remote_path_edit:
                        tab.remote_path_edit.returnPressed.connect(self.navigate_remote_path)
                    if tab.remote_up_btn:
                        tab.remote_up_btn.clicked.connect(self.remote_up)
                    if tab.remote_table:
                        tab.remote_table.doubleClicked.connect(self.on_remote_double_click)
                        tab.remote_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                        tab.remote_table.customContextMenuRequested.connect(self.show_remote_context_menu)
                        if hasattr(tab.remote_table, 'set_drag_drop_enabled'):
                            drag_drop_enabled = self.settings.get('enable_drag_drop', True)
                            tab.remote_table.set_drag_drop_enabled(drag_drop_enabled)
                            tab.remote_table.drop_callback = self.handle_file_drop
                    
                    if tab.manager:
                        if hasattr(self, 'disconnect_btn'):
                            self.disconnect_btn.setEnabled(True)
                        if hasattr(self, 'disconnect_action'):
                            self.disconnect_action.setEnabled(True)
                        if hasattr(self, 'connect_btn'):
                            self.connect_btn.setText("Connected")
                            self.connect_btn.setStyleSheet("""
                                QPushButton {
                                    background-color: #4caf50;
                                    color: #ffffff;
                                    font-weight: 600;
                                    padding: 7px 16px;
                                    border-radius: 5px;
                                    font-size: 12px;
                                }
                                QPushButton:hover {
                                    background-color: #45a049;
                                }
                                QPushButton:pressed {
                                    background-color: #388e3c;
                                }
                            """)
                    else:
                        if hasattr(self, 'disconnect_btn'):
                            self.disconnect_btn.setEnabled(False)
                        if hasattr(self, 'disconnect_action'):
                            self.disconnect_action.setEnabled(False)
                        if hasattr(self, 'connect_btn'):
                            self.connect_btn.setText("Connect")
                            self.reset_connect_button_style()
    
    def close_connection_tab(self, index):
        """Close a connection tab"""
        widget = self.remote_tabs.widget(index)
        if widget:
            tab_id = id(widget)
            tab = self.connection_tabs.get(tab_id)
            if tab and tab.manager:
                reply = QMessageBox.question(
                    self, "Close Connection",
                    f"Close connection to {tab.config.host if tab.config else 'server'}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        tab.manager.disconnect()
                    except:
                        pass
            
            self.remote_tabs.removeTab(index)
            if tab_id in self.connection_tabs:
                del self.connection_tabs[tab_id]
            
            if self.remote_tabs.count() == 0:
                new_tab = ConnectionTab(self)
                new_tab_id = id(new_tab)
                self.connection_tabs[new_tab_id] = new_tab
                self.active_tab_id = new_tab_id
                self.remote_tabs.addTab(new_tab, "New Connection")
    
    def create_new_tab(self, config: ConnectionConfig = None) -> ConnectionTab:
        """Create a new connection tab"""
        new_tab = ConnectionTab(self, config)
        tab_id = id(new_tab)
        self.connection_tabs[tab_id] = new_tab
        self.active_tab_id = tab_id
        title = new_tab.get_tab_title()
        index = self.remote_tabs.addTab(new_tab, title)
        self.remote_tabs.setCurrentIndex(index)
        return new_tab
    
    def load_remote_files(self):
        """Refresh remote file list in table"""
        tab = self.get_current_tab()
        if not tab:
            return
        
        if tab.manager and hasattr(tab.manager, 'is_connected'):
            if not tab.manager.is_connected():
                self.log("Connection lost, attempting to reconnect...", "warning")
                self.statusBar().showMessage("Connection lost, reconnecting...")
                if tab.config:
                    self.reconnect_tab(tab)
                return
        
        tab.current_remote_path = load_remote_files_to_table(
            tab.remote_table,
            tab.remote_path_edit,
            tab.manager,
            tab.current_remote_path,
            self.log,
            lambda msg: self.statusBar().showMessage(msg)
        )
        self.current_remote_path = tab.current_remote_path
    
    def reconnect_tab(self, tab):
        """Reconnect a tab that lost connection"""
        if not tab.config:
            return
        
        try:
            if tab.manager:
                try:
                    tab.manager.disconnect()
                except:
                    pass
                tab.manager = None
            
            manager_class = SFTPManager if tab.config.protocol == "sftp" else FTPManager
            tab.manager = manager_class(tab.config)
            success, msg = tab.manager.connect()
            
            if success:
                self.log(f"Reconnected to {tab.config.host}", "success")
                self.status_bar.update_connection_status(f"Connected to {tab.config.host}", True)
                self.status_bar.show_message(f"Reconnected to {tab.config.host}")
                self.load_remote_files()
            else:
                self.log(f"Reconnection failed: {msg}", "error")
                self.statusBar().showMessage(f"Reconnection failed: {msg}")
        except Exception as e:
            self.log(f"Reconnection error: {str(e)}", "error")
            self.statusBar().showMessage(f"Reconnection error: {str(e)}")
    
    def format_size(self, size: int) -> str:
        """Format file size"""
        return format_size(size)
    
    def on_local_tree_clicked(self, index):
        """Handle local tree view click - update current directory"""
        if index.isValid():
            path = self.local_tree_model.filePath(index)
            if Path(path).is_dir():
                self.navigate_local_with_sync(path)
    
    def on_local_tree_double_clicked(self, index):
        """Handle local tree view double-click"""
        if index.isValid():
            path = self.local_tree_model.filePath(index)
            if Path(path).is_dir():
                self.navigate_local_with_sync(path)
                self.local_tree.setRootIndex(index)
            else:
                open_local_file(Path(path), parent_widget=self)
    
    def show_local_tree_context_menu(self, position):
        """Show context menu for local tree"""
        self.context_menu_manager.create_local_tree_context_menu(self.local_tree, position)
    
    def on_local_table_double_click(self, index):
        """Handle local table double-click"""
        row = index.row()
        item = self.local_table.item(row, 0)
        if not item:
            return
        
        path_str = item.data(Qt.ItemDataRole.UserRole)
        if not path_str:
            if item.text() == "..":
                self.current_local_path = str(Path(self.current_local_path).parent)
                self.load_local_files()
            return
        
        path = Path(path_str)
        if path.is_dir():
            self.current_local_path = str(path)
            self.local_tree.setRootIndex(self.local_tree_model.index(str(path)))
            self.load_local_files()
        else:
            open_local_file(path, parent_widget=self)
    
    def on_local_double_click(self, index):
        """Handle local file/folder double-click (legacy)"""
        self.on_local_table_double_click(index)
    
    def upload_file_from_path(self, path: Path):
        """Upload file from given path"""
        tab = self.get_current_tab()
        if not tab or not tab.manager:
            QMessageBox.warning(self, "Not Connected", "Please connect to a server first")
            return
        
        if path.is_file():
            success = upload_file(
                tab.manager, path, tab.current_remote_path,
                log_callback=self.log,
                status_callback=lambda msg: self.statusBar().showMessage(msg),
                queue_callback=lambda d, l, r, s, st: self.add_to_transfer_queue(d, l, r, s, st),
                move_completed_callback=lambda: self.move_to_completed(self.queue_table.rowCount() - 1),
                refresh_callback=self.load_remote_files,
                format_size_func=self.format_size
            )
            if not success:
                QMessageBox.critical(self, "Upload Error", f"Failed to upload {path.name}")
    
    def on_remote_double_click(self, index):
        """Handle remote file/folder double-click"""
        tab = self.get_current_tab()
        if not tab:
            return
        
        row = index.row()
        item = tab.remote_table.item(row, 0)
        if not item:
            return
        
        file = item.data(Qt.ItemDataRole.UserRole)
        if file and file.is_dir:
            tab.current_remote_path = file.path
            self.current_remote_path = tab.current_remote_path
            self.load_remote_files()
    
    def local_up(self):
        """Navigate up in local directory"""
        self.current_local_path = str(Path(self.current_local_path).parent)
        self.load_local_files()
    
    def remote_up(self):
        """Navigate up in remote directory"""
        tab = self.get_current_tab()
        if not tab:
            return
        
        if tab.current_remote_path == "." or tab.current_remote_path == "/":
            return
        parts = tab.current_remote_path.rstrip("/").split("/")
        if len(parts) > 1:
            tab.current_remote_path = "/".join(parts[:-1])
        else:
            tab.current_remote_path = "."
        self.current_remote_path = tab.current_remote_path
        self.load_remote_files()
    
    def navigate_local_path(self):
        """Navigate to custom local path"""
        path = self.local_path_edit.text()
        if Path(path).exists():
            self.navigate_local_with_sync(path)
    
    def navigate_remote_path(self):
        """Navigate to custom remote path"""
        tab = self.get_current_tab()
        if not tab:
            return

        new_path = tab.remote_path_edit.text()
        self.navigate_remote_with_sync(new_path)
    
    def show_local_context_menu(self, position):
        """Show context menu for local files"""
        selected_items = self.local_table.selectedItems()
        self.context_menu_manager.create_local_context_menu(self.local_table, position, selected_items)
    
    def show_remote_context_menu(self, position):
        """Show context menu for remote files"""
        tab = self.get_current_tab()
        if not tab:
            return

        selected_items = tab.remote_table.selectedItems()
        self.context_menu_manager.create_remote_context_menu(tab.remote_table, position, selected_items)
    
    def upload_selected_local(self):
        """Upload selected local file"""
        tab = self.get_current_tab()
        if not tab or not tab.manager:
            QMessageBox.warning(self, "Not Connected", "Please connect to a server first")
            return
        
        if hasattr(tab.manager, 'is_connected') and not tab.manager.is_connected():
            self.log("Connection lost during upload, reconnecting...", "warning")
            self.reconnect_tab(tab)
            if not tab.manager or (hasattr(tab.manager, 'is_connected') and not tab.manager.is_connected()):
                QMessageBox.warning(self, "Connection Lost", "Could not reconnect. Please reconnect manually.")
                return
        
        row = self.local_table.currentRow()
        if row < 0:
            return
        
        item = self.local_table.item(row, 0)
        if not item:
            return
        
        path_str = item.data(Qt.ItemDataRole.UserRole)
        if not path_str:
            return
        
        path = Path(path_str)
        if path.is_file():
            success = upload_file(
                tab.manager, path, tab.current_remote_path,
                log_callback=self.log,
                status_callback=lambda msg: self.statusBar().showMessage(msg),
                queue_callback=lambda d, l, r, s, st: self.add_to_transfer_queue(d, l, r, s, st),
                move_completed_callback=lambda: self.move_to_completed(self.queue_table.rowCount() - 1),
                refresh_callback=self.load_remote_files,
                format_size_func=self.format_size
            )
            if not success:
                QMessageBox.critical(self, "Upload Error", f"Failed to upload {path.name}")
                if self.queue_table.rowCount() > 0:
                    self.queue_table.item(self.queue_table.rowCount() - 1, 4).setText("Error")
    
    def download_selected_remote(self):
        """Download selected remote file"""
        tab = self.get_current_tab()
        if not tab or not tab.manager:
            QMessageBox.warning(self, "Not Connected", "Please connect to a server first")
            return
        
        if hasattr(tab.manager, 'is_connected') and not tab.manager.is_connected():
            self.log("Connection lost during download, reconnecting...", "warning")
            self.reconnect_tab(tab)
            if not tab.manager or (hasattr(tab.manager, 'is_connected') and not tab.manager.is_connected()):
                QMessageBox.warning(self, "Connection Lost", "Could not reconnect. Please reconnect manually.")
                return
        
        row = tab.remote_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "No Selection", "Please select a file to download")
            return
        
        item = tab.remote_table.item(row, 0)
        if not item:
            return
        
        file = item.data(Qt.ItemDataRole.UserRole)
        if not file:
            return
        
        if file.is_dir:
            QMessageBox.information(self, "Directory", "Please select a file, not a directory")
            return
        
        if file and not file.is_dir:
            success = download_file(
                tab.manager, file, self.current_local_path,
                log_callback=self.log,
                status_callback=lambda msg: self.statusBar().showMessage(msg),
                queue_callback=lambda d, l, r, s, st: self.add_to_transfer_queue(d, l, r, s, st),
                move_completed_callback=lambda: self.move_to_completed(self.queue_table.rowCount() - 1),
                refresh_callback=self.load_local_files,
                format_size_func=self.format_size
            )
            if not success:
                QMessageBox.critical(self, "Download Error", f"Failed to download {file.name}")
                if self.queue_table.rowCount() > 0:
                    self.queue_table.item(self.queue_table.rowCount() - 1, 4).setText("Error")
    
    def delete_selected_remote(self):
        """Delete selected remote file"""
        tab = self.get_current_tab()
        if not tab or not tab.manager:
            return
        
        row = tab.remote_table.currentRow()
        if row < 0:
            return
        
        item = tab.remote_table.item(row, 0)
        if not item:
            return
        
        file = item.data(Qt.ItemDataRole.UserRole)
        if file:
            delete_remote_file(
                tab.manager, file, parent_widget=self,
                log_callback=self.log,
                status_callback=lambda msg: self.statusBar().showMessage(msg),
                refresh_callback=self.load_remote_files
            )
    
    def create_remote_folder(self):
        """Create new remote folder"""
        tab = self.get_current_tab()
        if not tab or not tab.manager:
            return
        
        create_remote_folder(
            tab.manager, tab.current_remote_path, parent_widget=self,
            log_callback=self.log,
            status_callback=lambda msg: self.statusBar().showMessage(msg),
            refresh_callback=self.load_remote_files
        )
    
    def load_settings(self) -> dict:
        """Load settings from file"""
        settings_file = Path.home() / ".fftp" / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file) as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def load_connections(self) -> list:
        """Load saved connections from encrypted storage"""
        if not self.encryption_manager.has_master_password():
            return []
        
        password = self.get_master_password()
        if not password:
            return []
        
        try:
            connections = self.encryption_manager.decrypt_connections(password)
            return connections
        except Exception as e:
            return []
    
    def apply_theme(self, theme='Light'):
        """Apply premium theme styling"""
        if theme == 'Dark':
            self.setStyleSheet(PREMIUM_DARK_THEME)
        else:
            self.setStyleSheet(PREMIUM_LIGHT_THEME)

    def apply_global_theme(self):
        """Apply global theme styling"""
        # Force theme application to all child widgets
        for widget in self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()
    
    def add_to_transfer_queue(self, direction, local_file, remote_file, size, status):
        """Add transfer to active queue"""
        if not hasattr(self, 'active_queue_table'):
            return

        row = self.active_queue_table.rowCount()
        self.active_queue_table.insertRow(row)
        self.active_queue_table.setItem(row, 0, QTableWidgetItem(direction))
        self.active_queue_table.setItem(row, 1, QTableWidgetItem(local_file))
        self.active_queue_table.setItem(row, 2, QTableWidgetItem(remote_file))
        self.active_queue_table.setItem(row, 3, QTableWidgetItem(size))
        # Set status to "Queued" if not specified
        if not status:
            status = "Queued"
        self.active_queue_table.setItem(row, 4, QTableWidgetItem(status))

        # Auto-start transfer if queue processing is enabled
        if hasattr(self, 'auto_process_queue') and self.auto_process_queue:
            self.process_next_transfer()
    
    def move_to_completed(self, row):
        """Move transfer from active to completed queue"""
        if not hasattr(self, 'active_queue_table') or not hasattr(self, 'completed_queue_table'):
            return

        if row < 0 or row >= self.active_queue_table.rowCount():
            return

        direction = self.active_queue_table.item(row, 0).text()
        local_file = self.active_queue_table.item(row, 1).text()
        remote_file = self.active_queue_table.item(row, 2).text()
        size = self.active_queue_table.item(row, 3).text()
        status = self.active_queue_table.item(row, 4).text()

        completed_row = self.completed_queue_table.rowCount()
        self.completed_queue_table.insertRow(completed_row)
        self.completed_queue_table.setItem(completed_row, 0, QTableWidgetItem(direction))
        self.completed_queue_table.setItem(completed_row, 1, QTableWidgetItem(local_file))
        self.completed_queue_table.setItem(completed_row, 2, QTableWidgetItem(remote_file))
        self.completed_queue_table.setItem(completed_row, 3, QTableWidgetItem(size))
        self.completed_queue_table.setItem(completed_row, 4, QTableWidgetItem(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        self.active_queue_table.removeRow(row)

        # Process next transfer if available
        if hasattr(self, 'auto_process_queue') and self.auto_process_queue:
            self.process_next_transfer()

    def process_next_transfer(self):
        """Process the next transfer in queue if slots available"""
        if not hasattr(self, 'active_queue_table'):
            return

        active_transfers = len(self.transfer_engines)
        if active_transfers >= self.max_concurrent_transfers:
            return  # Max concurrent transfers reached

        # Find next pending transfer
        for row in range(self.active_queue_table.rowCount()):
            status_item = self.active_queue_table.item(row, 4)
            if status_item and status_item.text() == "Queued":
                self.start_transfer(row)
                break

    def start_transfer(self, row):
        """Start a transfer from the queue"""
        if not hasattr(self, 'active_queue_table') or row >= self.active_queue_table.rowCount():
            return

        direction = self.active_queue_table.item(row, 0).text()
        local_file = self.active_queue_table.item(row, 1).text()
        remote_file = self.active_queue_table.item(row, 2).text()

        # Update status to "Transferring"
        self.active_queue_table.item(row, 4).setText("Transferring")

        # Create transfer engine
        engine = TransferEngine(direction, local_file, remote_file, row, self)
        self.transfer_engines.append(engine)
        engine.start()

    def remove_transfer_engine(self, engine):
        """Remove a completed transfer engine"""
        if engine in self.transfer_engines:
            self.transfer_engines.remove(engine)

        # Process next transfer
        if self.auto_process_queue:
            self.process_next_transfer()

    def cancel_transfer(self, row):
        """Cancel a transfer"""
        if not hasattr(self, 'active_queue_table') or row >= self.active_queue_table.rowCount():
            return

        # Find and cancel the transfer engine
        for engine in self.transfer_engines:
            if engine.queue_row == row:
                engine.cancel()
                break

    def cancel_all_transfers(self):
        """Cancel all active transfers"""
        for engine in self.transfer_engines[:]:  # Copy list to avoid modification during iteration
            engine.cancel()

    def pause_all_transfers(self):
        """Pause all active transfers"""
        for engine in self.transfer_engines:
            engine.pause()

    def resume_all_transfers(self):
        """Resume all paused transfers"""
        for engine in self.transfer_engines:
            engine.resume()

    def on_transfer_completed(self, row, success, message):
        """Handle transfer completion"""
        if hasattr(self, 'active_queue_table') and row < self.active_queue_table.rowCount():
            if success:
                self.active_queue_table.item(row, 4).setText("Completed")
                self.move_to_completed(row)
            else:
                self.active_queue_table.item(row, 4).setText(f"Failed: {message}")

        # Remove the transfer engine
        for engine in self.transfer_engines[:]:
            if engine.queue_row == row:
                self.transfer_engines.remove(engine)
                break

        # Log the result
        self.log(f"Transfer {'succeeded' if success else 'failed'}: {message}")

    def on_transfer_progress(self, row, bytes_transferred, total_bytes):
        """Handle transfer progress updates"""
        if hasattr(self, 'active_queue_table') and row < self.active_queue_table.rowCount():
            # Update progress in the status column
            progress_pct = (bytes_transferred / total_bytes * 100) if total_bytes > 0 else 0
            self.active_queue_table.item(row, 4).setText(f"Transferring ({progress_pct:.1f}%)")

    def set_max_concurrent_transfers(self, max_transfers):
        """Set maximum concurrent transfers"""
        self.max_concurrent_transfers = max_transfers
        if self.auto_process_queue:
            self.process_next_transfer()

    def set_transfer_speed_limit(self, speed_limit):
        """Set transfer speed limit (bytes/second, 0 = unlimited)"""
        self.transfer_speed_limit = speed_limit

    def process_queue_manually(self):
        """Manually process the transfer queue"""
        if hasattr(self, 'auto_process_queue'):
            was_auto = self.auto_process_queue
            self.auto_process_queue = True
            self.process_next_transfer()
            self.auto_process_queue = was_auto

    def clear_queue(self):
        """Clear the transfer queue"""
        if hasattr(self, 'active_queue_table'):
            # Cancel all active transfers first
            self.cancel_all_transfers()
            # Clear the queue table
            self.active_queue_table.setRowCount(0)

        if hasattr(self, 'completed_queue_table'):
            # Optionally clear completed transfers too
            reply = QMessageBox.question(
                self, "Clear Queue",
                "Also clear completed transfers?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.completed_queue_table.setRowCount(0)

        self.log("Transfer queue cleared")
    
    def open_local_file(self, path: Path):
        """Open local file with system default application"""
        open_local_file(path, parent_widget=self)
    
    def delete_local_file(self, path: Path):
        """Delete local file or folder"""
        delete_local_file(
            path, parent_widget=self,
            status_callback=lambda msg: self.statusBar().showMessage(msg),
            refresh_callback=self.load_local_files
        )
    
    def rename_remote_file(self, file):
        """Rename remote file"""
        tab = self.get_current_tab()
        if not tab or not tab.manager:
            return
        
        rename_remote_file(
            tab.manager, file, parent_widget=self,
            log_callback=self.log,
            status_callback=lambda msg: self.statusBar().showMessage(msg),
            refresh_callback=self.load_remote_files
        )
    
    def _show_local_context_menu(self, position):
        """Show enhanced local context menu"""
        selected_items = self.local_table.selectedItems()
        self.context_menu_manager.create_local_context_menu(self.local_table, position, selected_items)

    def _show_remote_context_menu(self, position):
        """Show enhanced remote context menu"""
        selected_items = []
        if hasattr(self, 'remote_table'):
            selected_items = self.remote_table.selectedItems()
        self.context_menu_manager.create_remote_context_menu(self.remote_table, position, selected_items)

    def _show_local_tree_context_menu(self, position):
        """Show enhanced local tree context menu"""
        self.context_menu_manager.create_local_tree_context_menu(self.local_tree, position)

    def _show_remote_tree_context_menu(self, position):
        """Show enhanced remote tree context menu"""
        # For now, delegate to connection tab
        tab = self.get_current_tab()
        if tab and hasattr(tab, 'remote_tree'):
            tab.context_menu_manager.create_remote_tree_context_menu(tab.remote_tree, position)

    # Context menu action implementations
    def upload_selected_local(self):
        """Upload selected local files"""
        selected_rows = set()
        for item in self.local_table.selectedItems():
            selected_rows.add(item.row())

        for row in selected_rows:
            item = self.local_table.item(row, 0)
            if item:
                path_str = item.data(Qt.ItemDataRole.UserRole)
                if path_str:
                    self.upload_file_from_path(Path(path_str))

    def download_selected_remote(self):
        """Download selected remote files"""
        tab = self.get_current_tab()
        if tab:
            selected_rows = set()
            for item in tab.remote_table.selectedItems():
                selected_rows.add(item.row())

            for row in selected_rows:
                item = tab.remote_table.item(row, 0)
                if item:
                    file_data = item.data(Qt.ItemDataRole.UserRole)
                    if file_data and hasattr(file_data, 'name'):
                        self.download_remote_file(file_data)

    def open_selected_local_file(self):
        """Open selected local file"""
        selected_rows = set()
        for item in self.local_table.selectedItems():
            selected_rows.add(item.row())

        for row in selected_rows:
            item = self.local_table.item(row, 0)
            if item:
                path_str = item.data(Qt.ItemDataRole.UserRole)
                if path_str:
                    path = Path(path_str)
                    if path.is_file():
                        self.open_local_file(path)
                        break  # Open only first file

    def view_selected_remote_file(self):
        """View/edit selected remote file"""
        tab = self.get_current_tab()
        if tab:
            selected_rows = set()
            for item in tab.remote_table.selectedItems():
                selected_rows.add(item.row())

            for row in selected_rows:
                item = tab.remote_table.item(row, 0)
                if item:
                    file_data = item.data(Qt.ItemDataRole.UserRole)
                    if file_data and hasattr(file_data, 'name') and not getattr(file_data, 'is_dir', False):
                        # Open file in remote editor
                        edit_remote_file(tab.manager, file_data.path, file_data.name, self)
                        break

    def delete_selected_local(self):
        """Delete selected local files/folders"""
        selected_rows = set()
        for item in self.local_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            return

        # Confirm deletion
        count = len(selected_rows)
        if count == 1:
            message = "Are you sure you want to delete the selected item?"
        else:
            message = f"Are you sure you want to delete {count} selected items?"

        reply = QMessageBox.question(self, "Confirm Delete", message,
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            for row in sorted(selected_rows, reverse=True):  # Delete from bottom up
                item = self.local_table.item(row, 0)
                if item:
                    path_str = item.data(Qt.ItemDataRole.UserRole)
                    if path_str:
                        self.delete_local_file(Path(path_str))
                        self.local_table.removeRow(row)

    def delete_selected_remote(self):
        """Delete selected remote files/folders"""
        tab = self.get_current_tab()
        if not tab:
            return

        selected_rows = set()
        for item in tab.remote_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            return

        # Confirm deletion
        count = len(selected_rows)
        if count == 1:
            message = "Are you sure you want to delete the selected remote item?"
        else:
            message = f"Are you sure you want to delete {count} selected remote items?"

        reply = QMessageBox.question(self, "Confirm Delete", message,
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            for row in sorted(selected_rows, reverse=True):  # Delete from bottom up
                item = tab.remote_table.item(row, 0)
                if item:
                    file_data = item.data(Qt.ItemDataRole.UserRole)
                    if file_data:
                        self.delete_remote_file(file_data)
                        tab.remote_table.removeRow(row)

    def rename_selected_local(self):
        """Rename selected local file/folder"""
        selected_rows = set()
        for item in self.local_table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) != 1:
            QMessageBox.warning(self, "Rename", "Please select exactly one item to rename.")
            return

        row = list(selected_rows)[0]
        item = self.local_table.item(row, 0)
        if item:
            old_path_str = item.data(Qt.ItemDataRole.UserRole)
            if old_path_str:
                old_path = Path(old_path_str)
                old_name = old_path.name

                new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=old_name)
                if ok and new_name and new_name != old_name:
                    new_path = old_path.parent / new_name
                    try:
                        old_path.rename(new_path)
                        # Update table
                        item.setText(f"📁 {new_name}" if old_path.is_dir() else f"📄 {new_name}")
                        item.setData(Qt.ItemDataRole.UserRole, str(new_path))
                        # Update other columns if needed
                        self.local_table.item(row, 2).setText(new_path.suffix or ("<Directory>" if new_path.is_dir() else "File"))
                    except Exception as e:
                        QMessageBox.critical(self, "Rename Error", f"Failed to rename: {e}")

    def rename_selected_remote(self):
        """Rename selected remote file/folder"""
        tab = self.get_current_tab()
        if not tab:
            return

        selected_rows = set()
        for item in tab.remote_table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) != 1:
            QMessageBox.warning(self, "Rename", "Please select exactly one item to rename.")
            return

        row = list(selected_rows)[0]
        item = tab.remote_table.item(row, 0)
        if item:
            file_data = item.data(Qt.ItemDataRole.UserRole)
            if file_data and hasattr(file_data, 'name'):
                old_name = file_data.name

                new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=old_name)
                if ok and new_name and new_name != old_name:
                    self.rename_remote_file(file_data, new_name)

    def create_local_folder(self):
        """Create new local folder"""
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and folder_name:
            try:
                new_folder = Path(self.current_local_path) / folder_name
                new_folder.mkdir(parents=True, exist_ok=False)
                self.load_local_files()  # Refresh
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create folder: {e}")

    def create_remote_folder(self):
        """Create new remote folder"""
        tab = self.get_current_tab()
        if not tab:
            return

        folder_name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and folder_name:
            self.create_remote_folder_at(tab.current_remote_path, folder_name)

    def enter_selected_local_directory(self):
        """Enter selected local directory"""
        selected_rows = set()
        for item in self.local_table.selectedItems():
            selected_rows.add(item.row())

        for row in selected_rows:
            item = self.local_table.item(row, 0)
            if item:
                path_str = item.data(Qt.ItemDataRole.UserRole)
                if path_str:
                    path = Path(path_str)
                    if path.is_dir():
                        self.navigate_local_with_sync(str(path))
                        break

    def enter_selected_remote_directory(self):
        """Enter selected remote directory"""
        tab = self.get_current_tab()
        if not tab:
            return

        selected_rows = set()
        for item in tab.remote_table.selectedItems():
            selected_rows.add(item.row())

        for row in selected_rows:
            item = tab.remote_table.item(row, 0)
            if item:
                file_data = item.data(Qt.ItemDataRole.UserRole)
                if file_data and getattr(file_data, 'is_dir', False):
                    self.navigate_remote_with_sync(file_data.path)
                    break

    def _on_local_selection_changed(self):
        """Handle local table selection changes"""
        selected_items = []
        for item in self.local_table.selectedItems():
            if item.column() == 0:  # Only count once per row
                row = item.row()
                file_item = self.local_table.item(row, 0)
                if file_item:
                    path_str = file_item.data(Qt.ItemDataRole.UserRole)
                    if path_str:
                        # Create a simple file info dict for the status bar
                        try:
                            path = Path(path_str)
                            file_info = {
                                'name': path.name,
                                'path': str(path.parent),
                                'size': path.stat().st_size if path.is_file() else 0,
                                'is_dir': path.is_dir()
                            }
                            selected_items.append(file_info)
                        except:
                            pass

        self.status_bar.update_selection_info(selected_items, is_local=True)

    def _on_local_item_changed(self, item):
        """Handle local table item changes (renaming)"""
        if item.column() != 0:  # Only handle filename column
            return

        row = item.row()
        new_name = item.text().strip()
        if not new_name:
            return

        # Get the original path
        original_item = self.local_table.item(row, 0)
        if not original_item:
            return

        original_path_str = original_item.data(Qt.ItemDataRole.UserRole)
        if not original_path_str:
            return

        original_path = Path(original_path_str)
        new_path = original_path.parent / new_name

        # Don't rename if name hasn't changed
        if new_path == original_path:
            return

        try:
            # Perform the rename
            original_path.rename(new_path)

            # Update the stored path data
            original_item.setData(Qt.ItemDataRole.UserRole, str(new_path))

            # Update other columns if needed
            if new_path.is_file():
                # Update file size
                size_str = self.format_size(new_path.stat().st_size)
                size_item = self.local_table.item(row, 1)
                if size_item:
                    size_item.setText(size_str)
                    size_item.setData(Qt.ItemDataRole.UserRole, new_path.stat().st_size)

                # Update file type
                type_item = self.local_table.item(row, 2)
                if type_item:
                    type_item.setText(new_path.suffix or "File")

            self.log(f"Renamed {original_path.name} to {new_name}")
            self.status_bar.show_message(f"Renamed to {new_name}")

        except Exception as e:
            # Revert the display name on error
            original_item.setText(original_path.name)
            QMessageBox.critical(self, "Rename Error", f"Failed to rename file:\n{str(e)}")
            self.log(f"Failed to rename {original_path.name}: {str(e)}", "error")

    def _on_remote_selection_changed(self):
        """Handle remote table selection changes"""
        tab = self.get_current_tab()
        if not tab:
            return

        selected_items = []
        for item in tab.remote_table.selectedItems():
            if item.column() == 0:  # Only count once per row
                row = item.row()
                file_item = tab.remote_table.item(row, 0)
                if file_item:
                    file_data = file_item.data(Qt.ItemDataRole.UserRole)
                    if file_data:
                        selected_items.append(file_data)

        self.status_bar.update_selection_info(selected_items, is_local=False)

    def _handle_local_drop(self, data, source="unknown"):
        """Handle drops onto local table"""
        if source == "remote":
            # Files dragged from remote to local
            self._handle_remote_file_drop(data)
        elif source == "fttp":
            # Files dragged between Fftp tables
            self._handle_fttp_drop_to_local(data)

    def _handle_local_drag(self, files):
        """Handle dragging files from local table"""
        # This is handled by the DragDropTableWidget
        pass

    def _handle_fttp_drop_to_local(self, data):
        """Handle Fftp file data dropped onto local table"""
        try:
            import json
            file_data = json.loads(data.decode())

            # Convert to local file operations
            for file_info in file_data:
                if not file_info.get('is_dir', False):
                    # For now, just show a message - could be enhanced to download
                    self.log(f"Would download {file_info['name']} to local directory", "info")

        except Exception as e:
            self.log(f"Error handling Fftp drop to local: {str(e)}", "error")

    def handle_file_drop(self, files, source="local"):
        """Handle files dropped onto remote table"""
        if source == "local":
            self._handle_local_file_drop(files)
        elif source == "remote":
            self._handle_remote_file_drop(files)
        elif source == "fttp":
            self._handle_fttp_file_drop(files)

    def _handle_local_file_drop(self, files):
        """Handle local files dropped onto remote table"""
        tab = self.get_current_tab()
        if not tab or not tab.manager:
            QMessageBox.warning(self, "Not Connected", "Please connect to a server first")
            return

        uploaded_count = 0
        failed_count = 0

        for path in files:
            try:
                if path.is_file():
                    # Upload file
                    remote_name = path.name
                    remote_path = f"{tab.current_remote_path}/{remote_name}" if tab.current_remote_path != "." else remote_name

                    success = self._upload_single_file(path, remote_path, tab.manager)
                    if success:
                        uploaded_count += 1
                        self.log(f"Uploaded {path.name} to {remote_path}")
                    else:
                        failed_count += 1
                        self.log(f"Failed to upload {path.name}", "error")

                elif path.is_dir():
                    # Upload directory recursively
                    success = self._upload_directory(path, tab.current_remote_path, tab.manager)
                    if success:
                        uploaded_count += 1
                        self.log(f"Uploaded directory {path.name}")
                    else:
                        failed_count += 1
                        self.log(f"Failed to upload directory {path.name}", "error")

            except Exception as e:
                failed_count += 1
                self.log(f"Upload error for {path.name}: {str(e)}", "error")

        # Show summary
        if uploaded_count > 0:
            self.status_bar.show_message(f"Successfully uploaded {uploaded_count} items")
            self.load_remote_files()  # Refresh remote view

        if failed_count > 0:
            QMessageBox.warning(self, "Upload Complete",
                              f"Uploaded {uploaded_count} items, {failed_count} failed")

    def _handle_remote_file_drop(self, files):
        """Handle remote files dropped onto local table"""
        tab = self.get_current_tab()
        if not tab or not tab.manager:
            QMessageBox.warning(self, "Not Connected", "Please connect to a server first")
            return

        downloaded_count = 0
        failed_count = 0

        for remote_path in files:
            try:
                # Extract filename from remote path
                remote_name = remote_path.split('/')[-1]
                local_path = Path(self.current_local_path) / remote_name

                success = self._download_single_file(remote_path, local_path, tab.manager)
                if success:
                    downloaded_count += 1
                    self.log(f"Downloaded {remote_name} to {local_path}")
                else:
                    failed_count += 1
                    self.log(f"Failed to download {remote_name}", "error")

            except Exception as e:
                failed_count += 1
                self.log(f"Download error for {remote_path}: {str(e)}", "error")

        # Show summary
        if downloaded_count > 0:
            self.status_bar.show_message(f"Successfully downloaded {downloaded_count} items")
            self.load_local_files()  # Refresh local view

        if failed_count > 0:
            QMessageBox.warning(self, "Download Complete",
                              f"Downloaded {downloaded_count} items, {failed_count} failed")

    def _handle_fttp_file_drop(self, data):
        """Handle files dragged between Fftp tables"""
        try:
            import json
            file_data = json.loads(data.decode())

            # Determine source and destination
            # This is a simplified implementation
            tab = self.get_current_tab()
            if tab and tab.manager:
                self._handle_local_file_drop([Path(item['name']) for item in file_data if not item.get('is_dir', False)])
            else:
                self.log("Cannot handle Fftp file drop: no active connection", "warning")

        except Exception as e:
            self.log(f"Error handling Fftp file drop: {str(e)}", "error")

    def _upload_single_file(self, local_path, remote_path, manager):
        """Upload a single file with proper error handling"""
        try:
            # Add to transfer queue instead of direct upload
            self.add_to_transfer_queue(
                "Upload",
                str(local_path),
                remote_path,
                local_path.stat().st_size,
                "Queued"
            )
            return True
        except Exception as e:
            self.log(f"Failed to queue upload for {local_path.name}: {str(e)}", "error")
            return False

    def _upload_directory(self, local_dir, remote_base, manager):
        """Upload a directory recursively"""
        try:
            # Create remote directory first
            remote_dir_name = local_dir.name
            remote_dir_path = f"{remote_base}/{remote_dir_name}" if remote_base != "." else remote_dir_name

            manager.create_directory(remote_dir_path)

            # Upload all files and subdirectories
            for item in local_dir.rglob('*'):
                if item.is_file():
                    # Calculate relative path
                    relative_path = item.relative_to(local_dir.parent)
                    remote_path = str(relative_path).replace('\\', '/')

                    self.add_to_transfer_queue(
                        "Upload",
                        str(item),
                        remote_path,
                        item.stat().st_size,
                        "Queued"
                    )

            return True
        except Exception as e:
            self.log(f"Failed to upload directory {local_dir.name}: {str(e)}", "error")
            return False

    def _download_single_file(self, remote_path, local_path, manager):
        """Download a single file with proper error handling"""
        try:
            # Add to transfer queue instead of direct download
            # For download, we need to estimate file size from remote
            file_size = 0  # TODO: Get actual file size from remote
            self.add_to_transfer_queue(
                "Download",
                str(local_path),
                remote_path,
                file_size,
                "Queued"
            )
            return True
        except Exception as e:
            self.log(f"Failed to queue download for {remote_path}: {str(e)}", "error")
            return False
    
