"""
File operations: upload, download, delete, create folder, rename
"""

from pathlib import Path
from PyQt6.QtWidgets import QMessageBox, QInputDialog
from ..models import RemoteFile


def upload_file(manager, local_path: Path, current_remote_path: str,
                log_callback=None, status_callback=None,
                queue_callback=None, move_completed_callback=None,
                refresh_callback=None, format_size_func=None,
                parent_widget=None, overwrite_mode="ask"):
    """Upload a local file to remote server with overwrite checking

    Args:
        overwrite_mode: "ask", "overwrite", "skip", "rename"
    """
    if not manager:
        if status_callback:
            status_callback("Not connected")
        return False

    try:
        if current_remote_path == "." or current_remote_path == "":
            try:
                if hasattr(manager, 'get_current_directory'):
                    actual_dir = manager.get_current_directory()
                    if actual_dir and actual_dir != "." and actual_dir != "":
                        current_remote_path = actual_dir
                        if log_callback:
                            log_callback(f"Using actual directory: {actual_dir}")
            except:
                pass

            if current_remote_path == "." or current_remote_path == "":
                remote_path = local_path.name
            else:
                remote_path = f"{current_remote_path.rstrip('/')}/{local_path.name}".lstrip("./")
        else:
            remote_path = f"{current_remote_path.rstrip('/')}/{local_path.name}".lstrip("./")

        # Check if remote file exists and handle overwrite
        remote_file_exists = False
        remote_file_info = None

        try:
            # List current directory to check if file exists
            files = manager.list_files(current_remote_path)
            for file_info in files:
                if file_info.name == local_path.name:
                    remote_file_exists = True
                    remote_file_info = file_info
                    break
        except Exception:
            # If we can't list directory, assume file doesn't exist
            pass

        if remote_file_exists and remote_file_info:
            # Compare files to determine if they're different
            local_size = local_path.stat().st_size
            local_mtime = local_path.stat().st_mtime

            size_different = local_size != remote_file_info.size

            # Compare modification times (with some tolerance)
            time_different = False
            if hasattr(remote_file_info, 'modified') and remote_file_info.modified:
                try:
                    # Convert remote timestamp to float for comparison
                    if isinstance(remote_file_info.modified, str):
                        # Parse the date string (assuming format like "2024-01-01 12:00:00")
                        from datetime import datetime
                        remote_time = datetime.strptime(remote_file_info.modified, "%Y-%m-%d %H:%M:%S").timestamp()
                    else:
                        remote_time = remote_file_info.modified.timestamp() if hasattr(remote_file_info.modified, 'timestamp') else float(remote_file_info.modified)

                    time_diff = abs(local_mtime - remote_time)
                    time_different = time_diff > 60  # 1 minute tolerance
                except:
                    time_different = True  # If we can't compare times, assume different

            files_identical = not size_different and not time_different

            if files_identical and overwrite_mode == "ask":
                # Files are identical, no need to upload
                if log_callback:
                    log_callback(f"Skipping {local_path.name} - identical file already exists")
                if status_callback:
                    status_callback(f"Skipped {local_path.name} (identical)")
                return True
            elif remote_file_exists and overwrite_mode == "ask":
                # Ask user what to do
                if not parent_widget:
                    # If no parent widget, default to overwrite
                    pass
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    from PyQt6.QtCore import Qt

                    # Create detailed overwrite dialog
                    msg_box = QMessageBox(parent_widget)
                    msg_box.setIcon(QMessageBox.Icon.Question)
                    msg_box.setWindowTitle("File Already Exists")
                    msg_box.setText(f"The file '{local_path.name}' already exists on the remote server.")

                    # Add file details
                    local_size_str = format_size_func(local_size) if format_size_func else f"{local_size} bytes"
                    remote_size_str = format_size_func(remote_file_info.size) if format_size_func else f"{remote_file_info.size} bytes"

                    details = f"Local file: {local_size_str}"
                    if hasattr(remote_file_info, 'modified') and remote_file_info.modified:
                        details += f"\nRemote file: {remote_size_str}"

                    msg_box.setDetailedText(details)

                    # Add buttons
                    overwrite_btn = msg_box.addButton("Overwrite", QMessageBox.ButtonRole.AcceptRole)
                    skip_btn = msg_box.addButton("Skip", QMessageBox.ButtonRole.RejectRole)
                    rename_btn = msg_box.addButton("Rename", QMessageBox.ButtonRole.ActionRole)

                    msg_box.setDefaultButton(overwrite_btn)
                    msg_box.exec()

                    clicked_button = msg_box.clickedButton()

                    if clicked_button == skip_btn:
                        if log_callback:
                            log_callback(f"Skipped {local_path.name} - user chose to skip")
                        if status_callback:
                            status_callback(f"Skipped {local_path.name}")
                        return True
                    elif clicked_button == rename_btn:
                        # Generate new name
                        from PyQt6.QtWidgets import QInputDialog
                        base_name = local_path.stem
                        extension = local_path.suffix
                        counter = 1
                        while True:
                            new_name = f"{base_name} ({counter}){extension}"
                            # Check if this name exists
                            name_exists = False
                            for file_info in files:
                                if file_info.name == new_name:
                                    name_exists = True
                                    break
                            if not name_exists:
                                break
                            counter += 1

                        new_name, ok = QInputDialog.getText(parent_widget, "Rename File",
                                                          "New name:", text=new_name)
                        if ok and new_name:
                            remote_path = f"{current_remote_path.rstrip('/')}/{new_name}".lstrip("./")
                        else:
                            # User cancelled rename, skip
                            return True
                    # If overwrite_btn clicked, continue with upload

        size_str = format_size_func(local_path.stat().st_size) if local_path.exists() and format_size_func else "Unknown"

        if queue_callback:
            queue_callback("Upload", str(local_path), remote_path, size_str, "In Progress")

        if log_callback:
            log_callback(f"Uploading file: {local_path.name} ({size_str}) to {remote_path}")

        # Upload file
        manager.upload_file(str(local_path), remote_path)

        if log_callback:
            log_callback(f"File uploaded successfully: {local_path.name} -> {remote_path}", "success")
        if status_callback:
            status_callback(f"Uploaded {local_path.name}")
        if move_completed_callback:
            move_completed_callback()
        if refresh_callback:
            import time
            time.sleep(0.3)
            refresh_callback()
        return True
    except Exception as e:
        error_msg = f"Upload error for {local_path.name}: {str(e)}"
        if log_callback:
            log_callback(error_msg, "error")
        if status_callback:
            status_callback(error_msg)
        return False


def download_file(manager, remote_file: RemoteFile, current_local_path: str,
                  log_callback=None, status_callback=None,
                  queue_callback=None, move_completed_callback=None,
                  refresh_callback=None, format_size_func=None):
    """Download a remote file to local directory"""
    if not manager or remote_file.is_dir:
        return False
    
    try:
        local_path = Path(current_local_path) / remote_file.name
        size_str = format_size_func(remote_file.size) if format_size_func else str(remote_file.size)
        
        if queue_callback:
            queue_callback("Download", str(local_path), remote_file.path, size_str, "In Progress")
        
        if log_callback:
            log_callback(f"Downloading file: {remote_file.name} ({size_str}) from {remote_file.path} to {local_path}")
        
        try:
            manager.download_file(remote_file.path, str(local_path))
            
            if log_callback:
                log_callback(f"File downloaded successfully: {remote_file.name} -> {local_path}", "success")
            if status_callback:
                status_callback(f"Downloaded {remote_file.name}")
            if move_completed_callback:
                move_completed_callback()
            if refresh_callback:
                refresh_callback()
            return True
        except Exception as download_error:
            error_msg = f"Download error for {remote_file.name}: {str(download_error)}"
            if log_callback:
                log_callback(error_msg, "error")
            if status_callback:
                status_callback(error_msg)
            raise
    except Exception as e:
        error_msg = f"Download error for {remote_file.name}: {str(e)}"
        if log_callback:
            log_callback(error_msg, "error")
        if status_callback:
            status_callback(error_msg)
        return False


def delete_remote_file(manager, remote_file: RemoteFile, parent_widget=None,
                      log_callback=None, status_callback=None, refresh_callback=None):
    """Delete a remote file or folder"""
    if not manager:
        return False
    
    if parent_widget:
        reply = QMessageBox.question(
            parent_widget, "Confirm Delete",
            f"Are you sure you want to delete {remote_file.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return False
    
    try:
        file_type = "folder" if remote_file.is_dir else "file"
        if log_callback:
            log_callback(f"Deleting remote {file_type}: {remote_file.name} from {remote_file.path}")
        
        if remote_file.is_dir:
            manager.delete_folder(remote_file.path)
        else:
            manager.delete_file(remote_file.path)
        
        if log_callback:
            log_callback(f"Deleted {file_type} successfully: {remote_file.name}", "success")
        if status_callback:
            status_callback(f"Deleted {remote_file.name}")
        if refresh_callback:
            refresh_callback()
        return True
    except Exception as e:
        error_msg = f"Error deleting {remote_file.name}: {str(e)}"
        if log_callback:
            log_callback(error_msg, "error")
        if status_callback:
            status_callback(error_msg)
        if parent_widget:
            QMessageBox.critical(parent_widget, "Delete Error", str(e))
        return False


def create_remote_folder(manager, current_remote_path: str, parent_widget=None,
                         log_callback=None, status_callback=None, refresh_callback=None):
    """Create a new remote folder"""
    if not manager:
        return False
    
    if parent_widget:
        name, ok = QInputDialog.getText(parent_widget, "New Folder", "Folder name:")
        if not ok or not name:
            return False
    else:
        return False
    
    try:
        remote_path = f"{current_remote_path}/{name}".lstrip("./")
        if log_callback:
            log_callback(f"Creating remote folder: {name} at {remote_path}")
        
        manager.create_folder(remote_path)
        
        if log_callback:
            log_callback(f"Folder created successfully: {name}", "success")
        if status_callback:
            status_callback(f"Created folder {name}")
        if refresh_callback:
            refresh_callback()
        return True
    except Exception as e:
        error_msg = f"Error creating folder {name}: {str(e)}"
        if log_callback:
            log_callback(error_msg, "error")
        if status_callback:
            status_callback(error_msg)
        if parent_widget:
            QMessageBox.critical(parent_widget, "Error", str(e))
        return False


def rename_remote_file(manager, remote_file: RemoteFile, parent_widget=None,
                      log_callback=None, status_callback=None, refresh_callback=None):
    """Rename a remote file"""
    if not manager:
        return False
    
    if parent_widget:
        new_name, ok = QInputDialog.getText(
            parent_widget, "Rename File",
            f"Enter new name for {remote_file.name}:",
            text=remote_file.name
        )
        if not ok or not new_name or new_name == remote_file.name:
            return False
    else:
        return False
    
    try:
        old_path = remote_file.path
        path_parts = old_path.rstrip("/").split("/")
        path_parts[-1] = new_name
        new_path = "/".join(path_parts)
        
        if old_path != new_path:
            manager.rename_file(old_path, new_path)
            if log_callback:
                log_callback(f"Renamed {remote_file.name} to {new_name}", "success")
            if status_callback:
                status_callback(f"Renamed {remote_file.name} to {new_name}")
            if refresh_callback:
                refresh_callback()
            return True
        return False
    except Exception as e:
        error_msg = f"Rename error: {str(e)}"
        if log_callback:
            log_callback(error_msg, "error")
        if status_callback:
            status_callback(error_msg)
        if parent_widget:
            QMessageBox.critical(parent_widget, "Rename Error", str(e))
        return False


def delete_local_file(local_path: Path, parent_widget=None, status_callback=None, refresh_callback=None):
    """Delete a local file or folder"""
    if parent_widget:
        reply = QMessageBox.question(
            parent_widget, "Confirm Delete",
            f"Are you sure you want to delete {local_path.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return False
    
    try:
        if local_path.is_file():
            local_path.unlink()
        elif local_path.is_dir():
            import shutil
            shutil.rmtree(local_path)
        
        if status_callback:
            status_callback(f"Deleted {local_path.name}")
        if refresh_callback:
            refresh_callback()
        return True
    except Exception as e:
        if parent_widget:
            QMessageBox.critical(parent_widget, "Delete Error", str(e))
        return False


def open_local_file(local_path: Path, parent_widget=None):
    """Open local file with system default application"""
    import os
    import platform
    try:
        if platform.system() == 'Windows':
            os.startfile(str(local_path))
        elif platform.system() == 'Darwin':
            os.system(f'open "{local_path}"')
        else:
            os.system(f'xdg-open "{local_path}"')
        return True
    except Exception as e:
        if parent_widget:
            QMessageBox.warning(parent_widget, "Error", f"Could not open file: {str(e)}")
        return False
