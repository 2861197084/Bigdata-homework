"""Data model type definitions."""

from typing import TypedDict


class CityStats(TypedDict):
    city: str
    value: float


class NationalStats(TypedDict):
    national_avg_aqi: float
    worst_city: str
    worst_city_aqi: float
    best_city: str
    best_city_aqi: float
    exceed_count: int
    total_cities: int


class FilterParams(TypedDict, total=False):
    city: str | None
    start_date: str
    end_date: str
    pollutant: str
