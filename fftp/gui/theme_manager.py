"""
Theme Manager for FFTP
Centralizes application-wide styling with a modern professional theme.
Updated as part of Phase 14: UI/UX Redesign
"""

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

class ThemeManager:
    """Manages application theme and stylesheets"""
    
    # Professional Light Color Palette (Primary)
    LIGHT_COLORS = {
        # Primary Brand Colors
        "primary": "#2563eb",           # Modern blue (primary actions)
        "primary_hover": "#1d4ed8",     # Darker blue (hover state)
        "primary_pressed": "#1e40af",   # Even darker (pressed state)
        
        # Accent & Status Colors
        "accent": "#10b981",            # Success green (accent)
        "accent_hover": "#059669",      # Darker green
        "success": "#10b981",           # Success state
        "warning": "#f59e0b",           # Warning state
        "error": "#ef4444",             # Error state
        "info": "#3b82f6",              # Info state
        
        # Neutral Colors (Background & Surfaces)
        "background": "#ffffff",        # Main background (white)
        "surface": "#f9fafb",           # Secondary surface (very light gray)
        "panel_bg": "#ffffff",          # Panel background
        "toolbar_bg": "#ffffff",        # Toolbar background
        "input_bg": "#ffffff",          # Input background
        
        # Borders & Dividers
        "border": "#e5e7eb",            # Standard border (light gray)
        "border_dark": "#d1d5db",       # Darker border for emphasis
        "border_light": "#f3f4f6",      # Lighter border for subtle division
        
        # Text Colors
        "text": "#111827",              # Primary text (near black)
        "text_secondary": "#6b7280",    # Secondary text (gray)
        "text_tertiary": "#9ca3af",     # Tertiary text (light gray)
        "text_disabled": "#d1d5db",     # Disabled text
        
        # Interactive States
        "hover": "#f3f4f6",             # Hover background
        "selection": "#dbeafe",         # Selection background (light blue)
        "focus": "#3b82f6",             # Focus outline
        
        # Transfer States
        "transfer_active": "#3b82f6",   # Active transfer (blue)
        "transfer_complete": "#10b981", # Completed transfer (green)
        "transfer_failed": "#ef4444",   # Failed transfer (red)
        "transfer_queued": "#6b7280",   # Queued transfer (gray)
    }

    # Active colors (default to Light)
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

            /* Buttons - Modern Professional */
            QPushButton {{
                background-color: {cls.COLORS["surface"]};
                color: {cls.COLORS["text"]};
                border: 1px solid {cls.COLORS["border"]};
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {cls.COLORS["hover"]};
                border-color: {cls.COLORS["primary"]};
            }}
            QPushButton:pressed {{
                background-color: {cls.COLORS["border"]};
            }}
            QPushButton:disabled {{
                color: {cls.COLORS["text_disabled"]};
                background-color: {cls.COLORS["surface"]};
                border-color: {cls.COLORS["border_light"]};
            }}
            
            /* Primary Action Buttons */
            QPushButton[primary="true"] {{
                background-color: {cls.COLORS["primary"]};
                color: white;
                border: none;
            }}
            QPushButton[primary="true"]:hover {{
                background-color: {cls.COLORS["primary_hover"]};
            }}
            QPushButton[primary="true"]:pressed {{
                background-color: {cls.COLORS["primary_pressed"]};
            }}

            /* Inputs - Clean & Modern */
            QLineEdit {{
                background-color: {cls.COLORS["input_bg"]};
                border: 1px solid {cls.COLORS["border"]};
                border-radius: 6px;
                padding: 6px 8px;
                selection-background-color: {cls.COLORS["selection"]};
                selection-color: {cls.COLORS["text"]};
                font-size: 11px;
            }}
            QLineEdit:focus {{
                border: 2px solid {cls.COLORS["focus"]};
                padding: 5px 7px;
            }}
            QLineEdit:disabled {{
                background-color: {cls.COLORS["surface"]};
                color: {cls.COLORS["text_disabled"]};
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

            /* Tables & TreeViews - Modern & Clean */
            QTableView, QTreeView, QTableWidget {{
                background-color: {cls.COLORS["panel_bg"]};
                border: 1px solid {cls.COLORS["border"]};
                gridline-color: {cls.COLORS["border_light"]};
                outline: none;
                selection-background-color: {cls.COLORS["selection"]};
                selection-color: {cls.COLORS["text"]};
                font-size: 11px;
            }}
            QTableView::item:hover, QTreeView::item:hover {{
                background-color: {cls.COLORS["hover"]};
            }}
            QTableView::item:selected, QTreeView::item:selected {{
                background-color: {cls.COLORS["selection"]};
                color: {cls.COLORS["text"]};
            }}
            QHeaderView::section {{
                background-color: {cls.COLORS["surface"]};
                color: {cls.COLORS["text_secondary"]};
                padding: 8px 12px;
                border: none;
                border-bottom: 2px solid {cls.COLORS["border"]};
                border-right: 1px solid {cls.COLORS["border_light"]};
                font-weight: 600;
                font-size: 10px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QHeaderView::section:hover {{
                background-color: {cls.COLORS["hover"]};
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

            /* Menus - Modern & Professional */
            QMenu {{
                background-color: {cls.COLORS["background"]};
                border: 1px solid {cls.COLORS["border"]};
                padding: 4px;
                border-radius: 6px;
            }}
            QMenu::item {{
                padding: 6px 24px;
                border-radius: 4px;
                color: {cls.COLORS["text"]};
            }}
            QMenu::item:selected {{
                background-color: {cls.COLORS["selection"]};
                color: {cls.COLORS["primary"]};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {cls.COLORS["border"]};
                margin: 4px 8px;
            }}
            
            QMenuBar {{
                background-color: {cls.COLORS["background"]};
                border-bottom: 1px solid {cls.COLORS["border"]};
            }}
            QMenuBar::item {{
                padding: 8px 12px;
                background: transparent;
            }}
            QMenuBar::item:selected {{
                background-color: {cls.COLORS["hover"]};
                border-radius: 4px;
            }}
        """
