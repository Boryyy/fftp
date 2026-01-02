"""
UI component builders and styling helpers
"""

from PyQt6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox,
    QGroupBox, QTableWidget, QPlainTextEdit, QCheckBox,
    QWidget, QHBoxLayout, QVBoxLayout, QTabWidget,
    QHeaderView
)
from PyQt6.QtCore import Qt, QSize


def create_styled_button(text, min_height=32, min_width=None, style="default"):
    """Create a styled button
    Styles are now handled by global stylesheet via class properties
    """
    btn = QPushButton(text)
    btn.setMinimumHeight(min_height)
    if min_width:
        btn.setMinimumWidth(min_width)
    
    # Set style class property for stylesheet targeting
    if style == "primary":
        btn.setProperty("class", "primary")
    elif style == "secondary":
        btn.setProperty("class", "secondary")
    
    return btn


def create_styled_label(text, min_width=None, bold=True):
    """Create a styled label"""
    label = QLabel(text)
    if min_width:
        label.setMinimumWidth(min_width)
    
    # We use basic stylesheet here as it's specific to label weight
    if bold:
        label.setStyleSheet("font-weight: 600;")
    return label


def create_styled_groupbox(title):
    """Create a styled group box"""
    group = QGroupBox(title)
    # Styles managed by ThemeManager
    return group


def create_file_table(columns, double_click_callback=None, context_menu_callback=None, drag_enabled=False, drop_enabled=False):
    """Create a styled file table"""
    table = QTableWidget()
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels(columns)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setAlternatingRowColors(True)
    table.setSortingEnabled(True)
    
    # Setup header behavior
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    header.setStretchLastSection(True)
    
    table.verticalHeader().setVisible(False)
    table.setShowGrid(False)
    
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
    # Note: Modern UI typically uses status_panel, but keeping this for compatibility/bottom panel
    log_group = QGroupBox("Activity Log")
    log_layout = QVBoxLayout(log_group)
    log_layout.setContentsMargins(8, 8, 8, 8)
    log_layout.setSpacing(4)
    
    log_header = QHBoxLayout()
    if clear_callback:
        clear_log_btn = create_styled_button("Clear Log", min_height=26, min_width=80, style="secondary")
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
    # Font style needs to remain specific
    log_text.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace; font-size: 11px;")
    
    log_layout.addWidget(log_text)
    log_group.setMaximumHeight(150)
    
    return log_group, log_text, log_enabled_check


def create_transfer_queue():
    """Create transfer queue panel"""
    queue_group = QGroupBox("Transfer Queue")
    queue_layout = QVBoxLayout(queue_group)
    queue_layout.setContentsMargins(8, 8, 8, 8)
    queue_layout.setSpacing(8)
    
    queue_tabs = QTabWidget()
    
    active_widget = QWidget()
    active_layout = QVBoxLayout(active_widget)
    active_layout.setContentsMargins(0, 0, 0, 0)
    queue_table = create_file_table(["Direction", "Local File", "Remote File", "Size", "Status"])
    active_layout.addWidget(queue_table)
    queue_tabs.addTab(active_widget, "Active Transfers")
    
    completed_widget = QWidget()
    completed_layout = QVBoxLayout(completed_widget)
    completed_layout.setContentsMargins(0, 0, 0, 0)
    completed_table = create_file_table(["Direction", "Local File", "Remote File", "Size", "Status", "Completed"])
    completed_layout.addWidget(completed_table)
    queue_tabs.addTab(completed_widget, "Successful Transfers")
    
    failed_widget = QWidget()
    failed_layout = QVBoxLayout(failed_widget)
    failed_layout.setContentsMargins(0, 0, 0, 0)
    failed_table = create_file_table(["Direction", "Local File", "Remote File", "Size", "Status", "Error"])
    failed_layout.addWidget(failed_table)
    queue_tabs.addTab(failed_widget, "Failed Transfers")
    
    queue_layout.addWidget(queue_tabs)
    queue_group.setMaximumHeight(200)
    
    return queue_group, queue_table, completed_table, failed_table
