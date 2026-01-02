"""
Directory comparison functionality for Fftp
"""

from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
from datetime import datetime
import os


class DirectoryComparator:
    """Handles directory comparison operations"""

    def __init__(self):
        self.comparison_mode = False
        self.hide_identical = False
        self.compare_by = "size"  # "size", "date", "both"
        self.local_files: Dict[str, Dict] = {}
        self.remote_files: Dict[str, Dict] = {}

    def set_comparison_mode(self, enabled: bool):
        """Enable or disable comparison mode"""
        self.comparison_mode = enabled
        if not enabled:
            self.clear_comparison_data()

    def clear_comparison_data(self):
        """Clear stored comparison data"""
        self.local_files.clear()
        self.remote_files.clear()

    def set_local_directory(self, path: str, files: List[Dict]):
        """Set local directory contents for comparison"""
        if not self.comparison_mode:
            return

        self.local_files.clear()
        for file_info in files:
            name = file_info['name']
            if name not in ['.', '..']:
                self.local_files[name] = file_info.copy()

    def set_remote_directory(self, path: str, files: List[Dict]):
        """Set remote directory contents for comparison"""
        if not self.comparison_mode:
            return

        self.remote_files.clear()
        for file_info in files:
            name = file_info['name']
            if name not in ['.', '..']:
                self.remote_files[name] = file_info.copy()

    def get_comparison_result(self, filename: str, is_local: bool) -> str:
        """Get comparison result for a file

        Returns:
            "newer" - file is newer than counterpart
            "older" - file is older than counterpart
            "bigger" - file is bigger than counterpart
            "smaller" - file is smaller than counterpart
            "identical" - files are identical
            "orphaned" - file exists only on one side
            "" - no comparison or no difference
        """
        if not self.comparison_mode:
            return ""

        local_file = self.local_files.get(filename)
        remote_file = self.remote_files.get(filename)

        if is_local:
            if not local_file:
                return ""
            if not remote_file:
                return "orphaned"

            return self._compare_files(local_file, remote_file)
        else:
            if not remote_file:
                return ""
            if not local_file:
                return "orphaned"

            return self._compare_files(remote_file, local_file)

    def _compare_files(self, file1: Dict, file2: Dict) -> str:
        """Compare two files and return result"""
        # Check if identical first
        if self._files_identical(file1, file2):
            return "identical"

        # Compare based on settings
        if self.compare_by == "size":
            size1 = file1.get('size', 0)
            size2 = file2.get('size', 0)
            if size1 > size2:
                return "bigger"
            elif size1 < size2:
                return "smaller"

        elif self.compare_by == "date":
            date1 = file1.get('modified')
            date2 = file2.get('modified')
            if date1 and date2:
                if date1 > date2:
                    return "newer"
                elif date1 < date2:
                    return "older"

        elif self.compare_by == "both":
            # Compare size first, then date
            size1 = file1.get('size', 0)
            size2 = file2.get('size', 0)
            if size1 != size2:
                if size1 > size2:
                    return "bigger"
                else:
                    return "smaller"

            # If sizes are equal, compare dates
            date1 = file1.get('modified')
            date2 = file2.get('modified')
            if date1 and date2:
                if date1 > date2:
                    return "newer"
                elif date1 < date2:
                    return "older"

        return ""

    def _files_identical(self, file1: Dict, file2: Dict) -> bool:
        """Check if two files are identical"""
        # Must have same name (already checked)
        # Check size
        if file1.get('size', 0) != file2.get('size', 0):
            return False

        # Check modification date (within 1 second tolerance)
        date1 = file1.get('modified')
        date2 = file2.get('modified')
        if date1 and date2:
            diff = abs((date1 - date2).total_seconds())
            if diff > 1:  # 1 second tolerance
                return False

        return True

    def should_hide_file(self, filename: str) -> bool:
        """Check if file should be hidden based on comparison settings"""
        if not self.comparison_mode or not self.hide_identical:
            return False

        result = self.get_comparison_result(filename, True)  # Check local
        if not result:
            result = self.get_comparison_result(filename, False)  # Check remote

        return result == "identical"


class ComparisonManager:
    """Manages directory comparison operations"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.comparator = DirectoryComparator()
        self.comparison_active = False

    def start_comparison(self):
        """Start directory comparison"""
        if not self.main_window.manager:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self.main_window, "No Connection",
                              "Please connect to a server first.")
            return

        self.comparison_active = True
        self.comparator.set_comparison_mode(True)

        # Refresh both file lists to trigger comparison
        self.main_window.load_local_files()
        self.main_window.load_remote_files()

        self.main_window.log("Directory comparison started")

    def stop_comparison(self):
        """Stop directory comparison"""
        self.comparison_active = False
        self.comparator.set_comparison_mode(False)

        # Refresh file lists to clear comparison indicators
        self.main_window.load_local_files()
        self.main_window.load_remote_files()

        self.main_window.log("Directory comparison stopped")

    def set_comparison_options(self, hide_identical: bool = False, compare_by: str = "size"):
        """Set comparison options"""
        self.comparator.hide_identical = hide_identical
        self.comparator.compare_by = compare_by

        if self.comparison_active:
            # Refresh to apply new options
            self.main_window.load_local_files()
            self.main_window.load_remote_files()

    def get_comparison_color(self, result: str) -> str:
        """Get color for comparison result"""
        colors = {
            "newer": "#27ae60",      # Green
            "older": "#e74c3c",      # Red
            "bigger": "#f39c12",     # Orange
            "smaller": "#9b59b6",    # Purple
            "orphaned": "#3498db",   # Blue
            "identical": "#95a5a6"   # Gray
        }
        return colors.get(result, "")

    def update_directory_data(self, is_local: bool, files: List[Dict]):
        """Update directory data for comparison"""
        if not self.comparison_active:
            return

        if is_local:
            self.comparator.set_local_directory(
                self.main_window.current_local_path, files)
        else:
            tab = self.main_window.get_current_tab()
            if tab:
                self.comparator.set_remote_directory(
                    tab.current_remote_path, files)