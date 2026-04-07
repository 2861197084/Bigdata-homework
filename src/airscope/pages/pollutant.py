"""Pollutant analysis page."""

from .base_page import BasePage
from ..data.loader import DataLoader
from ..data.processor import (
    filter_data, pollutant_correlation, pollutant_boxplot_data,
    stacked_pollutant_data,
)


class PollutantPage(BasePage):

    def get_html_content(self) -> str:
        return """
<div class="dashboard" style="grid-template-rows: 1fr 1fr; grid-template-columns: 1fr 1fr;">
    <div class="chart-box">
        <div class="chart-title">平行坐标图 - 多污染物关系</div>
        <div id="parallel-chart" class="chart-container"></div>
    </div>
    <div class="chart-box">
        <div class="chart-title">PM2.5 vs O3 相关性</div>
        <div id="scatter-chart" class="chart-container"></div>
    </div>
    <div class="chart-box">
        <div class="chart-title">城市污染物构成</div>
        <div id="stacked-bar" class="chart-container"></div>
    </div>
    <div class="chart-box">
        <div class="chart-title">污染物分布箱线图</div>
        <div id="boxplot-chart" class="chart-container"></div>
    </div>
</div>

<script>
function updateCharts(data) {
    // Parallel coordinates
    var parallel = initChart('parallel-chart');
    var pNames = ['PM2.5','PM10','SO2','NO2','CO','O3'];
    var pMax = [200, 300, 60, 80, 3, 200];
    parallel.setOption({
        parallelAxis: pNames.map(function(n, i) {
            return { dim: i, name: n, max: pMax[i],
                     nameTextStyle: { color: '#8b8fa3' },
                     axisLabel: { color: '#8b8fa3' },
                     axisLine: { lineStyle: { color: '#2a2d3a' } } };
        }),
        parallel: { left: 60, right: 60, top: 30, bottom: 30,
                    parallelAxisDefault: { axisLine: { lineStyle: { color: '#2a2d3a' } } } },
        series: [{
            type: 'parallel',
            lineStyle: { width: 1, opacity: 0.3 },
            data: data.parallel_data,
            emphasis: { lineStyle: { width: 2, opacity: 1 } }
        }]
    });

    // Scatter: PM2.5 vs O3
    var scatter = initChart('scatter-chart');
    scatter.setOption({
        tooltip: {
            formatter: function(p) {
                return p.data[3] + '<br>PM2.5: ' + p.data[0] + '<br>O3: ' + p.data[1] + '<br>AQI: ' + p.data[2];
            }
        },
        grid: { left: 55, right: 20, top: 20, bottom: 45 },
        xAxis: { name: 'PM2.5 (μg/m³)', axisLabel: { color: '#8b8fa3' },
                 splitLine: { lineStyle: { color: 'rgba(42,45,58,0.6)' } },
                 axisLine: { lineStyle: { color: '#2a2d3a' } } },
        yAxis: { name: 'O3 (μg/m³)', axisLabel: { color: '#8b8fa3' },
                 splitLine: { lineStyle: { color: 'rgba(42,45,58,0.6)' } },
                 axisLine: { lineStyle: { color: '#2a2d3a' } } },
        series: [{
            type: 'scatter',
            symbolSize: function(d) { return Math.max(4, d[2] / 15); },
            data: data.correlation,
            itemStyle: {
                color: function(p) { return getAqiColor(p.data[2]); },
                opacity: 0.6
            }
        }]
    });

    // Stacked bar
    var sbar = initChart('stacked-bar');
    var colors = {'PM2.5':'#5470c6','PM10':'#91cc75','SO2':'#fac858','NO2':'#ee6666','O3':'#73c0de'};
    var stackSeries = [];
    for (var p in data.stacked.series) {
        stackSeries.push({
            name: p, type: 'bar', stack: 'total', barWidth: '55%',
            data: data.stacked.series[p],
            itemStyle: { color: colors[p] || '#5470c6' }
        });
    }
    sbar.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: Object.keys(data.stacked.series), textStyle: { color: '#e8eaed' }, top: 0 },
        grid: { left: 70, right: 20, top: 35, bottom: 10 },
        xAxis: {
            type: 'value',
            axisLabel: { color: '#8b8fa3' },
            splitLine: { lineStyle: { color: 'rgba(42,45,58,0.6)' } }
        },
        yAxis: {
            type: 'category', data: data.stacked.cities,
            axisLabel: { color: '#e8eaed', fontSize: 11 }
        },
        series: stackSeries
    });

    // Boxplot
    var box = initChart('boxplot-chart');
    var boxCategories = Object.keys(data.boxplot);
    var boxData = boxCategories.map(function(k) { return data.boxplot[k]; });
    box.setOption({
        tooltip: {
            trigger: 'item',
            formatter: function(p) {
                if (p.componentType === 'series') {
                    return p.name + '<br>下限: ' + p.data[1] + '<br>Q1: ' + p.data[2] +
                           '<br>中位数: ' + p.data[3] + '<br>Q3: ' + p.data[4] + '<br>上限: ' + p.data[5];
                }
                return '';
            }
        },
        grid: { left: 50, right: 20, top: 20, bottom: 40 },
        xAxis: {
            type: 'category', data: boxCategories,
            axisLabel: { color: '#e8eaed' },
            axisLine: { lineStyle: { color: '#2a2d3a' } }
        },
        yAxis: {
            type: 'value',
            axisLabel: { color: '#8b8fa3' },
            splitLine: { lineStyle: { color: 'rgba(42,45,58,0.6)' } }
        },
        series: [{
            type: 'boxplot',
            data: boxData,
            itemStyle: { color: 'rgba(30,144,255,0.2)', borderColor: '#1e90ff' }
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

        # Parallel coordinates data (sample)
        pollutants = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
        sample = df[pollutants].dropna()
        if len(sample) > 2000:
            sample = sample.sample(2000, random_state=42)
        parallel_data = sample.values.round(1).tolist()

        correlation = pollutant_correlation(df, "PM2.5", "O3")
        boxplot = pollutant_boxplot_data(df)
        stacked = stacked_pollutant_data(df)

        self.push_data({
            "parallel_data": parallel_data,
            "correlation": correlation,
            "boxplot": boxplot,
            "stacked": stacked,
        })
