# Fix for main_window.py - UI improvements

# 1. Fix darkdetect import fallback (line 141)
old_code = """            except ImportError:
                # darkdetect not available, use saved theme
                pass"""

new_code = """            except ImportError:
                # darkdetect not available, use saved theme
                theme = settings.get('theme', 'Light')"""

# 2. Toolbar styling improvements
old_toolbar_code = """        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)"""

new_toolbar_code = """        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                spacing: 8px;
                padding: 4px;
            }
        """)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)"""

# 3. Main layout improvements
old_layout_code = """        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)"""

new_layout_code = """        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)"""

# 4. Splitter size improvements
old_splitter_sizes = """        # Set splitter sizes with proper proportions
        self.top_splitter.setSizes([150, 400])  # Log panel at top
        self.bottom_splitter.setSizes([300, 150])  # Main area and queue
        self.view_splitter.setSizes([300, 300])  # Equal local/remote with minimums
        self.queue_log_splitter.setSizes([100, 50])  # Queue larger than log"""

new_splitter_sizes = """        # Set splitter sizes with proper proportions
        self.top_splitter.setSizes([120, 600])  # More space for main content
        self.bottom_splitter.setSizes([400, 200])  # Better balance
        self.view_splitter.setSizes([350, 350])  # Equal local/remote
        self.queue_log_splitter.setSizes([120, 80])  # Better proportions"""

print("Copy these fixes to main_window.py at the specified locations")