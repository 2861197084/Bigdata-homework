# AirScope - 中国城市空气质量监测可视化大屏

基于 Python + PySide6 + Apache ECharts 的桌面端大数据可视化应用，展示中国 40 个主要城市的空气质量数据（2015-2024）。

## 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.10+ | 主语言 |
| PySide6 (Qt6) | 桌面 GUI 框架 |
| QWebEngineView | 内嵌浏览器渲染图表 |
| Apache ECharts 5.5 | 专业级交互式图表库 |
| pandas + numpy | 数据处理与分析 |
| uv | Python 环境与包管理 |

## 核心架构

```
PySide6 桌面窗口
  └─ QWebEngineView
       └─ ECharts (JavaScript)
            ↕ QWebChannel 双向通信
       └─ pandas 数据处理 (Python)
```

Python 端用 pandas 处理数据，生成 ECharts option JSON，通过 QWebChannel 推送给 JavaScript 渲染。

## 功能特性

### 6 个仪表盘页面

1. **总览** — KPI 卡片、AQI 仪表盘、趋势折线图、Top10 柱状图、等级分布环形图
2. **城市排名** — 全城排名柱状图、多城趋势对比、污染物雷达图、数据表格
3. **污染物分析** — 平行坐标图、相关性散点图、构成堆叠柱状图、分布箱线图
4. **时空分布** — 中国地图散点、日历热力图、月度变化柱状图
5. **趋势预测** — 多年趋势（含冬季供暖标注）、逐年对比、城市×月份热力矩阵、移动平均预测
6. **健康影响** — 三联仪表盘、AQI 健康树图、PM2.5-温度散点、风速-AQI 气泡、季节雷达图

### 13 种图表类型

gauge、line、bar、pie/ring、radar、geo map、scatter/bubble、calendar heatmap、cartesian heatmap、parallel coordinates、boxplot、treemap、timeline

### 交互功能

- 数据缩放（鼠标滚轮 + 滑块）
- Tooltip 悬浮提示
- 城市/日期/指标筛选联动
- 地图缩放平移
- 图表动画效果

## 数据说明

- **数据集**: 40 个中国主要城市，2015-2024 年每日空气质量数据
- **指标**: AQI、PM2.5、PM10、SO2、NO2、CO、O3、温度、湿度、风速
- **记录数**: 146,120 条
- **AQI 标准**: 中国环境空气质量指数技术规定（HJ 633-2012）

## 安装与运行

### 环境要求

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) 包管理器

### 快速开始

```bash
# 克隆项目
git clone https://github.com/2861197084/Bigdata-homework.git
cd Bigdata-homework

# 生成数据（首次运行）
uv run python scripts/generate_data.py

# 安装依赖并启动
uv sync
uv run python -m airscope
```

## 项目结构

```
Bigdata-homework/
├── pyproject.toml          # 项目配置与依赖
├── data/                   # 数据文件
│   ├── china_air_quality.csv
│   └── city_coordinates.json
├── scripts/
│   └── generate_data.py    # 数据生成脚本
└── src/airscope/           # 应用源码
    ├── app.py              # 应用入口
    ├── ui/                 # UI 组件（主窗口、侧边栏、筛选栏、样式）
    ├── pages/              # 6 个仪表盘页面
    ├── charts/             # ECharts 桥接与模板
    ├── data/               # 数据加载与处理
    ├── assets/             # 静态资源（ECharts JS、中国地图 GeoJSON）
    └── utils/              # 工具函数（AQI 等级、配置）
```

## 视觉设计

- **暗色主题**: 深蓝黑底色 `#0f1117`，电光蓝主色 `#1e90ff`
- **毛玻璃效果**: KPI 卡片半透明背景 + 渐变
- **AQI 标准色**: 优(绿) → 良(黄) → 轻度(橙) → 中度(红) → 重度(紫) → 严重(褐)
