"""Application entry point and setup."""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from .ui.main_window import MainWindow
from .ui.styles import DARK_THEME_QSS
from .data.loader import DataLoader
from .pages.overview import OverviewPage
from .pages.ranking import RankingPage
from .pages.pollutant import PollutantPage
from .pages.geo_map import GeoMapPage
from .pages.trends import TrendsPage
from .pages.health import HealthPage


def create_app() -> tuple[QApplication, MainWindow]:
    """Create and configure the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("AirScope")
    app.setStyleSheet(DARK_THEME_QSS)

    # Load data
    loader = DataLoader.get_instance()

    window = MainWindow()

    # Update filter bar with actual cities
    window.filter_bar.set_cities(loader.get_cities())

    # Set date range from data
    date_min, date_max = loader.get_date_range()
    from PySide6.QtCore import QDate
    window.filter_bar.date_start.setDate(QDate.fromString(date_min, "yyyy-MM-dd"))
    window.filter_bar.date_end.setDate(QDate.fromString(date_max, "yyyy-MM-dd"))

    # Create and add pages
    pages = [
        OverviewPage(),
        RankingPage(),
        PollutantPage(),
        GeoMapPage(),
        TrendsPage(),
        HealthPage(),
    ]

    for page in pages:
        window.add_page(page)
        page.load_page()

    # Connect filter bar to refresh current page
    def on_filter_applied(filters):
        idx = window.page_stack.currentIndex()
        page = pages[idx]
        if hasattr(page, "on_activated"):
            page.on_activated(filters)

    window.filter_bar.filter_applied.connect(on_filter_applied)

    # Activate first page after load with a short delay
    def activate_first():
        filters = window.filter_bar.get_filters()
        pages[0].on_activated(filters)
        window.set_status(f"已加载 {len(loader.df)} 条记录 | {len(loader.get_cities())} 个城市 | {date_min} ~ {date_max}")

    QTimer.singleShot(1000, activate_first)

    return app, window


def run():
    """Run the application."""
    app, window = create_app()
    window.show()
    sys.exit(app.exec())
