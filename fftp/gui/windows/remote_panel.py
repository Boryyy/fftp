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
        """Initialize the remote file panel UI - Simplified for Modern Minimalism"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Connection tabs - Use flat style from ThemeManager
        self.remote_tabs = QTabWidget()
        self.remote_tabs.setTabsClosable(True)
        self.remote_tabs.setDocumentMode(True) # Cleaner look on some platforms
        self.remote_tabs.tabCloseRequested.connect(self.close_tab)

        # Add initial empty tab
        self.add_empty_tab()

        # Connect signal after tab is added
        self.remote_tabs.currentChanged.connect(self.main_window.on_tab_changed)

        layout.addWidget(self.remote_tabs)

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
        """No additional connections needed as ConnectionTab handles its own signals"""
        pass

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