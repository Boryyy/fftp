"""
Menu Manager - Manages application menus
Created as part of Phase 13: Main Window Decomposition
"""

from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt


class MenuManager:
    """Manages the main window menu bar and all menus"""
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.menubar = None
        
        # Menu references
        self.file_menu = None
        self.edit_menu = None
        self.view_menu = None
        self.transfer_menu = None
        self.bookmarks_menu = None
        self.tools_menu = None
        self.help_menu = None
        
        # Action references
        self.actions = {}
    
    def create_menus(self):
        """Create all application menus"""
        self.menubar = self.parent.menuBar()
        
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_transfer_menu()
        self._create_bookmarks_menu()
        self._create_tools_menu()
        self._create_help_menu()
    
    def _create_file_menu(self):
        """Create File menu"""
        self.file_menu = self.menubar.addMenu("&File")
        
        # Site Manager
        site_manager_action = QAction("&Site Manager...", self.parent)
        site_manager_action.setShortcut(QKeySequence("Ctrl+S"))
        site_manager_action.setStatusTip("Open Site Manager")
        site_manager_action.triggered.connect(self.parent.show_site_manager)
        self.file_menu.addAction(site_manager_action)
        self.actions['site_manager'] = site_manager_action
        
        self.file_menu.addSeparator()
        
        # New Tab
        new_tab_action = QAction("New &Tab", self.parent)
        new_tab_action.setShortcut(QKeySequence("Ctrl+T"))
        new_tab_action.setStatusTip("Open new connection tab")
        new_tab_action.triggered.connect(lambda: self.parent.show_site_manager())
        self.file_menu.addAction(new_tab_action)
        self.actions['new_tab'] = new_tab_action
        
        # Close Tab
        close_tab_action = QAction("&Close Tab", self.parent)
        close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        close_tab_action.setStatusTip("Close current tab")
        close_tab_action.triggered.connect(lambda: self.parent.disconnect())
        self.file_menu.addAction(close_tab_action)
        self.actions['close_tab'] = close_tab_action
        
        self.file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self.parent)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.parent.close)
        self.file_menu.addAction(exit_action)
        self.actions['exit'] = exit_action
    
    def _create_edit_menu(self):
        """Create Edit menu"""
        self.edit_menu = self.menubar.addMenu("&Edit")
        
        # Settings
        settings_action = QAction("&Settings...", self.parent)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.setStatusTip("Open Settings")
        settings_action.triggered.connect(self.parent.show_settings)
        self.edit_menu.addAction(settings_action)
        self.actions['settings'] = settings_action
        
        self.edit_menu.addSeparator()
        
        # Filters
        filters_action = QAction("&Filename Filters...", self.parent)
        filters_action.setStatusTip("Configure filename filters")
        if hasattr(self.parent, 'show_filter_dialog'):
            filters_action.triggered.connect(self.parent.show_filter_dialog)
        self.edit_menu.addAction(filters_action)
        self.actions['filters'] = filters_action
    
    def _create_view_menu(self):
        """Create View menu"""
        self.view_menu = self.menubar.addMenu("&View")
        
        # Refresh
        refresh_action = QAction("&Refresh", self.parent)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.setStatusTip("Refresh file lists")
        refresh_action.triggered.connect(self.parent.refresh_files)
        self.view_menu.addAction(refresh_action)
        self.actions['refresh'] = refresh_action
        
        self.view_menu.addSeparator()
        
        # Toggle panels
        toggle_local_action = QAction("Show &Local Panel", self.parent)
        toggle_local_action.setCheckable(True)
        toggle_local_action.setChecked(True)
        self.view_menu.addAction(toggle_local_action)
        self.actions['toggle_local'] = toggle_local_action
        
        toggle_remote_action = QAction("Show &Remote Panel", self.parent)
        toggle_remote_action.setCheckable(True)
        toggle_remote_action.setChecked(True)
        self.view_menu.addAction(toggle_remote_action)
        self.actions['toggle_remote'] = toggle_remote_action
        
        toggle_queue_action = QAction("Show &Queue Panel", self.parent)
        toggle_queue_action.setCheckable(True)
        toggle_queue_action.setChecked(True)
        self.view_menu.addAction(toggle_queue_action)
        self.actions['toggle_queue'] = toggle_queue_action
        
        toggle_log_action = QAction("Show &Message Log", self.parent)
        toggle_log_action.setCheckable(True)
        toggle_log_action.setChecked(True)
        self.view_menu.addAction(toggle_log_action)
        self.actions['toggle_log'] = toggle_log_action
    
    def _create_transfer_menu(self):
        """Create Transfer menu"""
        self.transfer_menu = self.menubar.addMenu("&Transfer")
        
        # Process Queue
        process_queue_action = QAction("&Process Queue", self.parent)
        process_queue_action.setShortcut(QKeySequence("Ctrl+P"))
        process_queue_action.setStatusTip("Start processing transfer queue")
        self.transfer_menu.addAction(process_queue_action)
        self.actions['process_queue'] = process_queue_action
        
        # Cancel
        cancel_action = QAction("&Cancel Current Transfer", self.parent)
        cancel_action.setShortcut(QKeySequence("Ctrl+C"))
        cancel_action.setStatusTip("Cancel current transfer")
        self.transfer_menu.addAction(cancel_action)
        self.actions['cancel_transfer'] = cancel_action
        
        self.transfer_menu.addSeparator()
        
        # Speed limits
        speed_limits_menu = self.transfer_menu.addMenu("Speed &Limits")
        
        unlimited_action = QAction("&Unlimited", self.parent)
        unlimited_action.setCheckable(True)
        unlimited_action.setChecked(True)
        speed_limits_menu.addAction(unlimited_action)
        self.actions['speed_unlimited'] = unlimited_action
    
    def _create_bookmarks_menu(self):
        """Create Bookmarks menu"""
        self.bookmarks_menu = self.menubar.addMenu("&Bookmarks")
        
        # Manage Bookmarks
        manage_bookmarks_action = QAction("&Manage Bookmarks...", self.parent)
        manage_bookmarks_action.setShortcut(QKeySequence("Ctrl+B"))
        manage_bookmarks_action.setStatusTip("Manage bookmarks")
        if hasattr(self.parent, 'show_bookmark_dialog'):
            manage_bookmarks_action.triggered.connect(self.parent.show_bookmark_dialog)
        self.bookmarks_menu.addAction(manage_bookmarks_action)
        self.actions['manage_bookmarks'] = manage_bookmarks_action
        
        self.bookmarks_menu.addSeparator()
        
        # Add current
        add_bookmark_action = QAction("&Add Current Connection", self.parent)
        add_bookmark_action.setShortcut(QKeySequence("Ctrl+D"))
        add_bookmark_action.setStatusTip("Bookmark current connection")
        self.bookmarks_menu.addAction(add_bookmark_action)
        self.actions['add_bookmark'] = add_bookmark_action
    
    def _create_tools_menu(self):
        """Create Tools menu"""
        self.tools_menu = self.menubar.addMenu("&Tools")
        
        # Search
        search_action = QAction("&Search Remote Files...", self.parent)
        search_action.setShortcut(QKeySequence("Ctrl+F"))
        search_action.setStatusTip("Search remote files")
        if hasattr(self.parent, 'show_search_dialog'):
            search_action.triggered.connect(self.parent.show_search_dialog)
        self.tools_menu.addAction(search_action)
        self.actions['search'] = search_action
        
        # Compare Directories
        compare_action = QAction("&Compare Directories", self.parent)
        compare_action.setStatusTip("Compare local and remote directories")
        if hasattr(self.parent, 'toggle_comparison'):
            compare_action.triggered.connect(self.parent.toggle_comparison)
        self.tools_menu.addAction(compare_action)
        self.actions['compare'] = compare_action
        
        self.tools_menu.addSeparator()
        
        # Export/Import
        export_action = QAction("&Export Settings...", self.parent)
        export_action.setStatusTip("Export settings to file")
        self.tools_menu.addAction(export_action)
        self.actions['export'] = export_action
        
        import_action = QAction("&Import Settings...", self.parent)
        import_action.setStatusTip("Import settings from file")
        self.tools_menu.addAction(import_action)
        self.actions['import'] = import_action
    
    def _create_help_menu(self):
        """Create Help menu"""
        self.help_menu = self.menubar.addMenu("&Help")
        
        # Documentation
        docs_action = QAction("&Documentation", self.parent)
        docs_action.setShortcut(QKeySequence("F1"))
        docs_action.setStatusTip("Open documentation")
        if hasattr(self.parent, 'show_help'):
            docs_action.triggered.connect(self.parent.show_help)
        self.help_menu.addAction(docs_action)
        self.actions['docs'] = docs_action
        
        # Keyboard Shortcuts
        shortcuts_action = QAction("&Keyboard Shortcuts", self.parent)
        shortcuts_action.setStatusTip("View keyboard shortcuts")
        if hasattr(self.parent, 'show_keyboard_shortcuts'):
            shortcuts_action.triggered.connect(self.parent.show_keyboard_shortcuts)
        self.help_menu.addAction(shortcuts_action)
        self.actions['shortcuts'] = shortcuts_action
        
        self.help_menu.addSeparator()
        
        # About
        about_action = QAction("&About FFTP", self.parent)
        about_action.setStatusTip("About FFTP")
        if hasattr(self.parent, 'show_about'):
            about_action.triggered.connect(self.parent.show_about)
        self.help_menu.addAction(about_action)
        self.actions['about'] = about_action
    
    def get_action(self, action_name: str) -> QAction:
        """Get action by name"""
        return self.actions.get(action_name)
    
    def enable_action(self, action_name: str, enabled: bool = True):
        """Enable/disable an action"""
        action = self.get_action(action_name)
        if action:
            action.setEnabled(enabled)
    
    def update_connection_state(self, connected: bool):
        """Update menu items based on connection state"""
        # Enable/disable actions based on connection
        self.enable_action('close_tab', connected)
        self.enable_action('add_bookmark', connected)
        self.enable_action('search', connected)
        self.enable_action('compare', connected)
