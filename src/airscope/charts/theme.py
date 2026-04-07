"""ECharts light theme configuration — Shopify-inspired."""

import json

ECHARTS_THEME = {
    "color": [
        "#5c6ac4", "#47c1bf", "#f49342", "#de3618", "#50b83c",
        "#9c6ade", "#006fbb", "#f4d03f", "#b5bec9", "#00848e",
    ],
    "backgroundColor": "transparent",
    "textStyle": {
        "color": "#303030",
        "fontFamily": "Microsoft YaHei, Segoe UI, sans-serif",
    },
    "title": {
        "textStyle": {"color": "#303030", "fontSize": 14, "fontWeight": 600},
        "subtextStyle": {"color": "#6d7175"},
    },
    "legend": {
        "textStyle": {"color": "#6d7175", "fontSize": 12},
    },
    "tooltip": {
        "backgroundColor": "#ffffff",
        "borderColor": "#e1e3e5",
        "borderWidth": 1,
        "textStyle": {"color": "#303030", "fontSize": 12},
        "extraCssText": "box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-radius: 8px;",
    },
    "categoryAxis": {
        "axisLine": {"lineStyle": {"color": "#e1e3e5"}},
        "axisLabel": {"color": "#6d7175"},
        "splitLine": {"show": False},
        "axisTick": {"show": False},
    },
    "valueAxis": {
        "axisLine": {"show": False},
        "axisLabel": {"color": "#6d7175"},
        "splitLine": {"lineStyle": {"color": "#f0f1f2"}},
        "axisTick": {"show": False},
    },
}


def get_theme_json() -> str:
    return json.dumps(ECHARTS_THEME, ensure_ascii=False)
