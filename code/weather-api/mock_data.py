"""
Mock weather data for testing and development.

This module provides simulated weather data for multiple cities
including current conditions and 3-day forecasts.
"""

from typing import Dict, List


# 模拟城市天气数据
WEATHER_DATA: Dict[str, Dict] = {
    "北京": {
        "current": {
            "city": "北京",
            "temperature": 15,
            "condition": "晴",
            "humidity": 45,
            "wind_speed": 12,
            "wind_direction": "西北",
            "aqi": 85
        },
        "forecast": [
            {"date": "2026-03-10", "high": 18, "low": 5, "condition": "晴"},
            {"date": "2026-03-11", "high": 20, "low": 7, "condition": "多云"},
            {"date": "2026-03-12", "high": 16, "low": 4, "condition": "小雨"}
        ]
    },
    "上海": {
        "current": {
            "city": "上海",
            "temperature": 12,
            "condition": "多云",
            "humidity": 68,
            "wind_speed": 8,
            "wind_direction": "东",
            "aqi": 62
        },
        "forecast": [
            {"date": "2026-03-10", "high": 14, "low": 8, "condition": "多云"},
            {"date": "2026-03-11", "high": 16, "low": 10, "condition": "阴"},
            {"date": "2026-03-12", "high": 18, "low": 11, "condition": "小雨"}
        ]
    },
    "广州": {
        "current": {
            "city": "广州",
            "temperature": 25,
            "condition": "晴",
            "humidity": 75,
            "wind_speed": 6,
            "wind_direction": "南",
            "aqi": 45
        },
        "forecast": [
            {"date": "2026-03-10", "high": 28, "low": 18, "condition": "晴"},
            {"date": "2026-03-11", "high": 29, "low": 19, "condition": "多云"},
            {"date": "2026-03-12", "high": 26, "low": 17, "condition": "雷阵雨"}
        ]
    },
    "深圳": {
        "current": {
            "city": "深圳",
            "temperature": 26,
            "condition": "晴",
            "humidity": 72,
            "wind_speed": 10,
            "wind_direction": "东南",
            "aqi": 38
        },
        "forecast": [
            {"date": "2026-03-10", "high": 28, "low": 19, "condition": "晴"},
            {"date": "2026-03-11", "high": 27, "low": 18, "condition": "多云"},
            {"date": "2026-03-12", "high": 25, "low": 17, "condition": "小雨"}
        ]
    },
    "杭州": {
        "current": {
            "city": "杭州",
            "temperature": 14,
            "condition": "阴",
            "humidity": 65,
            "wind_speed": 7,
            "wind_direction": "东北",
            "aqi": 55
        },
        "forecast": [
            {"date": "2026-03-10", "high": 17, "low": 9, "condition": "多云"},
            {"date": "2026-03-11", "high": 19, "low": 11, "condition": "晴"},
            {"date": "2026-03-12", "high": 15, "low": 8, "condition": "小雨"}
        ]
    }
}


def get_city_names() -> List[str]:
    """
    Get a list of all available city names.

    Returns:
        List[str]: A list of city names supported by the API.
    """
    return list(WEATHER_DATA.keys())


def get_weather_by_city(city: str) -> Dict | None:
    """
    Get current weather data for a specific city.

    Args:
        city: The name of the city to get weather for.

    Returns:
        Dict containing current weather data, or None if city not found.
    """
    if city in WEATHER_DATA:
        return WEATHER_DATA[city]["current"]
    return None


def get_forecast_by_city(city: str) -> List[Dict] | None:
    """
    Get 3-day weather forecast for a specific city.

    Args:
        city: The name of the city to get forecast for.

    Returns:
        List of forecast dictionaries, or None if city not found.
    """
    if city in WEATHER_DATA:
        return WEATHER_DATA[city]["forecast"]
    return None
