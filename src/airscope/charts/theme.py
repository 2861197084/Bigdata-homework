"""ECharts dark theme configuration."""

import json

ECHARTS_THEME = {
    "color": [
        "#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de",
        "#3ba272", "#fc8452", "#9a60b4", "#ea7ccc", "#48b8d0",
    ],
    "backgroundColor": "transparent",
    "textStyle": {
        "color": "#e8eaed",
        "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif",
    },
    "title": {
        "textStyle": {"color": "#e8eaed", "fontSize": 16, "fontWeight": 500},
        "subtextStyle": {"color": "#8b8fa3"},
    },
    "legend": {
        "textStyle": {"color": "#e8eaed"},
    },
    "tooltip": {
        "backgroundColor": "rgba(26, 29, 39, 0.95)",
        "borderColor": "#2a2d3a",
        "textStyle": {"color": "#e8eaed", "fontSize": 13},
    },
    "axisLine": {"lineStyle": {"color": "#2a2d3a"}},
    "splitLine": {"lineStyle": {"color": "#2a2d3a"}},
    "categoryAxis": {
        "axisLine": {"lineStyle": {"color": "#2a2d3a"}},
        "axisLabel": {"color": "#8b8fa3"},
        "splitLine": {"show": False},
    },
    "valueAxis": {
        "axisLine": {"lineStyle": {"color": "#2a2d3a"}},
        "axisLabel": {"color": "#8b8fa3"},
        "splitLine": {"lineStyle": {"color": "rgba(42, 45, 58, 0.6)"}},
    },
}


def get_theme_json() -> str:
    return json.dumps(ECHARTS_THEME, ensure_ascii=False)
