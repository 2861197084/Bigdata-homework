"""Generate realistic synthetic air quality data for Chinese cities.

Based on real-world patterns:
- Northern cities have worse winter pollution (heating season)
- Southern cities are generally cleaner
- AQI correlates with PM2.5 as primary pollutant
- Seasonal patterns: winter worst, summer best
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

# Major Chinese cities with approximate characteristics
# (city, base_aqi, winter_boost, latitude_factor)
CITIES = [
    ("北京", 85, 60, 1.0),
    ("上海", 65, 30, 0.8),
    ("广州", 55, 15, 0.6),
    ("深圳", 45, 10, 0.5),
    ("成都", 75, 40, 0.9),
    ("重庆", 70, 35, 0.85),
    ("天津", 80, 55, 0.95),
    ("武汉", 70, 35, 0.8),
    ("杭州", 60, 25, 0.7),
    ("南京", 65, 30, 0.75),
    ("西安", 80, 50, 0.95),
    ("郑州", 80, 50, 0.9),
    ("沈阳", 80, 55, 1.0),
    ("哈尔滨", 85, 65, 1.05),
    ("长春", 80, 60, 1.0),
    ("济南", 75, 45, 0.9),
    ("石家庄", 90, 65, 1.05),
    ("太原", 85, 55, 1.0),
    ("合肥", 65, 30, 0.75),
    ("长沙", 60, 25, 0.7),
    ("福州", 45, 10, 0.5),
    ("昆明", 40, 5, 0.4),
    ("贵阳", 50, 10, 0.5),
    ("南宁", 45, 8, 0.45),
    ("兰州", 75, 45, 0.9),
    ("呼和浩特", 70, 50, 0.95),
    ("乌鲁木齐", 80, 60, 1.0),
    ("拉萨", 30, 5, 0.3),
    ("银川", 65, 40, 0.85),
    ("西宁", 55, 30, 0.7),
    ("海口", 35, 5, 0.3),
    ("大连", 55, 30, 0.7),
    ("青岛", 55, 25, 0.65),
    ("厦门", 40, 8, 0.45),
    ("苏州", 60, 25, 0.7),
    ("无锡", 62, 28, 0.72),
    ("宁波", 55, 20, 0.65),
    ("佛山", 55, 15, 0.6),
    ("东莞", 50, 12, 0.55),
    ("珠海", 35, 8, 0.35),
]

# Date range: 2015-01-01 to 2024-12-31
dates = pd.date_range("2015-01-01", "2024-12-31", freq="D")

records = []

for city, base_aqi, winter_boost, lat_factor in CITIES:
    for date in dates:
        month = date.month
        year = date.year

        # Seasonal pattern: winter high, summer low
        if month in [12, 1, 2]:
            seasonal = winter_boost * (0.8 + 0.4 * np.random.random())
        elif month in [6, 7, 8]:
            seasonal = -base_aqi * 0.2 * (0.5 + np.random.random())
        elif month in [3, 4, 5]:
            seasonal = winter_boost * 0.2 * (np.random.random() - 0.3)
        else:  # 9, 10, 11
            seasonal = winter_boost * 0.4 * (0.3 + 0.7 * np.random.random())

        # Year-over-year improvement trend (China's pollution has decreased)
        year_trend = -(year - 2015) * 2.5

        # Daily random variation
        daily_noise = np.random.normal(0, 15)

        aqi = max(10, int(base_aqi + seasonal + year_trend + daily_noise))
        aqi = min(aqi, 500)

        # Derive pollutant values from AQI with realistic correlations
        pm25 = max(2, aqi * (0.6 + 0.3 * np.random.random()) + np.random.normal(0, 5))
        pm10 = max(5, pm25 * (1.3 + 0.4 * np.random.random()) + np.random.normal(0, 8))
        so2 = max(2, aqi * (0.1 + 0.08 * np.random.random()) + np.random.normal(0, 3))
        no2 = max(3, aqi * (0.3 + 0.2 * np.random.random()) + np.random.normal(0, 5))
        co = max(0.2, aqi * 0.008 + np.random.normal(0, 0.15))
        o3 = max(5, 80 - aqi * 0.3 + np.random.normal(0, 15))  # inversely correlated in winter
        if month in [6, 7, 8]:
            o3 = max(20, 120 + np.random.normal(0, 20))  # high ozone in summer

        # Temperature (rough latitude-based seasonal pattern)
        if month in [12, 1, 2]:
            temp = -5 * lat_factor + np.random.normal(0, 3)
        elif month in [6, 7, 8]:
            temp = 30 - 2 * (lat_factor - 0.5) + np.random.normal(0, 3)
        elif month in [3, 4, 5]:
            temp = 15 - 5 * lat_factor + np.random.normal(0, 3)
        else:
            temp = 20 - 8 * lat_factor + np.random.normal(0, 3)

        humidity = max(20, min(98, 60 + np.random.normal(0, 15) - 10 * lat_factor))
        wind_speed = max(0.5, 3 + np.random.exponential(2))

        records.append({
            "Date": date.strftime("%Y-%m-%d"),
            "City": city,
            "AQI": aqi,
            "PM2.5": round(pm25, 1),
            "PM10": round(pm10, 1),
            "SO2": round(so2, 1),
            "NO2": round(no2, 1),
            "CO": round(co, 2),
            "O3": round(o3, 1),
            "Temperature": round(temp, 1),
            "Humidity": round(humidity, 1),
            "Wind_Speed": round(wind_speed, 1),
        })

df = pd.DataFrame(records)
output_path = Path(__file__).parent.parent / "data" / "china_air_quality.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"Generated {len(df)} records for {len(CITIES)} cities")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"Saved to {output_path}")
print(f"File size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
print(f"\nSample:\n{df.head()}")
