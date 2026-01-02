"""
Fftp - FTP/SFTP Client
Main entry point
"""

import sys
from pathlib import Path

# Add the current directory to Python path to ensure proper imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from fftp.gui.main_window import FTPClientGUI


def main():
    try:
        app = QApplication(sys.argv)

        logo_path = Path(__file__).parent / "fftp" / "logo.png"
        if logo_path.exists():
            icon = QIcon(str(logo_path))
            app.setWindowIcon(icon)
            app.setProperty("applicationIcon", icon)

        print("Starting FFTP...")
        window = FTPClientGUI()
        window.show()
        print("FFTP started successfully")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting FFTP: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
