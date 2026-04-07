"""Trends and forecasting page."""

from .base_page import BasePage
from ..data.loader import DataLoader
from ..data.processor import (
    filter_data, yearly_comparison, monthly_heatmap_data, trend_with_forecast,
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
var TT = {backgroundColor:'#fff',borderColor:'#e1e3e5',textStyle:{color:'#303030',fontSize:12},
          extraCssText:'box-shadow:0 4px 12px rgba(0,0,0,0.1);border-radius:8px;'};

function updateCharts(data) {
    var fc = initChart('forecast-chart');
    var allDates = data.forecast.dates.concat(data.forecast.forecast_dates);
    var aLen = data.forecast.values.length;
    var actual = data.forecast.values.concat(new Array(data.forecast.forecast_dates.length).fill(null));
    var fore = new Array(aLen > 0 ? aLen - 1 : 0).fill(null);
    if (aLen > 0) fore.push(data.forecast.values[aLen - 1]);
    fore = fore.concat(data.forecast.forecast_values);

    var markAreas = [];
    var yrs = {};
    allDates.forEach(function(d){ yrs[d.substring(0,4)]=1; });
    Object.keys(yrs).forEach(function(y){
        markAreas.push([
            {xAxis:y+'-11',itemStyle:{color:'rgba(222,54,24,0.04)'}},
            {xAxis:(parseInt(y)+1)+'-03'}
        ]);
    });

    fc.setOption({
        tooltip: Object.assign({trigger:'axis'}, TT),
        legend: {data:['实际值','预测值'],textStyle:{color:'#6d7175'},top:0},
        grid: {left:45,right:16,top:30,bottom:50},
        xAxis: {type:'category',data:allDates,axisLabel:{color:'#6d7175',rotate:30,fontSize:10},
                axisLine:{lineStyle:{color:'#e1e3e5'}},axisTick:{show:false}},
        yAxis: {type:'value',name:'AQI',axisLabel:{color:'#6d7175'},
                splitLine:{lineStyle:{color:'#f0f1f2'}},axisLine:{show:false},axisTick:{show:false}},
        dataZoom: [{type:'inside'},{type:'slider',height:16,bottom:2,borderColor:'#e1e3e5',
                   fillerColor:'rgba(92,106,196,0.15)'}],
        series: [
            {name:'实际值',type:'line',data:actual,smooth:true,showSymbol:false,
             lineStyle:{width:2,color:'#5c6ac4'},
             areaStyle:{color:{type:'linear',x:0,y:0,x2:0,y2:1,
                colorStops:[{offset:0,color:'rgba(92,106,196,0.15)'},{offset:1,color:'rgba(92,106,196,0.01)'}]}},
             markArea:{silent:true,data:markAreas}},
            {name:'预测值',type:'line',data:fore,smooth:true,showSymbol:false,
             lineStyle:{width:2,color:'#f49342',type:'dashed'}}
        ]
    });

    var yoy = initChart('yoy-chart');
    var months = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
    var yoySeries = [], yoyLeg = [], idx = 0, total = Object.keys(data.yoy).length;
    for (var yr in data.yoy) {
        yoyLeg.push(yr);
        yoySeries.push({
            name:yr,type:'line',smooth:true,showSymbol:false,
            lineStyle:{width:idx===total-1?2.5:1.2,opacity:idx===total-1?1:0.4},
            data:data.yoy[yr]
        });
        idx++;
    }
    yoy.setOption({
        tooltip: Object.assign({trigger:'axis'}, TT),
        legend: {data:yoyLeg,textStyle:{color:'#6d7175',fontSize:10},type:'scroll',top:0,height:22},
        grid: {left:45,right:16,top:38,bottom:16},
        xAxis: {type:'category',data:months,axisLabel:{color:'#6d7175'},
                axisLine:{lineStyle:{color:'#e1e3e5'}},axisTick:{show:false}},
        yAxis: {type:'value',name:'AQI',axisLabel:{color:'#6d7175'},
                splitLine:{lineStyle:{color:'#f0f1f2'}},axisLine:{show:false},axisTick:{show:false}},
        series: yoySeries
    });

    var hm = initChart('heatmap-chart');
    hm.setOption({
        tooltip: Object.assign({
            formatter:function(p){
                return data.heatmap.cities[p.data[1]]+' - '+(p.data[0]+1)+'月<br>AQI: '+p.data[2];
            }}, TT),
        grid: {left:80,right:55,top:8,bottom:25},
        xAxis: {type:'category',data:months,axisLabel:{color:'#6d7175'},
                axisLine:{lineStyle:{color:'#e1e3e5'}},axisTick:{show:false},
                splitArea:{show:true,areaStyle:{color:['#fafbfc','#ffffff']}}},
        yAxis: {type:'category',data:data.heatmap.cities,
                axisLabel:{color:'#303030',fontSize:10},axisLine:{show:false},axisTick:{show:false}},
        visualMap: {
            min:20,max:200,calculable:true,orient:'vertical',right:3,top:'center',
            inRange:{color:['#2da44e','#e8a020','#e07b39','#c0392b','#862e9c']},
            textStyle:{color:'#6d7175'}
        },
        series: [{
            type:'heatmap',data:data.heatmap.data,label:{show:false},
            emphasis:{itemStyle:{shadowBlur:8,shadowColor:'rgba(0,0,0,0.12)'}}
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
        self.push_data({
            "forecast": trend_with_forecast(df, city, "AQI"),
            "yoy": yearly_comparison(df, city, "AQI"),
            "heatmap": monthly_heatmap_data(df, "AQI", 20),
        })
