"""
API routes for the weather application.

This module defines all API endpoints for the weather service,
including current weather, forecasts, and city listings.
"""

from flask import Blueprint, jsonify, request

from mock_data import get_city_names, get_weather_by_city, get_forecast_by_city
from models import Forecast, Weather, parse_forecast_list

# 创建 Blueprint
weather_bp = Blueprint("weather", __name__, url_prefix="/api")


@weather_bp.route("/weather", methods=["GET"])
def get_weather() -> tuple:
    """
    Get current weather for a specified city.

    Query Parameters:
        city: Name of the city (required)

    Returns:
        JSON response containing current weather data or error message.

    Example:
        GET /api/weather?city=北京

    Response:
        {
            "success": true,
            "data": {
                "city": "北京",
                "temperature": 15,
                "condition": "晴",
                ...
            }
        }
    """
    city = request.args.get("city")

    if not city:
        return jsonify({
            "success": False,
            "error": "缺少必要参数：city"
        }), 400

    weather_data = get_weather_by_city(city)

    if weather_data is None:
        return jsonify({
            "success": False,
            "error": f"未找到城市 '{city}' 的天气数据"
        }), 404

    # 使用 Weather 模型类转换数据
    weather = Weather.from_dict(weather_data)

    return jsonify({
        "success": True,
        "data": weather.to_dict()
    }), 200


@weather_bp.route("/forecast", methods=["GET"])
def get_forecast() -> tuple:
    """
    Get 3-day weather forecast for a specified city.

    Query Parameters:
        city: Name of the city (required)

    Returns:
        JSON response containing forecast data or error message.

    Example:
        GET /api/forecast?city=上海

    Response:
        {
            "success": true,
            "data": [
                {"date": "2026-03-10", "high": 14, "low": 8, "condition": "多云"},
                ...
            ]
        }
    """
    city = request.args.get("city")

    if not city:
        return jsonify({
            "success": False,
            "error": "缺少必要参数：city"
        }), 400

    forecast_data = get_forecast_by_city(city)

    if forecast_data is None:
        return jsonify({
            "success": False,
            "error": f"未找到城市 '{city}' 的预报数据"
        }), 404

    # 使用 Forecast 模型类转换数据
    forecasts = parse_forecast_list(forecast_data)

    return jsonify({
        "success": True,
        "data": [f.to_dict() for f in forecasts]
    }), 200


@weather_bp.route("/cities", methods=["GET"])
def list_cities() -> tuple:
    """
    Get list of all available cities.

    Returns:
        JSON response containing list of supported city names.

    Example:
        GET /api/cities

    Response:
        {
            "success": true,
            "data": {
                "cities": ["北京", "上海", "广州", "深圳", "杭州"],
                "count": 5
            }
        }
    """
    cities = get_city_names()

    return jsonify({
        "success": True,
        "data": {
            "cities": cities,
            "count": len(cities)
        }
    }), 200
