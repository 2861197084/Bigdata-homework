"""Main application window."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QStatusBar, QLabel,
)
from PySide6.QtCore import Qt

from .sidebar import Sidebar
from .filter_bar import FilterBar


class MainWindow(QMainWindow):
    """Main window with sidebar navigation and stacked pages."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AirScope - 中国城市空气质量监测可视化大屏")
        self.setMinimumSize(1280, 800)
        self.resize(1600, 900)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Right side: filter bar + page stack
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Filter bar
        self.filter_bar = FilterBar()
        right_layout.addWidget(self.filter_bar)

        # Page stack
        self.page_stack = QStackedWidget()
        right_layout.addWidget(self.page_stack)

        main_layout.addWidget(right)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status_label = QLabel("就绪")
        self.status.addWidget(self.status_label)

        # Wire sidebar navigation
        self.sidebar.page_changed.connect(self._switch_page)

        # Pages will be added by app.py
        self._pages = []

    def add_page(self, page: QWidget):
        """Add a page widget to the stack."""
        self._pages.append(page)
        self.page_stack.addWidget(page)

    def _switch_page(self, index: int):
        if 0 <= index < self.page_stack.count():
            self.page_stack.setCurrentIndex(index)
            page = self._pages[index]
            if hasattr(page, "on_activated"):
                page.on_activated(self.filter_bar.get_filters())

    def set_status(self, text: str):
        self.status_label.setText(text)
