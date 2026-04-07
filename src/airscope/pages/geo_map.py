"""Spatiotemporal distribution (map) page."""

import json

from .base_page import BasePage
from ..data.loader import DataLoader
from ..data.processor import filter_data, city_map_data, calendar_heatmap_data
from ..utils.config import ASSETS_DIR

# Cache GeoJSON
_china_geo_cache: str | None = None


def _get_china_geo() -> str:
    global _china_geo_cache
    if _china_geo_cache is None:
        _china_geo_cache = (ASSETS_DIR / "geo" / "china.json").read_text(encoding="utf-8")
    return _china_geo_cache


class GeoMapPage(BasePage):

    def get_html_content(self) -> str:
        china_geo = _get_china_geo()
        # Build HTML with string concatenation to avoid f-string issues with GeoJSON
        return (
            '<script>echarts.registerMap("china", ' + china_geo + ');</script>\n'
            + _GEO_MAP_HTML
        )

    def on_activated(self, filters: dict):
        loader = DataLoader.get_instance()
        df = filter_data(loader.df, None,
                         filters.get("start_date"), filters.get("end_date"))

        map_data = city_map_data(df, loader.city_coords, "AQI")

        cal_city = filters.get("city") or "北京"
        years = loader.get_years()
        cal_year = years[-1] if years else 2024
        cal_data = calendar_heatmap_data(loader.df, cal_city, cal_year, "AQI")

        monthly = df.groupby("Month")["AQI"].mean()
        monthly_avg = [round(monthly.get(m, 0), 1) for m in range(1, 13)]

        self.push_data({
            "map_data": map_data,
            "calendar": cal_data,
            "calendar_year": cal_year,
            "monthly_avg": monthly_avg,
        })


_GEO_MAP_HTML = """
<div class="dashboard" style="grid-template-rows: 1fr 1fr; grid-template-columns: 1.3fr 0.7fr;">
    <div class="chart-box" style="grid-row: 1 / 3;">
        <div class="chart-title">中国城市 AQI 分布地图</div>
        <div id="map-chart" style="width:100%;height:calc(100% - 30px);"></div>
    </div>
    <div class="chart-box">
        <div class="chart-title">日历热力图</div>
        <div id="calendar-chart" class="chart-container"></div>
    </div>
    <div class="chart-box">
        <div class="chart-title">月度变化</div>
        <div id="timeline-chart" class="chart-container"></div>
    </div>
</div>

<script>
function updateCharts(data) {
    var map = initChart('map-chart');
    map.setOption({
        tooltip: {
            trigger: 'item',
            formatter: function(p) {
                if (p.seriesType === 'effectScatter') {
                    return p.name + '<br>AQI: ' + p.value[2];
                }
                return p.name;
            }
        },
        geo: {
            map: 'china',
            roam: true,
            zoom: 1.2,
            center: [105, 36],
            itemStyle: {
                areaColor: '#1a1d27',
                borderColor: '#2a2d3a',
                borderWidth: 0.8
            },
            emphasis: {
                itemStyle: { areaColor: 'rgba(30,144,255,0.2)' },
                label: { show: true, color: '#e8eaed' }
            },
            label: { show: false }
        },
        series: [{
            type: 'effectScatter',
            coordinateSystem: 'geo',
            data: data.map_data,
            symbolSize: function(val) { return Math.max(6, Math.min(25, val[2] / 5)); },
            encode: { value: 2 },
            showEffectOn: 'emphasis',
            rippleEffect: { brushType: 'stroke', scale: 3 },
            itemStyle: {
                color: function(p) { return getAqiColor(p.value[2]); },
                shadowBlur: 10
            },
            label: { show: false },
            emphasis: {
                label: {
                    show: true,
                    formatter: function(p) { return p.name + ': ' + p.value[2]; },
                    color: '#e8eaed',
                    fontSize: 12
                }
            }
        }]
    });

    var cal = initChart('calendar-chart');
    cal.setOption({
        tooltip: {
            formatter: function(p) { return p.value[0] + '<br>AQI: ' + p.value[1]; }
        },
        visualMap: {
            min: 0, max: 300, show: true,
            orient: 'horizontal', left: 'center', bottom: 5,
            inRange: {
                color: ['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#8f3f97', '#7e0023']
            },
            textStyle: { color: '#8b8fa3' }
        },
        calendar: {
            top: 30, left: 30, right: 30, bottom: 40,
            range: String(data.calendar_year),
            cellSize: ['auto', 14],
            itemStyle: { color: '#1a1d27', borderColor: '#2a2d3a', borderWidth: 0.5 },
            yearLabel: { color: '#8b8fa3' },
            monthLabel: { color: '#8b8fa3' },
            dayLabel: { color: '#8b8fa3', firstDay: 1 }
        },
        series: [{
            type: 'heatmap',
            coordinateSystem: 'calendar',
            data: data.calendar
        }]
    });

    var timeline = initChart('timeline-chart');
    var months = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
    timeline.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: 50, right: 20, top: 20, bottom: 30 },
        xAxis: {
            type: 'category', data: months,
            axisLabel: { color: '#8b8fa3' },
            axisLine: { lineStyle: { color: '#2a2d3a' } }
        },
        yAxis: {
            type: 'value', name: 'AQI',
            axisLabel: { color: '#8b8fa3' },
            splitLine: { lineStyle: { color: 'rgba(42,45,58,0.6)' } }
        },
        series: [{
            type: 'bar', barWidth: '55%',
            data: data.monthly_avg.map(function(v) {
                return { value: v, itemStyle: { color: getAqiColor(v),
                         borderRadius: [4, 4, 0, 0] } };
            }),
            label: { show: true, position: 'top', color: '#e8eaed', fontSize: 10,
                     formatter: function(p) { return p.value; } }
        }]
    });

    resizeAll();
}
</script>
"""
