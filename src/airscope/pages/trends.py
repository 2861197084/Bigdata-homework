"""Trends and forecasting page."""

from .base_page import BasePage
from ..data.loader import DataLoader
from ..data.processor import (
    filter_data, yearly_comparison, monthly_heatmap_data, trend_with_forecast,
    multi_city_monthly_trend,
)


class TrendsPage(BasePage):

    def get_html_content(self) -> str:
        return """
<div class="dashboard" style="grid-template-rows: 1fr 1fr; grid-template-columns: 1fr 1fr;">
    <div class="chart-box">
        <div class="chart-title">多年趋势 & 移动平均预测</div>
        <div id="forecast-chart" class="chart-container"></div>
    </div>
    <div class="chart-box">
        <div class="chart-title">逐年月均对比</div>
        <div id="yoy-chart" class="chart-container"></div>
    </div>
    <div class="chart-box" style="grid-column: 1 / -1;">
        <div class="chart-title">城市 × 月份 AQI 热力矩阵</div>
        <div id="heatmap-chart" class="chart-container" style="min-height:350px;"></div>
    </div>
</div>

<script>
function updateCharts(data) {
    // Forecast line
    var fc = initChart('forecast-chart');
    var allDates = data.forecast.dates.concat(data.forecast.forecast_dates);
    var actualLen = data.forecast.values.length;
    var actualData = data.forecast.values.concat(new Array(data.forecast.forecast_dates.length).fill(null));
    var forecastData = new Array(actualLen > 0 ? actualLen - 1 : 0).fill(null);
    if (actualLen > 0) forecastData.push(data.forecast.values[actualLen - 1]);
    forecastData = forecastData.concat(data.forecast.forecast_values);

    // Mark heating seasons (Nov-Mar)
    var markAreas = [];
    var years = {};
    allDates.forEach(function(d) {
        var y = d.substring(0, 4);
        years[y] = true;
    });
    Object.keys(years).forEach(function(y) {
        markAreas.push([
            { xAxis: y + '-11', itemStyle: { color: 'rgba(238,102,102,0.08)' } },
            { xAxis: (parseInt(y)+1) + '-03' }
        ]);
    });

    fc.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['实际值', '预测值'], textStyle: { color: '#e8eaed' }, top: 0 },
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
        series: [
            {
                name: '实际值', type: 'line', data: actualData,
                smooth: true, showSymbol: false,
                lineStyle: { width: 2, color: '#1e90ff' },
                areaStyle: {
                    color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                        colorStops: [
                            { offset: 0, color: 'rgba(30,144,255,0.25)' },
                            { offset: 1, color: 'rgba(30,144,255,0.02)' }
                        ]
                    }
                },
                markArea: { silent: true, data: markAreas }
            },
            {
                name: '预测值', type: 'line', data: forecastData,
                smooth: true, showSymbol: false,
                lineStyle: { width: 2, color: '#fac858', type: 'dashed' }
            }
        ]
    });

    // Year-over-year comparison
    var yoy = initChart('yoy-chart');
    var months = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
    var yoySeries = [];
    var yoyLegend = [];
    var palette = ['#5470c6','#91cc75','#fac858','#ee6666','#73c0de','#3ba272','#fc8452','#9a60b4','#ea7ccc','#48b8d0'];
    var idx = 0;
    for (var year in data.yoy) {
        yoyLegend.push(year);
        yoySeries.push({
            name: year, type: 'line', smooth: true, showSymbol: false,
            lineStyle: { width: idx === Object.keys(data.yoy).length - 1 ? 3 : 1.5,
                         opacity: idx === Object.keys(data.yoy).length - 1 ? 1 : 0.5 },
            data: data.yoy[year]
        });
        idx++;
    }
    yoy.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: yoyLegend, textStyle: { color: '#e8eaed', fontSize: 10 },
                  type: 'scroll', top: 0 },
        grid: { left: 50, right: 20, top: 35, bottom: 20 },
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
        series: yoySeries
    });

    // City x Month heatmap
    var hm = initChart('heatmap-chart');
    var hmData = data.heatmap;
    hm.setOption({
        tooltip: {
            formatter: function(p) {
                var month = p.data[0] + 1;
                var city = hmData.cities[p.data[1]];
                return city + ' - ' + month + '月<br>AQI: ' + p.data[2];
            }
        },
        grid: { left: 80, right: 60, top: 10, bottom: 30 },
        xAxis: {
            type: 'category',
            data: ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'],
            axisLabel: { color: '#8b8fa3' },
            axisLine: { lineStyle: { color: '#2a2d3a' } },
            splitArea: { show: true, areaStyle: { color: ['rgba(255,255,255,0.02)', 'transparent'] } }
        },
        yAxis: {
            type: 'category',
            data: hmData.cities,
            axisLabel: { color: '#e8eaed', fontSize: 10 },
            axisLine: { lineStyle: { color: '#2a2d3a' } }
        },
        visualMap: {
            min: 20, max: 200, calculable: true,
            orient: 'vertical', right: 5, top: 'center',
            inRange: { color: ['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#8f3f97'] },
            textStyle: { color: '#8b8fa3' }
        },
        series: [{
            type: 'heatmap',
            data: hmData.data,
            label: { show: false },
            emphasis: {
                itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' }
            }
        }]
    });

    resizeAll();
}
</script>
"""

    def on_activated(self, filters: dict):
        loader = DataLoader.get_instance()
        df = filter_data(loader.df, None,
                         filters.get("start_date"), filters.get("end_date"))

        city = filters.get("city") or "北京"
        forecast = trend_with_forecast(df, city, "AQI")
        yoy = yearly_comparison(df, city, "AQI")
        heatmap = monthly_heatmap_data(df, "AQI", 20)

        self.push_data({
            "forecast": forecast,
            "yoy": yoy,
            "heatmap": heatmap,
        })
