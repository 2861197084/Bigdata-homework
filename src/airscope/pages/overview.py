"""Overview dashboard page."""

from .base_page import BasePage
from ..data.loader import DataLoader
from ..data.processor import (
    filter_data, national_stats, city_ranking, city_daily_trend,
    aqi_distribution,
)


class OverviewPage(BasePage):

    def get_html_content(self) -> str:
        return """
<div class="dashboard" style="grid-template-rows: auto auto 1fr; grid-template-columns: 1fr 1fr;">
    <!-- KPI Row -->
    <div class="kpi-row" style="grid-column: 1 / -1;">
        <div class="kpi-card" id="kpi-avg">
            <div class="kpi-label">全国平均 AQI</div>
            <div class="kpi-value" id="kpi-avg-value">--</div>
            <div class="kpi-sub" id="kpi-avg-sub"></div>
        </div>
        <div class="kpi-card" id="kpi-worst">
            <div class="kpi-label">最污染城市</div>
            <div class="kpi-value" id="kpi-worst-value" style="font-size:24px;">--</div>
            <div class="kpi-sub" id="kpi-worst-sub"></div>
        </div>
        <div class="kpi-card" id="kpi-best">
            <div class="kpi-label">最清洁城市</div>
            <div class="kpi-value" id="kpi-best-value" style="font-size:24px;">--</div>
            <div class="kpi-sub" id="kpi-best-sub"></div>
        </div>
        <div class="kpi-card" id="kpi-exceed">
            <div class="kpi-label">超标城市数</div>
            <div class="kpi-value" id="kpi-exceed-value">--</div>
            <div class="kpi-sub" id="kpi-exceed-sub"></div>
        </div>
    </div>

    <!-- Gauge + Line -->
    <div class="chart-box" style="grid-column: 1 / -1; height: 300px;">
        <div class="chart-title">AQI 仪表盘 & 日均趋势</div>
        <div style="display:flex; height:calc(100% - 30px);">
            <div id="gauge-chart" style="width:35%; height:100%;"></div>
            <div id="trend-chart" style="width:65%; height:100%;"></div>
        </div>
    </div>

    <!-- Bar + Pie -->
    <div class="chart-box" style="height: 380px;">
        <div class="chart-title">Top 10 污染城市</div>
        <div id="bar-chart" class="chart-container"></div>
    </div>
    <div class="chart-box" style="height: 380px;">
        <div class="chart-title">AQI 等级分布</div>
        <div id="pie-chart" class="chart-container"></div>
    </div>
</div>

<script>
function updateCharts(data) {
    // KPI cards
    var stats = data.stats;
    document.getElementById('kpi-avg-value').textContent = stats.national_avg_aqi;
    document.getElementById('kpi-avg-value').style.color = getAqiColor(stats.national_avg_aqi);

    document.getElementById('kpi-worst-value').textContent = stats.worst_city;
    document.getElementById('kpi-worst-sub').innerHTML = 'AQI: <span style="color:' + getAqiColor(stats.worst_city_aqi) + '">' + stats.worst_city_aqi + '</span>';

    document.getElementById('kpi-best-value').textContent = stats.best_city;
    document.getElementById('kpi-best-sub').innerHTML = 'AQI: <span style="color:' + getAqiColor(stats.best_city_aqi) + '">' + stats.best_city_aqi + '</span>';

    document.getElementById('kpi-exceed-value').textContent = stats.exceed_count;
    document.getElementById('kpi-exceed-sub').textContent = '共 ' + stats.total_cities + ' 个城市';

    // Gauge
    var gauge = initChart('gauge-chart');
    gauge.setOption({
        series: [{
            type: 'gauge',
            startAngle: 210,
            endAngle: -30,
            min: 0,
            max: 500,
            axisLine: {
                lineStyle: {
                    width: 20,
                    color: [
                        [0.1, '#00e400'], [0.2, '#ffff00'], [0.3, '#ff7e00'],
                        [0.4, '#ff0000'], [0.6, '#8f3f97'], [1, '#7e0023']
                    ]
                }
            },
            pointer: { itemStyle: { color: '#1e90ff' }, width: 5 },
            axisTick: { distance: -20, length: 6, lineStyle: { color: '#fff', width: 1 } },
            splitLine: { distance: -25, length: 20, lineStyle: { color: '#fff', width: 2 } },
            axisLabel: { color: '#8b8fa3', distance: 30, fontSize: 11 },
            detail: {
                valueAnimation: true, fontSize: 28, color: '#e8eaed',
                formatter: function(v) { return Math.round(v) + '\\n' + getAqiLabel(v); },
                offsetCenter: [0, '70%']
            },
            data: [{ value: stats.national_avg_aqi }]
        }]
    });

    // Daily trend line
    var trend = initChart('trend-chart');
    var trendData = data.trend;
    trend.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: 50, right: 20, top: 20, bottom: 50 },
        xAxis: {
            type: 'category',
            data: trendData.map(function(d) { return d.date; }),
            axisLabel: { color: '#8b8fa3', rotate: 30, fontSize: 10 },
            axisLine: { lineStyle: { color: '#2a2d3a' } }
        },
        yAxis: {
            type: 'value', name: 'AQI',
            axisLabel: { color: '#8b8fa3' },
            splitLine: { lineStyle: { color: 'rgba(42,45,58,0.6)' } }
        },
        dataZoom: [
            { type: 'inside', start: 80, end: 100 },
            { type: 'slider', height: 20, bottom: 5, borderColor: '#2a2d3a',
              fillerColor: 'rgba(30,144,255,0.2)', handleStyle: { color: '#1e90ff' } }
        ],
        series: [{
            type: 'line', data: trendData.map(function(d) { return d.value; }),
            smooth: true, showSymbol: false, lineStyle: { width: 2, color: '#1e90ff' },
            areaStyle: {
                color: {
                    type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                    colorStops: [
                        { offset: 0, color: 'rgba(30,144,255,0.35)' },
                        { offset: 1, color: 'rgba(30,144,255,0.02)' }
                    ]
                }
            }
        }]
    });

    // Top 10 bar
    var bar = initChart('bar-chart');
    var ranking = data.ranking.slice(0, 10).reverse();
    bar.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: 80, right: 30, top: 10, bottom: 10 },
        xAxis: {
            type: 'value',
            axisLabel: { color: '#8b8fa3' },
            splitLine: { lineStyle: { color: 'rgba(42,45,58,0.6)' } }
        },
        yAxis: {
            type: 'category',
            data: ranking.map(function(d) { return d.city; }),
            axisLabel: { color: '#e8eaed', fontSize: 12 }
        },
        series: [{
            type: 'bar', barWidth: '60%',
            data: ranking.map(function(d) {
                return { value: d.value, itemStyle: { color: getAqiColor(d.value) } };
            }),
            label: {
                show: true, position: 'right',
                formatter: function(p) { return p.value; },
                color: '#e8eaed', fontSize: 11
            }
        }]
    });

    // AQI distribution pie
    var pie = initChart('pie-chart');
    var aqiColors = { '优': '#00e400', '良': '#ffff00', '轻度污染': '#ff7e00',
                      '中度污染': '#ff0000', '重度污染': '#8f3f97', '严重污染': '#7e0023' };
    pie.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c} 个城市 ({d}%)' },
        legend: {
            orient: 'vertical', right: 10, top: 'center',
            textStyle: { color: '#e8eaed' }
        },
        series: [{
            type: 'pie', radius: ['40%', '70%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: true,
            itemStyle: { borderRadius: 6, borderColor: '#0f1117', borderWidth: 2 },
            label: { show: false },
            emphasis: {
                label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#e8eaed' }
            },
            data: data.distribution.map(function(d) {
                return { name: d.name, value: d.value,
                         itemStyle: { color: aqiColors[d.name] || '#5470c6' } };
            })
        }]
    });

    resizeAll();
}
</script>
"""

    def on_activated(self, filters: dict):
        loader = DataLoader.get_instance()
        df = filter_data(loader.df, filters.get("city"),
                         filters.get("start_date"), filters.get("end_date"))

        stats = national_stats(df)
        ranking = city_ranking(df, "AQI", 10)

        # Get trend for worst city (or selected city)
        trend_city = filters.get("city") or stats["worst_city"]
        trend = city_daily_trend(df, trend_city, "AQI")

        dist = aqi_distribution(df)

        self.push_data({
            "stats": stats,
            "ranking": ranking,
            "trend": trend,
            "distribution": dist,
        })
