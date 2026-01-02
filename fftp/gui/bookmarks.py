"""
Bookmarks system for Fftp - manage local and remote directory bookmarks
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QInputDialog, QMessageBox, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction


@dataclass
class Bookmark:
    """Represents a directory bookmark"""
    name: str
    path: str
    type: str  # "local" or "remote"
    server_name: Optional[str] = None  # For remote bookmarks

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Bookmark':
        return cls(**data)


class BookmarkManager:
    """Manages bookmarks for local and remote directories"""

    def __init__(self):
        self.bookmarks_file = Path.home() / ".fftp" / "bookmarks.json"
        self.bookmarks_file.parent.mkdir(exist_ok=True)
        self.bookmarks: List[Bookmark] = []
        self.load_bookmarks()

    def load_bookmarks(self):
        """Load bookmarks from file"""
        if self.bookmarks_file.exists():
            try:
                with open(self.bookmarks_file, 'r') as f:
                    data = json.load(f)
                    self.bookmarks = [Bookmark.from_dict(item) for item in data]
            except Exception as e:
                print(f"Error loading bookmarks: {e}")
                self.bookmarks = []

    def save_bookmarks(self):
        """Save bookmarks to file"""
        try:
            data = [bookmark.to_dict() for bookmark in self.bookmarks]
            with open(self.bookmarks_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving bookmarks: {e}")

    def add_bookmark(self, name: str, path: str, bookmark_type: str, server_name: Optional[str] = None) -> bool:
        """Add a new bookmark"""
        # Check if bookmark already exists
        for bookmark in self.bookmarks:
            if bookmark.path == path and bookmark.type == bookmark_type:
                return False

        bookmark = Bookmark(name=name, path=path, type=bookmark_type, server_name=server_name)
        self.bookmarks.append(bookmark)
        self.save_bookmarks()
        return True

    def remove_bookmark(self, path: str, bookmark_type: str) -> bool:
        """Remove a bookmark"""
        for i, bookmark in enumerate(self.bookmarks):
            if bookmark.path == path and bookmark.type == bookmark_type:
                del self.bookmarks[i]
                self.save_bookmarks()
                return True
        return False

    def get_bookmarks(self, bookmark_type: Optional[str] = None) -> List[Bookmark]:
        """Get bookmarks, optionally filtered by type"""
        if bookmark_type:
            return [b for b in self.bookmarks if b.type == bookmark_type]
        return self.bookmarks.copy()

    def get_local_bookmarks(self) -> List[Bookmark]:
        """Get local bookmarks"""
        return self.get_bookmarks("local")

    def get_remote_bookmarks(self, server_name: Optional[str] = None) -> List[Bookmark]:
        """Get remote bookmarks, optionally filtered by server"""
        bookmarks = self.get_bookmarks("remote")
        if server_name:
            return [b for b in bookmarks if b.server_name == server_name]
        return bookmarks


class BookmarkDialog(QDialog):
    """Dialog for managing bookmarks"""

    def __init__(self, bookmark_manager: BookmarkManager, parent=None):
        super().__init__(parent)
        self.bookmark_manager = bookmark_manager
        self.setWindowTitle("Manage Bookmarks - Fftp")
        self.setGeometry(300, 300, 500, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Bookmarks list
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bookmarks_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.bookmarks_list)

        # Buttons
        button_layout = QHBoxLayout()

        add_btn = QPushButton("Add Current")
        add_btn.clicked.connect(self.add_current_directory)
        button_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_selected)
        button_layout.addWidget(remove_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.refresh_bookmarks()

    def refresh_bookmarks(self):
        """Refresh the bookmarks list"""
        self.bookmarks_list.clear()
        bookmarks = self.bookmark_manager.get_bookmarks()

        for bookmark in bookmarks:
            icon = "[LOCAL]" if bookmark.type == "local" else "[REMOTE]"
            server_info = f" ({bookmark.server_name})" if bookmark.server_name else ""
            item_text = f"{icon} {bookmark.name}{server_info}\n   {bookmark.path}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, bookmark)
            self.bookmarks_list.addItem(item)

    def add_current_directory(self):
        """Add current directory as bookmark"""
        parent = self.parent()
        if not parent:
            return

        # Get current directory info
        current_local = getattr(parent, 'current_local_path', '')
        current_tab = getattr(parent, 'get_current_tab', lambda: None)()

        # Add local bookmark
        if current_local:
            name, ok = QInputDialog.getText(self, "Add Local Bookmark",
                                          f"Bookmark name for: {current_local}")
            if ok and name:
                success = self.bookmark_manager.add_bookmark(name, current_local, "local")
                if success:
                    self.refresh_bookmarks()
                    QMessageBox.information(self, "Success", "Local bookmark added!")
                else:
                    QMessageBox.warning(self, "Warning", "Bookmark already exists!")

        # Add remote bookmark
        if current_tab and hasattr(current_tab, 'current_remote_path') and current_tab.current_remote_path:
            remote_path = current_tab.current_remote_path
            server_name = current_tab.config.host if hasattr(current_tab, 'config') else None

            name, ok = QInputDialog.getText(self, "Add Remote Bookmark",
                                          f"Bookmark name for: {remote_path}")
            if ok and name:
                success = self.bookmark_manager.add_bookmark(name, remote_path, "remote", server_name)
                if success:
                    self.refresh_bookmarks()
                    QMessageBox.information(self, "Success", "Remote bookmark added!")
                else:
                    QMessageBox.warning(self, "Warning", "Bookmark already exists!")

    def remove_selected(self):
        """Remove selected bookmark"""
        current_item = self.bookmarks_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a bookmark to remove!")
            return

        bookmark = current_item.data(Qt.ItemDataRole.UserRole)
        if bookmark:
            reply = QMessageBox.question(self, "Confirm Remove",
                                       f"Remove bookmark '{bookmark.name}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                success = self.bookmark_manager.remove_bookmark(bookmark.path, bookmark.type)
                if success:
                    self.refresh_bookmarks()
                    QMessageBox.information(self, "Success", "Bookmark removed!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to remove bookmark!")

    def show_context_menu(self, position):
        """Show context menu for bookmarks"""
        item = self.bookmarks_list.itemAt(position)
        if not item:
            return

        menu = QMenu(self)
        bookmark = item.data(Qt.ItemDataRole.UserRole)

        # Navigate to bookmark
        navigate_action = QAction("Navigate to Bookmark", self)
        navigate_action.triggered.connect(lambda: self.navigate_to_bookmark(bookmark))
        menu.addAction(navigate_action)

        menu.addSeparator()

        # Remove bookmark
        remove_action = QAction("Remove Bookmark", self)
        remove_action.triggered.connect(self.remove_selected)
        menu.addAction(remove_action)

        menu.exec(self.bookmarks_list.mapToGlobal(position))

    def navigate_to_bookmark(self, bookmark: Bookmark):
        """Navigate to the selected bookmark"""
        parent = self.parent()
        if not parent:
            return

        try:
            if bookmark.type == "local":
                # Navigate local directory
                if hasattr(parent, 'navigate_local_with_sync'):
                    parent.navigate_local_with_sync(bookmark.path)
            elif bookmark.type == "remote":
                # Navigate remote directory
                if hasattr(parent, 'navigate_remote_with_sync'):
                    parent.navigate_remote_with_sync(bookmark.path)

            self.accept()  # Close dialog
        except Exception as e:
            QMessageBox.critical(self, "Navigation Error", f"Failed to navigate: {e}")


def create_bookmark_menu(bookmark_manager: BookmarkManager, parent) -> QMenu:
    """Create a bookmarks menu for quick access"""
    menu = QMenu("Bookmarks", parent)

    # Local bookmarks submenu
    local_menu = menu.addMenu("Local")
    local_bookmarks = bookmark_manager.get_local_bookmarks()

    if local_bookmarks:
        for bookmark in local_bookmarks:
            action = QAction(bookmark.name, parent)
            action.setData(bookmark)
            action.triggered.connect(lambda checked, b=bookmark: parent.navigate_local_with_sync(b.path))
            local_menu.addAction(action)
    else:
        no_local_action = QAction("(No local bookmarks)", parent)
        no_local_action.setEnabled(False)
        local_menu.addAction(no_local_action)

    menu.addSeparator()

    # Remote bookmarks submenu
    remote_menu = menu.addMenu("Remote")
    remote_bookmarks = bookmark_manager.get_remote_bookmarks()

    if remote_bookmarks:
        for bookmark in remote_bookmarks:
            server_info = f" ({bookmark.server_name})" if bookmark.server_name else ""
            action = QAction(f"{bookmark.name}{server_info}", parent)
            action.setData(bookmark)
            action.triggered.connect(lambda checked, b=bookmark: parent.navigate_remote_with_sync(b.path))
            remote_menu.addAction(action)
    else:
        no_remote_action = QAction("(No remote bookmarks)", parent)
        no_remote_action.setEnabled(False)
        remote_menu.addAction(no_remote_action)

    menu.addSeparator()

    # Manage bookmarks
    manage_action = QAction("Manage Bookmarks...", parent)
    manage_action.triggered.connect(lambda: show_bookmark_dialog(bookmark_manager, parent))
    menu.addAction(manage_action)

    return menu


def show_bookmark_dialog(bookmark_manager: BookmarkManager, parent):
    """Show the bookmark management dialog"""
    dialog = BookmarkDialog(bookmark_manager, parent)
    dialog.exec()