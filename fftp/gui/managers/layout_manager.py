from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QTabWidget, QPlainTextEdit, QTableWidget, QHeaderView
from PyQt6.QtCore import Qt

# Import panels (assumes these are available in sys.path or relative imports work)
# We will pass the classes or use local imports to avoid circular deps if possible
# But LayoutManager acts as a factory here.

class LayoutManager:
    """Manages the main window layout, splitters, and panels"""
    def __init__(self, parent_window):
        self.parent = parent_window
        self.top_splitter = None
        self.bottom_splitter = None
        
    def setup_layout(self):
        """Setup the central layout and splitters"""
        central = QWidget()
        self.parent.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main vertical splitter (Message Log / File Views / Queue)
        self.bottom_splitter = QSplitter(Qt.Orientation.Vertical)
        self.bottom_splitter.setHandleWidth(1)
        self.parent.bottom_splitter = self.bottom_splitter

        # --- Top: Message Log (Status) ---
        from ..windows.status_panel import StatusPanel
        self.parent.status_panel = StatusPanel(self.parent)
        self.bottom_splitter.addWidget(self.parent.status_panel)

        # --- Middle: File Panels (Local | Remote) ---
        self.top_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.top_splitter.setHandleWidth(1)
        self.parent.top_splitter = self.top_splitter

        # Local Panel
        from ..windows.local_panel import LocalFilePanel
        self.parent.local_panel = LocalFilePanel(self.parent, self.parent.current_local_path)
        self.top_splitter.addWidget(self.parent.local_panel)
        
        # Remote Panel
        from ..windows.remote_panel import RemoteFilePanel
        self.parent.remote_panel = RemoteFilePanel(self.parent)
        self.top_splitter.addWidget(self.parent.remote_panel)
        
        # Set initial sizes for horizontal splitter (50/50)
        self.top_splitter.setSizes([500, 500])
        
        # Add horizontal splitter to vertical splitter
        self.bottom_splitter.addWidget(self.top_splitter)
        
        # --- Bottom: Queue Panel (Unified) ---
        from ..windows.queue_panel import QueuePanel
        self.parent.queue_panel = QueuePanel(self.parent)
        self.bottom_splitter.addWidget(self.parent.queue_panel)
        
        # Set initial sizes for vertical splitter (Log: 15%, Files: 60%, Queue: 25%)
        self.bottom_splitter.setSizes([100, 600, 150])
        
        # Add to main layout
        main_layout.addWidget(self.bottom_splitter)

    # create_bottom_panel removed - QueuePanel now handles all bottom tabs

