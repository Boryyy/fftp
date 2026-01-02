"""
Enhanced context menu system for Fftp
"""

from pathlib import Path
from PyQt6.QtWidgets import QMenu, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon


class ContextMenuManager:
    """Enhanced context menu manager for Fftp"""

    def __init__(self, parent):
        self.parent = parent

    def create_local_context_menu(self, table, position, selected_items):
        """Create comprehensive context menu for local files"""
        menu = QMenu(self.parent)

        # Transfer operations submenu
        if selected_items:
            transfer_menu = menu.addMenu("Transfer")

            # Upload selected files/folders
            upload_action = transfer_menu.addAction("Upload")
            upload_action.triggered.connect(self._upload_selected_local)

            # Add to queue
            queue_action = transfer_menu.addAction("Add to Queue")
            queue_action.triggered.connect(self._queue_selected_local)

            menu.addSeparator()

        # File operations submenu
        file_menu = menu.addMenu("File Operations")

        # Open/Edit
        open_action = file_menu.addAction("Open")
        open_action.triggered.connect(self._open_selected_local)

        # Open with...
        open_with_menu = file_menu.addMenu("Open with...")
        # Add common applications
        notepad_action = open_with_menu.addAction("Notepad")
        notepad_action.triggered.connect(lambda: self._open_with_application("notepad.exe"))

        # Add system default
        default_action = open_with_menu.addAction("System Default")
        default_action.triggered.connect(self._open_with_system_default)

        file_menu.addSeparator()

        # Create new
        new_menu = file_menu.addMenu("New")
        new_file_action = new_menu.addAction("File")
        new_file_action.triggered.connect(self._create_new_file_local)

        new_folder_action = new_menu.addAction("Folder")
        new_folder_action.triggered.connect(self._create_new_folder_local)

        file_menu.addSeparator()

        # Copy/Paste operations
        copy_action = file_menu.addAction("Copy")
        copy_action.triggered.connect(self._copy_selected_local)

        paste_action = file_menu.addAction("Paste")
        paste_action.triggered.connect(self._paste_to_local)

        file_menu.addSeparator()

        # Rename
        rename_action = file_menu.addAction("Rename")
        rename_action.triggered.connect(self._rename_selected_local)

        # Delete
        delete_action = file_menu.addAction("Delete")
        delete_action.triggered.connect(self._delete_selected_local)

        menu.addSeparator()

        # Directory operations
        if self._has_directory_selected(selected_items):
            dir_menu = menu.addMenu("Directory")

            enter_action = dir_menu.addAction("Enter Directory")
            enter_action.triggered.connect(self._enter_selected_directory)

            add_bookmark_action = dir_menu.addAction("Add to Bookmarks")
            add_bookmark_action.triggered.connect(self._add_directory_bookmark)

        # Refresh
        menu.addSeparator()
        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self._refresh_local_files)

        # Properties
        menu.addSeparator()
        properties_action = menu.addAction("Properties")
        properties_action.triggered.connect(self._show_local_properties)

        menu.exec(table.mapToGlobal(position))

    def create_remote_context_menu(self, table, position, selected_items):
        """Create comprehensive context menu for remote files"""
        menu = QMenu(self.parent)

        # Transfer operations submenu
        if selected_items:
            transfer_menu = menu.addMenu("Transfer")

            # Download selected files/folders
            download_action = transfer_menu.addAction("Download")
            download_action.triggered.connect(self._download_selected_remote)

            # Add to queue
            queue_action = transfer_menu.addAction("Add to Queue")
            queue_action.triggered.connect(self._queue_selected_remote)

            menu.addSeparator()

        # File operations submenu
        file_menu = menu.addMenu("File Operations")

        # View/Edit remote file
        view_action = file_menu.addAction("View/Edit")
        view_action.triggered.connect(self._view_selected_remote)

        file_menu.addSeparator()

        # Create new
        new_menu = file_menu.addMenu("New")
        new_file_action = new_menu.addAction("File")
        new_file_action.triggered.connect(self._create_new_file_remote)

        new_folder_action = new_menu.addAction("Folder")
        new_folder_action.triggered.connect(self._create_new_folder_remote)

        file_menu.addSeparator()

        # Copy/Paste operations (between local/remote)
        copy_action = file_menu.addAction("Copy")
        copy_action.triggered.connect(self._copy_selected_remote)

        paste_action = file_menu.addAction("Paste")
        paste_action.triggered.connect(self._paste_to_remote)

        file_menu.addSeparator()

        # Rename
        rename_action = file_menu.addAction("Rename")
        rename_action.triggered.connect(self._rename_selected_remote)

        # Delete
        delete_action = file_menu.addAction("Delete")
        delete_action.triggered.connect(self._delete_selected_remote)

        # Change permissions
        chmod_action = file_menu.addAction("Change Permissions")
        chmod_action.triggered.connect(self._change_permissions_remote)

        menu.addSeparator()

        # Directory operations
        if self._has_directory_selected(selected_items):
            dir_menu = menu.addMenu("Directory")

            enter_action = dir_menu.addAction("Enter Directory")
            enter_action.triggered.connect(self._enter_selected_directory_remote)

            add_bookmark_action = dir_menu.addAction("Add to Bookmarks")
            add_bookmark_action.triggered.connect(self._add_remote_directory_bookmark)

        # URL operations
        url_menu = menu.addMenu("URL")

        copy_url_action = url_menu.addAction("Copy URL to Clipboard")
        copy_url_action.triggered.connect(self._copy_url_to_clipboard)

        open_url_action = url_menu.addAction("Open URL in Browser")
        open_url_action.triggered.connect(self._open_url_in_browser)

        menu.addSeparator()

        # Refresh
        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self._refresh_remote_files)

        # Properties
        menu.addSeparator()
        properties_action = menu.addAction("Properties")
        properties_action.triggered.connect(self._show_remote_properties)

        menu.exec(table.mapToGlobal(position))

    def create_local_tree_context_menu(self, tree, position):
        """Create context menu for local directory tree"""
        menu = QMenu(self.parent)

        # Get selected item
        item = tree.itemAt(position)
        if item:
            path_data = item.data(0, Qt.ItemDataRole.UserRole)
            if path_data:
                # Transfer operations
                upload_action = menu.addAction("Upload")
                upload_action.triggered.connect(lambda: self._upload_from_tree(path_data))

                menu.addSeparator()

                # Directory operations
                new_folder_action = menu.addAction("New Folder")
                new_folder_action.triggered.connect(lambda: self._create_folder_in_tree(path_data))

                refresh_action = menu.addAction("Refresh")
                refresh_action.triggered.connect(lambda: self._refresh_tree_item(tree, item))

                menu.addSeparator()

                # Properties
                properties_action = menu.addAction("Properties")
                properties_action.triggered.connect(lambda: self._show_tree_properties(path_data))

        menu.exec(tree.mapToGlobal(position))

    def create_remote_tree_context_menu(self, tree, position):
        """Create context menu for remote directory tree"""
        menu = QMenu(self.parent)

        # Get selected item
        item = tree.itemAt(position)
        if item:
            path_data = item.data(0, Qt.ItemDataRole.UserRole)
            if path_data:
                # Transfer operations
                download_action = menu.addAction("Download")
                download_action.triggered.connect(lambda: self._download_from_tree(path_data))

                menu.addSeparator()

                # Directory operations
                new_folder_action = menu.addAction("New Folder")
                new_folder_action.triggered.connect(lambda: self._create_remote_folder_in_tree(path_data))

                refresh_action = menu.addAction("Refresh")
                refresh_action.triggered.connect(lambda: self._refresh_remote_tree_item(tree, item))

                menu.addSeparator()

                # Properties
                properties_action = menu.addAction("Properties")
                properties_action.triggered.connect(lambda: self._show_remote_tree_properties(path_data))

        menu.exec(tree.mapToGlobal(position))

    # Implementation methods (delegate to main window)
    def _upload_selected_local(self):
        self.parent.upload_selected_local()

    def _queue_selected_local(self):
        self.parent.upload_selected_local()  # For now, same as upload

    def _open_selected_local(self):
        self.parent.open_selected_local_file()

    def _open_with_application(self, app_path):
        """Open selected file with specific application"""
        self.parent.open_selected_local_file_with_app(app_path)

    def _open_with_system_default(self):
        """Open selected file with system default application"""
        self.parent.open_selected_local_file()

    def _create_new_file_local(self):
        # TODO: Implement
        pass

    def _create_new_folder_local(self):
        self.parent.create_local_folder()

    def _copy_selected_local(self):
        # TODO: Implement clipboard operations
        pass

    def _paste_to_local(self):
        # TODO: Implement paste operations
        pass

    def _rename_selected_local(self):
        self.parent.rename_selected_local()

    def _delete_selected_local(self):
        self.parent.delete_selected_local()

    def _enter_selected_directory(self):
        self.parent.enter_selected_local_directory()

    def _add_directory_bookmark(self):
        """Add current directory to bookmarks"""
        # This will be implemented when the bookmark system is integrated
        if hasattr(self.parent, 'bookmark_manager'):
            # Get current directory
            current_path = getattr(self.parent, 'current_local_path', '')
            if current_path:
                bookmark_name = f"Bookmark {len(self.parent.bookmark_manager.get_local_bookmarks()) + 1}"
                self.parent.bookmark_manager.add_bookmark(bookmark_name, current_path, "local")

    def _refresh_local_files(self):
        self.parent.load_local_files()

    def _show_local_properties(self):
        # TODO: Implement properties dialog
        pass

    def _download_selected_remote(self):
        self.parent.download_selected_remote()

    def _queue_selected_remote(self):
        self.parent.download_selected_remote()  # For now, same as download

    def _view_selected_remote(self):
        self.parent.view_selected_remote_file()

    def _create_new_file_remote(self):
        # TODO: Implement
        pass

    def _create_new_folder_remote(self):
        self.parent.create_remote_folder()

    def _copy_selected_remote(self):
        # TODO: Implement
        pass

    def _paste_to_remote(self):
        # TODO: Implement
        pass

    def _rename_selected_remote(self):
        self.parent.rename_selected_remote()

    def _delete_selected_remote(self):
        self.parent.delete_selected_remote()

    def _change_permissions_remote(self):
        # TODO: Implement chmod dialog
        pass

    def _enter_selected_directory_remote(self):
        self.parent.enter_selected_remote_directory()

    def _add_remote_directory_bookmark(self):
        """Add current remote directory to bookmarks"""
        if hasattr(self.parent, 'bookmark_manager'):
            tab = self.parent.get_current_tab()
            if tab and hasattr(tab, 'current_remote_path') and tab.current_remote_path:
                server_name = tab.config.host if hasattr(tab, 'config') else None
                bookmark_name = f"Remote {len(self.parent.bookmark_manager.get_remote_bookmarks()) + 1}"
                self.parent.bookmark_manager.add_bookmark(bookmark_name, tab.current_remote_path, "remote", server_name)

    def _copy_url_to_clipboard(self):
        # TODO: Implement URL operations
        pass

    def _open_url_in_browser(self):
        # TODO: Implement URL operations
        pass

    def _refresh_remote_files(self):
        self.parent.load_remote_files()

    def _show_remote_properties(self):
        # TODO: Implement properties dialog
        pass

    def _upload_from_tree(self, path):
        # TODO: Implement tree upload
        pass

    def _create_folder_in_tree(self, path):
        # TODO: Implement tree folder creation
        pass

    def _refresh_tree_item(self, tree, item):
        # TODO: Implement tree refresh
        pass

    def _show_tree_properties(self, path):
        # TODO: Implement tree properties
        pass

    def _download_from_tree(self, path):
        # TODO: Implement tree download
        pass

    def _create_remote_folder_in_tree(self, path):
        # TODO: Implement remote tree folder creation
        pass

    def _refresh_remote_tree_item(self, tree, item):
        # TODO: Implement remote tree refresh
        pass

    def _show_remote_tree_properties(self, path):
        # TODO: Implement remote tree properties
        pass

    def _has_directory_selected(self, selected_items):
        """Check if any selected items are directories"""
        for item in selected_items:
            file_data = item.data(Qt.ItemDataRole.UserRole)
            if file_data and getattr(file_data, 'is_dir', False):
                return True
        return False


# Legacy functions for backward compatibility
def create_local_context_menu(parent, table, position,
                              upload_callback=None, open_callback=None,
                              delete_callback=None, refresh_callback=None):
    """Legacy function - creates basic context menu"""
    menu = QMenu(parent)
    row = table.rowAt(position.y())

    if row >= 0:
        item = table.item(row, 0)
        if item:
            path_str = item.data(Qt.ItemDataRole.UserRole)
            if path_str:
                path = Path(path_str)
                if path.exists():
                    if path.is_file():
                        if upload_callback:
                            upload_action = menu.addAction("Upload")
                            upload_action.triggered.connect(lambda: upload_callback())
                            menu.addSeparator()

                        if open_callback:
                            open_action = menu.addAction("Open")
                            open_action.triggered.connect(lambda: open_callback(path))
                            menu.addSeparator()

                        if delete_callback:
                            delete_action = menu.addAction("Delete")
                            delete_action.triggered.connect(lambda: delete_callback(path))
                    elif path.is_dir():
                        if upload_callback:
                            upload_action = menu.addAction("Upload Folder")
                            upload_action.triggered.connect(lambda: upload_callback())
                            menu.addSeparator()

                        if delete_callback:
                            delete_action = menu.addAction("Delete")
                            delete_action.triggered.connect(lambda: delete_callback(path))

    menu.addSeparator()
    if refresh_callback:
        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(refresh_callback)

    menu.exec(table.viewport().mapToGlobal(position))


def create_remote_context_menu(parent, table, position,
                              download_callback=None, delete_callback=None,
                              refresh_callback=None):
    """Legacy function - creates basic context menu"""
    menu = QMenu(parent)
    row = table.rowAt(position.y())

    if row >= 0:
        item = table.item(row, 0)
        if item:
            file_data = item.data(Qt.ItemDataRole.UserRole)
            if file_data:
                if download_callback:
                    download_action = menu.addAction("Download")
                    download_action.triggered.connect(lambda: download_callback())
                    menu.addSeparator()

                if delete_callback:
                    delete_action = menu.addAction("Delete")
                    delete_action.triggered.connect(lambda: delete_callback(file_data))

    menu.addSeparator()
    if refresh_callback:
        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(refresh_callback)

    menu.exec(table.viewport().mapToGlobal(position))
