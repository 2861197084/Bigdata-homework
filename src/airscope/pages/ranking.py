"""City ranking and comparison page."""

from .base_page import BasePage
from ..data.loader import DataLoader
from ..data.processor import (
    filter_data, city_ranking, multi_city_monthly_trend, pollutant_profile,
)

_TOOLTIP = """backgroundColor:'#fff',borderColor:'#e1e3e5',textStyle:{color:'#303030',fontSize:12},extraCssText:'box-shadow:0 4px 12px rgba(0,0,0,0.1);border-radius:8px;'"""


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
        <div id="data-table" style="width:100%;height:calc(100% - 35px);overflow-y:auto;"></div>
    </div>
</div>

<script>
var TT = {backgroundColor:'#fff',borderColor:'#e1e3e5',textStyle:{color:'#303030',fontSize:12},extraCssText:'box-shadow:0 4px 12px rgba(0,0,0,0.1);border-radius:8px;'};

function updateCharts(data) {
    var bar = initChart('ranking-bar');
    var ranking = data.ranking.slice().reverse();
    bar.setOption({
        tooltip: Object.assign({trigger:'axis',axisPointer:{type:'shadow'}}, TT),
        grid: { left: 75, right: 25, top: 8, bottom: 8 },
        xAxis: { type:'value', axisLabel:{color:'#6d7175'}, splitLine:{lineStyle:{color:'#f0f1f2'}},
                 axisLine:{show:false}, axisTick:{show:false} },
        yAxis: { type:'category', data: ranking.map(function(d){return d.city;}),
                 axisLabel:{color:'#303030',fontSize:11}, axisLine:{show:false}, axisTick:{show:false} },
        dataZoom: [{ type:'slider',yAxisIndex:0,right:3,width:10,
                     fillerColor:'rgba(92,106,196,0.15)',borderColor:'#e1e3e5',
                     startValue:Math.max(0,ranking.length-15),endValue:ranking.length }],
        series: [{
            type:'bar', barWidth:'60%',
            data: ranking.map(function(d){
                return {value:d.value, itemStyle:{color:getAqiColor(d.value),borderRadius:[0,4,4,0]}};
            }),
            label:{show:true,position:'right',color:'#6d7175',fontSize:11,
                   formatter:function(p){return p.value;}}
        }]
    });

    var line = initChart('multi-line');
    var series = [], legendData = [], allDates = [];
    for (var city in data.trends) {
        legendData.push(city);
        var cd = data.trends[city];
        if (!allDates.length) allDates = cd.map(function(d){return d.date;});
        series.push({name:city,type:'line',smooth:true,showSymbol:false,lineStyle:{width:2},
                     data:cd.map(function(d){return d.value;})});
    }
    line.setOption({
        tooltip: Object.assign({trigger:'axis'}, TT),
        legend: {data:legendData,textStyle:{color:'#6d7175',fontSize:12},top:0},
        grid: {left:45,right:16,top:32,bottom:50},
        xAxis: {type:'category',data:allDates,axisLabel:{color:'#6d7175',rotate:30,fontSize:10},
                axisLine:{lineStyle:{color:'#e1e3e5'}},axisTick:{show:false}},
        yAxis: {type:'value',name:'AQI',axisLabel:{color:'#6d7175'},
                splitLine:{lineStyle:{color:'#f0f1f2'}},axisLine:{show:false},axisTick:{show:false}},
        dataZoom: [{type:'inside'},{type:'slider',height:16,bottom:2,borderColor:'#e1e3e5',
                   fillerColor:'rgba(92,106,196,0.15)'}],
        series: series
    });

    var radar = initChart('radar-chart');
    var pollutants = ['PM2.5','PM10','SO2','NO2','CO','O3'];
    var maxVals = {'PM2.5':150,'PM10':200,'SO2':40,'NO2':60,'CO':2,'O3':150};
    var radarSeries = [], radarLegend = [];
    for (var c in data.profiles) {
        radarLegend.push(c);
        radarSeries.push({
            value: pollutants.map(function(p){return data.profiles[c][p]||0;}),
            name: c
        });
    }
    radar.setOption({
        tooltip: TT,
        legend: {data:radarLegend,textStyle:{color:'#6d7175'},bottom:0},
        radar: {
            indicator: pollutants.map(function(p){return {name:p,max:maxVals[p]||100};}),
            axisName: {color:'#6d7175'},
            splitArea: {areaStyle:{color:['#fafbfc','#f0f1f2']}},
            splitLine: {lineStyle:{color:'#e1e3e5'}},
            axisLine: {lineStyle:{color:'#e1e3e5'}}
        },
        series: [{type:'radar',data:radarSeries,areaStyle:{opacity:0.12}}]
    });

    // Table
    var h = '<table><thead><tr><th>排名</th><th>城市</th><th>AQI</th><th>等级</th></tr></thead><tbody>';
    data.ranking_full.forEach(function(d,i){
        h += '<tr><td>'+(i+1)+'</td><td>'+d.city+'</td>';
        h += '<td style="color:'+getAqiColor(d.value)+';font-weight:600;">'+d.value+'</td>';
        h += '<td style="color:'+getAqiColor(d.value)+';">'+getAqiLabel(d.value)+'</td></tr>';
    });
    h += '</tbody></table>';
    document.getElementById('data-table').innerHTML = h;

    resizeAll();
}
</script>
"""

    def on_activated(self, filters: dict):
        loader = DataLoader.get_instance()
        df = filter_data(loader.df, filters.get("city"),
                         filters.get("start_date"), filters.get("end_date"))

        ranking = city_ranking(df, "AQI")
        top5 = [r["city"] for r in ranking[:5]]
        trends = multi_city_monthly_trend(df, top5, "AQI")
        profiles = pollutant_profile(df, top5)

        self.push_data({
            "ranking": ranking,
            "ranking_full": ranking,
            "trends": trends,
            "profiles": profiles,
        })
