"""
Remote File Panel - Handles remote file browsing and connection tabs
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QGroupBox, QPushButton, QSplitter, QTreeWidget
)
from PyQt6.QtCore import Qt

from ..connection_tab import ConnectionTab


class RemoteFilePanel(QWidget):
    """Panel for remote file browsing and connection management"""

    def __init__(self, parent):
        super().__init__(parent)
        self.main_window = parent

        # Initialize components
        self.remote_tabs = None
        self.connection_tabs = {}
        self.active_tab_id = None
        self.title_label = None

        self.init_ui()

    def init_ui(self):
        """Initialize the remote file panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Remote file browser container
        remote_container = QWidget()
        remote_layout = QVBoxLayout(remote_container)
        remote_layout.setContentsMargins(8, 8, 8, 8)
        remote_layout.setSpacing(4)

        # Title bar
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(8, 8, 8, 4)

        self.title_label = QLabel("Remote Site - Not Connected")
        self.title_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #2c3e50; border: 2px solid #bdc3c7; border-radius: 5px; padding: 4px 8px;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        remote_layout.addWidget(title_bar)

        # Connection tabs
        self.remote_tabs = QTabWidget()
        self.remote_tabs.setTabsClosable(True)
        self.remote_tabs.tabCloseRequested.connect(self.close_tab)

        # Add initial empty tab (before connecting signal to avoid premature emission)
        self.add_empty_tab()

        # Update title for initial state
        self.update_title()

        # Connect signal after tab is added
        self.remote_tabs.currentChanged.connect(self.main_window.on_tab_changed)

        remote_layout.addWidget(self.remote_tabs)
        layout.addWidget(remote_container)

    def add_empty_tab(self):
        """Add an empty connection tab"""
        tab = ConnectionTab(main_window=self.main_window)
        tab_id = id(tab)

        self.connection_tabs[tab_id] = tab
        self.active_tab_id = tab_id

        tab_index = self.remote_tabs.addTab(tab, "New Connection")
        self.remote_tabs.setCurrentIndex(tab_index)

        # Set up tab connections
        self._setup_tab_connections(tab)

    def create_new_tab(self, config=None):
        """Create a new connection tab"""
        tab = ConnectionTab(main_window=self.main_window, config=config)
        tab_id = id(tab)

        self.connection_tabs[tab_id] = tab
        self.active_tab_id = tab_id

        # Set tab title
        title = tab.get_tab_title()
        tab_index = self.remote_tabs.addTab(tab, title)
        self.remote_tabs.setCurrentIndex(tab_index)

        # Set up tab connections
        self._setup_tab_connections(tab)

        return tab

    def _setup_tab_connections(self, tab):
        """Set up connections for a tab"""
        if hasattr(tab, 'remote_path_edit'):
            tab.remote_path_edit.returnPressed.connect(self.main_window.navigate_remote_path)
        if hasattr(tab, 'remote_up_btn'):
            tab.remote_up_btn.clicked.connect(self.main_window.remote_up)
        if hasattr(tab, 'remote_table'):
            tab.remote_table.doubleClicked.connect(self.main_window.on_remote_double_click)
            tab.remote_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            tab.remote_table.customContextMenuRequested.connect(self.main_window.show_remote_context_menu)

            # Set up drag and drop
            if hasattr(tab.remote_table, 'set_drag_drop_enabled'):
                drag_drop_enabled = self.main_window.settings.get('enable_drag_drop', True)
                tab.remote_table.set_drag_drop_enabled(drag_drop_enabled)
                tab.remote_table.drop_callback = self.main_window.handle_file_drop

    def close_tab(self, index):
        """Close a connection tab"""
        widget = self.remote_tabs.widget(index)
        if widget:
            tab_id = id(widget)

            # Clean up tab connections
            if hasattr(widget, 'connection_worker') and widget.connection_worker:
                widget.connection_worker.cancel()

            # Remove from tracking
            if tab_id in self.connection_tabs:
                del self.connection_tabs[tab_id]

            # Remove tab
            self.remote_tabs.removeTab(index)

            # If no tabs left, add empty one
            if self.remote_tabs.count() == 0:
                self.add_empty_tab()

    def get_current_tab(self):
        """Get the currently active tab"""
        if self.active_tab_id and self.active_tab_id in self.connection_tabs:
            return self.connection_tabs[self.active_tab_id]
        return None

    def get_tab_count(self):
        """Get the number of connection tabs"""
        return self.remote_tabs.count()

    def get_all_tabs(self):
        """Get all connection tabs"""
        return list(self.connection_tabs.values())

    def update_tab_title(self, tab, title):
        """Update the title of a tab"""
        for i in range(self.remote_tabs.count()):
            if self.remote_tabs.widget(i) == tab:
                self.remote_tabs.setTabText(i, title)
                break

    def set_active_tab(self, tab_id):
        """Set the active tab by ID"""
        if tab_id in self.connection_tabs:
            tab = self.connection_tabs[tab_id]
            for i in range(self.remote_tabs.count()):
                if self.remote_tabs.widget(i) == tab:
                    self.remote_tabs.setCurrentIndex(i)
                    self.active_tab_id = tab_id
                    break

    def update_title(self):
        """Update the remote panel title based on connection status"""
        if not self.title_label:
            return

        current_tab = self.get_current_tab()
        if current_tab and current_tab.manager and hasattr(current_tab.manager, 'is_connected') and current_tab.manager.is_connected():
            title = f"Remote Site - {current_tab.config.host if current_tab.config else 'Connected'}"
        else:
            title = "Remote Site - Not Connected"

        self.title_label.setText(title)