"""
Search dialog for finding files locally and remotely
"""

import os
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox,
    QCheckBox, QTableWidget, QTableWidgetItem, QTabWidget,
    QProgressBar, QMessageBox, QSplitter, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon


class SearchWorker(QThread):
    """Worker thread for performing searches"""

    progress_updated = pyqtSignal(int, int)  # current, total
    file_found = pyqtSignal(dict)  # file info dict
    search_finished = pyqtSignal(int)  # total files found

    def __init__(self, search_params, manager=None):
        super().__init__()
        self.search_params = search_params
        self.manager = manager
        self.cancelled = False

    def cancel(self):
        """Cancel the search"""
        self.cancelled = True

    def run(self):
        """Run the search"""
        try:
            if self.search_params['search_type'] == 'local':
                self._search_local()
            elif self.search_params['search_type'] == 'remote':
                self._search_remote()
        except Exception as e:
            print(f"Search error: {e}")

    def _search_local(self):
        """Search local filesystem"""
        path = self.search_params['path']
        filename_pattern = self.search_params.get('filename', '')
        case_sensitive = self.search_params.get('case_sensitive', False)

        files_found = 0
        total_searched = 0

        try:
            for root, dirs, files in os.walk(path):
                if self.cancelled:
                    break

                # Search files
                for file in files:
                    if self.cancelled:
                        break

                    total_searched += 1

                    # Check filename pattern
                    if filename_pattern:
                        if case_sensitive:
                            match = filename_pattern in file
                        else:
                            match = filename_pattern.lower() in file.lower()

                        if not match:
                            continue

                    # Get file info
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.stat(file_path)
                        file_info = {
                            'name': file,
                            'path': root,
                            'full_path': file_path,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime),
                            'type': 'File'
                        }

                        # Apply additional filters
                        if self._matches_filters(file_info):
                            self.file_found.emit(file_info)
                            files_found += 1

                    except (OSError, PermissionError):
                        continue

                    if total_searched % 100 == 0:
                        self.progress_updated.emit(total_searched, -1)

            self.search_finished.emit(files_found)

        except Exception as e:
            print(f"Local search error: {e}")
            self.search_finished.emit(files_found)

    def _search_remote(self):
        """Search remote filesystem"""
        if not self.manager:
            self.search_finished.emit(0)
            return

        try:
            # For remote search, we'd need to implement directory traversal
            # This is a simplified version
            files_found = 0
            path = self.search_params['path']

            # Get directory listing
            files = self.manager.list_files(path)
            filename_pattern = self.search_params.get('filename', '')

            for file in files:
                if self.cancelled:
                    break

                # Check filename pattern
                if filename_pattern:
                    if self.search_params.get('case_sensitive', False):
                        match = filename_pattern in file.name
                    else:
                        match = filename_pattern.lower() in file.name.lower()

                    if not match:
                        continue

                file_info = {
                    'name': file.name,
                    'path': path,
                    'full_path': os.path.join(path, file.name),
                    'size': file.size,
                    'modified': file.modified,
                    'type': 'File' if not file.is_dir else 'Folder'
                }

                if self._matches_filters(file_info):
                    self.file_found.emit(file_info)
                    files_found += 1

            self.search_finished.emit(files_found)

        except Exception as e:
            print(f"Remote search error: {e}")
            self.search_finished.emit(0)

    def _matches_filters(self, file_info):
        """Check if file matches additional filters"""
        # Size filter
        min_size = self.search_params.get('min_size', 0)
        max_size = self.search_params.get('max_size', 0)

        if min_size > 0 and file_info['size'] < min_size:
            return False
        if max_size > 0 and file_info['size'] > max_size:
            return False

        # Date filter
        date_type = self.search_params.get('date_type', 'modified')
        date_condition = self.search_params.get('date_condition', '')
        date_value = self.search_params.get('date_value')

        if date_condition and date_value:
            file_date = file_info['modified']
            if date_condition == 'before' and file_date >= date_value:
                return False
            elif date_condition == 'after' and file_date <= date_value:
                return False

        return True


class SearchDialog(QDialog):
    """Search dialog for finding files"""

    def __init__(self, parent=None, manager=None):
        super().__init__(parent)
        self.manager = manager
        self.search_worker = None
        self.results = []

        self.setWindowTitle("Search - Fftp")
        self.setGeometry(200, 200, 800, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        # Search parameters
        search_group = QGroupBox("Search Parameters")
        search_layout = QVBoxLayout(search_group)

        # Search type and path
        type_layout = QHBoxLayout()
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["Local", "Remote"])
        self.search_type_combo.currentTextChanged.connect(self.on_search_type_changed)
        type_layout.addWidget(QLabel("Search in:"))
        type_layout.addWidget(self.search_type_combo)

        type_layout.addStretch()

        type_layout.addWidget(QLabel("Path:"))
        self.path_input = QLineEdit()
        self.path_input.setText(str(Path.home()))
        type_layout.addWidget(self.path_input)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_path)
        type_layout.addWidget(self.browse_btn)

        search_layout.addLayout(type_layout)

        # Search criteria
        criteria_layout = QHBoxLayout()

        # Filename
        filename_group = QVBoxLayout()
        filename_group.addWidget(QLabel("Filename:"))
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("* for all files")
        filename_group.addWidget(self.filename_input)

        criteria_layout.addLayout(filename_group)

        # Size filters
        size_group = QVBoxLayout()
        size_group.addWidget(QLabel("Size:"))

        size_range_layout = QHBoxLayout()
        self.min_size_input = QSpinBox()
        self.min_size_input.setRange(0, 999999999)
        self.min_size_input.setSuffix(" bytes")
        size_range_layout.addWidget(QLabel("Min:"))
        size_range_layout.addWidget(self.min_size_input)

        self.max_size_input = QSpinBox()
        self.max_size_input.setRange(0, 999999999)
        self.max_size_input.setSuffix(" bytes")
        self.max_size_input.setValue(0)
        size_range_layout.addWidget(QLabel("Max:"))
        size_range_layout.addWidget(self.max_size_input)

        size_group.addLayout(size_range_layout)
        criteria_layout.addLayout(size_group)

        # Date filters
        date_group = QVBoxLayout()
        date_group.addWidget(QLabel("Date:"))

        date_type_layout = QHBoxLayout()
        self.date_type_combo = QComboBox()
        self.date_type_combo.addItems(["Modified", "Created", "Accessed"])
        date_type_layout.addWidget(self.date_type_combo)

        self.date_condition_combo = QComboBox()
        self.date_condition_combo.addItems(["", "Before", "After"])
        date_type_layout.addWidget(self.date_condition_combo)

        date_group.addLayout(date_type_layout)
        criteria_layout.addLayout(date_group)

        search_layout.addLayout(criteria_layout)

        # Options
        options_layout = QHBoxLayout()
        self.case_sensitive_check = QCheckBox("Case sensitive")
        options_layout.addWidget(self.case_sensitive_check)

        self.subdirs_check = QCheckBox("Search in subdirectories")
        self.subdirs_check.setChecked(True)
        options_layout.addWidget(self.subdirs_check)

        options_layout.addStretch()

        search_layout.addLayout(options_layout)

        layout.addWidget(search_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.start_search)
        self.search_btn.setDefault(True)
        button_layout.addWidget(self.search_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_search)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)

        button_layout.addStretch()

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout(results_group)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Name", "Path", "Size", "Modified", "Type"])
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.doubleClicked.connect(self.on_result_double_clicked)

        results_layout.addWidget(self.results_table)

        # Results info
        self.results_info = QLabel("Ready")
        results_layout.addWidget(self.results_info)

        layout.addWidget(results_group)

        # Update initial state
        self.on_search_type_changed("Local")

    def on_search_type_changed(self, search_type):
        """Handle search type change"""
        if search_type == "Remote":
            self.browse_btn.setEnabled(False)
            if self.manager:
                # Set current remote path
                if hasattr(self.parent(), 'current_remote_path'):
                    self.path_input.setText(self.parent().current_remote_path)
        else:
            self.browse_btn.setEnabled(True)

    def browse_path(self):
        """Browse for search path"""
        from PyQt6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, "Select Search Directory")
        if path:
            self.path_input.setText(path)

    def start_search(self):
        """Start the search"""
        if not self.path_input.text():
            QMessageBox.warning(self, "Error", "Please specify a search path")
            return

        # Prepare search parameters
        search_params = {
            'search_type': self.search_type_combo.currentText().lower(),
            'path': self.path_input.text(),
            'filename': self.filename_input.text(),
            'case_sensitive': self.case_sensitive_check.isChecked(),
            'min_size': self.min_size_input.value(),
            'max_size': self.max_size_input.value() if self.max_size_input.value() > 0 else 0,
            'date_type': self.date_type_combo.currentText().lower(),
            'date_condition': self.date_condition_combo.currentText().lower(),
            'subdirs': self.subdirs_check.isChecked()
        }

        # Clear previous results
        self.results_table.setRowCount(0)
        self.results.clear()
        self.results_info.setText("Searching...")

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        # Update buttons
        self.search_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # Start search worker
        self.search_worker = SearchWorker(search_params, self.manager if search_params['search_type'] == 'remote' else None)
        self.search_worker.progress_updated.connect(self.on_search_progress)
        self.search_worker.file_found.connect(self.on_file_found)
        self.search_worker.search_finished.connect(self.on_search_finished)
        self.search_worker.start()

    def stop_search(self):
        """Stop the current search"""
        if self.search_worker:
            self.search_worker.cancel()
            self.stop_search()

    def on_search_progress(self, current, total):
        """Handle search progress updates"""
        if total > 0:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(current)
        else:
            self.progress_bar.setRange(0, 0)  # Keep indeterminate

    def on_file_found(self, file_info):
        """Handle found file"""
        self.results.append(file_info)

        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        # Name
        name_item = QTableWidgetItem(file_info['name'])
        name_item.setData(Qt.ItemDataRole.UserRole, file_info)
        self.results_table.setItem(row, 0, name_item)

        # Path
        path_item = QTableWidgetItem(file_info['path'])
        self.results_table.setItem(row, 1, path_item)

        # Size
        size_str = self.parent().format_size(file_info['size']) if hasattr(self.parent(), 'format_size') else str(file_info['size'])
        size_item = QTableWidgetItem(size_str)
        self.results_table.setItem(row, 2, size_item)

        # Modified date
        date_str = file_info['modified'].strftime("%Y-%m-%d %H:%M") if file_info['modified'] else ""
        date_item = QTableWidgetItem(date_str)
        self.results_table.setItem(row, 3, date_item)

        # Type
        type_item = QTableWidgetItem(file_info['type'])
        self.results_table.setItem(row, 4, type_item)

    def on_search_finished(self, total_found):
        """Handle search completion"""
        self.progress_bar.setVisible(False)
        self.results_info.setText(f"Search completed. Found {total_found} files.")

        # Update buttons
        self.search_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        # Clean up worker
        if self.search_worker:
            self.search_worker = None

    def on_result_double_clicked(self, index):
        """Handle result double-click"""
        row = index.row()
        if row < len(self.results):
            file_info = self.results[row]
            # Open file or navigate to directory
            if hasattr(self.parent(), 'open_local_file'):
                try:
                    self.parent().open_local_file(Path(file_info['full_path']))
                except:
                    pass  # File might not be accessible

    def get_selected_files(self):
        """Get selected files from results"""
        selected_rows = set()
        for item in self.results_table.selectedItems():
            selected_rows.add(item.row())

        return [self.results[row] for row in selected_rows if row < len(self.results)]