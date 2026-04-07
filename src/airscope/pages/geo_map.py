"""Spatiotemporal distribution (map) page."""

from .base_page import BasePage
from ..data.loader import DataLoader
from ..data.processor import filter_data, city_map_data, calendar_heatmap_data
from ..utils.config import ASSETS_DIR

_china_geo_cache: str | None = None


def _get_china_geo() -> str:
    global _china_geo_cache
    if _china_geo_cache is None:
        _china_geo_cache = (ASSETS_DIR / "geo" / "china.json").read_text(encoding="utf-8")
    return _china_geo_cache


class GeoMapPage(BasePage):

    def get_html_content(self) -> str:
        return (
            '<script>echarts.registerMap("china", ' + _get_china_geo() + ');</script>\n'
            + _GEO_MAP_HTML
        )

    def on_activated(self, filters: dict):
        loader = DataLoader.get_instance()
        df = filter_data(loader.df, None,
                         filters.get("start_date"), filters.get("end_date"))

        map_data = city_map_data(df, loader.city_coords, "AQI")
        cal_city = filters.get("city") or "北京"
        years = loader.get_years()
        cal_year = years[-1] if years else 2024
        cal_data = calendar_heatmap_data(loader.df, cal_city, cal_year, "AQI")
        monthly = df.groupby("Month")["AQI"].mean()
        monthly_avg = [round(monthly.get(m, 0), 1) for m in range(1, 13)]

        self.push_data({
            "map_data": map_data,
            "calendar": cal_data,
            "calendar_year": cal_year,
            "monthly_avg": monthly_avg,
        })


_GEO_MAP_HTML = """
<div class="dashboard" style="grid-template-rows: 1fr 1fr; grid-template-columns: 1.3fr 0.7fr;">
    <div class="chart-box" style="grid-row: 1 / 3;">
        <div class="chart-title">中国城市 AQI 分布地图</div>
        <div id="map-chart" style="width:100%;height:calc(100% - 35px);"></div>
    </div>
    <div class="chart-box">
        <div class="chart-title">日历热力图</div>
        <div id="calendar-chart" class="chart-container"></div>
    </div>
    <div class="chart-box">
        <div class="chart-title">月度变化</div>
        <div id="timeline-chart" class="chart-container"></div>
    </div>
</div>

<script>
var TT = {backgroundColor:'#fff',borderColor:'#e1e3e5',textStyle:{color:'#303030',fontSize:12},
          extraCssText:'box-shadow:0 4px 12px rgba(0,0,0,0.1);border-radius:8px;'};

function updateCharts(data) {
    var map = initChart('map-chart');
    map.setOption({
        tooltip: Object.assign({trigger:'item',
            formatter:function(p){
                if(p.seriesType==='effectScatter') return p.name+'<br>AQI: '+p.value[2];
                return p.name;
            }}, TT),
        geo: {
            map:'china', roam:true, zoom:1.2, center:[105,36],
            itemStyle: {areaColor:'#f0f1f2',borderColor:'#c9cccf',borderWidth:0.6},
            emphasis: {
                itemStyle:{areaColor:'rgba(92,106,196,0.15)'},
                label:{show:true,color:'#303030'}
            },
            label: {show:false}
        },
        series: [{
            type:'effectScatter', coordinateSystem:'geo',
            data: data.map_data,
            symbolSize: function(v){return Math.max(6,Math.min(25,v[2]/5));},
            encode:{value:2},
            showEffectOn:'emphasis',
            rippleEffect:{brushType:'stroke',scale:3},
            itemStyle: {
                color:function(p){return getAqiColor(p.value[2]);},
                shadowBlur:6,shadowColor:'rgba(0,0,0,0.15)'
            },
            label:{show:false},
            emphasis:{label:{show:true,
                formatter:function(p){return p.name+': '+p.value[2];},
                color:'#303030',fontSize:12}}
        }]
    });

    var cal = initChart('calendar-chart');
    cal.setOption({
        tooltip: Object.assign({formatter:function(p){return p.value[0]+'<br>AQI: '+p.value[1];}}, TT),
        visualMap: {
            min:0,max:300,show:true,orient:'horizontal',left:'center',bottom:5,
            inRange:{color:['#2da44e','#e8a020','#e07b39','#c0392b','#862e9c','#5c2e7e']},
            textStyle:{color:'#6d7175'}
        },
        calendar: {
            top:25,left:25,right:25,bottom:40,
            range:String(data.calendar_year),
            cellSize:['auto',14],
            itemStyle:{color:'#f9fafb',borderColor:'#e1e3e5',borderWidth:0.5},
            yearLabel:{color:'#6d7175'},
            monthLabel:{color:'#6d7175'},
            dayLabel:{color:'#6d7175',firstDay:1}
        },
        series: [{type:'heatmap',coordinateSystem:'calendar',data:data.calendar}]
    });

    var tl = initChart('timeline-chart');
    var months = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
    tl.setOption({
        tooltip: Object.assign({trigger:'axis',axisPointer:{type:'shadow'}}, TT),
        grid: {left:45,right:16,top:16,bottom:25},
        xAxis: {type:'category',data:months,axisLabel:{color:'#6d7175'},
                axisLine:{lineStyle:{color:'#e1e3e5'}},axisTick:{show:false}},
        yAxis: {type:'value',name:'AQI',axisLabel:{color:'#6d7175'},
                splitLine:{lineStyle:{color:'#f0f1f2'}},axisLine:{show:false},axisTick:{show:false}},
        series: [{
            type:'bar',barWidth:'55%',
            data: data.monthly_avg.map(function(v){
                return {value:v,itemStyle:{color:getAqiColor(v),borderRadius:[4,4,0,0]}};
            }),
            label:{show:true,position:'top',color:'#6d7175',fontSize:10,
                   formatter:function(p){return p.value;}}
        }]
    });

    resizeAll();
}
</script>
"""
