"""
Fftp - FTP/SFTP Client
Main entry point
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from fftp.gui.main_window import FTPClientGUI


def main():
    app = QApplication(sys.argv)
    
    logo_path = Path(__file__).parent / "fftp" / "logo.png"
    if logo_path.exists():
        icon = QIcon(str(logo_path))
        app.setWindowIcon(icon)
        app.setProperty("applicationIcon", icon)
    
    window = FTPClientGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
