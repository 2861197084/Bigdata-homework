"""QSS theme stylesheet — clean light Shopify-inspired design."""

DARK_THEME_QSS = """
/* ============ Global ============ */
QMainWindow {
    background-color: #f6f6f7;
}

QWidget {
    background-color: transparent;
    color: #303030;
    font-family: "Microsoft YaHei", "Segoe UI", "PingFang SC", sans-serif;
    font-size: 13px;
}

/* ============ Sidebar ============ */
#sidebar {
    background-color: #1a1c23;
    border: none;
}

#sidebar QPushButton {
    background: transparent;
    color: rgba(255, 255, 255, 0.7);
    border: none;
    border-radius: 8px;
    text-align: left;
    padding: 10px 16px;
    margin: 2px 8px;
    font-size: 13px;
    font-weight: 400;
}

#sidebar QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.08);
    color: #ffffff;
}

#sidebar QPushButton:checked {
    background-color: rgba(255, 255, 255, 0.12);
    color: #ffffff;
    font-weight: 600;
}

#sidebar_logo {
    color: #ffffff;
    font-size: 17px;
    font-weight: 700;
    padding: 18px 16px 18px 16px;
    border: none;
    letter-spacing: 0.3px;
}

/* ============ Filter Bar ============ */
#filter_bar {
    background-color: #ffffff;
    border-bottom: 1px solid #e1e3e5;
    padding: 6px 16px;
}

QComboBox {
    background-color: #ffffff;
    color: #303030;
    border: 1px solid #c9cccf;
    border-radius: 8px;
    padding: 5px 10px;
    min-width: 110px;
    font-size: 13px;
}

QComboBox:hover {
    border-color: #919eab;
}

QComboBox:focus {
    border-color: #5c6ac4;
    outline: none;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #303030;
    border: 1px solid #c9cccf;
    border-radius: 8px;
    selection-background-color: #f2f7fe;
    selection-color: #303030;
    outline: none;
}

QDateEdit {
    background-color: #ffffff;
    color: #303030;
    border: 1px solid #c9cccf;
    border-radius: 8px;
    padding: 5px 10px;
    font-size: 13px;
}

QDateEdit:hover {
    border-color: #919eab;
}

QPushButton#apply_btn {
    background-color: #303030;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 6px 18px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton#apply_btn:hover {
    background-color: #1a1c23;
}

QPushButton#apply_btn:pressed {
    background-color: #000000;
}

/* ============ Scroll Bar ============ */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #c9cccf;
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #919eab;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ============ Status Bar ============ */
QStatusBar {
    background-color: #ffffff;
    color: #6d7175;
    border-top: 1px solid #e1e3e5;
    font-size: 12px;
    padding: 2px 8px;
}

/* ============ Labels ============ */
QLabel {
    color: #303030;
}

QLabel#secondary {
    color: #6d7175;
}

/* ============ Calendar Popup ============ */
QCalendarWidget {
    background-color: #ffffff;
    border: 1px solid #c9cccf;
    border-radius: 8px;
}
"""
