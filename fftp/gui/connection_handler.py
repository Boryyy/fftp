"""
Connection handling logic
"""

from PyQt6.QtWidgets import QMessageBox
from ..models import ConnectionConfig
from ..managers import SFTPManager, FTPManager
from .connection_worker import ConnectionWorker


def connect_to_server(config: ConnectionConfig, manager, connection_worker,
                     connect_btn, status_callback=None, log_callback=None):
    """Initiate connection to server"""
    if not config:
        if status_callback:
            status_callback("No connection configuration")
        QMessageBox.warning(None, "Error", "No connection configuration")
        return None
    
    if connection_worker and connection_worker.isRunning():
        if status_callback:
            status_callback("Connection already in progress...")
        return None
    
    if manager:
        try:
            manager.disconnect()
        except:
            pass
        manager = None
    
    if connect_btn:
        connect_btn.setEnabled(False)
        connect_btn.setText("Connecting...")
    
    if status_callback:
        status_callback(f"Initializing connection to {config.host}...")
    
    manager_class = SFTPManager if config.protocol == "sftp" else FTPManager
    worker = ConnectionWorker(config, manager_class)
    
    if log_callback:
        log_callback(f"Starting connection to {config.host}:{config.port} ({config.protocol.upper()})")
    
    return worker


def handle_connection_finished(worker, success, msg, config, manager_ref,
                               current_remote_path_ref, connect_btn, disconnect_action,
                               status_callback=None, log_callback=None, refresh_callback=None,
                               disconnect_btn=None, status_bar=None):
    """Handle connection completion"""
    if connect_btn:
        connect_btn.setEnabled(True)
    
    if success:
        manager_ref[0] = worker.manager
        try:
            if hasattr(worker.manager, 'get_current_directory'):
                current_dir = worker.manager.get_current_directory()
                if current_dir and current_dir != ".":
                    current_remote_path_ref[0] = current_dir
                    if log_callback:
                        log_callback(f"Detected current remote directory: {current_dir}")
                else:
                    current_remote_path_ref[0] = "."
            else:
                current_remote_path_ref[0] = "."
        except Exception as e:
            if log_callback:
                log_callback(f"Could not detect current directory: {str(e)}", "warning")
            current_remote_path_ref[0] = "."
        
        if status_callback:
            status_callback(f"✓ Connected to {config.host} - Loading files...")
        if status_bar:
            status_bar.update_connection_status(f"Connected to {config.host}", True)
            status_bar.show_message(f"Connected to {config.host}")
        if disconnect_action:
            disconnect_action.setEnabled(True)
        if disconnect_btn:
            disconnect_btn.setEnabled(True)
        if connect_btn:
            connect_btn.setText("Connected")
            connect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: #ffffff;
                    font-weight: 600;
                    padding: 9px 20px;
                    border-radius: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
                QPushButton:pressed {
                    background-color: #1e8449;
                }
            """)
        if log_callback:
            log_callback(f"Connection established, loading remote files from: {current_remote_path_ref[0]}")
        if refresh_callback:
            try:
                refresh_callback()
            except Exception as e:
                error_msg = f"Connected but failed to load files: {str(e)}"
                if log_callback:
                    log_callback(error_msg, "error")
                if status_callback:
                    status_callback(error_msg)
                QMessageBox.warning(None, "Warning", f"Connected but failed to load remote files:\n{str(e)}")
    else:
        manager_ref[0] = None
        if status_callback:
            status_callback(f"✗ Connection failed: {msg}")
        if disconnect_btn:
            disconnect_btn.setEnabled(False)
        if connect_btn:
            connect_btn.setText("Connect")
            connect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: #ffffff;
                    font-weight: 600;
                    padding: 9px 20px;
                    border-radius: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
                QPushButton:disabled {
                    background-color: #bdc3c7;
                    color: #7f8c8d;
                }
            """)
        error_msg = f"Failed to connect to {config.host}:\n\n{msg}\n\nPlease check:\n• Host and port are correct\n• Username and password are valid\n• Server is accessible\n• Firewall is not blocking the connection"
        QMessageBox.critical(None, "Connection Error", error_msg)


def disconnect(manager, connection_worker, disconnect_action, remote_table,
                  connect_btn, log_callback=None, status_callback=None, disconnect_btn=None):
    """Disconnect from server"""
    if connection_worker and connection_worker.isRunning():
        if log_callback:
            log_callback("WARNING: Connection in progress, cannot disconnect", "warning")
        if status_callback:
            status_callback("Connection in progress, cannot disconnect")
        return False
    
    if manager:
        try:
            if log_callback:
                log_callback("Disconnecting from server...")
            if status_callback:
                status_callback("Disconnecting...")
            manager.disconnect()
            manager = None
            if log_callback:
                log_callback("Disconnected successfully", "success")
            if status_callback:
                status_callback("Disconnected")
            if disconnect_action:
                disconnect_action.setEnabled(False)
            if disconnect_btn:
                disconnect_btn.setEnabled(False)
            if remote_table:
                remote_table.setRowCount(0)
            if connect_btn:
                connect_btn.setText("Connect")
                connect_btn.setEnabled(True)
                connect_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: #ffffff;
                        font-weight: 600;
                        padding: 9px 20px;
                        border-radius: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                    QPushButton:pressed {
                        background-color: #21618c;
                    }
                    QPushButton:disabled {
                        background-color: #bdc3c7;
                        color: #7f8c8d;
                    }
                """)
            return True
        except Exception as e:
            error_msg = f"Error disconnecting: {str(e)}"
            if log_callback:
                log_callback(error_msg, "error")
            if status_callback:
                status_callback(error_msg)
            QMessageBox.warning(None, "Error", error_msg)
            return False
    else:
        if log_callback:
            log_callback("Not connected - nothing to disconnect")
        if status_callback:
            status_callback("Not connected")
        return False
