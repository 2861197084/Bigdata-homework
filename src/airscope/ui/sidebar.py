"""Navigation sidebar widget — dark sidebar, Shopify-style."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QButtonGroup
from PySide6.QtCore import Signal


class Sidebar(QWidget):
    """Vertical navigation sidebar."""

    page_changed = Signal(int)

    PAGES = [
        "总览",
        "城市排名",
        "污染物分析",
        "时空分布",
        "趋势预测",
        "健康影响",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo
        logo = QLabel("  AirScope")
        logo.setObjectName("sidebar_logo")
        layout.addWidget(logo)

        # Nav buttons
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        for i, label in enumerate(self.PAGES):
            btn = QPushButton(f"  {label}")
            btn.setCheckable(True)
            btn.setObjectName(f"nav_{i}")
            self._btn_group.addButton(btn, i)
            layout.addWidget(btn)

        layout.addStretch()

        self._btn_group.idClicked.connect(self.page_changed.emit)

        first_btn = self._btn_group.button(0)
        if first_btn:
            first_btn.setChecked(True)
