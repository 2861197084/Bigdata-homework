"""Health impact and correlation page."""

from .base_page import BasePage
from ..data.loader import DataLoader
from ..data.processor import (
    filter_data, health_treemap_data, weather_correlation_data,
    seasonal_pollutant_data, national_stats,
)


class HealthPage(BasePage):

    def get_html_content(self) -> str:
        return """
<div class="dashboard" style="grid-template-rows: auto 1fr 1fr; grid-template-columns: 1fr 1fr;">
    <!-- Triple gauges -->
    <div class="chart-box" style="grid-column: 1 / -1; height: 200px;">
        <div class="chart-title">关键健康指标</div>
        <div style="display:flex; height:calc(100% - 30px);">
            <div id="gauge-pm25" style="flex:1;height:100%;"></div>
            <div id="gauge-o3" style="flex:1;height:100%;"></div>
            <div id="gauge-aqi" style="flex:1;height:100%;"></div>
        </div>
    </div>

    <div class="chart-box">
        <div class="chart-title">AQI 健康等级树图</div>
        <div id="treemap-chart" class="chart-container"></div>
    </div>
    <div class="chart-box">
        <div class="chart-title">季节污染物雷达</div>
        <div id="season-radar" class="chart-container"></div>
    </div>

    <div class="chart-box">
        <div class="chart-title">PM2.5 vs 温度（按季节着色）</div>
        <div id="pm-temp-scatter" class="chart-container"></div>
    </div>
    <div class="chart-box">
        <div class="chart-title">风速 vs AQI（气泡大小=PM2.5）</div>
        <div id="wind-aqi-scatter" class="chart-container"></div>
    </div>
</div>

<script>
function makeGauge(id, name, value, max, unit) {
    var g = initChart(id);
    g.setOption({
        series: [{
            type: 'gauge',
            startAngle: 210, endAngle: -30,
            min: 0, max: max,
            axisLine: {
                lineStyle: { width: 15,
                    color: [[0.2, '#00e400'], [0.4, '#ffff00'], [0.6, '#ff7e00'],
                            [0.8, '#ff0000'], [1, '#8f3f97']] }
            },
            pointer: { width: 4, itemStyle: { color: '#1e90ff' } },
            axisTick: { show: false },
            splitLine: { distance: -15, length: 12, lineStyle: { color: '#fff', width: 1 } },
            axisLabel: { color: '#8b8fa3', distance: 20, fontSize: 10 },
            detail: {
                valueAnimation: true, fontSize: 22, color: '#e8eaed',
                formatter: function(v) { return Math.round(v) + unit; },
                offsetCenter: [0, '70%']
            },
            title: { color: '#8b8fa3', fontSize: 13, offsetCenter: [0, '90%'] },
            data: [{ value: value, name: name }]
        }]
    });
}

function updateCharts(data) {
    // Triple gauges
    makeGauge('gauge-pm25', 'PM2.5', data.gauges.pm25, 300, ' μg/m³');
    makeGauge('gauge-o3', 'O3', data.gauges.o3, 300, ' μg/m³');
    makeGauge('gauge-aqi', 'AQI', data.gauges.aqi, 500, '');

    // Treemap
    var tree = initChart('treemap-chart');
    tree.setOption({
        tooltip: {
            formatter: function(p) {
                if (p.data.children) return p.name;
                return p.name + '<br>平均 AQI: ' + p.value;
            }
        },
        series: [{
            type: 'treemap',
            data: data.treemap,
            roam: false,
            breadcrumb: {
                itemStyle: { color: '#1a1d27', borderColor: '#2a2d3a' },
                textStyle: { color: '#e8eaed' }
            },
            levels: [{
                itemStyle: { borderColor: '#2a2d3a', borderWidth: 2, gapWidth: 2 },
                upperLabel: { show: true, height: 24, color: '#e8eaed', fontSize: 12 }
            }, {
                itemStyle: { borderColor: '#2a2d3a', borderWidth: 1, gapWidth: 1 },
                label: { show: true, color: '#e8eaed', fontSize: 11 }
            }],
            label: { show: true, color: '#e8eaed', fontSize: 11 }
        }]
    });

    // Seasonal radar
    var sradar = initChart('season-radar');
    var pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3'];
    var maxVals = { 'PM2.5': 120, 'PM10': 160, 'SO2': 30, 'NO2': 50, 'CO': 1.5, 'O3': 150 };
    var indicator = pollutants.map(function(p) {
        return { name: p, max: maxVals[p] };
    });
    var seasons = ['春季', '夏季', '秋季', '冬季'];
    var seasonColors = ['#91cc75', '#ee6666', '#fac858', '#5470c6'];
    var radarData = seasons.map(function(s, i) {
        return {
            name: s,
            value: pollutants.map(function(p) { return data.seasonal[s] ? data.seasonal[s][p] || 0 : 0; }),
            lineStyle: { color: seasonColors[i] },
            itemStyle: { color: seasonColors[i] },
            areaStyle: { color: seasonColors[i], opacity: 0.1 }
        };
    });
    sradar.setOption({
        tooltip: { trigger: 'item' },
        legend: { data: seasons, textStyle: { color: '#e8eaed' }, bottom: 0 },
        radar: {
            indicator: indicator,
            axisName: { color: '#8b8fa3' },
            splitArea: { areaStyle: { color: ['rgba(30,144,255,0.03)', 'rgba(30,144,255,0.06)'] } },
            splitLine: { lineStyle: { color: '#2a2d3a' } },
            axisLine: { lineStyle: { color: '#2a2d3a' } }
        },
        series: [{ type: 'radar', data: radarData }]
    });

    // PM2.5 vs Temperature scatter
    var pts = initChart('pm-temp-scatter');
    var seasonMap = { '春季': '#91cc75', '夏季': '#ee6666', '秋季': '#fac858', '冬季': '#5470c6' };
    var scatterSeries = {};
    data.weather.pm_temp.forEach(function(d) {
        var s = d[2];
        if (!scatterSeries[s]) scatterSeries[s] = [];
        scatterSeries[s].push([d[0], d[1]]);
    });
    var ptsSeries = Object.keys(scatterSeries).map(function(s) {
        return {
            name: s, type: 'scatter', data: scatterSeries[s],
            symbolSize: 5,
            itemStyle: { color: seasonMap[s] || '#5470c6', opacity: 0.6 }
        };
    });
    pts.setOption({
        tooltip: { formatter: function(p) { return p.seriesName+'<br>温度: '+p.data[0]+'°C<br>PM2.5: '+p.data[1]; } },
        legend: { data: Object.keys(scatterSeries), textStyle: { color: '#e8eaed' }, top: 0 },
        grid: { left: 55, right: 20, top: 35, bottom: 40 },
        xAxis: { name: '温度 (°C)', axisLabel: { color: '#8b8fa3' },
                 splitLine: { lineStyle: { color: 'rgba(42,45,58,0.6)' } },
                 axisLine: { lineStyle: { color: '#2a2d3a' } } },
        yAxis: { name: 'PM2.5 (μg/m³)', axisLabel: { color: '#8b8fa3' },
                 splitLine: { lineStyle: { color: 'rgba(42,45,58,0.6)' } },
                 axisLine: { lineStyle: { color: '#2a2d3a' } } },
        series: ptsSeries
    });

    // Wind vs AQI bubble
    var wb = initChart('wind-aqi-scatter');
    wb.setOption({
        tooltip: {
            formatter: function(p) { return '风速: '+p.data[0]+' m/s<br>AQI: '+p.data[1]+'<br>PM2.5: '+p.data[2]; }
        },
        grid: { left: 55, right: 20, top: 20, bottom: 40 },
        xAxis: { name: '风速 (m/s)', axisLabel: { color: '#8b8fa3' },
                 splitLine: { lineStyle: { color: 'rgba(42,45,58,0.6)' } },
                 axisLine: { lineStyle: { color: '#2a2d3a' } } },
        yAxis: { name: 'AQI', axisLabel: { color: '#8b8fa3' },
                 splitLine: { lineStyle: { color: 'rgba(42,45,58,0.6)' } },
                 axisLine: { lineStyle: { color: '#2a2d3a' } } },
        series: [{
            type: 'scatter',
            data: data.weather.wind_aqi,
            symbolSize: function(d) { return Math.max(4, d[2] / 10); },
            itemStyle: {
                color: function(p) { return getAqiColor(p.data[1]); },
                opacity: 0.5
            }
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

        city = filters.get("city") or "北京"

        # Gauge values
        stats = national_stats(df)
        pm25_avg = round(df["PM2.5"].mean(), 1)
        o3_avg = round(df["O3"].mean(), 1)

        treemap = health_treemap_data(df)
        seasonal = seasonal_pollutant_data(df, city)
        weather = weather_correlation_data(df, city)

        self.push_data({
            "gauges": {
                "pm25": pm25_avg,
                "o3": o3_avg,
                "aqi": stats["national_avg_aqi"],
            },
            "treemap": treemap,
            "seasonal": seasonal,
            "weather": weather,
        })
