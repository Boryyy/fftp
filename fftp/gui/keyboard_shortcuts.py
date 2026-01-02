"""
Keyboard shortcuts system for Fftp
"""

from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt
from typing import Dict, Callable


class KeyboardShortcutsManager:
    """Manages keyboard shortcuts for Fftp"""

    def __init__(self, parent):
        self.parent = parent
        self.shortcuts: Dict[str, QShortcut] = {}
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """Set up all keyboard shortcuts"""
        shortcuts_config = {
            # Connection shortcuts
            "connect": ("Ctrl+Shift+C", "Connect to server", self._connect),
            "disconnect": ("Ctrl+Shift+D", "Disconnect from server", self._disconnect),

            # File operations
            "upload": ("Ctrl+U", "Upload selected files", self._upload),
            "download": ("Ctrl+D", "Download selected files", self._download),
            "new_folder": ("Ctrl+Shift+N", "Create new folder", self._new_folder),
            "delete": ("Delete", "Delete selected items", self._delete),
            "rename": ("F2", "Rename selected item", self._rename),

            # Navigation
            "refresh": ("F5", "Refresh file lists", self._refresh),
            "parent_directory": ("Backspace", "Go to parent directory", self._parent_directory),
            "enter_directory": ("Return", "Enter selected directory", self._enter_directory),

            # Search and find
            "search": ("Ctrl+F", "Search files", self._search),
            "filter": ("Ctrl+Shift+F", "Toggle filters", self._toggle_filters),

            # Bookmarks
            "bookmarks": ("Ctrl+B", "Show bookmarks", self._show_bookmarks),
            "add_bookmark": ("Ctrl+Shift+B", "Add current directory to bookmarks", self._add_bookmark),

            # View operations
            "directory_comparison": ("Ctrl+Shift+M", "Toggle directory comparison", self._toggle_comparison),
            "synchronized_browsing": ("Ctrl+Alt+S", "Toggle synchronized browsing", self._toggle_sync),

            # Application
            "settings": ("Ctrl+,", "Open settings", self._settings),
            "help": ("F1", "Show help", self._help),
            "quit": ("Ctrl+Q", "Quit application", self._quit),

            # Tab operations (for multiple connections)
            "new_tab": ("Ctrl+T", "New connection tab", self._new_tab),
            "close_tab": ("Ctrl+W", "Close current tab", self._close_tab),
            "next_tab": ("Ctrl+Tab", "Next tab", self._next_tab),
            "prev_tab": ("Ctrl+Shift+Tab", "Previous tab", self._prev_tab),

            # Transfer queue
            "process_queue": ("Ctrl+P", "Process transfer queue", self._process_queue),
            "cancel_all": ("Ctrl+Shift+X", "Cancel all transfers", self._cancel_all),
            "pause_all": ("Ctrl+Shift+P", "Pause/resume all transfers", self._pause_resume_all),
        }

        for action_name, (key_sequence, description, callback) in shortcuts_config.items():
            shortcut = QShortcut(QKeySequence(key_sequence), self.parent)
            shortcut.activated.connect(callback)
            shortcut.setWhatsThis(description)
            self.shortcuts[action_name] = shortcut

    # Connection shortcuts
    def _connect(self):
        """Connect to server"""
        if hasattr(self.parent, 'quick_connect'):
            self.parent.quick_connect()

    def _disconnect(self):
        """Disconnect from server"""
        if hasattr(self.parent, 'disconnect'):
            self.parent.disconnect()

    # File operations
    def _upload(self):
        """Upload selected files"""
        if hasattr(self.parent, 'upload_selected_local'):
            self.parent.upload_selected_local()

    def _download(self):
        """Download selected files"""
        if hasattr(self.parent, 'download_selected_remote'):
            self.parent.download_selected_remote()

    def _new_folder(self):
        """Create new folder"""
        if hasattr(self.parent, 'create_local_folder'):
            self.parent.create_local_folder()

    def _delete(self):
        """Delete selected items"""
        # Determine which table has focus
        if hasattr(self.parent, 'local_table') and self.parent.local_table.hasFocus():
            if hasattr(self.parent, 'delete_selected_local'):
                self.parent.delete_selected_local()
        elif hasattr(self.parent, 'remote_tabs'):
            current_tab = self.parent.get_current_tab()
            if current_tab and hasattr(current_tab, 'remote_table') and current_tab.remote_table.hasFocus():
                if hasattr(self.parent, 'delete_selected_remote'):
                    self.parent.delete_selected_remote()

    def _rename(self):
        """Rename selected item"""
        # Determine which table has focus
        if hasattr(self.parent, 'local_table') and self.parent.local_table.hasFocus():
            if hasattr(self.parent, 'rename_selected_local'):
                self.parent.rename_selected_local()
        elif hasattr(self.parent, 'remote_tabs'):
            current_tab = self.parent.get_current_tab()
            if current_tab and hasattr(current_tab, 'remote_table') and current_tab.remote_table.hasFocus():
                if hasattr(self.parent, 'rename_selected_remote'):
                    self.parent.rename_selected_remote()

    # Navigation
    def _refresh(self):
        """Refresh file lists"""
        if hasattr(self.parent, 'refresh_files'):
            self.parent.refresh_files()

    def _parent_directory(self):
        """Go to parent directory"""
        # Determine which side has focus
        if hasattr(self.parent, 'local_table') and self.parent.local_table.hasFocus():
            if hasattr(self.parent, 'local_up'):
                self.parent.local_up()
        elif hasattr(self.parent, 'remote_tabs'):
            current_tab = self.parent.get_current_tab()
            if current_tab and hasattr(current_tab, 'remote_table') and current_tab.remote_table.hasFocus():
                if hasattr(current_tab, 'remote_up'):
                    current_tab.remote_up()

    def _enter_directory(self):
        """Enter selected directory"""
        # Determine which table has focus
        if hasattr(self.parent, 'local_table') and self.parent.local_table.hasFocus():
            if hasattr(self.parent, 'enter_selected_local_directory'):
                self.parent.enter_selected_local_directory()
        elif hasattr(self.parent, 'remote_tabs'):
            current_tab = self.parent.get_current_tab()
            if current_tab and hasattr(current_tab, 'remote_table') and current_tab.remote_table.hasFocus():
                if hasattr(self.parent, 'enter_selected_remote_directory'):
                    self.parent.enter_selected_remote_directory()

    # Search and find
    def _search(self):
        """Search files"""
        if hasattr(self.parent, 'show_search_dialog'):
            self.parent.show_search_dialog()

    def _toggle_filters(self):
        """Toggle filters"""
        if hasattr(self.parent, 'toggle_filters'):
            self.parent.toggle_filters()

    # Bookmarks
    def _show_bookmarks(self):
        """Show bookmarks dialog"""
        from .bookmarks import show_bookmark_dialog
        if hasattr(self.parent, 'bookmark_manager'):
            show_bookmark_dialog(self.parent.bookmark_manager, self.parent)

    def _add_bookmark(self):
        """Add current directory to bookmarks"""
        if hasattr(self.parent, 'bookmark_manager'):
            # This would open a quick add dialog or use current directory
            # For now, just show the bookmarks dialog
            self._show_bookmarks()

    # View operations
    def _toggle_comparison(self):
        """Toggle directory comparison"""
        if hasattr(self.parent, 'toggle_directory_comparison'):
            self.parent.toggle_directory_comparison()

    def _toggle_sync(self):
        """Toggle synchronized browsing"""
        if hasattr(self.parent, 'toggle_synchronized_browsing'):
            self.parent.toggle_synchronized_browsing()

    # Application
    def _settings(self):
        """Open settings"""
        if hasattr(self.parent, 'show_settings'):
            self.parent.show_settings()

    def _help(self):
        """Show help"""
        if hasattr(self.parent, 'show_help'):
            self.parent.show_help()

    def _quit(self):
        """Quit application"""
        if hasattr(self.parent, 'close'):
            self.parent.close()

    # Tab operations
    def _new_tab(self):
        """New connection tab"""
        if hasattr(self.parent, 'create_new_tab'):
            self.parent.create_new_tab()

    def _close_tab(self):
        """Close current tab"""
        if hasattr(self.parent, 'close_connection_tab'):
            current_index = self.parent.remote_tabs.currentIndex()
            if current_index >= 0:
                self.parent.close_connection_tab(current_index)

    def _next_tab(self):
        """Next tab"""
        if hasattr(self.parent, 'remote_tabs'):
            current_index = self.parent.remote_tabs.currentIndex()
            next_index = (current_index + 1) % self.parent.remote_tabs.count()
            self.parent.remote_tabs.setCurrentIndex(next_index)

    def _prev_tab(self):
        """Previous tab"""
        if hasattr(self.parent, 'remote_tabs'):
            current_index = self.parent.remote_tabs.currentIndex()
            prev_index = (current_index - 1) % self.parent.remote_tabs.count()
            self.parent.remote_tabs.setCurrentIndex(prev_index)

    # Transfer queue
    def _process_queue(self):
        """Process transfer queue"""
        if hasattr(self.parent, 'process_queue_manually'):
            self.parent.process_queue_manually()

    def _cancel_all(self):
        """Cancel all transfers"""
        if hasattr(self.parent, 'cancel_all_transfers'):
            self.parent.cancel_all_transfers()

    def _pause_resume_all(self):
        """Pause/resume all transfers"""
        if hasattr(self.parent, 'pause_all_transfers'):
            self.parent.pause_all_transfers()

    def get_shortcuts_list(self) -> list:
        """Get list of all shortcuts for display"""
        shortcuts_list = []
        for action_name, shortcut in self.shortcuts.items():
            key_sequence = shortcut.key().toString()
            description = shortcut.whatsThis()
            shortcuts_list.append({
                'action': action_name,
                'shortcut': key_sequence,
                'description': description
            })
        return shortcuts_list


def show_keyboard_shortcuts_dialog(parent):
    """Show a dialog displaying all available keyboard shortcuts"""
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel

    dialog = QDialog(parent)
    dialog.setWindowTitle("Keyboard Shortcuts - Fftp")
    dialog.setGeometry(300, 300, 600, 500)

    layout = QVBoxLayout(dialog)

    # Header
    header = QLabel("Available Keyboard Shortcuts")
    header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
    layout.addWidget(header)

    # Table
    table = QTableWidget()
    table.setColumnCount(3)
    table.setHorizontalHeaderLabels(["Action", "Shortcut", "Description"])
    table.setAlternatingRowColors(True)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    # Get shortcuts from parent if available
    shortcuts_list = []
    if hasattr(parent, 'keyboard_shortcuts'):
        shortcuts_list = parent.keyboard_shortcuts.get_shortcuts_list()

    table.setRowCount(len(shortcuts_list))

    for row, shortcut_info in enumerate(shortcuts_list):
        table.setItem(row, 0, QTableWidgetItem(shortcut_info['action'].replace('_', ' ').title()))
        table.setItem(row, 1, QTableWidgetItem(shortcut_info['shortcut']))
        table.setItem(row, 2, QTableWidgetItem(shortcut_info['description']))

    table.resizeColumnsToContents()
    layout.addWidget(table)

    # Buttons
    button_layout = QHBoxLayout()
    button_layout.addStretch()

    close_btn = QPushButton("Close")
    close_btn.clicked.connect(dialog.accept)
    button_layout.addWidget(close_btn)

    layout.addLayout(button_layout)

    dialog.exec()