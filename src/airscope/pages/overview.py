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
        <div class="kpi-card">
            <div class="kpi-label">全国平均 AQI</div>
            <div class="kpi-value" id="kpi-avg-value">--</div>
            <div class="kpi-sub" id="kpi-avg-sub"></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">最污染城市</div>
            <div class="kpi-value" id="kpi-worst-value" style="font-size:22px;">--</div>
            <div class="kpi-sub" id="kpi-worst-sub"></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">最清洁城市</div>
            <div class="kpi-value" id="kpi-best-value" style="font-size:22px;">--</div>
            <div class="kpi-sub" id="kpi-best-sub"></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">超标城市数</div>
            <div class="kpi-value" id="kpi-exceed-value">--</div>
            <div class="kpi-sub" id="kpi-exceed-sub"></div>
        </div>
    </div>

    <!-- Gauge + Line -->
    <div class="chart-box" style="grid-column: 1 / -1; height: 300px;">
        <div class="chart-title">AQI 仪表盘 & 日均趋势</div>
        <div style="display:flex; height:calc(100% - 35px);">
            <div id="gauge-chart" style="width:30%; height:100%;"></div>
            <div id="trend-chart" style="width:70%; height:100%;"></div>
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
    var stats = data.stats;

    document.getElementById('kpi-avg-value').textContent = stats.national_avg_aqi;
    document.getElementById('kpi-avg-value').style.color = getAqiColor(stats.national_avg_aqi);

    document.getElementById('kpi-worst-value').textContent = stats.worst_city;
    document.getElementById('kpi-worst-sub').innerHTML = 'AQI: <span style="color:' + getAqiColor(stats.worst_city_aqi) + ';font-weight:600;">' + stats.worst_city_aqi + '</span>';

    document.getElementById('kpi-best-value').textContent = stats.best_city;
    document.getElementById('kpi-best-sub').innerHTML = 'AQI: <span style="color:' + getAqiColor(stats.best_city_aqi) + ';font-weight:600;">' + stats.best_city_aqi + '</span>';

    document.getElementById('kpi-exceed-value').textContent = stats.exceed_count;
    document.getElementById('kpi-exceed-value').style.color = stats.exceed_count > 0 ? '#de3618' : '#50b83c';
    document.getElementById('kpi-exceed-sub').textContent = '共 ' + stats.total_cities + ' 个城市';

    // Gauge
    var gauge = initChart('gauge-chart');
    gauge.setOption({
        series: [{
            type: 'gauge',
            startAngle: 210, endAngle: -30,
            min: 0, max: 500,
            axisLine: {
                lineStyle: { width: 18,
                    color: [[0.1,'#2da44e'],[0.2,'#e8a020'],[0.3,'#e07b39'],
                            [0.4,'#c0392b'],[0.6,'#862e9c'],[1,'#5c2e7e']] }
            },
            pointer: { itemStyle: { color: '#303030' }, width: 4, length: '60%' },
            axisTick: { distance: -18, length: 4, lineStyle: { color: '#c9cccf', width: 1 } },
            splitLine: { distance: -20, length: 14, lineStyle: { color: '#c9cccf', width: 1 } },
            axisLabel: { color: '#6d7175', distance: 25, fontSize: 10 },
            detail: {
                valueAnimation: true, fontSize: 24, color: '#303030', fontWeight: 700,
                formatter: function(v) { return Math.round(v) + '\\n' + getAqiLabel(v); },
                offsetCenter: [0, '70%']
            },
            data: [{ value: stats.national_avg_aqi }]
        }]
    });

    // Trend line
    var trend = initChart('trend-chart');
    var trendData = data.trend;
    trend.setOption({
        tooltip: { trigger: 'axis',
            backgroundColor: '#fff', borderColor: '#e1e3e5',
            textStyle: { color: '#303030', fontSize: 12 },
            extraCssText: 'box-shadow:0 4px 12px rgba(0,0,0,0.1);border-radius:8px;' },
        grid: { left: 45, right: 16, top: 16, bottom: 50 },
        xAxis: {
            type: 'category',
            data: trendData.map(function(d) { return d.date; }),
            axisLabel: { color: '#6d7175', rotate: 30, fontSize: 10 },
            axisLine: { lineStyle: { color: '#e1e3e5' } },
            axisTick: { show: false }
        },
        yAxis: {
            type: 'value', name: 'AQI',
            axisLabel: { color: '#6d7175' },
            splitLine: { lineStyle: { color: '#f0f1f2' } },
            axisLine: { show: false },
            axisTick: { show: false }
        },
        dataZoom: [
            { type: 'inside', start: 80, end: 100 },
            { type: 'slider', height: 18, bottom: 2, borderColor: '#e1e3e5',
              fillerColor: 'rgba(92,106,196,0.15)', handleStyle: { color: '#5c6ac4' } }
        ],
        series: [{
            type: 'line', data: trendData.map(function(d) { return d.value; }),
            smooth: true, showSymbol: false,
            lineStyle: { width: 2, color: '#5c6ac4' },
            areaStyle: {
                color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                    colorStops: [
                        { offset: 0, color: 'rgba(92,106,196,0.18)' },
                        { offset: 1, color: 'rgba(92,106,196,0.01)' }
                    ] }
            }
        }]
    });

    // Top 10 bar
    var bar = initChart('bar-chart');
    var ranking = data.ranking.slice(0, 10).reverse();
    bar.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' },
            backgroundColor: '#fff', borderColor: '#e1e3e5',
            textStyle: { color: '#303030' },
            extraCssText: 'box-shadow:0 4px 12px rgba(0,0,0,0.1);border-radius:8px;' },
        grid: { left: 75, right: 30, top: 8, bottom: 8 },
        xAxis: {
            type: 'value',
            axisLabel: { color: '#6d7175' },
            splitLine: { lineStyle: { color: '#f0f1f2' } },
            axisLine: { show: false }, axisTick: { show: false }
        },
        yAxis: {
            type: 'category',
            data: ranking.map(function(d) { return d.city; }),
            axisLabel: { color: '#303030', fontSize: 12 },
            axisLine: { show: false }, axisTick: { show: false }
        },
        series: [{
            type: 'bar', barWidth: '55%',
            data: ranking.map(function(d) {
                return { value: d.value, itemStyle: { color: getAqiColor(d.value),
                         borderRadius: [0, 4, 4, 0] } };
            }),
            label: { show: true, position: 'right', color: '#6d7175', fontSize: 11,
                     formatter: function(p) { return p.value; } }
        }]
    });

    // Pie
    var pie = initChart('pie-chart');
    var aqiColors = { '优':'#2da44e','良':'#e8a020','轻度污染':'#e07b39',
                      '中度污染':'#c0392b','重度污染':'#862e9c','严重污染':'#5c2e7e' };
    pie.setOption({
        tooltip: { trigger: 'item',
            formatter: '{b}: {c} 个城市 ({d}%)',
            backgroundColor: '#fff', borderColor: '#e1e3e5',
            textStyle: { color: '#303030' },
            extraCssText: 'box-shadow:0 4px 12px rgba(0,0,0,0.1);border-radius:8px;' },
        legend: {
            orient: 'vertical', right: 10, top: 'center',
            textStyle: { color: '#6d7175', fontSize: 12 }
        },
        series: [{
            type: 'pie', radius: ['42%', '72%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: true,
            itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
            label: { show: false },
            emphasis: {
                label: { show: true, fontSize: 13, fontWeight: 600, color: '#303030' }
            },
            data: data.distribution.map(function(d) {
                return { name: d.name, value: d.value,
                         itemStyle: { color: aqiColors[d.name] || '#5c6ac4' } };
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
        trend_city = filters.get("city") or stats["worst_city"]
        trend = city_daily_trend(df, trend_city, "AQI")
        dist = aqi_distribution(df)

        self.push_data({
            "stats": stats,
            "ranking": ranking,
            "trend": trend,
            "distribution": dist,
        })
