"""
Connection tab widget for multiple server connections
"""

import os
import traceback
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QSplitter, QHeaderView, QMenu
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap
from ..models import ConnectionConfig, RemoteFile
from .drag_drop_table import DragDropTableWidget
from .context_menus import ContextMenuManager


class ConnectionTab(QWidget):
    """Tab widget for a single FTP/SFTP connection"""
    
    def __init__(self, main_window=None, config: ConnectionConfig = None):
        super().__init__(main_window if main_window else None)
        self.main_window = main_window
        self.config = config
        self.manager = None
        self.current_remote_path = "."
        self.connection_worker = None

        # Context menu manager
        self.context_menu_manager = ContextMenuManager(self.parent())

        self.init_ui()
    
    def init_ui(self):
        """Initialize the remote file panel UI - Aligned with LocalFilePanel"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # Removed 2px left margin for perfect parity

        remote_container = QWidget()
        remote_layout = QVBoxLayout(remote_container)
        remote_layout.setContentsMargins(0, 0, 0, 0)
        remote_layout.setSpacing(2)

        # Path navigation bar - Identical to Local
        remote_path_layout = QHBoxLayout()
        remote_path_layout.setContentsMargins(2, 2, 2, 2)
        remote_path_layout.setSpacing(4)

        self.remote_path_edit = QLineEdit()
        self.remote_path_edit.setText(self.current_remote_path)
        self.remote_path_edit.returnPressed.connect(self.navigate_remote_path)
        self.remote_path_edit.setPlaceholderText("Remote Path")
        self.remote_path_edit.setMinimumWidth(200)
        remote_path_layout.addWidget(self.remote_path_edit, 1)

        # Up button - Compact but visible
        remote_up_btn = QPushButton("Up")
        remote_up_btn.setFixedWidth(40)
        remote_up_btn.setMinimumHeight(24)
        remote_up_btn.setToolTip("Go up one directory")
        remote_up_btn.clicked.connect(self.remote_up)
        self.remote_up_btn = remote_up_btn
        remote_path_layout.addWidget(remote_up_btn)

        # Refresh button - Visible
        remote_refresh_btn = QPushButton("Refresh")
        remote_refresh_btn.setFixedWidth(65)
        remote_refresh_btn.setMinimumHeight(24)
        remote_refresh_btn.setToolTip("Refresh remote files")
        remote_refresh_btn.clicked.connect(self.load_remote_files)
        remote_path_layout.addWidget(remote_refresh_btn)

        # New Folder button - Extra but styled identical
        remote_new_folder_btn = QPushButton("New Folder")
        remote_new_folder_btn.setFixedWidth(85)
        remote_new_folder_btn.setMinimumHeight(24)
        remote_new_folder_btn.setToolTip("Create new folder")
        remote_new_folder_btn.clicked.connect(lambda: self.main_window.create_remote_folder())
        remote_path_layout.addWidget(remote_new_folder_btn)

        remote_layout.addLayout(remote_path_layout)

        # Remote file browser browser - Splitter identical to Local
        self.remote_splitter = QSplitter(Qt.Orientation.Vertical)

        # Remote tree view
        self.remote_tree = QTreeWidget()
        self.remote_tree.setHeaderHidden(True)
        self.remote_tree.setRootIsDecorated(True)
        self.remote_tree.setAnimated(True)
        self.remote_tree.setIndentation(20) # Match LocalFilePanel indentation
        self.remote_tree.setRootIsDecorated(True)
        self.remote_tree.itemExpanded.connect(self.on_remote_tree_expanded)
        self.remote_tree.itemClicked.connect(self.on_remote_tree_clicked)
        self.remote_tree.itemDoubleClicked.connect(self.on_remote_tree_double_clicked)
        self.remote_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.remote_tree.customContextMenuRequested.connect(self.show_remote_tree_context_menu)
        self.remote_tree.setMinimumHeight(150)
        self.remote_tree.setMinimumWidth(50)

        self.remote_splitter.addWidget(self.remote_tree)

        # Remote file list
        self.remote_table = DragDropTableWidget(
            parent=self,
            drop_callback=None,  # Will be set by main window
            drag_callback=self._handle_remote_drag,
            enabled=True
        )
        self.remote_table.setColumnCount(4)
        self.remote_table.setHorizontalHeaderLabels(["Filename", "Filesize", "Filetype", "Last modified"])
        self.remote_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.remote_table.setAlternatingRowColors(True)
        self.remote_table.setSortingEnabled(True)

        # Configure scroll bars
        self.remote_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.remote_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Set minimum height
        self.remote_table.setMinimumHeight(200)
        self.remote_table.setWordWrap(False)

        # Column widths identical to Local
        self.remote_table.setColumnWidth(0, 280)
        self.remote_table.setColumnWidth(1, 80)
        self.remote_table.setColumnWidth(2, 100)
        self.remote_table.setColumnWidth(3, 120)

        self.remote_table.horizontalHeader().setMinimumSectionSize(60)
        self.remote_table.horizontalHeader().setMaximumSectionSize(400)

        # Section resize modes
        self.remote_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.remote_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.remote_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.remote_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)

        self.remote_table.horizontalHeader().setStretchLastSection(False)

        # Connect events
        self.remote_table.doubleClicked.connect(self.on_remote_table_double_click)
        self.remote_table.keyPressEvent = self._remote_table_key_press
        self.remote_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.remote_table.customContextMenuRequested.connect(self._show_remote_context_menu)
        self.remote_table.itemSelectionChanged.connect(self._on_remote_selection_changed)

        self.remote_splitter.addWidget(self.remote_table)

        # Set splitter proportions (Directories above, Files below)
        self.remote_splitter.setSizes([200, 400])
        remote_layout.addWidget(self.remote_splitter)
        
        layout.addWidget(remote_container)
    
    def get_tab_title(self) -> str:
        """Get title for this tab"""
        if self.config:
            if self.manager:
                return f"{self.config.name} ({self.config.host}) ✓"
            return f"{self.config.name} ({self.config.host})"
        return "New Connection"
    
    def is_connected(self) -> bool:
        """Check if this tab is connected"""
        return self.manager is not None

    def load_remote_tree(self):
        """Load the remote directory tree"""
        if not self.manager or not self.is_connected():
            return

        try:
            # Clear existing tree
            self.remote_tree.clear()

            # Create root item
            root_item = QTreeWidgetItem(self.remote_tree)
            root_item.setText(0, "/")
            root_item.setData(0, Qt.ItemDataRole.UserRole, "/")

            # Set folder icon
            root_item.setIcon(0, QIcon("folder.png"))  # You might want to add proper icons

            # Load subdirectories for root
            self.load_remote_tree_children(root_item, "/")

            self.remote_tree.addTopLevelItem(root_item)
            root_item.setExpanded(True)

        except Exception as e:
            print(f"Error loading remote tree: {e}")

    def load_remote_tree_children(self, parent_item, path):
        """Load children for a tree item"""
        if not self.manager:
            return

        try:
            files = self.manager.list_files(path)
            for file in files:
                if file.is_dir and file.name not in [".", ".."]:
                    child_item = QTreeWidgetItem(parent_item)
                    child_item.setText(0, file.name)
                    child_item.setData(0, Qt.ItemDataRole.UserRole, file.path)
                    child_item.setIcon(0, QIcon("folder.png"))  # Add folder icon

                    # Add dummy child to show expand arrow
                    dummy = QTreeWidgetItem(child_item)
                    dummy.setText(0, "")
                    child_item.addChild(dummy)

        except Exception as e:
            print(f"Error loading tree children for {path}: {e}")

    def on_remote_tree_expanded(self, item):
        """Handle tree item expansion"""
        # Remove dummy child and load real children
        if item.childCount() == 1 and item.child(0).text(0) == "":
            item.takeChildren()  # Remove dummy
            path = item.data(0, Qt.ItemDataRole.UserRole)
            if path:
                self.load_remote_tree_children(item, path)

    def on_remote_tree_clicked(self, item, column):
        """Handle tree item click"""
        if item:
            path = item.data(column, Qt.ItemDataRole.UserRole)
            if path:
                self.parent().navigate_remote_with_sync(path)

    def on_remote_tree_double_clicked(self, item, column):
        """Handle tree item double-click"""
        if item:
            path = item.data(column, Qt.ItemDataRole.UserRole)
            if path:
                self.parent().navigate_remote_with_sync(path)

    def show_remote_tree_context_menu(self, position):
        """Show context menu for remote tree"""
        item = self.remote_tree.itemAt(position)
        if item:
            path = item.data(0, Qt.ItemDataRole.UserRole)
            if path:
                # Create context menu for remote tree
                menu = QMenu(self)

                if path != "/":
                    menu.addAction("Open", lambda: self.navigate_to_remote_path(path))
                    menu.addAction("Refresh", lambda: self.refresh_remote_tree_item(item))

                menu.addSeparator()
                menu.addAction("Create Directory...", lambda: self.create_remote_folder_at(path))
                menu.addSeparator()
                menu.addAction("Download to Local", lambda: self.download_remote_folder(path))

                menu.exec(self.remote_tree.mapToGlobal(position))

    def show_remote_table_context_menu(self, position):
        """Show context menu for remote table"""
        # Implementation for table context menu
        pass

    def navigate_remote_path(self):
        """Navigate to custom remote path"""
        if not self.manager:
            return
        path = self.remote_path_edit.text().strip()
        if not path:
            path = "/"
        # Try to navigate to the path
        try:
            # Check if path exists by listing it
            files = self.manager.list_files(path)
            self.current_remote_path = path
            # Update main window's current path too
            if hasattr(self.main_window, 'current_remote_path'):
                self.main_window.current_remote_path = path
            self.load_remote_files()
        except Exception:
            # If path doesn't exist or is invalid, stay on current path
            self.remote_path_edit.setText(self.current_remote_path)

    def remote_up(self):
        """Navigate up in remote directory"""
        if not self.manager:
            return

        path_parts = self.current_remote_path.rstrip('/').split('/')
        if len(path_parts) > 1:
            new_path = '/'.join(path_parts[:-1]) or '/'
        else:
            new_path = '/'

        # Try to navigate up
        try:
            files = self.manager.list_files(new_path)
            self.current_remote_path = new_path
            self.remote_path_edit.setText(new_path)
            # Update main window's current path too
            if hasattr(self.main_window, 'current_remote_path'):
                self.main_window.current_remote_path = new_path
            self.load_remote_files()
        except Exception:
            # If can't go up, stay on current path
            pass

    def on_remote_table_double_click(self, index):
        """Handle remote table double-click"""
        row = index.row()
        if row >= 0:
            item = self.remote_table.item(row, 0)
            if item:
                filename = item.text()
                file_data = item.data(Qt.ItemDataRole.UserRole)

                if filename == "..":
                    # Go up one directory
                    self.remote_up()
                elif file_data and hasattr(file_data, 'is_dir') and file_data.is_dir:
                    # Navigate into directory
                    new_path = file_data.path
                    self.current_remote_path = new_path
                    self.remote_path_edit.setText(new_path)
                    # Update main window's current path too
                    if hasattr(self.main_window, 'current_remote_path'):
                        self.main_window.current_remote_path = new_path
                    # Navigate with sync if enabled, otherwise just load
                    if self.main_window.synchronized_browsing:
                        self.main_window.navigate_remote_with_sync(new_path)
                    else:
                        self.load_remote_files()

    def _remote_table_key_press(self, event):
        """Handle key press events for remote table (Enter navigation)"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Get current selection
            current_row = self.remote_table.currentRow()
            if current_row >= 0:
                item = self.remote_table.item(current_row, 0)
                if item:
                    filename = item.text()
                    file_data = item.data(Qt.ItemDataRole.UserRole)

                    if filename == "..":
                        # Go up one directory
                        self.remote_up()
                    elif file_data and hasattr(file_data, 'is_dir') and file_data.is_dir:
                        # Navigate into directory
                        new_path = file_data.path
                        self.current_remote_path = new_path
                        self.remote_path_edit.setText(new_path)
                        # Update main window's current path too
                        if hasattr(self.main_window, 'current_remote_path'):
                            self.main_window.current_remote_path = new_path
                        self.load_remote_files()
        else:
            # Call the original key press event for other keys
            QTableWidget.keyPressEvent(self.remote_table, event)

    # Helper methods (stubs - need to be implemented)
    def load_remote_files(self):
        """Load remote files for current path"""
        import logging
        logger = logging.getLogger(__name__)

        if not self.manager or not self.is_connected():
            if hasattr(self, 'remote_table'):
                self.remote_table.setRowCount(0)
            return

        if not hasattr(self, 'remote_table'):
            return

        try:
            self.remote_table.setSortingEnabled(False)  # Disable sorting during load
            self.remote_table.setRowCount(0)

            files = self.manager.list_files(self.current_remote_path)

            if not files:
                # Empty directory - just clear the table
                self.remote_table.setRowCount(0)
                self.remote_table.setSortingEnabled(True)
                return

            # Process files with filtering
            visible_files = []
            for file in files:
                file_info = {
                    'name': file.name,
                    'path': self.current_remote_path,
                    'full_path': os.path.join(self.current_remote_path, file.name) if self.current_remote_path != "/" else f"/{file.name}",
                    'size': file.size,
                    'modified': file.modified,
                    'is_dir': file.is_dir
                }

                # Check if filtered (using parent's filter manager)
                if hasattr(self.parent(), 'filter_manager') and self.parent().filter_manager.is_filtered(file_info):
                    continue

                # Check if should be hidden in comparison mode
                if hasattr(self.parent(), 'comparison_manager') and self.parent().comparison_manager.comparator.should_hide_file(file.name):
                    continue

                visible_files.append(file)

            # Add parent directory entry (..) if not at root
            if self.current_remote_path and self.current_remote_path != "/" and self.current_remote_path != ".":
                self.remote_table.insertRow(0)
                parent_item = QTableWidgetItem("..")
                self.remote_table.setItem(0, 0, parent_item)
                self.remote_table.setItem(0, 1, QTableWidgetItem(""))
                self.remote_table.setItem(0, 2, QTableWidgetItem("Parent Directory"))
                self.remote_table.setItem(0, 3, QTableWidgetItem(""))

                # Create a mock file object for parent directory
                class ParentDir:
                    def __init__(self, path):
                        self.name = ".."
                        self.path = path
                        self.is_dir = True
                        self.size = 0
                        self.modified = ""
                parent_dir = ParentDir("/".join(self.current_remote_path.split("/")[:-1]) or "/")
                self.remote_table.item(0, 0).setData(Qt.ItemDataRole.UserRole, parent_dir)

            # Populate table with visible files
            for i, file in enumerate(visible_files):
                row = i + (1 if self.current_remote_path and self.current_remote_path != "/" and self.current_remote_path != "." else 0)
                self.remote_table.insertRow(row)

                # Simple text-only display (no icons needed for clean UI)
                name_item = QTableWidgetItem(file.name)

                # Text color will be handled by theme, don't force black
                self.remote_table.setItem(row, 0, name_item)

                if file.is_dir:
                    size_item = QTableWidgetItem("")
                    size_item.setData(Qt.ItemDataRole.UserRole, 0)
                else:
                    try:
                        from ..table_managers import format_size, NumericTableWidgetItem
                        size_str = format_size(file.size)
                        size_item = NumericTableWidgetItem(size_str)
                        size_item.setData(Qt.ItemDataRole.UserRole, file.size)
                    except ImportError:
                        # Fallback if import fails
                        size_str = f"{file.size}"
                        size_item = QTableWidgetItem(size_str)
                        size_item.setData(Qt.ItemDataRole.UserRole, file.size)

                self.remote_table.setItem(row, 1, size_item)

                type_item = QTableWidgetItem("Directory" if file.is_dir else "File")
                self.remote_table.setItem(row, 2, type_item)

                date_item = QTableWidgetItem(file.modified or "")
                self.remote_table.setItem(row, 3, date_item)

                self.remote_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, file)

            self.remote_table.setSortingEnabled(True)
            self.remote_table.resizeColumnsToContents()
            self.remote_table.viewport().update()  # Force refresh
            self.remote_table.repaint()  # Force repaint


        except Exception as e:
            # Show error in table
            if hasattr(self, 'remote_table'):
                self.remote_table.setRowCount(1)
                error_item = QTableWidgetItem(f"Error: {str(e)}")
                error_item.setForeground(Qt.GlobalColor.red)
                self.remote_table.setItem(0, 0, error_item)
                for col in range(1, 4):
                    empty_item = QTableWidgetItem("")
                    self.remote_table.setItem(0, col, empty_item)
                self.remote_table.setSortingEnabled(True)

    def navigate_to_remote_path(self, path):
        """Navigate to remote path"""
        self.current_remote_path = path
        self.remote_path_edit.setText(path)
        self.load_remote_files()

    def refresh_remote_tree_item(self, item):
        """Refresh a tree item"""
        # Implementation needed
        pass

    def create_remote_folder_at(self, path):
        """Create remote folder at path"""
        # Implementation needed
        pass

    def download_remote_folder(self, path):
        """Download remote folder"""
        # Implementation needed
        pass

    def show_remote_tree_context_menu(self, position):
        """Show context menu for remote tree"""
        self.context_menu_manager.create_remote_tree_context_menu(self.remote_tree, position)

    def _handle_remote_drag(self, files):
        """Handle dragging files from remote table"""
        # This will be called by the DragDropTableWidget when a drag starts
        # The actual drag handling is done in the table widget's startDrag method
        pass

    def _show_remote_context_menu(self, position):
        """Show enhanced remote context menu"""
        selected_items = self.remote_table.selectedItems()
        self.context_menu_manager.create_remote_context_menu(self.remote_table, position, selected_items)

    def _on_remote_selection_changed(self):
        """Handle remote table selection changes"""
        if hasattr(self.parent(), 'status_bar'):
            selected_items = []
            for item in self.remote_table.selectedItems():
                if item.column() == 0:  # Only count once per row
                    row = item.row()
                    file_item = self.remote_table.item(row, 0)
                    if file_item:
                        file_data = file_item.data(Qt.ItemDataRole.UserRole)
                        if file_data:
                            selected_items.append(file_data)

            self.parent().status_bar.update_selection_info(selected_items, is_local=False)
