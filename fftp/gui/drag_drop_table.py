"""
Enhanced drag-and-drop table widget for Fftp
"""

from pathlib import Path
from typing import List, Callable
from PyQt6.QtWidgets import QTableWidget, QApplication
from PyQt6.QtCore import Qt, QMimeData, QUrl, QPoint
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDrag, QPixmap, QColor


class DragDropTableWidget(QTableWidget):
    """Enhanced table widget with comprehensive drag-and-drop support"""

    def __init__(self, parent=None, drop_callback=None, drag_callback=None, enabled=True):
        super().__init__(parent)
        self.drop_callback = drop_callback
        self.drag_callback = drag_callback
        self.drag_drop_enabled = enabled
        self.drag_start_position = None

        if enabled:
            self.setAcceptDrops(True)
            self.setDragDropMode(QTableWidget.DragDropMode.DragDrop)
        else:
            self.setAcceptDrops(False)
            self.setDragDropMode(QTableWidget.DragDropMode.NoDragDrop)

    def set_drag_drop_enabled(self, enabled: bool):
        """Enable or disable drag-and-drop"""
        self.drag_drop_enabled = enabled
        if enabled:
            self.setAcceptDrops(True)
            self.setDragDropMode(QTableWidget.DragDropMode.DragDrop)
        else:
            self.setAcceptDrops(False)
            self.setDragDropMode(QTableWidget.DragDropMode.NoDragDrop)

    def mousePressEvent(self, event):
        """Handle mouse press for drag start"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for drag initiation"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        if self.drag_start_position is None:
            return

        # Check if we've moved enough to start a drag
        distance = (event.pos() - self.drag_start_position).manhattanLength()
        if distance < QApplication.startDragDistance():
            return

        # Get selected items
        selected_rows = set()
        for item in self.selectedItems():
            if item.column() == 0:  # Only consider first column
                selected_rows.add(item.row())

        if not selected_rows:
            return

        # Collect file information for drag
        drag_files = []
        for row in selected_rows:
            item = self.item(row, 0)
            if item:
                file_data = item.data(Qt.ItemDataRole.UserRole)
                if file_data:
                    drag_files.append(file_data)

        if drag_files and self.drag_callback:
            self.startDrag(drag_files)
        elif not drag_files:
            # Try to get file paths from table data
            drag_paths = []
            for row in selected_rows:
                item = self.item(row, 0)
                if item:
                    path_str = item.data(Qt.ItemDataRole.UserRole)
                    if path_str and isinstance(path_str, str):
                        path = Path(path_str)
                        if path.exists():
                            drag_paths.append(path)

            if drag_paths:
                self.startDrag(drag_paths)

    def startDrag(self, files):
        """Start a drag operation"""
        if not files:
            return

        # Create mime data
        mime_data = QMimeData()

        # Add URLs for file paths
        urls = []
        for file_item in files:
            if isinstance(file_item, Path):
                urls.append(QUrl.fromLocalFile(str(file_item)))
            elif hasattr(file_item, 'path'):
                # Remote file
                urls.append(QUrl(f"ftp://{file_item.path}"))
            elif isinstance(file_item, str):
                path = Path(file_item)
                if path.exists():
                    urls.append(QUrl.fromLocalFile(file_item))

        if urls:
            mime_data.setUrls(urls)

        # Create drag object
        drag = QDrag(self)
        drag.setMimeData(mime_data)

        # Set drag pixmap (optional)
        if len(files) == 1:
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(100, 149, 237, 128))  # Light blue with transparency
            drag.setPixmap(pixmap)

        # Execute drag
        drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event with enhanced validation"""
        if not self.drag_drop_enabled:
            event.ignore()
            return

        mime_data = event.mimeData()

        # Accept URLs (files/folders)
        if mime_data.hasUrls():
            urls = mime_data.urls()
            valid_files = 0

            for url in urls:
                file_path = url.toLocalFile()
                if file_path:
                    path = Path(file_path)
                    if path.exists():
                        valid_files += 1
                elif url.scheme() in ['ftp', 'ftps', 'sftp']:
                    # Remote URL
                    valid_files += 1

            if valid_files > 0:
                event.acceptProposedAction()
                return

        # Accept custom data (from our own tables)
        if mime_data.hasFormat("application/x-fttp-file-data"):
            event.acceptProposedAction()
            return

        event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move event with visual feedback"""
        if not self.drag_drop_enabled:
            event.ignore()
            return

        mime_data = event.mimeData()

        if mime_data.hasUrls() or mime_data.hasFormat("application/x-fttp-file-data"):
            event.acceptProposedAction()

            # Provide visual feedback by highlighting the drop target
            # This could be enhanced with custom highlighting
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event with comprehensive file processing"""
        if not self.drag_drop_enabled:
            event.ignore()
            return

        mime_data = event.mimeData()

        if mime_data.hasUrls() and self.drop_callback:
            files = []
            remote_files = []

            for url in mime_data.urls():
                file_path = url.toLocalFile()
                if file_path:
                    # Local file/folder
                    path = Path(file_path)
                    if path.exists():
                        files.append(path)
                elif url.scheme() in ['ftp', 'ftps', 'sftp']:
                    # Remote URL - extract path
                    remote_path = url.path()
                    if remote_path:
                        remote_files.append(remote_path)

            # Handle local files
            if files:
                self.drop_callback(files, source="local")
                event.acceptProposedAction()
                return

            # Handle remote files
            if remote_files:
                self.drop_callback(remote_files, source="remote")
                event.acceptProposedAction()
                return

        # Handle custom Fftp data
        elif mime_data.hasFormat("application/x-fttp-file-data") and self.drop_callback:
            # This would be used for dragging between our own tables
            data = mime_data.data("application/x-fttp-file-data")
            # Parse and handle custom data
            self.drop_callback(data, source="fttp")
            event.acceptProposedAction()
            return

        event.ignore()

    def create_mime_data_for_files(self, files) -> QMimeData:
        """Create mime data for Fftp file objects"""
        mime_data = QMimeData()

        # Store custom data
        file_data = []
        urls = []

        for file_obj in files:
            if hasattr(file_obj, 'name') and hasattr(file_obj, 'path'):
                # Remote file object
                file_info = {
                    'name': file_obj.name,
                    'path': file_obj.path,
                    'size': getattr(file_obj, 'size', 0),
                    'is_dir': getattr(file_obj, 'is_dir', False)
                }
                file_data.append(file_info)
            elif isinstance(file_obj, Path):
                # Local path
                urls.append(QUrl.fromLocalFile(str(file_obj)))
            elif isinstance(file_obj, str):
                # String path
                path = Path(file_obj)
                if path.exists():
                    urls.append(QUrl.fromLocalFile(file_obj))

        if file_data:
            # Store custom Fftp data
            import json
            mime_data.setData("application/x-fttp-file-data", json.dumps(file_data).encode())

        if urls:
            mime_data.setUrls(urls)

        return mime_data
