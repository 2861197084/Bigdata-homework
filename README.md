# AirScope - 中国城市空气质量监测可视化大屏

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

# 生成数据
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
    ├── ui/                 # UI 组件
    ├── pages/              # 6 个仪表盘页面
    ├── charts/             # ECharts 桥接与模板
    ├── data/               # 数据加载与处理
    ├── assets/             # 静态资源
    └── utils/              # 工具函数
```
