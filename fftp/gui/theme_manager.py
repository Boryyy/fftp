"""
Theme Manager for FFTP
Centralizes application-wide styling with modern professional themes.
"""

from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtWidgets import QApplication



def _check_icon() -> str:
    """Render a white check mark PNG for checked checkboxes"""
    import tempfile
    from pathlib import Path
    from PyQt6.QtCore import Qt, QPointF
    from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen

    path = Path(tempfile.gettempdir()) / "fftp_arrows" / "check_white.png"
    if not path.exists():
        path.parent.mkdir(exist_ok=True)
        pm = QPixmap(32, 32)
        pm.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pm)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#ffffff"))
        pen.setWidthF(3.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPolyline([QPointF(8, 17), QPointF(14, 23), QPointF(24, 10)])
        painter.end()
        pm.save(str(path))
    return path.as_posix()


_ARROW_CACHE = {}


def _arrow_icon(direction: str, color: str) -> str:
    """Render a small chevron PNG for spin/combo arrows (Qt can't draw CSS triangles).
    Returns a forward-slash path usable inside a stylesheet url()."""
    import tempfile
    from pathlib import Path
    from PyQt6.QtCore import Qt, QPointF
    from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen

    key = (direction, color)
    if key in _ARROW_CACHE and Path(_ARROW_CACHE[key]).exists():
        return _ARROW_CACHE[key]
    folder = Path(tempfile.gettempdir()) / "fftp_arrows"
    folder.mkdir(exist_ok=True)
    path = folder / f"{direction}_{color.lstrip('#')}.png"
    pm = QPixmap(20, 20)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(color))
    pen.setWidthF(2.4)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    y1, y2 = (13, 7) if direction == "up" else (7, 13)
    painter.drawPolyline([QPointF(4.5, y1), QPointF(10, y2), QPointF(15.5, y1)])
    painter.end()
    pm.save(str(path))
    _ARROW_CACHE[key] = path.as_posix()
    return _ARROW_CACHE[key]

class ThemeManager:
    """Manages application theme and stylesheets"""

    # Professional Light Color Palette
    LIGHT_COLORS = {
        "primary": "#2563eb",
        "primary_hover": "#1d4ed8",
        "primary_pressed": "#1e40af",
        "accent": "#10b981",
        "accent_hover": "#059669",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#3b82f6",
        "background": "#f8f9fc",
        "surface": "#ffffff",
        "panel_bg": "#ffffff",
        "toolbar_bg": "#ffffff",
        "input_bg": "#ffffff",
        "border": "#e2e8f0",
        "border_dark": "#cbd5e1",
        "border_light": "#f1f5f9",
        "text": "#1e293b",
        "text_secondary": "#64748b",
        "text_tertiary": "#94a3b8",
        "text_disabled": "#cbd5e1",
        "hover": "#f1f5f9",
        "selection": "#dbeafe",
        "selection_text": "#1e40af",
        "focus": "#3b82f6",
        "tab_active_bg": "#ffffff",
        "tab_inactive_bg": "transparent",
        "header_bg": "#f8fafc",
        "alt_row": "#f8fafc",
        "scrollbar_bg": "transparent",
        "scrollbar_handle": "#cbd5e1",
        "scrollbar_handle_hover": "#94a3b8",
        "log_bg": "#f8fafc",
        "log_border": "#e2e8f0",
        "transfer_active": "#3b82f6",
        "transfer_complete": "#10b981",
        "transfer_failed": "#ef4444",
        "transfer_queued": "#64748b",
    }

    # Professional Dark Color Palette
    DARK_COLORS = {
        "primary": "#3b82f6",
        "primary_hover": "#60a5fa",
        "primary_pressed": "#2563eb",
        "accent": "#34d399",
        "accent_hover": "#6ee7b7",
        "success": "#34d399",
        "warning": "#fbbf24",
        "error": "#f87171",
        "info": "#60a5fa",
        "background": "#0f172a",
        "surface": "#1e293b",
        "panel_bg": "#1e293b",
        "toolbar_bg": "#1e293b",
        "input_bg": "#0f172a",
        "border": "#334155",
        "border_dark": "#475569",
        "border_light": "#1e293b",
        "text": "#f1f5f9",
        "text_secondary": "#94a3b8",
        "text_tertiary": "#64748b",
        "text_disabled": "#475569",
        "hover": "#334155",
        "selection": "#1e3a5f",
        "selection_text": "#93c5fd",
        "focus": "#3b82f6",
        "tab_active_bg": "#1e293b",
        "tab_inactive_bg": "transparent",
        "header_bg": "#1e293b",
        "alt_row": "#162032",
        "scrollbar_bg": "transparent",
        "scrollbar_handle": "#475569",
        "scrollbar_handle_hover": "#64748b",
        "log_bg": "#0f172a",
        "log_border": "#334155",
        "transfer_active": "#3b82f6",
        "transfer_complete": "#34d399",
        "transfer_failed": "#f87171",
        "transfer_queued": "#64748b",
    }

    # Active colors (default to Dark)
    COLORS = DARK_COLORS
    _current_theme = "Dark"

    @classmethod
    def set_theme(cls, theme_name: str):
        """Set the active theme ('Light' or 'Dark')"""
        cls._current_theme = theme_name
        if theme_name.lower() == "light":
            cls.COLORS = cls.LIGHT_COLORS
        else:
            cls.COLORS = cls.DARK_COLORS

    @classmethod
    def get_current_theme(cls) -> str:
        return cls._current_theme

    @classmethod
    def apply_theme(cls, app: QApplication):
        """Apply the global theme to the application"""
        palette = QPalette()
        c = cls.COLORS
        palette.setColor(QPalette.ColorRole.Window, QColor(c["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(c["text"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(c["surface"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(c["alt_row"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(c["text"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(c["surface"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(c["text"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(c["selection"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(c["selection_text"]))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(c["surface"]))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(c["text"]))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(c["text_tertiary"]))
        app.setPalette(palette)
        app.setStyleSheet(cls.get_stylesheet())

    @classmethod
    def get_stylesheet(cls) -> str:
        """Get the full application stylesheet"""
        c = cls.COLORS
        return f"""
            /* ===== Global ===== */
            QWidget {{
                color: {c["text"]};
                font-family: 'Segoe UI', 'Inter', 'Roboto', -apple-system, sans-serif;
                font-size: 12px;
            }}

            QMainWindow, QDialog {{
                background-color: {c["background"]};
            }}

            /* ===== Splitters ===== */
            QSplitter::handle {{
                background-color: {c["border"]};
            }}
            QSplitter::handle:hover {{
                background-color: {c["primary"]};
            }}
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
            QSplitter::handle:vertical {{
                height: 2px;
            }}

            /* ===== Toolbar ===== */
            QToolBar {{
                background-color: {c["toolbar_bg"]};
                border: none;
                border-bottom: 1px solid {c["border"]};
                spacing: 6px;
                padding: 6px 8px;
            }}
            QToolBar QLabel {{
                color: {c["text_secondary"]};
                font-size: 11px;
                font-weight: 500;
                padding: 0 2px;
            }}

            /* ===== Buttons ===== */
            QPushButton {{
                background-color: {c["surface"]};
                color: {c["text"]};
                border: 1px solid {c["border"]};
                padding: 5px 14px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 11px;
                min-height: 18px;
            }}
            QPushButton:hover {{
                background-color: {c["hover"]};
                border-color: {c["primary"]};
                color: {c["primary"]};
            }}
            QPushButton:pressed {{
                background-color: {c["selection"]};
            }}
            QPushButton:disabled {{
                color: {c["text_disabled"]};
                background-color: {c["background"]};
                border-color: {c["border_light"]};
            }}
            QPushButton[primary="true"] {{
                background-color: {c["primary"]};
                color: #ffffff;
                border: none;
                font-weight: 600;
            }}
            QPushButton[primary="true"]:hover {{
                background-color: {c["primary_hover"]};
            }}
            QPushButton[primary="true"]:pressed {{
                background-color: {c["primary_pressed"]};
            }}

            /* ===== Inputs ===== */
            QLineEdit {{
                background-color: {c["input_bg"]};
                color: {c["text"]};
                border: 1px solid {c["border"]};
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 12px;
                selection-background-color: {c["selection"]};
                selection-color: {c["selection_text"]};
            }}
            QLineEdit:focus {{
                border: 1px solid {c["focus"]};
                outline: none;
            }}
            QLineEdit:disabled {{
                background-color: {c["background"]};
                color: {c["text_disabled"]};
            }}
            QLineEdit[echoMode="2"] {{
                lineedit-password-character: 9679;
            }}

            QSpinBox {{
                background-color: {c["input_bg"]};
                color: {c["text"]};
                border: 1px solid {c["border"]};
                border-radius: 6px;
                padding: 4px 8px;
                padding-right: 18px;
                font-size: 12px;
            }}
            QSpinBox:focus {{
                border: 1px solid {c["focus"]};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 16px;
                border: none;
                background-color: transparent;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {c["hover"]};
            }}
            QSpinBox::up-arrow {{
                image: url({_arrow_icon("up", c["text_secondary"])});
                width: 10px; height: 10px;
            }}
            QSpinBox::down-arrow {{
                image: url({_arrow_icon("down", c["text_secondary"])});
                width: 10px; height: 10px;
            }}

            QComboBox {{
                background-color: {c["input_bg"]};
                color: {c["text"]};
                border: 1px solid {c["border"]};
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 12px;
                min-width: 80px;
            }}
            QComboBox:focus {{
                border: 1px solid {c["focus"]};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: url({_arrow_icon("down", c["text_secondary"])});
                width: 10px; height: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {c["surface"]};
                border: 1px solid {c["border"]};
                selection-background-color: {c["selection"]};
                selection-color: {c["selection_text"]};
                padding: 4px;
            }}

            QCheckBox {{
                spacing: 8px;
                color: {c["text"]};
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {c["border_dark"]};
                border-radius: 4px;
                background-color: {c["input_bg"]};
            }}
            QCheckBox::indicator:checked {{
                background-color: {c["primary"]};
                border-color: {c["primary"]};
                image: url({_check_icon()});
            }}
            QCheckBox::indicator:hover {{
                border-color: {c["primary"]};
            }}

            /* ===== Tables & Trees ===== */
            QTableWidget, QTableView {{
                background-color: {c["surface"]};
                alternate-background-color: {c["alt_row"]};
                border: 1px solid {c["border"]};
                gridline-color: {c["border_light"]};
                outline: none;
                selection-background-color: {c["selection"]};
                selection-color: {c["selection_text"]};
                font-size: 12px;
                border-radius: 0px;
            }}
            QTableWidget::item, QTableView::item {{
                padding: 4px 8px;
                border: none;
            }}
            QTableWidget::item:hover, QTableView::item:hover {{
                background-color: {c["hover"]};
            }}
            QTableWidget::item:selected, QTableView::item:selected {{
                background-color: {c["selection"]};
                color: {c["selection_text"]};
            }}

            QTreeView, QTreeWidget {{
                background-color: {c["surface"]};
                border: 1px solid {c["border"]};
                outline: none;
                selection-background-color: {c["selection"]};
                selection-color: {c["selection_text"]};
                font-size: 12px;
            }}
            QTreeView::item, QTreeWidget::item {{
                padding: 3px 4px;
                border: none;
            }}
            QTreeView::item:hover, QTreeWidget::item:hover {{
                background-color: {c["hover"]};
            }}
            QTreeView::item:selected, QTreeWidget::item:selected {{
                background-color: {c["selection"]};
                color: {c["selection_text"]};
            }}
            QTreeView::branch {{
                background-color: {c["surface"]};
            }}

            QHeaderView::section {{
                background-color: {c["header_bg"]};
                color: {c["text_secondary"]};
                padding: 6px 10px;
                border: none;
                border-bottom: 1px solid {c["border"]};
                border-right: 1px solid {c["border_light"]};
                font-weight: 600;
                font-size: 11px;
            }}
            QHeaderView::section:hover {{
                background-color: {c["hover"]};
                color: {c["text"]};
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}

            /* ===== Tabs ===== */
            QTabWidget::pane {{
                border: 1px solid {c["border"]};
                background-color: {c["panel_bg"]};
                border-radius: 0px;
            }}
            QTabBar {{
                background-color: transparent;
            }}
            QTabBar::tab {{
                background-color: {c["tab_inactive_bg"]};
                color: {c["text_secondary"]};
                padding: 8px 18px;
                border: none;
                border-bottom: 2px solid transparent;
                font-size: 11px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                color: {c["primary"]};
                border-bottom: 2px solid {c["primary"]};
                background-color: {c["tab_active_bg"]};
                font-weight: 600;
            }}
            QTabBar::tab:hover:!selected {{
                color: {c["text"]};
                background-color: {c["hover"]};
            }}
            QTabBar::close-button {{
                image: none;
                subcontrol-position: right;
                padding: 2px;
            }}
            QTabBar::close-button:hover {{
                background-color: {c["error"]};
                border-radius: 3px;
            }}

            /* ===== Scrollbars ===== */
            QScrollBar:vertical {{
                background-color: {c["scrollbar_bg"]};
                width: 8px;
                margin: 0;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {c["scrollbar_handle"]};
                min-height: 30px;
                border-radius: 4px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {c["scrollbar_handle_hover"]};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            QScrollBar:horizontal {{
                background-color: {c["scrollbar_bg"]};
                height: 8px;
                margin: 0;
                border: none;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {c["scrollbar_handle"]};
                min-width: 30px;
                border-radius: 4px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {c["scrollbar_handle_hover"]};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}

            /* ===== Menus ===== */
            QMenuBar {{
                background-color: {c["toolbar_bg"]};
                border-bottom: 1px solid {c["border"]};
                padding: 2px 0;
            }}
            QMenuBar::item {{
                padding: 6px 12px;
                background: transparent;
                color: {c["text_secondary"]};
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {c["hover"]};
                color: {c["text"]};
            }}

            QMenu {{
                background-color: {c["surface"]};
                border: 1px solid {c["border"]};
                padding: 6px;
                border-radius: 8px;
            }}
            QMenu::item {{
                padding: 6px 28px 6px 16px;
                border-radius: 4px;
                color: {c["text"]};
            }}
            QMenu::item:selected {{
                background-color: {c["selection"]};
                color: {c["selection_text"]};
            }}
            QMenu::item:disabled {{
                color: {c["text_disabled"]};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {c["border"]};
                margin: 4px 8px;
            }}
            QMenu::indicator {{
                width: 14px;
                height: 14px;
                margin-left: 4px;
            }}

            /* ===== Status Bar ===== */
            QStatusBar {{
                background-color: {c["toolbar_bg"]};
                border-top: 1px solid {c["border"]};
                color: {c["text_secondary"]};
                font-size: 11px;
                padding: 2px 8px;
            }}
            QStatusBar::item {{
                border: none;
            }}

            /* ===== Text Edit (Logs) ===== */
            QTextEdit, QPlainTextEdit {{
                background-color: {c["log_bg"]};
                color: {c["text"]};
                border: 1px solid {c["log_border"]};
                font-family: 'Cascadia Code', 'Consolas', 'Fira Code', monospace;
                font-size: 11px;
                padding: 4px;
                selection-background-color: {c["selection"]};
                selection-color: {c["selection_text"]};
            }}

            /* ===== Group Box ===== */
            QGroupBox {{
                border: 1px solid {c["border"]};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
                font-weight: 600;
                color: {c["text"]};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: {c["text_secondary"]};
            }}

            /* ===== Dialog ===== */
            QDialog {{
                background-color: {c["background"]};
            }}
            QDialogButtonBox QPushButton {{
                min-width: 80px;
            }}

            /* ===== Progress Bar ===== */
            QProgressBar {{
                background-color: {c["background"]};
                border: 1px solid {c["border"]};
                border-radius: 4px;
                text-align: center;
                font-size: 10px;
                color: {c["text"]};
                height: 16px;
            }}
            QProgressBar::chunk {{
                background-color: {c["primary"]};
                border-radius: 3px;
            }}

            /* ===== Tooltips ===== */
            QToolTip {{
                background-color: {c["surface"]};
                color: {c["text"]};
                border: 1px solid {c["border"]};
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 11px;
            }}
        """
