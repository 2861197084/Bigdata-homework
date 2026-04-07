"""Application configuration and constants."""

import os
from pathlib import Path

# Paths
APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = APP_DIR / "assets"

# AQI levels per China HJ 633-2012
AQI_LEVELS = [
    {"label": "优", "min": 0, "max": 50, "color": "#00e400"},
    {"label": "良", "min": 51, "max": 100, "color": "#ffff00"},
    {"label": "轻度污染", "min": 101, "max": 150, "color": "#ff7e00"},
    {"label": "中度污染", "min": 151, "max": 200, "color": "#ff0000"},
    {"label": "重度污染", "min": 201, "max": 300, "color": "#8f3f97"},
    {"label": "严重污染", "min": 301, "max": 500, "color": "#7e0023"},
]

# App theme colors
COLORS = {
    "bg_primary": "#0f1117",
    "bg_surface": "#1a1d27",
    "bg_sidebar": "#141620",
    "accent": "#1e90ff",
    "accent_teal": "#00d4aa",
    "text_primary": "#e8eaed",
    "text_secondary": "#8b8fa3",
    "border": "#2a2d3a",
    "success": "#91cc75",
    "warning": "#fac858",
    "error": "#ee6666",
}

# Chart series palette
CHART_COLORS = [
    "#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de",
    "#3ba272", "#fc8452", "#9a60b4", "#ea7ccc", "#48b8d0",
]

# Default cities for filter
DEFAULT_CITIES = ["北京", "上海", "广州", "深圳", "成都"]

# Pollutant columns
POLLUTANTS = ["AQI", "PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
