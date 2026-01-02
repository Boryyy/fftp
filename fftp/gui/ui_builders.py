"""
UI component builders and styling helpers
"""

from PyQt6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox,
    QGroupBox, QTableWidget, QPlainTextEdit, QCheckBox,
    QWidget, QHBoxLayout, QVBoxLayout, QTabWidget
)
from PyQt6.QtCore import Qt, QSize


def create_styled_button(text, min_height=32, min_width=None, style="default"):
    """Create a styled button"""
    btn = QPushButton(text)
    btn.setMinimumHeight(min_height)
    if min_width:
        btn.setMinimumWidth(min_width)
    
    if style == "primary":
        btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-weight: 600;
                padding: 7px 16px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
        """)
    elif style == "secondary":
        btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #212121;
                font-weight: 600;
                font-size: 12px;
                padding: 7px 14px;
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                border-color: #b0b0b0;
            }
            QPushButton:pressed {
                background-color: #dcdcdc;
                border-color: #999999;
            }
        """)
    elif style == "up":
        btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
            QPushButton:pressed {
                background-color: #dcdcdc;
            }
        """)
    else:
        btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #212121;
                font-weight: 600;
                font-size: 12px;
                padding: 7px 14px;
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
            QPushButton:pressed {
                background-color: #dcdcdc;
            }
        """)
    
    return btn


def create_styled_label(text, min_width=None, bold=True):
    """Create a styled label"""
    label = QLabel(text)
    if min_width:
        label.setMinimumWidth(min_width)
    if bold:
        label.setStyleSheet("font-weight: 600; color: #424242;")
    return label


def create_styled_groupbox(title):
    """Create a styled group box"""
    group = QGroupBox(title)
    group.setStyleSheet("""
        QGroupBox {
            font-weight: 600;
            font-size: 13px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
        }
    """)
    return group


def create_file_table(columns, double_click_callback=None, context_menu_callback=None, drag_enabled=False, drop_enabled=False):
    """Create a styled file table"""
    table = QTableWidget()
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels(columns)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setAlternatingRowColors(True)
    table.setSortingEnabled(True)
    
    if double_click_callback:
        table.doubleClicked.connect(double_click_callback)
    
    if context_menu_callback:
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(context_menu_callback)
    
    if drag_enabled:
        table.setDragEnabled(True)
        table.setDragDropMode(QTableWidget.DragDropMode.DragOnly)
    
    if drop_enabled:
        table.setAcceptDrops(True)
        table.setDragDropMode(QTableWidget.DragDropMode.DropOnly)
    
    return table


def create_log_panel(clear_callback=None):
    """Create activity log panel"""
    log_group = create_styled_groupbox("Activity Log")
    log_layout = QVBoxLayout(log_group)
    log_layout.setContentsMargins(8, 8, 8, 8)
    log_layout.setSpacing(4)
    
    log_header = QHBoxLayout()
    if clear_callback:
        clear_log_btn = create_styled_button("Clear Log", min_height=28, min_width=100, style="secondary")
        clear_log_btn.clicked.connect(clear_callback)
        log_header.addWidget(clear_log_btn)
    
    log_header.addStretch()
    log_enabled_check = QCheckBox("Enable Logging")
    log_enabled_check.setChecked(True)
    log_header.addWidget(log_enabled_check)
    log_layout.addLayout(log_header)
    
    log_text = QPlainTextEdit()
    log_text.setReadOnly(True)
    log_text.setMaximumBlockCount(1000)
    log_text.setStyleSheet("""
        QPlainTextEdit {
            background-color: #1e1e1e;
            color: #d4d4d4;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            border: 1px solid #3e3e3e;
            border-radius: 4px;
            padding: 4px;
        }
    """)
    log_layout.addWidget(log_text)
    log_group.setMaximumHeight(150)
    
    return log_group, log_text, log_enabled_check


def create_transfer_queue():
    """Create transfer queue panel"""
    queue_group = create_styled_groupbox("Transfer Queue")
    queue_layout = QVBoxLayout(queue_group)
    queue_layout.setContentsMargins(12, 12, 12, 12)
    queue_layout.setSpacing(8)
    
    queue_tabs = QTabWidget()
    
    active_widget = QWidget()
    active_layout = QVBoxLayout(active_widget)
    active_layout.setContentsMargins(0, 0, 0, 0)
    queue_table = create_file_table(["Direction", "Local File", "Remote File", "Size", "Status"])
    active_layout.addWidget(queue_table)
    queue_tabs.addTab(active_widget, "Active")
    
    completed_widget = QWidget()
    completed_layout = QVBoxLayout(completed_widget)
    completed_layout.setContentsMargins(0, 0, 0, 0)
    completed_table = create_file_table(["Direction", "Local File", "Remote File", "Size", "Status", "Completed"])
    completed_layout.addWidget(completed_table)
    queue_tabs.addTab(completed_widget, "Transferred")
    
    queue_layout.addWidget(queue_tabs)
    queue_group.setMaximumHeight(200)
    
    return queue_group, queue_table, completed_table
