"""QSS dark theme stylesheet."""

DARK_THEME_QSS = """
/* ============ Global ============ */
QMainWindow, QWidget {
    background-color: #0f1117;
    color: #e8eaed;
    font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 13px;
}

/* ============ Sidebar ============ */
#sidebar {
    background-color: #141620;
    border-right: 1px solid #2a2d3a;
}

#sidebar QPushButton {
    background: transparent;
    color: #8b8fa3;
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 14px 20px;
    font-size: 14px;
}

#sidebar QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.05);
    color: #e8eaed;
}

#sidebar QPushButton:checked {
    background-color: rgba(30, 144, 255, 0.12);
    color: #1e90ff;
    border-left: 3px solid #1e90ff;
    font-weight: bold;
}

#sidebar_logo {
    color: #1e90ff;
    font-size: 20px;
    font-weight: bold;
    padding: 20px;
    border-bottom: 1px solid #2a2d3a;
}

/* ============ Filter Bar ============ */
#filter_bar {
    background-color: #141620;
    border-bottom: 1px solid #2a2d3a;
    padding: 8px 16px;
}

QComboBox {
    background-color: #1a1d27;
    color: #e8eaed;
    border: 1px solid #2a2d3a;
    border-radius: 6px;
    padding: 6px 12px;
    min-width: 120px;
}

QComboBox:hover {
    border-color: #1e90ff;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #1a1d27;
    color: #e8eaed;
    border: 1px solid #2a2d3a;
    selection-background-color: rgba(30, 144, 255, 0.3);
}

QDateEdit {
    background-color: #1a1d27;
    color: #e8eaed;
    border: 1px solid #2a2d3a;
    border-radius: 6px;
    padding: 6px 12px;
}

QDateEdit:hover {
    border-color: #1e90ff;
}

QPushButton#apply_btn {
    background-color: #1e90ff;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 7px 20px;
    font-weight: bold;
}

QPushButton#apply_btn:hover {
    background-color: #3aa0ff;
}

QPushButton#apply_btn:pressed {
    background-color: #1670cc;
}

/* ============ Scroll Bar ============ */
QScrollBar:vertical {
    background: #0f1117;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #2a2d3a;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #3a3d4a;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ============ Status Bar ============ */
QStatusBar {
    background-color: #141620;
    color: #8b8fa3;
    border-top: 1px solid #2a2d3a;
    font-size: 12px;
}

/* ============ Labels ============ */
QLabel {
    color: #e8eaed;
}

QLabel#secondary {
    color: #8b8fa3;
}
"""
