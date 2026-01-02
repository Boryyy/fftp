"""
Icon themes system for Fftp - customizable file type icons and UI elements
"""

import json
from pathlib import Path
from typing import Dict, Optional
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QFont
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import QSize


class IconTheme:
    """Represents an icon theme with file type mappings"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.file_icons: Dict[str, QIcon] = {}
        self.ui_icons: Dict[str, QIcon] = {}
        self._create_default_icons()

    def _create_default_icons(self):
        """Create default monochrome icons for common file types"""
        # File type icons
        self.file_icons = {
            'folder': self._create_folder_icon(),
            'file': self._create_file_icon(),
            'image': self._create_image_icon(),
            'text': self._create_text_icon(),
            'archive': self._create_archive_icon(),
            'executable': self._create_executable_icon(),
            'audio': self._create_audio_icon(),
            'video': self._create_video_icon(),
            'code': self._create_code_icon(),
            'pdf': self._create_pdf_icon(),
        }

        # UI element icons
        self.ui_icons = {
            'connect': self._create_connect_icon(),
            'disconnect': self._create_disconnect_icon(),
            'upload': self._create_upload_icon(),
            'download': self._create_download_icon(),
            'refresh': self._create_refresh_icon(),
            'settings': self._create_settings_icon(),
            'search': self._create_search_icon(),
            'bookmark': self._create_bookmark_icon(),
        }

    def _create_folder_icon(self) -> QIcon:
        """Create a simple folder icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))  # Transparent background

        painter = QPainter(pixmap)
        painter.setPen(QColor(60, 120, 180))  # Blue color
        painter.setBrush(QColor(220, 235, 255))  # Light blue fill

        # Draw folder shape
        painter.drawRect(2, 4, 12, 8)  # Main folder body
        painter.drawRect(1, 3, 12, 3)  # Folder tab

        painter.end()
        return QIcon(pixmap)

    def _create_file_icon(self) -> QIcon:
        """Create a simple file icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(100, 100, 100))
        painter.setBrush(QColor(240, 240, 240))

        # Draw file shape
        points = [
            QPoint(3, 2), QPoint(11, 2), QPoint(12, 3), QPoint(12, 13), QPoint(3, 13)
        ]
        from PyQt6.QtGui import QPolygon
        polygon = QPolygon(points)
        painter.drawPolygon(polygon)

        painter.end()
        return QIcon(pixmap)

    def _create_image_icon(self) -> QIcon:
        """Create an image file icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(150, 100, 200))
        painter.setBrush(QColor(230, 210, 250))

        # Draw image shape with small square for picture
        painter.drawRect(2, 2, 12, 12)
        painter.setBrush(QColor(200, 150, 220))
        painter.drawRect(4, 4, 8, 6)

        painter.end()
        return QIcon(pixmap)

    def _create_text_icon(self) -> QIcon:
        """Create a text file icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(80, 120, 80))
        painter.setBrush(QColor(220, 240, 220))

        painter.drawRect(2, 2, 12, 12)

        # Draw text lines
        painter.setPen(QColor(60, 100, 60))
        painter.drawLine(4, 6, 12, 6)
        painter.drawLine(4, 8, 10, 8)
        painter.drawLine(4, 10, 12, 10)

        painter.end()
        return QIcon(pixmap)

    def _create_archive_icon(self) -> QIcon:
        """Create an archive file icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(120, 80, 60))
        painter.setBrush(QColor(240, 220, 200))

        painter.drawRect(2, 2, 12, 12)

        # Draw compression lines
        painter.setPen(QColor(100, 60, 40))
        for y in [5, 8, 11]:
            painter.drawLine(4, y, 12, y)

        painter.end()
        return QIcon(pixmap)

    def _create_executable_icon(self) -> QIcon:
        """Create an executable file icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(120, 60, 60))
        painter.setBrush(QColor(240, 220, 220))

        painter.drawRect(2, 2, 12, 12)

        # Draw gear-like pattern
        painter.setPen(QColor(100, 40, 40))
        painter.drawLine(6, 4, 10, 4)
        painter.drawLine(6, 12, 10, 12)
        painter.drawLine(4, 6, 4, 10)
        painter.drawLine(12, 6, 12, 10)

        painter.end()
        return QIcon(pixmap)

    def _create_audio_icon(self) -> QIcon:
        """Create an audio file icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(100, 80, 150))
        painter.setBrush(QColor(230, 220, 250))

        painter.drawRect(2, 2, 12, 12)

        # Draw sound waves
        painter.setPen(QColor(80, 60, 130))
        painter.drawLine(6, 5, 6, 11)
        painter.drawLine(8, 4, 8, 12)
        painter.drawLine(10, 6, 10, 10)

        painter.end()
        return QIcon(pixmap)

    def _create_video_icon(self) -> QIcon:
        """Create a video file icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(120, 100, 60))
        painter.setBrush(QColor(240, 235, 220))

        painter.drawRect(2, 2, 12, 12)

        # Draw play triangle
        painter.setBrush(QColor(200, 180, 100))
        points = [QPoint(5, 5), QPoint(5, 11), QPoint(9, 8)]
        from PyQt6.QtGui import QPolygon
        polygon = QPolygon(points)
        painter.drawPolygon(polygon)

        painter.end()
        return QIcon(pixmap)

    def _create_code_icon(self) -> QIcon:
        """Create a code file icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(60, 100, 120))
        painter.setBrush(QColor(220, 235, 240))

        painter.drawRect(2, 2, 12, 12)

        # Draw angle brackets
        painter.setPen(QColor(40, 80, 100))
        painter.drawLine(5, 6, 7, 4)
        painter.drawLine(7, 4, 7, 6)
        painter.drawLine(9, 6, 11, 4)
        painter.drawLine(9, 4, 11, 6)

        painter.end()
        return QIcon(pixmap)

    def _create_pdf_icon(self) -> QIcon:
        """Create a PDF file icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(180, 60, 60))
        painter.setBrush(QColor(250, 220, 220))

        painter.drawRect(2, 2, 12, 12)

        # Draw "PDF" text
        painter.setPen(QColor(150, 40, 40))
        font = QFont("Arial", 6, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(4, 10, "PDF")

        painter.end()
        return QIcon(pixmap)

    def _create_connect_icon(self) -> QIcon:
        """Create a connect icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(40, 120, 80))

        # Draw connection symbol
        painter.drawEllipse(6, 6, 4, 4)
        painter.drawLine(8, 2, 8, 6)
        painter.drawLine(8, 10, 8, 14)
        painter.drawLine(2, 8, 6, 8)
        painter.drawLine(10, 8, 14, 8)

        painter.end()
        return QIcon(pixmap)

    def _create_disconnect_icon(self) -> QIcon:
        """Create a disconnect icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(120, 40, 40))

        # Draw crossed connection symbol
        painter.drawEllipse(6, 6, 4, 4)
        painter.drawLine(8, 2, 8, 6)
        painter.drawLine(8, 10, 8, 14)
        painter.drawLine(2, 8, 6, 8)
        painter.drawLine(10, 8, 14, 8)
        # Cross lines
        painter.drawLine(3, 3, 13, 13)
        painter.drawLine(3, 13, 13, 3)

        painter.end()
        return QIcon(pixmap)

    def _create_upload_icon(self) -> QIcon:
        """Create an upload icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(40, 100, 150))

        # Draw arrow pointing up
        painter.drawLine(8, 14, 8, 2)
        painter.drawLine(8, 2, 5, 5)
        painter.drawLine(8, 2, 11, 5)

        painter.end()
        return QIcon(pixmap)

    def _create_download_icon(self) -> QIcon:
        """Create a download icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(40, 100, 150))

        # Draw arrow pointing down
        painter.drawLine(8, 2, 8, 14)
        painter.drawLine(8, 14, 5, 11)
        painter.drawLine(8, 14, 11, 11)

        painter.end()
        return QIcon(pixmap)

    def _create_refresh_icon(self) -> QIcon:
        """Create a refresh icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(80, 120, 80))

        # Draw circular arrow
        painter.drawArc(3, 3, 10, 10, 45 * 16, 270 * 16)
        painter.drawLine(8, 1, 10, 3)
        painter.drawLine(8, 1, 6, 3)

        painter.end()
        return QIcon(pixmap)

    def _create_settings_icon(self) -> QIcon:
        """Create a settings icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(100, 100, 100))

        # Draw gear
        painter.drawEllipse(4, 4, 8, 8)
        painter.drawEllipse(6, 6, 4, 4)

        # Draw gear teeth
        for angle in [0, 60, 120, 180, 240, 300]:
            import math
            rad = math.radians(angle)
            x1 = 8 + 6 * math.cos(rad)
            y1 = 8 + 6 * math.sin(rad)
            x2 = 8 + 4 * math.cos(rad)
            y2 = 8 + 4 * math.sin(rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        painter.end()
        return QIcon(pixmap)

    def _create_search_icon(self) -> QIcon:
        """Create a search icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(100, 100, 100))

        # Draw magnifying glass
        painter.drawEllipse(2, 2, 8, 8)
        painter.drawLine(8, 8, 12, 12)
        painter.drawLine(10, 10, 12, 12)

        painter.end()
        return QIcon(pixmap)

    def _create_bookmark_icon(self) -> QIcon:
        """Create a bookmark icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 255, 255, 0))

        painter = QPainter(pixmap)
        painter.setPen(QColor(150, 100, 60))
        painter.setBrush(QColor(250, 235, 210))

        # Draw bookmark shape
        points = [QPoint(4, 2), QPoint(12, 2), QPoint(12, 14), QPoint(8, 12), QPoint(4, 14)]
        from PyQt6.QtGui import QPolygon
        polygon = QPolygon(points)
        painter.drawPolygon(polygon)

        painter.end()
        return QIcon(pixmap)

    def get_file_icon(self, file_name: str, is_dir: bool = False) -> QIcon:
        """Get appropriate icon for a file"""
        if is_dir:
            return self.file_icons.get('folder', self.file_icons['file'])

        if not file_name:
            return self.file_icons['file']

        # Get file extension
        from pathlib import Path
        ext = Path(file_name).suffix.lower()

        # Map extensions to icon types
        icon_mapping = {
            # Images
            ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg', '.ico'): 'image',

            # Text files
            ('.txt', '.md', '.rtf'): 'text',

            # Archives
            ('.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'): 'archive',

            # Executables
            ('.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm'): 'executable',

            # Audio
            ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'): 'audio',

            # Video
            ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'): 'video',

            # Code files
            ('.py', '.js', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs',
             '.html', '.css', '.xml', '.json', '.yaml', '.yml', '.sh', '.bat', '.ps1'): 'code',

            # Documents
            ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'): 'pdf',
        }

        for extensions, icon_type in icon_mapping.items():
            if ext in extensions:
                return self.file_icons.get(icon_type, self.file_icons['file'])

        return self.file_icons['file']

    def get_ui_icon(self, icon_name: str) -> QIcon:
        """Get a UI icon by name"""
        return self.ui_icons.get(icon_name, QIcon())


class IconThemeManager:
    """Manages icon themes for the application"""

    def __init__(self):
        self.themes_dir = Path.home() / ".fftp" / "themes" / "icons"
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        self.themes: Dict[str, IconTheme] = {}
        self.current_theme: Optional[IconTheme] = None

        self._load_builtin_themes()
        self.set_theme("Default")

    def _load_builtin_themes(self):
        """Load built-in icon themes"""
        # Default monochrome theme
        default_theme = IconTheme("Default", "Simple monochrome icons")
        self.themes["Default"] = default_theme

        # Could add more themes here in the future

    def set_theme(self, theme_name: str):
        """Set the current icon theme"""
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]

    def get_current_theme(self) -> Optional[IconTheme]:
        """Get the current theme"""
        return self.current_theme

    def get_available_themes(self) -> list[str]:
        """Get list of available theme names"""
        return list(self.themes.keys())

    def get_file_icon(self, file_name: str, is_dir: bool = False) -> QIcon:
        """Get file icon from current theme"""
        if self.current_theme:
            return self.current_theme.get_file_icon(file_name, is_dir)
        return QIcon()

    def get_ui_icon(self, icon_name: str) -> QIcon:
        """Get UI icon from current theme"""
        if self.current_theme:
            return self.current_theme.get_ui_icon(icon_name)
        return QIcon()


# Global instance - lazy initialized
_icon_theme_manager = None

def get_icon_theme_manager() -> IconThemeManager:
    """Get the global icon theme manager instance (lazy initialization)"""
    global _icon_theme_manager, icon_theme_manager
    if _icon_theme_manager is None:
        _icon_theme_manager = IconThemeManager()
        icon_theme_manager = _icon_theme_manager  # Set backward compatibility
    return _icon_theme_manager