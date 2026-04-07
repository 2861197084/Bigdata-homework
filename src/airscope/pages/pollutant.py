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
        <div class="chart-title">平行坐标图 — 多污染物关系</div>
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
var TT = {backgroundColor:'#fff',borderColor:'#e1e3e5',textStyle:{color:'#303030',fontSize:12},
          extraCssText:'box-shadow:0 4px 12px rgba(0,0,0,0.1);border-radius:8px;'};

function updateCharts(data) {
    var parallel = initChart('parallel-chart');
    var pNames = ['PM2.5','PM10','SO2','NO2','CO','O3'];
    var pMax = [200,300,60,80,3,200];
    parallel.setOption({
        visualMap: {
            show: false, dimension: 6,
            min: 0, max: 300,
            inRange: {color: ['#2da44e','#e8a020','#e07b39','#c0392b','#862e9c']}
        },
        parallelAxis: pNames.map(function(n,i){
            return {dim:i,name:n,max:pMax[i],
                    nameTextStyle:{color:'#6d7175'},
                    axisLabel:{color:'#6d7175'},
                    axisLine:{lineStyle:{color:'#e1e3e5'}}};
        }),
        parallel: {left:55,right:55,top:25,bottom:25,
                   parallelAxisDefault:{axisLine:{lineStyle:{color:'#e1e3e5'}}}},
        series: [{
            type:'parallel',
            lineStyle: {width:1,opacity:0.25},
            data: data.parallel_data,
            emphasis: {lineStyle:{width:2,opacity:0.9}}
        }]
    });

    var scatter = initChart('scatter-chart');
    scatter.setOption({
        tooltip: Object.assign({
            formatter: function(p){
                return p.data[3]+'<br>PM2.5: '+p.data[0]+'<br>O3: '+p.data[1]+'<br>AQI: '+p.data[2];
            }
        }, TT),
        grid: {left:50,right:16,top:16,bottom:40},
        xAxis: {name:'PM2.5 (μg/m³)',axisLabel:{color:'#6d7175'},
                splitLine:{lineStyle:{color:'#f0f1f2'}},
                axisLine:{lineStyle:{color:'#e1e3e5'}},axisTick:{show:false}},
        yAxis: {name:'O3 (μg/m³)',axisLabel:{color:'#6d7175'},
                splitLine:{lineStyle:{color:'#f0f1f2'}},
                axisLine:{show:false},axisTick:{show:false}},
        series: [{
            type:'scatter',
            symbolSize: function(d){return Math.max(4,d[2]/18);},
            data: data.correlation,
            itemStyle: {
                color: function(p){return getAqiColor(p.data[2]);},
                opacity: 0.55
            }
        }]
    });

    var sbar = initChart('stacked-bar');
    var colors = {'PM2.5':'#5c6ac4','PM10':'#47c1bf','SO2':'#f49342','NO2':'#de3618','O3':'#50b83c'};
    var stackSeries = [];
    for (var p in data.stacked.series) {
        stackSeries.push({
            name:p, type:'bar', stack:'total', barWidth:'55%',
            data: data.stacked.series[p],
            itemStyle: {color:colors[p]||'#5c6ac4'}
        });
    }
    sbar.setOption({
        tooltip: Object.assign({trigger:'axis',axisPointer:{type:'shadow'}}, TT),
        legend: {data:Object.keys(data.stacked.series),textStyle:{color:'#6d7175'},top:0},
        grid: {left:70,right:16,top:30,bottom:8},
        xAxis: {type:'value',axisLabel:{color:'#6d7175'},splitLine:{lineStyle:{color:'#f0f1f2'}},
                axisLine:{show:false},axisTick:{show:false}},
        yAxis: {type:'category',data:data.stacked.cities,
                axisLabel:{color:'#303030',fontSize:11},axisLine:{show:false},axisTick:{show:false}},
        series: stackSeries
    });

    var box = initChart('boxplot-chart');
    var boxCat = Object.keys(data.boxplot);
    box.setOption({
        tooltip: Object.assign({trigger:'item',
            formatter:function(p){
                if(p.componentType==='series'){
                    return p.name+'<br>下限: '+p.data[1]+'<br>Q1: '+p.data[2]+
                           '<br>中位数: '+p.data[3]+'<br>Q3: '+p.data[4]+'<br>上限: '+p.data[5];
                } return '';
            }}, TT),
        grid: {left:45,right:16,top:16,bottom:35},
        xAxis: {type:'category',data:boxCat,axisLabel:{color:'#303030'},
                axisLine:{lineStyle:{color:'#e1e3e5'}},axisTick:{show:false}},
        yAxis: {type:'value',axisLabel:{color:'#6d7175'},
                splitLine:{lineStyle:{color:'#f0f1f2'}},axisLine:{show:false},axisTick:{show:false}},
        series: [{
            type:'boxplot',
            data: boxCat.map(function(k){return data.boxplot[k];}),
            itemStyle: {color:'rgba(92,106,196,0.15)',borderColor:'#5c6ac4',borderWidth:1.5}
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

        pollutants = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", "AQI"]
        sample = df[pollutants].dropna()
        if len(sample) > 2000:
            sample = sample.sample(2000, random_state=42)
        parallel_data = sample.values.round(1).tolist()

        self.push_data({
            "parallel_data": parallel_data,
            "correlation": pollutant_correlation(df, "PM2.5", "O3"),
            "boxplot": pollutant_boxplot_data(df),
            "stacked": stacked_pollutant_data(df),
        })
