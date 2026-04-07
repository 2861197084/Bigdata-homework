"""AQI level classification and color utilities."""

from .config import AQI_LEVELS


def get_aqi_level(value: float) -> dict:
    """Return the AQI level info dict for a given AQI value."""
    for level in AQI_LEVELS:
        if level["min"] <= value <= level["max"]:
            return level
    return AQI_LEVELS[-1]


def get_aqi_color(value: float) -> str:
    """Return hex color for an AQI value."""
    return get_aqi_level(value)["color"]


def get_aqi_label(value: float) -> str:
    """Return Chinese label for an AQI value."""
    return get_aqi_level(value)["label"]
