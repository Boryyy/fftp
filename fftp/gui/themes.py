
PREMIUM_LIGHT_THEME = """
QMainWindow {
    background-color: #f5f6fa;
    color: #2c3e50;
}

/* Ensure all text is visible with proper contrast */
QWidget {
    color: #2c3e50;
}

QLabel, QCheckBox, QRadioButton, QPushButton, QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QTableWidget {
    color: #2c3e50;
}

QTableWidget::item {
    color: #2c3e50;
}

QMenu::item, QMenuBar::item {
    color: #2c3e50;
}

QMenuBar {
    background-color: #ffffff;
    color: #2c3e50;
    border-bottom: 2px solid #e1e8ed;
    padding: 6px 0px;
    font-size: 13px;
    font-weight: 500;
}

QMenuBar::item {
    background-color: transparent;
    color: #34495e;
    padding: 8px 18px;
    border-radius: 4px;
    margin: 0px 1px;
}

QMenuBar::item:selected {
    background-color: #3498db;
    color: #ffffff;
}

QMenuBar::item:pressed {
    background-color: #2980b9;
}

QMenu {
    background-color: #ffffff;
    color: #2c3e50;
    border: 1px solid #e1e8ed;
    border-radius: 6px;
    padding: 6px;
    font-size: 13px;
}

QMenu::item {
    background-color: transparent;
    color: #34495e;
    padding: 8px 35px 8px 25px;
    border-radius: 4px;
    margin: 1px 0px;
    min-width: 160px;
}

QMenu::item:selected {
    background-color: #3498db;
    color: #ffffff;
}

QMenu::item:disabled {
    color: #bdc3c7;
}

QMenu::separator {
    height: 1px;
    background-color: #e1e8ed;
    margin: 6px 10px;
}

QToolBar {
    background-color: #ffffff;
    border: none;
    border-bottom: 2px solid #e1e8ed;
    spacing: 8px;
    padding: 10px 14px;
    min-height: 50px;
}

QToolBar QPushButton {
    background-color: #ecf0f1;
    color: #2c3e50;
    border: 1px solid #bdc3c7;
    border-radius: 5px;
    padding: 8px 18px;
    min-height: 34px;
    font-size: 12px;
    font-weight: 600;
}

QToolBar QPushButton:hover {
    background-color: #d5dbdb;
    border-color: #95a5a6;
    color: #2c3e50;
}

QToolBar QPushButton:pressed {
    background-color: #bdc3c7;
    border-color: #7f8c8d;
}

QToolBar QPushButton:disabled {
    background-color: #ecf0f1;
    color: #bdc3c7;
    border-color: #ecf0f1;
}

QToolBar QLabel {
    color: #34495e;
    font-size: 12px;
    font-weight: 600;
    padding: 0px 4px;
}

QLineEdit, QSpinBox, QComboBox {
    background-color: #ffffff;
    color: #2c3e50;
    border: 2px solid #bdc3c7;
    border-radius: 5px;
    padding: 8px 12px;
    font-size: 12px;
    selection-background-color: #3498db;
    selection-color: #ffffff;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 2px solid #3498db;
    background-color: #ffffff;
}

QLineEdit:hover, QSpinBox:hover, QComboBox:hover {
    border-color: #95a5a6;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #34495e;
    margin-right: 6px;
}

QPlainTextEdit, QTextEdit {
    background-color: #ffffff;
    color: #2c3e50;
    border: 2px solid #bdc3c7;
    border-radius: 5px;
    padding: 6px;
    font-size: 11px;
    font-family: 'Consolas', 'Courier New', monospace;
}

QLabel {
    color: #2c3e50;
    font-size: 12px;
    font-weight: 500;
}

QPushButton {
    background-color: #3498db;
    color: #ffffff;
    border: none;
    border-radius: 5px;
    padding: 9px 20px;
    min-height: 34px;
    font-size: 12px;
    font-weight: 600;
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

QGroupBox {
    font-weight: 700;
    font-size: 13px;
    color: #2c3e50;
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 18px;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0px 8px;
    background-color: #ffffff;
    color: #3498db;
}

QTableWidget {
    background-color: #ffffff;
    color: #2c3e50;
    border: 2px solid #bdc3c7;
    border-radius: 5px;
    gridline-color: #ecf0f1;
    selection-background-color: #3498db;
    selection-color: #ffffff;
    font-size: 11px;
}

QTableWidget::item {
    color: #2c3e50;
    padding: 5px 8px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #3498db;
    color: #ffffff;
}

QTableWidget::item:hover {
    background-color: #ecf0f1;
}

QHeaderView::section {
    background-color: #ecf0f1;
    color: #2c3e50;
    padding: 10px 8px;
    border: none;
    border-bottom: 2px solid #bdc3c7;
    border-right: 1px solid #bdc3c7;
    font-weight: 700;
    font-size: 11px;
}

QHeaderView::section:first {
    border-left: none;
}

QHeaderView::section:last {
    border-right: none;
}

QHeaderView::section:hover {
    background-color: #d5dbdb;
}

QStatusBar {
    background-color: #ffffff;
    color: #34495e;
    border-top: 2px solid #e1e8ed;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: 500;
}

QScrollBar:vertical {
    background-color: #ecf0f1;
    width: 14px;
    border: none;
    margin: 0px;
    border-radius: 7px;
}

QScrollBar::handle:vertical {
    background-color: #95a5a6;
    border-radius: 7px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #7f8c8d;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #ecf0f1;
    height: 14px;
    border: none;
    margin: 0px;
    border-radius: 7px;
}

QScrollBar::handle:horizontal {
    background-color: #95a5a6;
    border-radius: 7px;
    min-width: 30px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #7f8c8d;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QTabWidget::pane {
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #ecf0f1;
    color: #34495e;
    border: none;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #3498db;
    border-bottom: 3px solid #3498db;
}

QTabBar::tab:hover {
    background-color: #d5dbdb;
    color: #2c3e50;
}

QTreeView {
    background-color: #ffffff;
    color: #2c3e50;
    border: 2px solid #bdc3c7;
    border-radius: 5px;
    font-size: 11px;
}

QTreeView::item {
    padding: 4px;
    border: none;
    color: #2c3e50;
}

QTreeView::item:selected {
    background-color: #3498db;
    color: #ffffff;
}

QTreeView::item:hover {
    background-color: #ecf0f1;
}

QCheckBox {
    color: #2c3e50;
    font-size: 12px;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #bdc3c7;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #3498db;
    border-color: #3498db;
}

QCheckBox::indicator:hover {
    border-color: #95a5a6;
}

/* Secondary buttons styling */
QPushButton[class="secondary"] {
    background-color: #ecf0f1;
    color: #2c3e50;
    font-weight: 500;
    padding: 6px 12px;
    border: 1px solid #bdc3c7;
    border-radius: 3px;
    font-size: 11px;
}

QPushButton[class="secondary"]:hover {
    background-color: #d5dbdb;
    border-color: #95a5a6;
}

QPushButton[class="secondary"]:pressed {
    background-color: #bdc3c7;
}
"""

PREMIUM_DARK_THEME = """
QMainWindow {
    background-color: #1a1a1a;
    color: #e0e0e0;
}

/* Ensure all text is visible with proper contrast in dark theme */
QWidget {
    color: #e0e0e0;
}

QLabel, QCheckBox, QRadioButton, QPushButton, QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QTableWidget {
    color: #e0e0e0;
}

QTableWidget::item {
    color: #e0e0e0;
}

QMenu::item, QMenuBar::item {
    color: #e0e0e0;
}

QMenuBar {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border-bottom: 2px solid #404040;
    padding: 6px 0px;
    font-size: 13px;
    font-weight: 500;
}

QMenuBar::item {
    background-color: transparent;
    color: #e0e0e0;
    padding: 8px 18px;
    border-radius: 4px;
    margin: 0px 1px;
}

QMenuBar::item:selected {
    background-color: #3498db;
    color: #ffffff;
}

QMenuBar::item:pressed {
    background-color: #2980b9;
}

QMenu {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #404040;
    border-radius: 6px;
    padding: 6px;
    font-size: 13px;
}

QMenu::item {
    background-color: transparent;
    color: #e0e0e0;
    padding: 8px 35px 8px 25px;
    border-radius: 4px;
    margin: 1px 0px;
    min-width: 160px;
}

QMenu::item:selected {
    background-color: #3498db;
    color: #ffffff;
}

QMenu::item:disabled {
    color: #666666;
}

QMenu::separator {
    height: 1px;
    background-color: #404040;
    margin: 6px 10px;
}

QToolBar {
    background-color: #2d2d2d;
    border: none;
    border-bottom: 2px solid #404040;
    spacing: 8px;
    padding: 10px 14px;
    min-height: 50px;
}

QToolBar QPushButton {
    background-color: #3d3d3d;
    color: #e0e0e0;
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 8px 18px;
    min-height: 34px;
    font-size: 12px;
    font-weight: 600;
}

QToolBar QPushButton:hover {
    background-color: #4d4d4d;
    border-color: #666666;
    color: #ffffff;
}

QToolBar QPushButton:pressed {
    background-color: #555555;
}

QToolBar QPushButton:disabled {
    background-color: #3d3d3d;
    color: #666666;
    border-color: #3d3d3d;
}

QToolBar QLabel {
    color: #b0b0b0;
    font-size: 12px;
    font-weight: 600;
    padding: 0px 4px;
}

QLineEdit, QSpinBox, QComboBox {
    background-color: #3d3d3d;
    color: #e0e0e0;
    border: 2px solid #555555;
    border-radius: 5px;
    padding: 8px 12px;
    font-size: 12px;
    selection-background-color: #3498db;
    selection-color: #ffffff;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 2px solid #3498db;
    background-color: #444444;
}

QLineEdit:hover, QSpinBox:hover, QComboBox:hover {
    border-color: #666666;
}

QPlainTextEdit, QTextEdit {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 2px solid #555555;
    border-radius: 5px;
    padding: 6px;
    font-size: 11px;
    font-family: 'Consolas', 'Courier New', monospace;
}

QLabel {
    color: #e0e0e0;
    font-size: 12px;
    font-weight: 500;
}

QPushButton {
    background-color: #3498db;
    color: #ffffff;
    border: none;
    border-radius: 5px;
    padding: 9px 20px;
    min-height: 34px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #21618c;
}

QPushButton:disabled {
    background-color: #555555;
    color: #888888;
}

QGroupBox {
    font-weight: 700;
    font-size: 13px;
    color: #e0e0e0;
    border: 2px solid #555555;
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 18px;
    background-color: #2d2d2d;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0px 8px;
    background-color: #2d2d2d;
    color: #3498db;
}

QTableWidget {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 2px solid #555555;
    border-radius: 5px;
    gridline-color: #404040;
    selection-background-color: #3498db;
    selection-color: #ffffff;
    font-size: 11px;
}

QTableWidget::item {
    color: #e0e0e0;
    padding: 5px 8px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #3498db;
    color: #ffffff;
}

QTableWidget::item:hover {
    background-color: #3d3d3d;
}

QHeaderView::section {
    background-color: #3d3d3d;
    color: #e0e0e0;
    padding: 10px 8px;
    border: none;
    border-bottom: 2px solid #555555;
    border-right: 1px solid #555555;
    font-weight: 700;
    font-size: 11px;
}

QHeaderView::section:first {
    border-left: none;
}

QHeaderView::section:last {
    border-right: none;
}

QHeaderView::section:hover {
    background-color: #4d4d4d;
}

QStatusBar {
    background-color: #2d2d2d;
    color: #b0b0b0;
    border-top: 2px solid #404040;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: 500;
}

QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 14px;
    border: none;
    margin: 0px;
    border-radius: 7px;
}

QScrollBar::handle:vertical {
    background-color: #666666;
    border-radius: 7px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #777777;
}

QScrollBar:horizontal {
    background-color: #2d2d2d;
    height: 14px;
    border: none;
    margin: 0px;
    border-radius: 7px;
}

QScrollBar::handle:horizontal {
    background-color: #666666;
    border-radius: 7px;
    min-width: 30px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #777777;
}

QTabWidget::pane {
    border: 2px solid #555555;
    border-radius: 6px;
    background-color: #2d2d2d;
}

QTabBar::tab {
    background-color: #3d3d3d;
    color: #b0b0b0;
    border: none;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #2d2d2d;
    color: #3498db;
    border-bottom: 3px solid #3498db;
}

QTabBar::tab:hover {
    background-color: #4d4d4d;
    color: #ffffff;
}

QTreeView {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 2px solid #555555;
    border-radius: 5px;
    font-size: 11px;
}

QTreeView::item {
    padding: 4px;
    border: none;
    color: #e0e0e0;
}

QTreeView::item:selected {
    background-color: #3498db;
    color: #ffffff;
}

QTreeView::item:hover {
    background-color: #3d3d3d;
}

QCheckBox {
    color: #e0e0e0;
    font-size: 12px;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #555555;
    border-radius: 3px;
    background-color: #3d3d3d;
}

QCheckBox::indicator:checked {
    background-color: #3498db;
    border-color: #3498db;
}

QCheckBox::indicator:hover {
    border-color: #666666;
}

/* Secondary buttons styling for dark theme */
QPushButton[class="secondary"] {
    background-color: #3d3d3d;
    color: #e0e0e0;
    font-weight: 500;
    padding: 6px 12px;
    border: 1px solid #666666;
    border-radius: 3px;
    font-size: 11px;
}

QPushButton[class="secondary"]:hover {
    background-color: #4d4d4d;
    border-color: #777777;
}

QPushButton[class="secondary"]:pressed {
    background-color: #555555;
}
"""
