"""Filter bar widget for city, date range, and pollutant selection."""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QComboBox, QDateEdit, QLabel, QPushButton,
)
from PySide6.QtCore import Signal, QDate

from ..utils.config import DEFAULT_CITIES, POLLUTANTS


class FilterBar(QWidget):
    """Horizontal filter bar with city, date range, and pollutant selectors."""

    filter_applied = Signal(dict)

    def __init__(self, cities: list[str] | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("filter_bar")
        self.setFixedHeight(50)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 4)
        layout.setSpacing(12)

        # City selector
        layout.addWidget(QLabel("城市:"))
        self.city_combo = QComboBox()
        all_cities = cities or DEFAULT_CITIES
        self.city_combo.addItem("全部城市")
        self.city_combo.addItems(all_cities)
        self.city_combo.setEditable(True)
        layout.addWidget(self.city_combo)

        # Date range
        layout.addWidget(QLabel("从:"))
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate(2020, 1, 1))
        self.date_start.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.date_start)

        layout.addWidget(QLabel("至:"))
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate(2024, 12, 31))
        self.date_end.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.date_end)

        # Pollutant selector
        layout.addWidget(QLabel("指标:"))
        self.pollutant_combo = QComboBox()
        self.pollutant_combo.addItems(POLLUTANTS)
        layout.addWidget(self.pollutant_combo)

        # Apply button
        apply_btn = QPushButton("应用筛选")
        apply_btn.setObjectName("apply_btn")
        apply_btn.clicked.connect(self._on_apply)
        layout.addWidget(apply_btn)

        layout.addStretch()

    def _on_apply(self):
        city = self.city_combo.currentText()
        self.filter_applied.emit({
            "city": None if city == "全部城市" else city,
            "start_date": self.date_start.date().toString("yyyy-MM-dd"),
            "end_date": self.date_end.date().toString("yyyy-MM-dd"),
            "pollutant": self.pollutant_combo.currentText(),
        })

    def get_filters(self) -> dict:
        city = self.city_combo.currentText()
        return {
            "city": None if city == "全部城市" else city,
            "start_date": self.date_start.date().toString("yyyy-MM-dd"),
            "end_date": self.date_end.date().toString("yyyy-MM-dd"),
            "pollutant": self.pollutant_combo.currentText(),
        }

    def set_cities(self, cities: list[str]):
        current = self.city_combo.currentText()
        self.city_combo.clear()
        self.city_combo.addItem("全部城市")
        self.city_combo.addItems(cities)
        idx = self.city_combo.findText(current)
        if idx >= 0:
            self.city_combo.setCurrentIndex(idx)
