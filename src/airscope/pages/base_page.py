"""Base page class with QWebEngineView for ECharts rendering."""

import json
import tempfile
from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QUrl

from ..charts.bridge import ChartBridge
from ..charts.theme import get_theme_json
from ..utils.config import ASSETS_DIR

# Temp directory for rendered pages
_TEMP_DIR = Path(tempfile.mkdtemp(prefix="airscope_"))

# Cache the ECharts JS content
_echarts_js_cache: str | None = None


def _get_echarts_js() -> str:
    global _echarts_js_cache
    if _echarts_js_cache is None:
        _echarts_js_cache = (ASSETS_DIR / "js" / "echarts.min.js").read_text(encoding="utf-8")
    return _echarts_js_cache


class BasePage(QWidget):
    """Base class for all dashboard pages."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.web_view.setStyleSheet("background: #0f1117;")

        self.bridge = ChartBridge()
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        layout.addWidget(self.web_view)

        self._loaded = False
        self._pending_data = None
        self.web_view.loadFinished.connect(self._on_load_finished)

    def load_page(self):
        """Write HTML to temp file and load via file:// URL.

        Using file:// loading instead of setHtml() because:
        1. setHtml has a 2MB size limit
        2. file:// allows proper local resource loading
        3. Better security context for JavaScript execution
        """
        html = self._build_full_html()
        page_name = self.__class__.__name__.lower()
        html_path = _TEMP_DIR / f"{page_name}.html"
        html_path.write_text(html, encoding="utf-8")
        self.web_view.load(QUrl.fromLocalFile(str(html_path)))

    def _build_full_html(self) -> str:
        """Build the complete HTML page with ECharts inlined."""
        echarts_js = _get_echarts_js()
        theme_json = get_theme_json()
        page_content = self.get_html_content()

        parts = [
            '<!DOCTYPE html><html><head><meta charset="utf-8"><style>',
            CSS_STYLES,
            '</style></head><body>',
            '<script>', echarts_js, '</script>',
            '<script>', UTILITY_JS.replace('__THEME_JSON__', theme_json), '</script>',
            page_content,
            '</body></html>',
        ]
        return ''.join(parts)

    def get_html_content(self) -> str:
        """Override in subclass: return page-specific HTML + JS."""
        return "<div style='text-align:center;padding:100px;color:#8b8fa3;'>Loading...</div>"

    def _on_load_finished(self, ok: bool):
        self._loaded = True
        if ok and self._pending_data is not None:
            self._push_data(self._pending_data)
            self._pending_data = None

    def push_data(self, data: dict):
        """Push data to the page's JavaScript updateCharts function."""
        if self._loaded:
            self._push_data(data)
        else:
            self._pending_data = data

    def _push_data(self, data: dict):
        js = json.dumps(data, ensure_ascii=False, default=str)
        self.web_view.page().runJavaScript(f"updateCharts({js});")

    def on_activated(self, filters: dict):
        """Called when this page becomes visible. Override in subclass."""
        pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._loaded:
            self.web_view.page().runJavaScript("resizeAll();")


# ── Static CSS ──

CSS_STYLES = """
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 100%; height: 100%; overflow: hidden; background: #0f1117; }
body {
    font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    color: #e8eaed;
}
.dashboard {
    width: 100%; height: 100%; padding: 16px;
    display: grid; gap: 12px; overflow-y: auto;
}
.chart-box {
    background: rgba(26, 29, 39, 0.85);
    border: 1px solid #2a2d3a;
    border-radius: 12px;
    padding: 12px;
    position: relative;
    min-height: 0;
}
.chart-box .chart-title {
    font-size: 14px; font-weight: 500; color: #e8eaed;
    margin-bottom: 8px; padding-left: 4px;
}
.chart-container {
    width: 100%; height: calc(100% - 30px); min-height: 200px;
}
.kpi-row {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
}
.kpi-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 18px 20px;
    position: relative; overflow: hidden;
}
.kpi-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, transparent 60%);
    pointer-events: none;
}
.kpi-label { font-size: 12px; color: #8b8fa3; margin-bottom: 8px; }
.kpi-value {
    font-size: 32px; font-weight: 700;
    font-family: "Consolas", "DIN Alternate", "Roboto Mono", monospace;
    line-height: 1.1;
}
.kpi-sub { font-size: 12px; color: #8b8fa3; margin-top: 6px; }
.kpi-sub .up { color: #ee6666; }
.kpi-sub .down { color: #91cc75; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2d3a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a3d4a; }
"""

# ── Static JS ──

UTILITY_JS = """
var charts = {};

function getAqiColor(value) {
    if (value <= 50) return '#00e400';
    if (value <= 100) return '#ffff00';
    if (value <= 150) return '#ff7e00';
    if (value <= 200) return '#ff0000';
    if (value <= 300) return '#8f3f97';
    return '#7e0023';
}

function getAqiLabel(value) {
    if (value <= 50) return '优';
    if (value <= 100) return '良';
    if (value <= 150) return '轻度污染';
    if (value <= 200) return '中度污染';
    if (value <= 300) return '重度污染';
    return '严重污染';
}

function initChart(id) {
    var dom = document.getElementById(id);
    if (!dom) { console.error('DOM not found: ' + id); return null; }
    if (charts[id]) { charts[id].dispose(); }
    var chart = echarts.init(dom, null, {renderer: 'canvas'});
    charts[id] = chart;
    return chart;
}

function resizeAll() {
    Object.values(charts).forEach(function(c) {
        if (c && !c.isDisposed()) c.resize();
    });
}

window.addEventListener('resize', resizeAll);

echarts.registerTheme('airscope-dark', __THEME_JSON__);
"""
