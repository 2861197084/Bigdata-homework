"""Data loading and caching."""

import json
import pandas as pd
from pathlib import Path

from ..utils.config import DATA_DIR


class DataLoader:
    """Singleton-like data loader for air quality CSV data."""

    _instance = None
    _df = None
    _city_coords = None

    @classmethod
    def get_instance(cls) -> "DataLoader":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._load_data()

    def _load_data(self):
        csv_path = DATA_DIR / "china_air_quality.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Data file not found: {csv_path}")

        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        df["Date"] = pd.to_datetime(df["Date"])
        df["City"] = df["City"].astype("category")
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month

        # Ensure numeric columns
        for col in ["AQI", "PM2.5", "PM10", "SO2", "NO2", "CO", "O3",
                     "Temperature", "Humidity", "Wind_Speed"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        self._df = df

        # Load city coordinates
        coords_path = DATA_DIR / "city_coordinates.json"
        if coords_path.exists():
            with open(coords_path, "r", encoding="utf-8") as f:
                self._city_coords = json.load(f)
        else:
            self._city_coords = {}

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @property
    def city_coords(self) -> dict:
        return self._city_coords

    def get_cities(self) -> list[str]:
        return sorted(self._df["City"].cat.categories.tolist())

    def get_date_range(self) -> tuple[str, str]:
        return (
            self._df["Date"].min().strftime("%Y-%m-%d"),
            self._df["Date"].max().strftime("%Y-%m-%d"),
        )

    def get_years(self) -> list[int]:
        return sorted(self._df["Year"].unique().tolist())
