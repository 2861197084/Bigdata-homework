"""Data processing and aggregation functions."""

import pandas as pd
import numpy as np


def filter_data(df: pd.DataFrame, city: str | None = None,
                start_date: str | None = None, end_date: str | None = None) -> pd.DataFrame:
    """Filter DataFrame by city and date range."""
    result = df.copy()
    if city:
        result = result[result["City"] == city]
    if start_date:
        result = result[result["Date"] >= pd.Timestamp(start_date)]
    if end_date:
        result = result[result["Date"] <= pd.Timestamp(end_date)]
    return result


def city_ranking(df: pd.DataFrame, metric: str = "AQI", top_n: int = 40) -> list[dict]:
    """Rank cities by average of a metric."""
    avg = df.groupby("City", observed=True)[metric].mean().sort_values(ascending=False).head(top_n)
    return [{"city": city, "value": round(val, 1)} for city, val in avg.items()]


def city_daily_trend(df: pd.DataFrame, city: str, metric: str = "AQI") -> list[dict]:
    """Get daily trend for a single city."""
    cdf = df[df["City"] == city].sort_values("Date")
    return [{"date": d.strftime("%Y-%m-%d"), "value": round(v, 1)}
            for d, v in zip(cdf["Date"], cdf[metric])]


def multi_city_monthly_trend(df: pd.DataFrame, cities: list[str],
                              metric: str = "AQI") -> dict:
    """Get monthly trend for multiple cities."""
    result = {}
    for city in cities:
        cdf = df[df["City"] == city]
        monthly = cdf.groupby([cdf["Date"].dt.to_period("M")])[metric].mean()
        result[city] = [{"date": str(p), "value": round(v, 1)}
                        for p, v in monthly.items()]
    return result


def pollutant_profile(df: pd.DataFrame, cities: list[str]) -> dict:
    """Get average pollutant values for radar chart."""
    pollutants = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
    result = {}
    for city in cities:
        cdf = df[df["City"] == city]
        result[city] = {p: round(cdf[p].mean(), 2) for p in pollutants}
    return result


def aqi_distribution(df: pd.DataFrame) -> list[dict]:
    """Count cities in each AQI category."""
    city_avg = df.groupby("City", observed=True)["AQI"].mean()
    categories = [
        ("优", 0, 50), ("良", 51, 100), ("轻度污染", 101, 150),
        ("中度污染", 151, 200), ("重度污染", 201, 300), ("严重污染", 301, 500),
    ]
    result = []
    for label, lo, hi in categories:
        count = int(((city_avg >= lo) & (city_avg <= hi)).sum())
        if count > 0:
            result.append({"name": label, "value": count})
    return result


def national_stats(df: pd.DataFrame) -> dict:
    """Compute national-level statistics."""
    city_avg = df.groupby("City", observed=True)["AQI"].mean()
    worst_city = city_avg.idxmax()
    best_city = city_avg.idxmin()
    exceed_count = int((city_avg > 100).sum())
    return {
        "national_avg_aqi": round(city_avg.mean(), 1),
        "worst_city": worst_city,
        "worst_city_aqi": round(city_avg[worst_city], 1),
        "best_city": best_city,
        "best_city_aqi": round(city_avg[best_city], 1),
        "exceed_count": exceed_count,
        "total_cities": len(city_avg),
    }


def city_map_data(df: pd.DataFrame, city_coords: dict, metric: str = "AQI") -> list[dict]:
    """Get per-city average for map scatter."""
    city_avg = df.groupby("City", observed=True)[metric].mean()
    result = []
    for city, val in city_avg.items():
        if city in city_coords:
            lon, lat = city_coords[city]
            result.append({
                "name": city,
                "value": [lon, lat, round(val, 1)],
            })
    return result


def calendar_heatmap_data(df: pd.DataFrame, city: str, year: int,
                           metric: str = "AQI") -> list[list]:
    """Get daily data for calendar heatmap. Returns [[date_str, value], ...]."""
    cdf = df[(df["City"] == city) & (df["Year"] == year)].sort_values("Date")
    return [[d.strftime("%Y-%m-%d"), round(v, 1)]
            for d, v in zip(cdf["Date"], cdf[metric])]


def monthly_heatmap_data(df: pd.DataFrame, metric: str = "AQI",
                          top_n: int = 20) -> dict:
    """City x Month heatmap data."""
    city_avg = df.groupby("City", observed=True)[metric].mean().sort_values(ascending=False).head(top_n)
    cities = city_avg.index.tolist()
    cdf = df[df["City"].isin(cities)]
    pivot = cdf.groupby(["City", "Month"], observed=True)[metric].mean().unstack(fill_value=0)
    data = []
    for i, city in enumerate(cities):
        for month in range(1, 13):
            val = round(pivot.loc[city, month], 1) if month in pivot.columns else 0
            data.append([month - 1, i, val])
    return {"cities": cities, "data": data}


def yearly_comparison(df: pd.DataFrame, city: str, metric: str = "AQI") -> dict:
    """Year-over-year monthly comparison."""
    cdf = df[df["City"] == city]
    result = {}
    for year in sorted(cdf["Year"].unique()):
        ydf = cdf[cdf["Year"] == year]
        monthly = ydf.groupby("Month")[metric].mean()
        result[str(year)] = [round(monthly.get(m, 0), 1) for m in range(1, 13)]
    return result


def pollutant_correlation(df: pd.DataFrame, pol_x: str, pol_y: str,
                           sample_n: int = 2000) -> list[list]:
    """Scatter data for two pollutants correlation."""
    sample = df[[pol_x, pol_y, "AQI", "City"]].dropna()
    if len(sample) > sample_n:
        sample = sample.sample(sample_n, random_state=42)
    return [[round(row[pol_x], 1), round(row[pol_y], 1),
             round(row["AQI"], 1), row["City"]]
            for _, row in sample.iterrows()]


def pollutant_boxplot_data(df: pd.DataFrame) -> dict:
    """Box plot data for each pollutant."""
    pollutants = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
    result = {}
    for p in pollutants:
        vals = df[p].dropna()
        q1, median, q3 = vals.quantile([0.25, 0.5, 0.75]).values
        iqr = q3 - q1
        lower = max(vals.min(), q1 - 1.5 * iqr)
        upper = min(vals.max(), q3 + 1.5 * iqr)
        result[p] = [round(lower, 1), round(q1, 1), round(median, 1),
                      round(q3, 1), round(upper, 1)]
    return result


def stacked_pollutant_data(df: pd.DataFrame, top_n: int = 15) -> dict:
    """Stacked bar data: pollutant composition per city."""
    pollutants = ["PM2.5", "PM10", "SO2", "NO2", "O3"]
    city_avg = df.groupby("City", observed=True)["AQI"].mean().sort_values(ascending=False).head(top_n)
    cities = city_avg.index.tolist()
    cdf = df[df["City"].isin(cities)]
    series = {}
    for p in pollutants:
        city_p = cdf.groupby("City", observed=True)[p].mean()
        series[p] = [round(city_p.get(c, 0), 1) for c in cities]
    return {"cities": cities, "series": series}


def trend_with_forecast(df: pd.DataFrame, city: str, metric: str = "AQI",
                         forecast_days: int = 60) -> dict:
    """Monthly trend with polynomial forecast."""
    cdf = df[df["City"] == city].sort_values("Date")
    monthly = cdf.groupby(cdf["Date"].dt.to_period("M"))[metric].mean()
    dates = [str(p) for p in monthly.index]
    values = [round(v, 1) for v in monthly.values]

    # Simple polynomial forecast
    x = np.arange(len(values))
    coeffs = np.polyfit(x, values, 3)
    poly = np.poly1d(coeffs)
    forecast_n = forecast_days // 30
    forecast_x = np.arange(len(values), len(values) + forecast_n)
    forecast_vals = [round(max(0, float(poly(xi))), 1) for xi in forecast_x]

    # Generate future date labels
    last_period = monthly.index[-1]
    forecast_dates = []
    for i in range(1, forecast_n + 1):
        fp = last_period + i
        forecast_dates.append(str(fp))

    return {
        "dates": dates,
        "values": values,
        "forecast_dates": forecast_dates,
        "forecast_values": forecast_vals,
    }


def seasonal_pollutant_data(df: pd.DataFrame, city: str) -> dict:
    """Seasonal average of pollutants for radar chart."""
    pollutants = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
    cdf = df[df["City"] == city]
    seasons = {
        "春季": [3, 4, 5], "夏季": [6, 7, 8],
        "秋季": [9, 10, 11], "冬季": [12, 1, 2],
    }
    result = {}
    for season, months in seasons.items():
        sdf = cdf[cdf["Month"].isin(months)]
        result[season] = {p: round(sdf[p].mean(), 2) for p in pollutants}
    return result


def health_treemap_data(df: pd.DataFrame) -> list[dict]:
    """Treemap: cities grouped by AQI health level."""
    city_avg = df.groupby("City", observed=True)["AQI"].mean()
    levels = [
        ("优 (0-50)", 0, 50, "#2da44e"),
        ("良 (51-100)", 51, 100, "#e8a020"),
        ("轻度污染 (101-150)", 101, 150, "#e07b39"),
        ("中度污染 (151-200)", 151, 200, "#c0392b"),
        ("重度污染 (201-300)", 201, 300, "#862e9c"),
    ]
    result = []
    for label, lo, hi, color in levels:
        children = []
        for city, aqi in city_avg.items():
            if lo <= aqi <= hi:
                children.append({"name": city, "value": round(aqi, 1)})
        if children:
            result.append({
                "name": label,
                "itemStyle": {"color": color},
                "children": children,
            })
    return result


def weather_correlation_data(df: pd.DataFrame, city: str | None = None,
                              sample_n: int = 3000) -> dict:
    """PM2.5 vs Temperature and Wind vs AQI scatter data."""
    cdf = df if city is None else df[df["City"] == city]
    cdf = cdf[["PM2.5", "Temperature", "Wind_Speed", "AQI", "Month"]].dropna()
    if len(cdf) > sample_n:
        cdf = cdf.sample(sample_n, random_state=42)

    def season(m):
        if m in [3, 4, 5]: return "春季"
        if m in [6, 7, 8]: return "夏季"
        if m in [9, 10, 11]: return "秋季"
        return "冬季"

    pm_temp = [[round(row["Temperature"], 1), round(row["PM2.5"], 1), season(row["Month"])]
               for _, row in cdf.iterrows()]
    wind_aqi = [[round(row["Wind_Speed"], 1), round(row["AQI"], 1),
                  round(row["PM2.5"], 1)]
                 for _, row in cdf.iterrows()]
    return {"pm_temp": pm_temp, "wind_aqi": wind_aqi}
