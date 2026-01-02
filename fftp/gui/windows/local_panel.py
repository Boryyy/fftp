"""
Local File Panel - Handles local file browsing and operations
"""

from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QGroupBox, QPushButton,
    QTreeView, QSplitter, QHeaderView
)
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QColor

try:
    from ..table_managers import NumericTableWidgetItem, format_size
except ImportError:
    # Fallback if import fails
    class NumericTableWidgetItem:
        def __init__(self, text):
            pass
    def format_size(size):
        return f"{size}"
from ..drag_drop_table import DragDropTableWidget


class LocalFilePanel(QWidget):
    """Panel for local file browsing and operations"""

    def __init__(self, parent, initial_path: str):
        super().__init__(parent)
        self.parent = parent
        self.current_local_path = initial_path

        # Initialize UI components
        self.local_table = None
        self.local_tree = None
        self.local_tree_model = None
        self.local_path_edit = None

        self.init_ui()

    def init_ui(self):
        """Initialize the local file panel UI - Simplified for Modern Minimalism"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # Removed 2px right margin for perfect parity
  # Minimal right margin for separation

        local_container = QWidget()
        local_layout = QVBoxLayout(local_container)
        local_layout.setContentsMargins(0, 0, 0, 0)
        local_layout.setSpacing(2)

        # Path navigation bar - Simplified
        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(2, 2, 2, 2)
        path_layout.setSpacing(4)

        self.local_path_edit = QLineEdit()
        self.local_path_edit.setText(self.current_local_path)
        self.local_path_edit.returnPressed.connect(self.navigate_local_path)
        self.local_path_edit.setPlaceholderText("Local Path")
        self.local_path_edit.setMinimumWidth(200)
        path_layout.addWidget(self.local_path_edit, 1)

        # Up button - Compact but visible
        local_up_btn = QPushButton("Up")
        local_up_btn.setFixedWidth(40)
        local_up_btn.setMinimumHeight(24)
        local_up_btn.setToolTip("Go up one directory")
        local_up_btn.clicked.connect(self.local_up)
        path_layout.addWidget(local_up_btn)

        # Refresh button - Visible
        local_refresh_btn = QPushButton("Refresh")
        local_refresh_btn.setFixedWidth(65)
        local_refresh_btn.setMinimumHeight(24)
        local_refresh_btn.setToolTip("Refresh local files")
        local_refresh_btn.clicked.connect(self.load_local_files)
        path_layout.addWidget(local_refresh_btn)

        # New Folder button - Match Remote
        local_new_folder_btn = QPushButton("New Folder")
        local_new_folder_btn.setFixedWidth(85)
        local_new_folder_btn.setMinimumHeight(24)
        local_new_folder_btn.setToolTip("Create new local folder")
        local_new_folder_btn.clicked.connect(self.create_local_folder)
        path_layout.addWidget(local_new_folder_btn)

        local_layout.addLayout(path_layout)

        # Splitter for tree and table views
        self.local_splitter = QSplitter(Qt.Orientation.Vertical)

        # Tree view for directory navigation
        self.local_tree = QTreeView()
        self.local_tree_model = QFileSystemModel()
        self.local_tree_model.setRootPath(QDir.rootPath())
        self.local_tree.setModel(self.local_tree_model)
        self.local_tree.setRootIndex(self.local_tree_model.index(self.current_local_path))

        # Hide unnecessary columns
        for i in range(1, 4):
            self.local_tree.setColumnHidden(i, True)

        self.local_tree.setHeaderHidden(True)
        self.local_tree.clicked.connect(self.on_tree_clicked)
        self.local_tree.doubleClicked.connect(self.on_tree_double_clicked)
        self.local_tree.setMinimumHeight(150)
        self.local_tree.setMinimumWidth(50)  # Allow width resizing

        self.local_splitter.addWidget(self.local_tree)

        # File table
        self.local_table = DragDropTableWidget(
            parent=self,
            drop_callback=None,  # Will be set by parent
            drag_callback=self._handle_local_drag,
            enabled=True
        )
        self.local_table.setColumnCount(4)
        self.local_table.setHorizontalHeaderLabels(["Filename", "Filesize", "Filetype", "Last modified"])
        self.local_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.local_table.setAlternatingRowColors(True)
        self.local_table.setSortingEnabled(True)

        # Configure scroll bars for better usability
        self.local_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.local_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Set minimum height for the table to ensure it's visible
        self.local_table.setMinimumHeight(200)

        # Enable word wrap for filename column to handle long names better
        self.local_table.setWordWrap(False)  # Keep filenames on single line
        self.local_table.resizeRowsToContents()  # Adjust row heights if needed

        # Set reasonable default column widths with maximum constraints
        self.local_table.setColumnWidth(0, 280)  # Filename: reasonable width
        self.local_table.setColumnWidth(1, 80)   # Filesize: compact
        self.local_table.setColumnWidth(2, 100)  # Filetype: reasonable
        self.local_table.setColumnWidth(3, 120)  # Modified: reasonable

        self.local_table.horizontalHeader().setMinimumSectionSize(60)  # Minimum column width
        self.local_table.horizontalHeader().setMaximumSectionSize(400)  # Maximum for filename column

        # Make all columns resizable for user flexibility
        self.local_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.local_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.local_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.local_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)

        # No stretching to maintain proportions
        self.local_table.horizontalHeader().setStretchLastSection(False)

        # Connect table events
        self.local_table.doubleClicked.connect(self.on_table_double_click)
        self.local_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.local_table.customContextMenuRequested.connect(self.show_context_menu)

        self.local_splitter.addWidget(self.local_table)

        # Set splitter proportions (Directories above, Files below)
        self.local_splitter.setSizes([200, 400])

        local_layout.addWidget(self.local_splitter)
        layout.addWidget(local_container)

        # Load initial local files
        self.load_local_files()

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
                self.local_table.setItem(row, 2, QTableWidgetItem("Parent Directory"))
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
                    if hasattr(self.parent, 'filter_manager') and self.parent.filter_manager.is_filtered(file_info):
                        continue

                    # Check if should be hidden in comparison mode
                    if hasattr(self.parent, 'comparison_manager') and self.parent.comparison_manager.comparator.should_hide_file(item.name):
                        continue

                    local_files_data.append(file_info)

                    row = self.local_table.rowCount()
                    self.local_table.insertRow(row)
                    name_item = QTableWidgetItem(item.name)
                    self.local_table.setItem(row, 0, name_item)
                    size_item = QTableWidgetItem("")
                    size_item.setData(Qt.ItemDataRole.UserRole, 0)
                    self.local_table.setItem(row, 1, size_item)
                    self.local_table.setItem(row, 2, QTableWidgetItem("Directory"))
                    try:
                        mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    except:
                        mtime = ""
                    self.local_table.setItem(row, 3, QTableWidgetItem(mtime))
                    self.local_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(item))

                    # Apply comparison highlighting
                    if hasattr(self.parent, 'comparison_manager'):
                        comparison_result = self.parent.comparison_manager.comparator.get_comparison_result(item.name, True)
                        if comparison_result:
                            color = self.parent.comparison_manager.get_comparison_color(comparison_result)
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
                    if hasattr(self.parent, 'filter_manager') and self.parent.filter_manager.is_filtered(file_info):
                        continue

                    # Check if should be hidden in comparison mode
                    if hasattr(self.parent, 'comparison_manager') and self.parent.comparison_manager.comparator.should_hide_file(item.name):
                        continue

                    local_files_data.append(file_info)

                    row = self.local_table.rowCount()
                    self.local_table.insertRow(row)
                    name_item = QTableWidgetItem(item.name)
                    self.local_table.setItem(row, 0, name_item)
                    size_str = format_size(size)
                    size_item = NumericTableWidgetItem(size_str)
                    size_item.setData(Qt.ItemDataRole.UserRole, size)
                    self.local_table.setItem(row, 1, size_item)
                    self.local_table.setItem(row, 2, QTableWidgetItem(item.suffix.lstrip('.') or "File"))
                    try:
                        mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    except:
                        mtime = ""
                    self.local_table.setItem(row, 3, QTableWidgetItem(mtime))
                    self.local_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(item))

                    # Apply comparison highlighting
                    if hasattr(self.parent, 'comparison_manager'):
                        comparison_result = self.parent.comparison_manager.comparator.get_comparison_result(item.name, True)
                        if comparison_result:
                            color = self.parent.comparison_manager.get_comparison_color(comparison_result)
                            if color:
                                name_item.setBackground(QColor(color))

            # Update comparison manager with local file data
            if hasattr(self.parent, 'comparison_manager'):
                self.parent.comparison_manager.update_directory_data(True, local_files_data)

            # Update status bar with directory info
            if hasattr(self.parent, 'status_bar'):
                self.parent.status_bar.update_local_directory_info(self.current_local_path, local_files_data)

            self.local_table.setSortingEnabled(True)
            self.local_table.resizeColumnsToContents()
            self.local_table.viewport().update()  # Force refresh
            self.local_table.repaint()  # Force repaint
            self.local_path_edit.setText(self.current_local_path)

        except Exception as e:
            if hasattr(self.parent, 'statusBar'):
                self.parent.statusBar().showMessage(f"Error loading local files: {str(e)}")
            self.local_table.setSortingEnabled(True)

    def navigate_local_path(self):
        """Navigate to custom local path"""
        path = self.local_path_edit.text()
        if Path(path).exists():
            self.parent.navigate_local_with_sync(path)

    def local_up(self):
        """Navigate up in local directory"""
        parent_path = Path(self.current_local_path).parent
        self.current_local_path = str(parent_path)
        self.local_path_edit.setText(self.current_local_path)
        self.load_local_files()

    def create_local_folder(self):
        """Create new local folder"""
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and folder_name:
            try:
                new_folder = Path(self.current_local_path) / folder_name
                new_folder.mkdir(parents=True, exist_ok=False)
                self.load_local_files()  # Refresh
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create folder: {e}")

    def on_tree_clicked(self, index):
        """Handle tree item click"""
        if index.isValid():
            path = self.local_tree_model.filePath(index)
            if Path(path).is_dir():
                self.current_local_path = path
                self.load_local_files()

    def on_tree_double_clicked(self, index):
        """Handle tree item double-click"""
        if index.isValid():
            path = self.local_tree_model.filePath(index)
            if Path(path).is_dir():
                self.current_local_path = path
                self.load_local_files()

    def on_table_double_click(self, index):
        """Handle table double-click"""
        row = index.row()
        if row >= 0:
            item = self.local_table.item(row, 0)
            if item:
                path_str = item.data(Qt.ItemDataRole.UserRole)
                if path_str:
                    path = Path(path_str)
                    if path.is_dir():
                        self.current_local_path = str(path)
                        self.load_local_files()
                    else:
                        from ..file_operations import open_local_file
                        open_local_file(path, parent_widget=self.parent)

    def show_context_menu(self, position):
        """Show context menu for local files"""
        selected_items = self.local_table.selectedItems()
        if hasattr(self.parent, 'context_menu_manager'):
            self.parent.context_menu_manager.create_local_context_menu(self.local_table, position, selected_items)

    def _handle_local_drag(self, files):
        """Handle dragging files from local table"""
        # This will be called by the DragDropTableWidget when a drag starts
        # The actual drag handling is done in the table widget's startDrag method
        pass