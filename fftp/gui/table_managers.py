"""
Table management utilities for loading files into tables
"""

from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from ..models import RemoteFile


class NumericTableWidgetItem(QTableWidgetItem):
    """Table item for numerical sorting"""
    def __lt__(self, other):
        try:
            return float(self.data(Qt.ItemDataRole.UserRole)) < float(other.data(Qt.ItemDataRole.UserRole))
        except:
            return super().__lt__(other)


def format_size(size: int) -> str:
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def load_local_files_to_table(table: QTableWidget, path_edit, current_path: str, status_callback=None):
    """Load local directory into table"""
    try:
        path = Path(current_path)
        if not path.exists():
            path = Path.home()
            current_path = str(path)
        
        table.setSortingEnabled(False)
        table.setRowCount(0)
        
        if path.parent != path:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(".."))
            table.setItem(row, 1, QTableWidgetItem(""))
            table.setItem(row, 2, QTableWidgetItem("<Parent Directory>"))
            table.setItem(row, 3, QTableWidgetItem(""))
        
        for item in sorted(path.iterdir()):
            if item.is_dir():
                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(f"[DIR] {item.name}"))
                size_item = QTableWidgetItem("")
                size_item.setData(Qt.ItemDataRole.UserRole, 0)
                table.setItem(row, 1, size_item)
                table.setItem(row, 2, QTableWidgetItem("<Directory>"))
                try:
                    mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                except:
                    mtime = ""
                table.setItem(row, 3, QTableWidgetItem(mtime))
                table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(item))
        
        for item in sorted(path.iterdir()):
            if item.is_file():
                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(f"[FILE] {item.name}"))
                size = item.stat().st_size
                size_str = format_size(size)
                size_item = NumericTableWidgetItem(size_str)
                size_item.setData(Qt.ItemDataRole.UserRole, size)
                table.setItem(row, 1, size_item)
                table.setItem(row, 2, QTableWidgetItem(item.suffix or "File"))
                try:
                    mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                except:
                    mtime = ""
                table.setItem(row, 3, QTableWidgetItem(mtime))
                table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(item))
        
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()
        if path_edit:
            path_edit.setText(current_path)
        return current_path
    except Exception as e:
        if status_callback:
            status_callback(f"Error loading local files: {str(e)}")
        table.setSortingEnabled(True)
        return current_path


def load_remote_files_to_table(table: QTableWidget, path_edit, manager, current_path: str, 
                               log_callback=None, status_callback=None):
    """Load remote directory into table"""
    try:
        if not manager:
            if status_callback:
                status_callback("Not connected - cannot load remote files")
            return current_path
        
        if log_callback:
            log_callback(f"Loading files from remote path: {current_path}")
        if status_callback:
            status_callback(f"Loading files from {current_path}...")
        
        if not current_path or current_path == "":
            current_path = "."
        
        table.setSortingEnabled(False)
        table.setRowCount(0)
        
        try:
            if log_callback:
                log_callback(f"Requesting file list from server...")
            if status_callback:
                status_callback(f"Requesting file list from server...")
            files = manager.list_files(current_path)
            if log_callback:
                log_callback(f"Received {len(files) if files else 0} items from server", "success")
            if status_callback:
                status_callback(f"Received {len(files) if files else 0} items from server")
        except Exception as e:
            error_msg = f"Error listing files: {str(e)}"
            if status_callback:
                status_callback(error_msg)
            table.setSortingEnabled(True)
            return current_path
        
        if not files:
            if log_callback:
                log_callback(f"Directory '{current_path}' is empty - connection verified and working", "warning")
            if status_callback:
                status_callback(f"Directory '{current_path}' is empty - Connection OK")
            table.setSortingEnabled(True)
            if path_edit:
                path_edit.setText(current_path)
            
            try:
                if hasattr(manager, 'get_current_directory'):
                    actual_path = manager.get_current_directory()
                    if actual_path and actual_path != current_path and actual_path != ".":
                        if log_callback:
                            log_callback(f"Detected actual working directory: {actual_path}, retrying...")
                        current_path = actual_path
                        if path_edit:
                            path_edit.setText(actual_path)
                        return load_remote_files_to_table(table, path_edit, manager, actual_path, log_callback, status_callback)
            except Exception as e:
                if log_callback:
                    log_callback(f"Could not get current directory: {str(e)}", "warning")
            
            row = table.rowCount()
            table.insertRow(row)
            empty_item = QTableWidgetItem("(Directory is empty - Connection is working)")
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
            empty_item.setForeground(Qt.GlobalColor.gray)
            empty_item.setData(Qt.ItemDataRole.UserRole, None)
            table.setItem(row, 0, empty_item)
            table.setItem(row, 1, QTableWidgetItem(""))
            table.setItem(row, 2, QTableWidgetItem(""))
            table.setItem(row, 3, QTableWidgetItem(""))
            table.setSortingEnabled(True)
            return current_path
        
        if log_callback:
            log_callback(f"Processing {len(files)} items...")
        if status_callback:
            status_callback(f"Processing {len(files)} items...")
        
        for file in files:
            row = table.rowCount()
            table.insertRow(row)
            
            icon = "[DIR]" if file.is_dir else "[FILE]"
            table.setItem(row, 0, QTableWidgetItem(f"{icon} {file.name}"))
            if file.is_dir:
                size_item = QTableWidgetItem("<DIR>")
                size_item.setData(Qt.ItemDataRole.UserRole, 0)
            else:
                size_str = format_size(file.size)
                size_item = NumericTableWidgetItem(size_str)
                size_item.setData(Qt.ItemDataRole.UserRole, file.size)
            table.setItem(row, 1, size_item)
            table.setItem(row, 2, QTableWidgetItem("Directory" if file.is_dir else "File"))
            table.setItem(row, 3, QTableWidgetItem(file.modified))
            
            table.item(row, 0).setData(Qt.ItemDataRole.UserRole, file)
        
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()
        if path_edit:
            path_edit.setText(current_path)
        if log_callback:
            log_callback(f"Successfully loaded {len(files)} items from {current_path}", "success")
        if status_callback:
            status_callback(f"✓ Loaded {len(files)} items from {current_path}")
        return current_path
    except Exception as e:
        error_msg = f"Error loading files: {str(e)}"
        if log_callback:
            log_callback(error_msg, "error")
        if status_callback:
            status_callback(error_msg)
        table.setSortingEnabled(True)
        return current_path
