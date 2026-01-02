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
        """Initialize UI for this connection tab"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        remote_group = QGroupBox("Remote site")
        remote_group.setStyleSheet("""
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
        remote_layout = QVBoxLayout(remote_group)
        remote_layout.setContentsMargins(8, 8, 8, 8)
        remote_layout.setSpacing(4)
        
        remote_path_layout = QHBoxLayout()
        remote_path_layout.setSpacing(6)
        path_label = QLabel("Remote site:")
        path_label.setMinimumWidth(85)
        path_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 12px;")
        remote_path_layout.addWidget(path_label)
        self.remote_path_edit = QLineEdit()
        self.remote_path_edit.setText(self.current_remote_path)
        self.remote_path_edit.setStyleSheet("font-size: 12px; padding: 8px 12px; border: 2px solid #bdc3c7; border-radius: 5px;")
        remote_path_layout.addWidget(self.remote_path_edit, 1)
        remote_up_btn = QPushButton("↑")
        remote_up_btn.setMaximumWidth(44)
        remote_up_btn.setMinimumHeight(34)
        remote_up_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-weight: 600;
                font-size: 14px;
                color: #2c3e50;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
                border-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #bdc3c7;
            }
        """)
        self.remote_up_btn = remote_up_btn
        remote_path_layout.addWidget(remote_up_btn)

        # Add refresh and create folder buttons
        remote_refresh_btn = QPushButton("Refresh")
        remote_refresh_btn.setMaximumWidth(44)
        remote_refresh_btn.setMinimumHeight(34)
        remote_refresh_btn.setToolTip("Refresh remote files")
        remote_refresh_btn.setProperty("class", "secondary")
        remote_refresh_btn.clicked.connect(self.load_remote_files)
        remote_path_layout.addWidget(remote_refresh_btn)

        remote_new_folder_btn = QPushButton("New Folder")
        remote_new_folder_btn.setMaximumWidth(44)
        remote_new_folder_btn.setMinimumHeight(34)
        remote_new_folder_btn.setToolTip("Create new folder")
        remote_new_folder_btn.setProperty("class", "secondary")
        remote_new_folder_btn.clicked.connect(lambda: self.main_window.create_remote_folder())
        remote_path_layout.addWidget(remote_new_folder_btn)

        remote_layout.addLayout(remote_path_layout)

        # Remote file browser 
        remote_browser = QSplitter(Qt.Orientation.Horizontal)

        # Remote tree view
        self.remote_tree = QTreeWidget()
        self.remote_tree.setHeaderHidden(True)
        self.remote_tree.setRootIsDecorated(True)
        self.remote_tree.setAnimated(True)
        self.remote_tree.setIndentation(15)
        self.remote_tree.setStyleSheet("""
            QTreeWidget {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ffffff;
                font-size: 10px;
            }
            QTreeWidget::item {
                padding: 3px;
                border: none;
                color: #2c3e50;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QTreeWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        self.remote_tree.itemExpanded.connect(self.on_remote_tree_expanded)
        self.remote_tree.itemClicked.connect(self.on_remote_tree_clicked)
        self.remote_tree.itemDoubleClicked.connect(self.on_remote_tree_double_clicked)
        self.remote_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.remote_tree.customContextMenuRequested.connect(self.show_remote_tree_context_menu)
        remote_browser.addWidget(self.remote_tree)

        # Remote file list
        drag_drop_enabled = True
        self.remote_table = DragDropTableWidget(
            parent=self,
            drop_callback=None,  # Will be set by main window
            drag_callback=self._handle_remote_drag,
            enabled=drag_drop_enabled
        )
        self.remote_table.setColumnCount(4)
        self.remote_table.setHorizontalHeaderLabels(["Filename", "Filesize", "Filetype", "Last modified"])
        self.remote_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.remote_table.setAlternatingRowColors(True)
        self.remote_table.setSortingEnabled(True)
        self.remote_table.setSortingEnabled(True)
        # Table styling is handled by the global theme
        self.remote_table.setColumnWidth(0, 200)
        self.remote_table.setColumnWidth(1, 80)
        self.remote_table.setColumnWidth(2, 80)
        self.remote_table.setColumnWidth(3, 120)

        # Connect events
        self.remote_table.doubleClicked.connect(self.on_remote_table_double_click)
        self.remote_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.remote_table.customContextMenuRequested.connect(self._show_remote_context_menu)
        self.remote_table.itemSelectionChanged.connect(self._on_remote_selection_changed)

        remote_browser.addWidget(self.remote_table)

        remote_browser.setSizes([150, 350])
        remote_layout.addWidget(remote_browser)
        
        layout.addWidget(remote_group)
    
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

    def on_remote_table_double_click(self, index):
        """Handle remote table double-click"""
        row = index.row()
        if row >= 0:
            item = self.remote_table.item(row, 0)
            if item:
                file_data = item.data(Qt.ItemDataRole.UserRole)
                if file_data and hasattr(file_data, 'is_dir') and file_data.is_dir:
                    # Navigate into directory
                    new_path = file_data.path
                    self.current_remote_path = new_path
                    self.remote_path_edit.setText(new_path)
                    self.load_remote_files()

    # Helper methods (stubs - need to be implemented)
    def load_remote_files(self):
        """Load remote files for current path"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"TAB DEBUG: load_remote_files called, manager: {self.manager}, connected: {self.is_connected() if self.manager else False}")
        logger.info(f"TAB DEBUG: Current remote path: {self.current_remote_path}")
        logger.info(f"TAB DEBUG: Remote table exists: {hasattr(self, 'remote_table')}")
        
        if not self.manager or not self.is_connected():
            logger.warning("TAB DEBUG: Not connected, clearing table")
            if hasattr(self, 'remote_table'):
                self.remote_table.setRowCount(0)
            return

        if not hasattr(self, 'remote_table'):
            logger.error("TAB ERROR: remote_table does not exist!")
            return

        try:
            self.remote_table.setSortingEnabled(False)  # Disable sorting during load
            self.remote_table.setRowCount(0)

            logger.info(f"TAB DEBUG: Calling manager.list_files with path: {self.current_remote_path}")
            files = self.manager.list_files(self.current_remote_path)
            logger.info(f"TAB DEBUG: manager.list_files returned {len(files) if files else 0} files")
            
            if files:
                for i, f in enumerate(files[:5]):  # Log first 5 files
                    logger.info(f"TAB DEBUG: File {i}: name={f.name}, size={f.size}, is_dir={f.is_dir}, modified={f.modified}")

            if not files:
                print("TAB DEBUG: No files returned, showing empty message")
                # Show empty message
                self.remote_table.setRowCount(1)
                empty_item = QTableWidgetItem("(Directory is empty - Connection is working)")
                empty_item.setData(Qt.ItemDataRole.UserRole, None)
                self.remote_table.setItem(0, 0, empty_item)
                for col in range(1, 4):
                    empty_item = QTableWidgetItem("")
                    empty_item.setData(Qt.ItemDataRole.UserRole, None)
                    self.remote_table.setItem(0, col, empty_item)
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

            # Populate table with visible files
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"TAB DEBUG: Populating table with {len(visible_files)} visible files")
            for row, file in enumerate(visible_files):
                logger.info(f"TAB DEBUG: Adding file {row}: {file.name} (size={file.size}, is_dir={file.is_dir})")
                self.remote_table.insertRow(row)

                # Use proper icons from theme manager
                try:
                    if self.main_window and hasattr(self.main_window, 'icon_theme_manager'):
                        icon_theme_manager = self.main_window.icon_theme_manager
                        icon = icon_theme_manager.get_file_icon(file.name, is_dir=file.is_dir)
                        name_item = QTableWidgetItem(icon, file.name)
                        logger.debug(f"TAB DEBUG: Created item with icon for {file.name}")
                    else:
                        # Fallback to text-only if icon_theme_manager not available
                        name_item = QTableWidgetItem(file.name)
                        logger.warning(f"TAB DEBUG: icon_theme_manager not available, using text-only")
                except Exception as e:
                    logger.warning(f"TAB DEBUG: Icon loading failed for {file.name}: {e}")
                    # Fallback to text-only if icon loading fails
                    name_item = QTableWidgetItem(file.name)

                # Text color will be handled by theme, don't force black
                self.remote_table.setItem(row, 0, name_item)

                if file.is_dir:
                    size_item = QTableWidgetItem("<DIR>")
                    size_item.setData(Qt.ItemDataRole.UserRole, 0)
                else:
                    size_str = self.parent().format_size(file.size) if hasattr(self.parent(), 'format_size') else str(file.size)
                    from .table_managers import NumericTableWidgetItem
                    size_item = NumericTableWidgetItem(size_str)
                    size_item.setData(Qt.ItemDataRole.UserRole, file.size)

                self.remote_table.setItem(row, 1, size_item)

                type_item = QTableWidgetItem("Directory" if file.is_dir else "File")
                self.remote_table.setItem(row, 2, type_item)

                date_item = QTableWidgetItem(file.modified or "")
                self.remote_table.setItem(row, 3, date_item)

                self.remote_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, file)

            self.remote_table.setSortingEnabled(True)
            self.remote_table.resizeColumnsToContents()

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            error_msg = f"Error loading remote files: {e}"
            logger.error(f"TAB ERROR: {error_msg}")
            logger.error(f"TAB ERROR TRACEBACK:\n{traceback.format_exc()}")
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
