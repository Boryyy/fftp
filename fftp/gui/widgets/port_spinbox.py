"""
Custom Port Spinbox - Native, reliable implementation
Created as part of Phase 14 (UI/UX Redesign)
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIntValidator


class PortSpinBox(QWidget):
    """
    Custom port spinbox with reliable up/down buttons
    Uses native QPushButton instead of CSS-styled QSpinBox subcontrols
    """
    
    valueChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 21
        self._minimum = 1
        self._maximum = 65535
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI with line edit and buttons"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Line edit for value display/input
        self.line_edit = QLineEdit()
        self.line_edit.setText(str(self._value))
        self.line_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.line_edit.setMaximumWidth(50)
        self.line_edit.setMinimumHeight(24)
        
        # Validator for numeric input
        validator = QIntValidator(self._minimum, self._maximum)
        self.line_edit.setValidator(validator)
        self.line_edit.editingFinished.connect(self._on_text_changed)
        
        layout.addWidget(self.line_edit)
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        
        # Up button
        self.up_button = QPushButton("▲")
        self.up_button.setMaximumWidth(18)
        self.up_button.setMinimumHeight(24)
        self.up_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #d0d0d0;
                border-left: none;
                background-color: #f8f9fa;
                padding: 0px;
                font-size: 8px;
            }
            QPushButton:hover {
                background-color: #e8eaed;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.up_button.clicked.connect(self.step_up)
        
        # Down button
        self.down_button = QPushButton("▼")
        self.down_button.setMaximumWidth(18)
        self.down_button.setMinimumHeight(24)
        self.down_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #d0d0d0;
                border-left: none;
                background-color: #f8f9fa;
                padding: 0px;
                font-size: 8px;
            }
            QPushButton:hover {
                background-color: #e8eaed;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.down_button.clicked.connect(self.step_down)
        
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        
        layout.addLayout(button_layout)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    
    def value(self) -> int:
        """Get current value"""
        return self._value
    
    def setValue(self, value: int):
        """Set value"""
        value = max(self._minimum, min(self._maximum, value))
        if value != self._value:
            self._value = value
            self.line_edit.setText(str(self._value))
            self.valueChanged.emit(self._value)
    
    def setRange(self, minimum: int, maximum: int):
        """Set value range"""
        self._minimum = minimum
        self._maximum = maximum
        self.line_edit.setValidator(QIntValidator(minimum, maximum))
        # Ensure current value is within range
        self.setValue(self._value)
    
    def setMinimum(self, minimum: int):
        """Set minimum value"""
        self.setRange(minimum, self._maximum)
    
    def setMaximum(self, maximum: int):
        """Set maximum value"""
        self.setRange(self._minimum, maximum)
    
    def minimum(self) -> int:
        """Get minimum value"""
        return self._minimum
    
    def maximum(self) -> int:
        """Get maximum value"""
        return self._maximum
    
    def step_up(self):
        """Increment value"""
        self.setValue(self._value + 1)
    
    def step_down(self):
        """Decrement value"""
        self.setValue(self._value - 1)
    
    def _on_text_changed(self):
        """Handle manual text input"""
        try:
            value = int(self.line_edit.text())
            self.setValue(value)
        except ValueError:
            # Reset to current value if invalid
            self.line_edit.setText(str(self._value))
    
    def setMinimumWidth(self, width: int):
        """Override to set line edit width"""
        self.line_edit.setMaximumWidth(width - 36)  # Account for buttons
        super().setMinimumWidth(width)
    
    def setMinimumHeight(self, height: int):
        """Override to set consistent height"""
        self.line_edit.setMinimumHeight(height)
        self.up_button.setMinimumHeight(height)
        self.down_button.setMinimumHeight(height)
        super().setMinimumHeight(height)
