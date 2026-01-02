"""
Queue Panel - Handles transfer queue management and display
"""

from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QTabWidget, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt


class QueuePanel(QWidget):
    """Panel for managing transfer queues"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Initialize queue tables
        self.active_queue_table = None
        self.completed_queue_table = None
        self.queue_tabs = None

        self.init_ui()

    def init_ui(self):
        """Initialize the queue panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Queue header with controls
        queue_header = QHBoxLayout()

        queue_label = QLabel("Transfer Queue")
        queue_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        queue_header.addWidget(queue_label)

        queue_header.addStretch()

        # Process Queue button removed as per user request
        # Clear Queue button removed as per user request

        layout.addLayout(queue_header)

        # Queue tabs (Active/Completed)
        self.queue_tabs = QTabWidget()

        # Active transfers tab
        active_tab = QWidget()
        active_layout = QVBoxLayout(active_tab)

        self.active_queue_table = QTableWidget()
        self.active_queue_table.setColumnCount(5)
        self.active_queue_table.setHorizontalHeaderLabels(["Direction", "Local File", "Remote File", "Size", "Status"])
        self.active_queue_table.setAlternatingRowColors(True)
        self.active_queue_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                selection-background-color: #3498db;
                selection-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #bdc3c7;
                font-weight: 600;
            }
        """)
        self.active_queue_table.setColumnWidth(0, 80)
        self.active_queue_table.setColumnWidth(1, 200)
        self.active_queue_table.setColumnWidth(2, 200)
        self.active_queue_table.setColumnWidth(3, 80)
        self.active_queue_table.setColumnWidth(4, 100)

        active_layout.addWidget(self.active_queue_table)
        self.queue_tabs.addTab(active_tab, "Active")

        # Completed transfers tab
        completed_tab = QWidget()
        completed_layout = QVBoxLayout(completed_tab)

        self.completed_queue_table = QTableWidget()
        self.completed_queue_table.setColumnCount(5)
        self.completed_queue_table.setHorizontalHeaderLabels(["Direction", "Local File", "Remote File", "Size", "Time"])
        self.completed_queue_table.setAlternatingRowColors(True)
        self.completed_queue_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                selection-background-color: #3498db;
                selection-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #bdc3c7;
                font-weight: 600;
            }
        """)
        self.completed_queue_table.setColumnWidth(0, 80)
        self.completed_queue_table.setColumnWidth(1, 200)
        self.completed_queue_table.setColumnWidth(2, 200)
        self.completed_queue_table.setColumnWidth(3, 80)
        self.completed_queue_table.setColumnWidth(4, 120)

        completed_layout.addWidget(self.completed_queue_table)
        self.queue_tabs.addTab(completed_tab, "Completed")

        layout.addWidget(self.queue_tabs)

    def add_to_transfer_queue(self, direction, local_file, remote_file, size, status):
        """Add transfer to active queue"""
        if not self.active_queue_table:
            return

        row = self.active_queue_table.rowCount()
        self.active_queue_table.insertRow(row)
        self.active_queue_table.setItem(row, 0, QTableWidgetItem(direction))
        self.active_queue_table.setItem(row, 1, QTableWidgetItem(local_file))
        self.active_queue_table.setItem(row, 2, QTableWidgetItem(remote_file))
        self.active_queue_table.setItem(row, 3, QTableWidgetItem(size))
        # Set status to "Queued" if not specified
        if not status:
            status = "Queued"
        self.active_queue_table.setItem(row, 4, QTableWidgetItem(status))

        # Auto-start transfer if queue processing is enabled
        if hasattr(self.parent, 'auto_process_queue') and self.parent.auto_process_queue:
            self.parent.process_next_transfer()

    def move_to_completed(self, row):
        """Move transfer from active to completed queue"""
        if not self.active_queue_table or not self.completed_queue_table:
            return

        if row < 0 or row >= self.active_queue_table.rowCount():
            return

        direction = self.active_queue_table.item(row, 0).text()
        local_file = self.active_queue_table.item(row, 1).text()
        remote_file = self.active_queue_table.item(row, 2).text()
        size = self.active_queue_table.item(row, 3).text()
        status = self.active_queue_table.item(row, 4).text()

        completed_row = self.completed_queue_table.rowCount()
        self.completed_queue_table.insertRow(completed_row)
        self.completed_queue_table.setItem(completed_row, 0, QTableWidgetItem(direction))
        self.completed_queue_table.setItem(completed_row, 1, QTableWidgetItem(local_file))
        self.completed_queue_table.setItem(completed_row, 2, QTableWidgetItem(remote_file))
        self.completed_queue_table.setItem(completed_row, 3, QTableWidgetItem(size))
        self.completed_queue_table.setItem(completed_row, 4, QTableWidgetItem(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        self.active_queue_table.removeRow(row)

        # Process next transfer if available
        if hasattr(self.parent, 'auto_process_queue') and self.parent.auto_process_queue:
            self.parent.process_next_transfer()

    def clear_completed_queue(self):
        """Clear the completed transfers queue"""
        if self.completed_queue_table:
            self.completed_queue_table.setRowCount(0)

    def get_active_transfer_count(self):
        """Get the number of active transfers"""
        return self.active_queue_table.rowCount() if self.active_queue_table else 0

    def get_completed_transfer_count(self):
        """Get the number of completed transfers"""
        return self.completed_queue_table.rowCount() if self.completed_queue_table else 0

    def update_transfer_status(self, row, status):
        """Update the status of a transfer"""
        if self.active_queue_table and row < self.active_queue_table.rowCount():
            self.active_queue_table.item(row, 4).setText(status)

    def update_transfer_progress(self, row, progress_text):
        """Update the progress of a transfer"""
        if self.active_queue_table and row < self.active_queue_table.rowCount():
            self.active_queue_table.item(row, 4).setText(progress_text)