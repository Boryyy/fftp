
class IconThemeManager:
    def __init__(self):
        self.themes = ["Default", "Flat", "High Contrast"]

    def get_available_themes(self):
        return self.themes

    def get_icon(self, name, theme="Default"):
        """Get standard QIcon for a given name"""
        from PyQt6.QtWidgets import QApplication, QStyle
        
        style = QApplication.style()
        if not style:
            return None
            
        # Map common names to StandardPixmap
        mapping = {
            "connect": QStyle.StandardPixmap.SP_DialogYesButton,
            "disconnect": QStyle.StandardPixmap.SP_DialogNoButton,
            "refresh": QStyle.StandardPixmap.SP_BrowserReload,
            "folder": QStyle.StandardPixmap.SP_DirIcon,
            "file": QStyle.StandardPixmap.SP_FileIcon,
            "site_manager": QStyle.StandardPixmap.SP_DriveNetIcon,
            "upload": QStyle.StandardPixmap.SP_ArrowUp,
            "download": QStyle.StandardPixmap.SP_ArrowDown,
            "delete": QStyle.StandardPixmap.SP_TrashIcon,
            "settings": QStyle.StandardPixmap.SP_FileDialogDetailedView,
            "cancel": QStyle.StandardPixmap.SP_DialogCancelButton,
        }
        
        if name in mapping:
            return style.standardIcon(mapping[name])
            
        return None

_instance = None

def get_icon_theme_manager():
    global _instance
    if _instance is None:
        _instance = IconThemeManager()
    return _instance
