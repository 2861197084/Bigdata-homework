"""City ranking and comparison page."""

from .base_page import BasePage
from ..data.loader import DataLoader
from ..data.processor import (
    filter_data, city_ranking, multi_city_monthly_trend, pollutant_profile,
)


class RankingPage(BasePage):

    def get_html_content(self) -> str:
        return """
<div class="dashboard" style="grid-template-rows: 1fr 1fr; grid-template-columns: 1fr 1fr;">
    <div class="chart-box">
        <div class="chart-title">城市 AQI 排名</div>
        <div id="ranking-bar" class="chart-container"></div>
    </div>
    <div class="chart-box">
        <div class="chart-title">多城市月均趋势对比</div>
        <div id="multi-line" class="chart-container"></div>
    </div>
    <div class="chart-box">
        <div class="chart-title">污染物雷达对比</div>
        <div id="radar-chart" class="chart-container"></div>
    </div>
    <div class="chart-box">
        <div class="chart-title">城市数据表</div>
        <div id="data-table" style="width:100%;height:calc(100% - 30px);overflow-y:auto;"></div>
    </div>
</div>

<script>
function updateCharts(data) {
    // Full ranking bar
    var bar = initChart('ranking-bar');
    var ranking = data.ranking.reverse();
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
            axisLabel: { color: '#e8eaed', fontSize: 11 }
        },
        dataZoom: [{ type: 'slider', yAxisIndex: 0, right: 5, width: 12,
                     fillerColor: 'rgba(30,144,255,0.2)', borderColor: '#2a2d3a',
                     startValue: Math.max(0, ranking.length - 15), endValue: ranking.length }],
        series: [{
            type: 'bar', barWidth: '65%',
            data: ranking.map(function(d) {
                return { value: d.value, itemStyle: { color: getAqiColor(d.value),
                         borderRadius: [0, 4, 4, 0] } };
            }),
            label: { show: true, position: 'right', color: '#e8eaed', fontSize: 11,
                     formatter: function(p) { return p.value; } }
        }]
    });

    // Multi-city trend lines
    var line = initChart('multi-line');
    var colors = ['#5470c6','#91cc75','#fac858','#ee6666','#73c0de'];
    var series = [];
    var legendData = [];
    var allDates = [];
    var ci = 0;
    for (var city in data.trends) {
        legendData.push(city);
        var cityData = data.trends[city];
        if (allDates.length === 0) allDates = cityData.map(function(d){return d.date;});
        series.push({
            name: city, type: 'line', smooth: true, showSymbol: false,
            lineStyle: { width: 2 },
            data: cityData.map(function(d){return d.value;})
        });
        ci++;
    }
    line.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: legendData, textStyle: { color: '#e8eaed' }, top: 0 },
        grid: { left: 50, right: 20, top: 35, bottom: 50 },
        xAxis: {
            type: 'category', data: allDates,
            axisLabel: { color: '#8b8fa3', rotate: 30, fontSize: 10 },
            axisLine: { lineStyle: { color: '#2a2d3a' } }
        },
        yAxis: {
            type: 'value', name: 'AQI',
            axisLabel: { color: '#8b8fa3' },
            splitLine: { lineStyle: { color: 'rgba(42,45,58,0.6)' } }
        },
        dataZoom: [{ type: 'inside' }, { type: 'slider', height: 18, bottom: 5,
                     borderColor: '#2a2d3a', fillerColor: 'rgba(30,144,255,0.2)' }],
        series: series
    });

    // Radar chart
    var radar = initChart('radar-chart');
    var pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3'];
    var maxVals = { 'PM2.5': 150, 'PM10': 200, 'SO2': 40, 'NO2': 60, 'CO': 2, 'O3': 150 };
    var radarIndicator = pollutants.map(function(p) {
        return { name: p, max: maxVals[p] || 100 };
    });
    var radarSeries = [];
    var radarLegend = [];
    for (var city in data.profiles) {
        radarLegend.push(city);
        radarSeries.push({
            value: pollutants.map(function(p) { return data.profiles[city][p] || 0; }),
            name: city
        });
    }
    radar.setOption({
        tooltip: { trigger: 'item' },
        legend: { data: radarLegend, textStyle: { color: '#e8eaed' }, bottom: 0 },
        radar: {
            indicator: radarIndicator,
            axisName: { color: '#8b8fa3' },
            splitArea: { areaStyle: { color: ['rgba(30,144,255,0.03)', 'rgba(30,144,255,0.06)'] } },
            splitLine: { lineStyle: { color: '#2a2d3a' } },
            axisLine: { lineStyle: { color: '#2a2d3a' } }
        },
        series: [{ type: 'radar', data: radarSeries,
                   areaStyle: { opacity: 0.15 } }]
    });

    // Data table
    var tableHtml = '<table style="width:100%;border-collapse:collapse;font-size:12px;">';
    tableHtml += '<thead><tr style="border-bottom:1px solid #2a2d3a;">';
    ['排名','城市','AQI','等级'].forEach(function(h){
        tableHtml += '<th style="padding:8px 6px;color:#8b8fa3;text-align:left;font-weight:500;">'+h+'</th>';
    });
    tableHtml += '</tr></thead><tbody>';
    data.ranking_full.forEach(function(d, i) {
        var rank = data.ranking_full.length - i;
        tableHtml += '<tr style="border-bottom:1px solid rgba(42,45,58,0.5);">';
        tableHtml += '<td style="padding:6px;">'+rank+'</td>';
        tableHtml += '<td style="padding:6px;">'+d.city+'</td>';
        tableHtml += '<td style="padding:6px;color:'+getAqiColor(d.value)+';">'+d.value+'</td>';
        tableHtml += '<td style="padding:6px;color:'+getAqiColor(d.value)+';">'+getAqiLabel(d.value)+'</td>';
        tableHtml += '</tr>';
    });
    tableHtml += '</tbody></table>';
    document.getElementById('data-table').innerHTML = tableHtml;

    resizeAll();
}
</script>
"""

    def on_activated(self, filters: dict):
        loader = DataLoader.get_instance()
        df = filter_data(loader.df, filters.get("city"),
                         filters.get("start_date"), filters.get("end_date"))

        ranking = city_ranking(df, "AQI")
        top5_cities = [r["city"] for r in ranking[:5]]
        trends = multi_city_monthly_trend(df, top5_cities, "AQI")
        profiles = pollutant_profile(df, top5_cities)

        self.push_data({
            "ranking": ranking,
            "ranking_full": ranking,
            "trends": trends,
            "profiles": profiles,
        })
