"""
Data models for the weather API.

This module defines data classes for weather information and forecasts
with proper type hints for better IDE support and code quality.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Weather:
    """
    Current weather data for a city.

    Attributes:
        city: Name of the city.
        temperature: Current temperature in Celsius.
        condition: Weather condition description (e.g., '晴', '多云').
        humidity: Relative humidity percentage.
        wind_speed: Wind speed in km/h.
        wind_direction: Wind direction (e.g., '西北', '东南').
        aqi: Air Quality Index value.
    """
    city: str
    temperature: int
    condition: str
    humidity: int
    wind_speed: int
    wind_direction: str
    aqi: int

    def to_dict(self) -> dict:
        """
        Convert weather data to dictionary format.

        Returns:
            dict: Dictionary representation of weather data.
        """
        return {
            "city": self.city,
            "temperature": self.temperature,
            "condition": self.condition,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction,
            "aqi": self.aqi
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Weather":
        """
        Create Weather instance from dictionary.

        Args:
            data: Dictionary containing weather data.

        Returns:
            Weather: New Weather instance.
        """
        return cls(
            city=data["city"],
            temperature=data["temperature"],
            condition=data["condition"],
            humidity=data["humidity"],
            wind_speed=data["wind_speed"],
            wind_direction=data["wind_direction"],
            aqi=data["aqi"]
        )


@dataclass
class Forecast:
    """
    Weather forecast for a specific date.

    Attributes:
        date: Forecast date in YYYY-MM-DD format.
        high: Maximum temperature in Celsius.
        low: Minimum temperature in Celsius.
        condition: Expected weather condition.
    """
    date: str
    high: int
    low: int
    condition: str

    def to_dict(self) -> dict:
        """
        Convert forecast data to dictionary format.

        Returns:
            dict: Dictionary representation of forecast data.
        """
        return {
            "date": self.date,
            "high": self.high,
            "low": self.low,
            "condition": self.condition
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Forecast":
        """
        Create Forecast instance from dictionary.

        Args:
            data: Dictionary containing forecast data.

        Returns:
            Forecast: New Forecast instance.
        """
        return cls(
            date=data["date"],
            high=data["high"],
            low=data["low"],
            condition=data["condition"]
        )


def parse_forecast_list(forecast_data: List[dict]) -> List[Forecast]:
    """
    Parse a list of forecast dictionaries into Forecast objects.

    Args:
        forecast_data: List of dictionaries containing forecast data.

    Returns:
        List[Forecast]: List of Forecast objects.
    """
    return [Forecast.from_dict(item) for item in forecast_data]
