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
        <div style="display:flex; height:calc(100% - 35px);">
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
var TT = {backgroundColor:'#fff',borderColor:'#e1e3e5',textStyle:{color:'#303030',fontSize:12},
          extraCssText:'box-shadow:0 4px 12px rgba(0,0,0,0.1);border-radius:8px;'};

function makeGauge(id, name, value, max, unit) {
    var g = initChart(id);
    g.setOption({
        series: [{
            type:'gauge', startAngle:210, endAngle:-30, min:0, max:max,
            axisLine: {lineStyle:{width:14,
                color:[[0.2,'#2da44e'],[0.4,'#e8a020'],[0.6,'#e07b39'],[0.8,'#c0392b'],[1,'#862e9c']]}},
            pointer: {width:4,itemStyle:{color:'#303030'},length:'55%'},
            axisTick: {show:false},
            splitLine: {show:false},
            axisLabel: {show:false},
            detail: {valueAnimation:true,fontSize:20,color:'#303030',fontWeight:700,
                     formatter:function(v){return Math.round(v)+unit;},offsetCenter:[0,'70%']},
            title: {color:'#6d7175',fontSize:12,offsetCenter:[0,'90%']},
            data: [{value:value,name:name}]
        }]
    });
}

function updateCharts(data) {
    makeGauge('gauge-pm25','PM2.5',data.gauges.pm25,300,' μg/m³');
    makeGauge('gauge-o3','O3',data.gauges.o3,300,' μg/m³');
    makeGauge('gauge-aqi','AQI',data.gauges.aqi,500,'');

    var tree = initChart('treemap-chart');
    tree.setOption({
        tooltip: Object.assign({
            formatter:function(p){
                if(p.data.children) return p.name;
                return p.name+'<br>平均 AQI: '+p.value;
            }}, TT),
        series: [{
            type:'treemap', data:data.treemap, roam:false,
            breadcrumb: {
                itemStyle:{color:'#f0f1f2',borderColor:'#e1e3e5'},
                textStyle:{color:'#303030'}
            },
            levels: [{
                itemStyle:{borderColor:'#e1e3e5',borderWidth:2,gapWidth:2},
                upperLabel:{show:true,height:22,color:'#303030',fontSize:12,fontWeight:600}
            },{
                itemStyle:{borderColor:'#e1e3e5',borderWidth:1,gapWidth:1},
                label:{show:true,color:'#303030',fontSize:11}
            }],
            label:{show:true,color:'#303030',fontSize:11}
        }]
    });

    var sradar = initChart('season-radar');
    var pollutants = ['PM2.5','PM10','SO2','NO2','CO','O3'];
    var maxVals = {'PM2.5':120,'PM10':160,'SO2':30,'NO2':50,'CO':1.5,'O3':150};
    var seasons = ['春季','夏季','秋季','冬季'];
    var sColors = ['#50b83c','#de3618','#f49342','#5c6ac4'];
    var radarData = seasons.map(function(s,i){
        return {
            name:s,
            value:pollutants.map(function(p){return data.seasonal[s]?data.seasonal[s][p]||0:0;}),
            lineStyle:{color:sColors[i]},
            itemStyle:{color:sColors[i]},
            areaStyle:{color:sColors[i],opacity:0.08}
        };
    });
    sradar.setOption({
        tooltip: TT,
        legend: {data:seasons,textStyle:{color:'#6d7175'},bottom:0},
        radar: {
            indicator:pollutants.map(function(p){return {name:p,max:maxVals[p]};}),
            axisName:{color:'#6d7175'},
            splitArea:{areaStyle:{color:['#fafbfc','#f0f1f2']}},
            splitLine:{lineStyle:{color:'#e1e3e5'}},
            axisLine:{lineStyle:{color:'#e1e3e5'}}
        },
        series: [{type:'radar',data:radarData}]
    });

    var pts = initChart('pm-temp-scatter');
    var sMap = {'春季':'#50b83c','夏季':'#de3618','秋季':'#f49342','冬季':'#5c6ac4'};
    var groups = {};
    data.weather.pm_temp.forEach(function(d){
        if(!groups[d[2]]) groups[d[2]]=[];
        groups[d[2]].push([d[0],d[1]]);
    });
    var ptsSeries = Object.keys(groups).map(function(s){
        return {name:s,type:'scatter',data:groups[s],symbolSize:4,
                itemStyle:{color:sMap[s]||'#5c6ac4',opacity:0.5}};
    });
    pts.setOption({
        tooltip: Object.assign({formatter:function(p){return p.seriesName+'<br>温度: '+p.data[0]+'°C<br>PM2.5: '+p.data[1];}}, TT),
        legend: {data:['春季','夏季','秋季','冬季'],textStyle:{color:'#6d7175'},bottom:0,itemGap:12},
        grid: {left:50,right:16,top:8,bottom:42},
        xAxis: {name:'温度 (°C)',axisLabel:{color:'#6d7175'},
                splitLine:{lineStyle:{color:'#f0f1f2'}},
                axisLine:{lineStyle:{color:'#e1e3e5'}},axisTick:{show:false}},
        yAxis: {name:'PM2.5 (μg/m³)',axisLabel:{color:'#6d7175'},
                splitLine:{lineStyle:{color:'#f0f1f2'}},axisLine:{show:false},axisTick:{show:false}},
        series: ptsSeries
    });

    var wb = initChart('wind-aqi-scatter');
    wb.setOption({
        tooltip: Object.assign({
            formatter:function(p){return '风速: '+p.data[0]+' m/s<br>AQI: '+p.data[1]+'<br>PM2.5: '+p.data[2];}
        }, TT),
        grid: {left:50,right:16,top:16,bottom:35},
        xAxis: {name:'风速 (m/s)',axisLabel:{color:'#6d7175'},
                splitLine:{lineStyle:{color:'#f0f1f2'}},
                axisLine:{lineStyle:{color:'#e1e3e5'}},axisTick:{show:false}},
        yAxis: {name:'AQI',axisLabel:{color:'#6d7175'},
                splitLine:{lineStyle:{color:'#f0f1f2'}},axisLine:{show:false},axisTick:{show:false}},
        series: [{
            type:'scatter',data:data.weather.wind_aqi,
            symbolSize:function(d){return Math.max(3,d[2]/12);},
            itemStyle:{color:function(p){return getAqiColor(p.data[1]);},opacity:0.45}
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
        stats = national_stats(df)

        self.push_data({
            "gauges": {
                "pm25": round(df["PM2.5"].mean(), 1),
                "o3": round(df["O3"].mean(), 1),
                "aqi": stats["national_avg_aqi"],
            },
            "treemap": health_treemap_data(df),
            "seasonal": seasonal_pollutant_data(df, city),
            "weather": weather_correlation_data(df, city),
        })
