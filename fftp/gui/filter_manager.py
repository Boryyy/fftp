"""
File filtering system for Fftp
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path


class FilterCondition:
    """Represents a single filter condition"""

    def __init__(self, filter_type: str = "", match_type: str = "contains",
                 value: str = "", case_sensitive: bool = False):
        self.filter_type = filter_type  # "filename", "path", "size", "date"
        self.match_type = match_type    # "contains", "equals", "begins", "ends", "regex"
        self.value = value
        self.case_sensitive = case_sensitive

    def matches(self, file_info: Dict[str, Any]) -> bool:
        """Check if this condition matches the file info"""
        if self.filter_type == "filename":
            return self._matches_string(file_info.get('name', ''))
        elif self.filter_type == "path":
            return self._matches_string(file_info.get('path', ''))
        elif self.filter_type == "size":
            return self._matches_size(file_info.get('size', 0))
        elif self.filter_type == "date":
            return self._matches_date(file_info.get('modified'))
        return True

    def _matches_string(self, text: str) -> bool:
        """Match string patterns"""
        if not text:
            return False

        value = self.value if self.case_sensitive else self.value.lower()
        text = text if self.case_sensitive else text.lower()

        if self.match_type == "contains":
            return value in text
        elif self.match_type == "equals":
            return value == text
        elif self.match_type == "begins":
            return text.startswith(value)
        elif self.match_type == "ends":
            return text.endswith(value)
        elif self.match_type == "regex":
            try:
                flags = 0 if self.case_sensitive else re.IGNORECASE
                return bool(re.search(value, text, flags))
            except re.error:
                return False
        return False

    def _matches_size(self, file_size: int) -> bool:
        """Match file size conditions"""
        try:
            # Parse size value (e.g., "1MB", "500KB", "1024")
            size_str = self.value.strip()
            if size_str.endswith('KB'):
                target_size = int(size_str[:-2]) * 1024
            elif size_str.endswith('MB'):
                target_size = int(size_str[:-2]) * 1024 * 1024
            elif size_str.endswith('GB'):
                target_size = int(size_str[:-2]) * 1024 * 1024 * 1024
            else:
                target_size = int(size_str)

            if self.match_type == "equals":
                return file_size == target_size
            elif self.match_type == "greater":
                return file_size > target_size
            elif self.match_type == "less":
                return file_size < target_size
        except (ValueError, IndexError):
            pass
        return False

    def _matches_date(self, file_date: Optional[datetime]) -> bool:
        """Match date conditions"""
        if not file_date:
            return False

        try:
            # Parse date value
            now = datetime.now()

            if self.value.lower() == "today":
                target_date = now.date()
                file_date_only = file_date.date()
            elif self.value.lower() == "yesterday":
                target_date = (now - timedelta(days=1)).date()
                file_date_only = file_date.date()
            elif self.value.lower() == "this week":
                # Monday of this week
                target_date = now - timedelta(days=now.weekday())
                target_date = target_date.date()
                file_date_only = file_date.date()
                return file_date_only >= target_date
            elif self.value.lower() == "last week":
                # Monday of last week
                last_week = now - timedelta(days=now.weekday() + 7)
                target_date = last_week.date()
                next_week = target_date + timedelta(days=7)
                file_date_only = file_date.date()
                return target_date <= file_date_only < next_week
            else:
                # Try to parse as relative days
                days = int(self.value)
                target_date = (now - timedelta(days=days)).date()
                file_date_only = file_date.date()

            if self.match_type == "equals":
                return file_date_only == target_date
            elif self.match_type == "before":
                return file_date_only < target_date
            elif self.match_type == "after":
                return file_date_only > target_date

        except (ValueError, AttributeError):
            pass
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'filter_type': self.filter_type,
            'match_type': self.match_type,
            'value': self.value,
            'case_sensitive': self.case_sensitive
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterCondition':
        """Create from dictionary"""
        return cls(
            filter_type=data.get('filter_type', ''),
            match_type=data.get('match_type', 'contains'),
            value=data.get('value', ''),
            case_sensitive=data.get('case_sensitive', False)
        )


class FilterSet:
    """A set of filter conditions"""

    def __init__(self, name: str = "", conditions: List[FilterCondition] = None,
                 match_all: bool = True, apply_to_dirs: bool = True,
                 apply_to_files: bool = True):
        self.name = name
        self.conditions = conditions or []
        self.match_all = match_all  # True = AND, False = OR
        self.apply_to_dirs = apply_to_dirs
        self.apply_to_files = apply_to_files

    def matches(self, file_info: Dict[str, Any]) -> bool:
        """Check if this filter set matches the file"""
        # Check if filter applies to this file type
        is_dir = file_info.get('is_dir', False)
        if is_dir and not self.apply_to_dirs:
            return True  # Don't filter directories if not enabled
        if not is_dir and not self.apply_to_files:
            return True  # Don't filter files if not enabled

        if not self.conditions:
            return True

        if self.match_all:  # AND logic
            return all(condition.matches(file_info) for condition in self.conditions)
        else:  # OR logic
            return any(condition.matches(file_info) for condition in self.conditions)

    def add_condition(self, condition: FilterCondition):
        """Add a condition to this filter set"""
        self.conditions.append(condition)

    def remove_condition(self, index: int):
        """Remove a condition by index"""
        if 0 <= index < len(self.conditions):
            self.conditions.pop(index)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'conditions': [cond.to_dict() for cond in self.conditions],
            'match_all': self.match_all,
            'apply_to_dirs': self.apply_to_dirs,
            'apply_to_files': self.apply_to_files
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterSet':
        """Create from dictionary"""
        conditions = [FilterCondition.from_dict(cond_data)
                     for cond_data in data.get('conditions', [])]
        return cls(
            name=data.get('name', ''),
            conditions=conditions,
            match_all=data.get('match_all', True),
            apply_to_dirs=data.get('apply_to_dirs', True),
            apply_to_files=data.get('apply_to_files', True)
        )


class FilterManager:
    """Manages file filtering"""

    def __init__(self):
        self.filter_sets: List[FilterSet] = []
        self.active_filters: List[FilterSet] = []
        self.filters_enabled = True

    def add_filter_set(self, filter_set: FilterSet):
        """Add a filter set"""
        self.filter_sets.append(filter_set)

    def remove_filter_set(self, name: str):
        """Remove a filter set by name"""
        self.filter_sets = [fs for fs in self.filter_sets if fs.name != name]

    def get_filter_set(self, name: str) -> Optional[FilterSet]:
        """Get a filter set by name"""
        for fs in self.filter_sets:
            if fs.name == name:
                return fs
        return None

    def activate_filter(self, filter_set: FilterSet):
        """Activate a filter set"""
        if filter_set not in self.active_filters:
            self.active_filters.append(filter_set)

    def deactivate_filter(self, filter_set: FilterSet):
        """Deactivate a filter set"""
        if filter_set in self.active_filters:
            self.active_filters.remove(filter_set)

    def clear_active_filters(self):
        """Clear all active filters"""
        self.active_filters.clear()

    def is_filtered(self, file_info: Dict[str, Any]) -> bool:
        """Check if a file should be filtered (hidden)"""
        if not self.filters_enabled or not self.active_filters:
            return False

        # File is filtered if ANY active filter matches it
        return any(fs.matches(file_info) for fs in self.active_filters)

    def toggle_filters(self):
        """Toggle filtering on/off"""
        self.filters_enabled = not self.filters_enabled

    def create_default_filters(self):
        """Create some default filter sets"""
        # Filter out hidden files
        hidden_files = FilterSet("Hidden files")
        hidden_condition = FilterCondition("filename", "begins", ".")
        hidden_files.add_condition(hidden_condition)
        self.add_filter_set(hidden_files)

        # Filter by size (> 100MB)
        large_files = FilterSet("Large files (>100MB)")
        large_condition = FilterCondition("size", "greater", "100MB")
        large_files.add_condition(large_condition)
        self.add_filter_set(large_files)

        # Filter old files (> 1 year)
        old_files = FilterSet("Old files (>1 year)")
        old_condition = FilterCondition("date", "before", "365")
        old_files.add_condition(old_condition)
        self.add_filter_set(old_files)

    def save_filters(self, filepath: str):
        """Save filter sets to file"""
        import json
        data = {
            'filter_sets': [fs.to_dict() for fs in self.filter_sets],
            'active_filters': [fs.name for fs in self.active_filters],
            'filters_enabled': self.filters_enabled
        }
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving filters: {e}")

    def load_filters(self, filepath: str):
        """Load filter sets from file"""
        import json
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            self.filter_sets = [FilterSet.from_dict(fs_data)
                              for fs_data in data.get('filter_sets', [])]

            active_names = data.get('active_filters', [])
            self.active_filters = [fs for fs in self.filter_sets if fs.name in active_names]

            self.filters_enabled = data.get('filters_enabled', True)

        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            print(f"Error loading filters: {e}")
            # Create default filters if loading fails
            self.create_default_filters()