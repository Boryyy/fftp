"""
Theme Manager for FFTP
Centralizes application-wide styling with a modern dark theme.
"""

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

class ThemeManager:
    """Manages application theme and stylesheets"""
    
    # Modern Dark Color Palette
    DARK_COLORS = {
        "background": "#1e1e1e",
        "surface": "#252526",
        "surface_light": "#2d2d30",
        "text": "#d4d4d4",
        "text_secondary": "#a0a0a0",
        "accent": "#007acc",
        "accent_hover": "#0098ff",
        "accent_pressed": "#005c99",
        "border": "#3e3e42",
        "success": "#4caf50",
        "error": "#f44336",
        "warning": "#ff9800",
        "selection": "#264f78",
        "input_bg": "#3c3c3c"
    }

    # Light Color Palette (Refined for Modern Minimalism)
    LIGHT_COLORS = {
        "background": "#f5f5f5",           # Subtle gray background
        "panel_bg": "#ffffff",             # White for file lists
        "toolbar_bg": "#ffffff",           # White toolbar for cleanliness
        "input_bg": "#ffffff",             # White inputs
        "border": "#d1d1d1",               # Very subtle gray borders
        "text": "#202124",                 # Modern dark gray text
        "text_secondary": "#5f6368",       # Modern gray for labels
        "accent": "#1a73e8",               # Modern Google-style blue
        "accent_hover": "#174ea6",         
        "accent_pressed": "#1558d6",
        "success": "#1e8e3e",              
        "error": "#d93025",                
        "warning": "#f9ab00",              
        "selection": "#e8f0fe",            # Subtle light blue selection
        "hover": "#f1f3f4",                # Subtle gray hover
    }

    # Active colors (default to Light based on previous request)
    COLORS = LIGHT_COLORS

    @classmethod
    def set_theme(cls, theme_name: str):
        """Set the active theme ('Light' or 'Dark')"""
        if theme_name.lower() == "light":
            cls.COLORS = cls.LIGHT_COLORS
        else:
            cls.COLORS = cls.DARK_COLORS

    @classmethod
    def apply_theme(cls, app: QApplication):
        """Apply the global theme to the application"""
        
        # Set QPalette
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(cls.COLORS["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(cls.COLORS["text"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(cls.COLORS["input_bg"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(cls.COLORS["hover"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(cls.COLORS["text"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(cls.COLORS["panel_bg"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(cls.COLORS["text"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(cls.COLORS["selection"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(cls.COLORS["accent"]))
        app.setPalette(palette)

        # Apply global stylesheet
        app.setStyleSheet(cls.get_stylesheet())

    @classmethod
    def get_stylesheet(cls) -> str:
        """Get the full application stylesheet - Reconstructed for Modern Minimalism"""
        return f"""
            /* Global Reset */
            QWidget {{
                color: {cls.COLORS["text"]};
                font-family: 'Segoe UI', 'Roboto', 'Inter', sans-serif;
                font-size: 13px;
            }}

            /* Container Backgrounds */
            QMainWindow, QDialog, QTabWidget, QSplitter, QStackedWidget, QScrollArea {{
                background-color: {cls.COLORS["background"]};
            }}

            /* Main Splitters */
            QSplitter::handle {{
                background-color: {cls.COLORS["border"]};
                border: none;
            }}
            QSplitter::handle:hover {{
                background-color: {cls.COLORS["accent"]};
            }}

            /* ToolBar */
            QToolBar {{
                background-color: {cls.COLORS["toolbar_bg"]};
                border-bottom: 1px solid {cls.COLORS["border"]};
                spacing: 4px;
                padding: 4px;
                border-top: none;
                border-left: none;
                border-right: none;
            }}

            /* Buttons - Minimalistic */
            QPushButton {{
                background-color: #f1f2f6; /* Slightly darker than background for contrast */
                color: {cls.COLORS["text"]};
                border: 1px solid {cls.COLORS["border"]};
                padding: 3px 8px; /* Reduced padding for compact buttons */
                border-radius: 4px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {cls.COLORS["hover"]};
                border-color: {cls.COLORS["accent"]};
            }}
            QPushButton:pressed {{
                background-color: {cls.COLORS["border"]};
                padding-top: 4px;
                padding-left: 9px;
            }}
            QPushButton:disabled {{
                color: {cls.COLORS["text_secondary"]};
            }}

            /* Inputs */
            QLineEdit, QSpinBox {{
                background-color: {cls.COLORS["input_bg"]};
                border: 1px solid {cls.COLORS["border"]};
                border-radius: 4px;
                padding: 3px 6px;
                selection-background-color: {cls.COLORS["selection"]};
                selection-color: {cls.COLORS["accent"]};
            }}
            QLineEdit:focus, QSpinBox:focus {{
                border: 1px solid {cls.COLORS["accent"]};
            }}

            QSpinBox {{
                padding-right: 15px;
                border: 1px solid {cls.COLORS["border"]};
                background: white;
            }}
            QSpinBox::up-button {{
                width: 16px;
                border-left: 1px solid {cls.COLORS["border"]};
                background-color: #f8f9fa;
            }}
            QSpinBox::down-button {{
                width: 16px;
                border-left: 1px solid {cls.COLORS["border"]};
                background-color: #f8f9fa;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: #e8eaed;
            }}
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {{
                background-color: {cls.COLORS["selection"]};
            }}
            QSpinBox::up-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid {cls.COLORS["text"]};
                width: 0;
                height: 0;
            }}
            QSpinBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {cls.COLORS["text"]};
                width: 0;
                height: 0;
            }}

            /* Tables & TreeViews - Seamless */
            QTableView, QTreeView, QTableWidget {{
                background-color: {cls.COLORS["panel_bg"]};
                border: 1px solid {cls.COLORS["border"]};
                gridline-color: {cls.COLORS["hover"]};
                outline: none;
            }}
            QHeaderView::section {{
                background-color: {cls.COLORS["background"]};
                color: {cls.COLORS["text_secondary"]};
                padding: 8px;
                border: none;
                border-bottom: 1px solid {cls.COLORS["border"]};
                border-right: 1px solid {cls.COLORS["border"]};
                font-weight: 600;
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}

            /* TabWidget - Flat & Modern */
            QTabWidget::pane {{
                border-top: 1px solid {cls.COLORS["border"]};
                background-color: {cls.COLORS["panel_bg"]};
            }}
            QTabBar::tab {{
                background-color: transparent;
                padding: 8px 16px;
                color: {cls.COLORS["text_secondary"]};
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {cls.COLORS["accent"]};
                border-bottom: 2px solid {cls.COLORS["accent"]};
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {cls.COLORS["hover"]};
            }}

            /* Scrollbars - Thin & Modern */
            QScrollBar:vertical {{
                background-color: transparent;
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {cls.COLORS["border"]};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {cls.COLORS["text_secondary"]};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar:horizontal {{
                background-color: transparent;
                height: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {cls.COLORS["border"]};
                min-width: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """
