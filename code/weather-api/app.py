"""
Flask Weather API Application

A simple weather API service providing current weather conditions
and 3-day forecasts for major Chinese cities.

Usage:
    python app.py

The API server will start at http://127.0.0.1:5000
"""

from flask import Flask, redirect, url_for

from routes import weather_bp


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)

    # 注册 Blueprint
    app.register_blueprint(weather_bp)

    @app.route("/")
    def index() -> tuple:
        """
        Redirect root URL to API documentation endpoint.

        Returns:
            Redirect response to /api/cities endpoint.
        """
        return redirect(url_for("weather.list_cities"))

    @app.route("/api")
    def api_info() -> tuple:
        """
        API information endpoint.

        Returns:
            JSON response with API documentation.
        """
        from flask import jsonify

        return jsonify({
            "name": "Weather API",
            "version": "1.0.0",
            "endpoints": {
                "GET /api/weather?city=<city>": "获取指定城市的当前天气",
                "GET /api/forecast?city=<city>": "获取指定城市的 3 天天气预报",
                "GET /api/cities": "获取所有支持的城市列表"
            },
            "supported_cities": ["北京", "上海", "广州", "深圳", "杭州"]
        }), 200

    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    # 启动开发服务器
    print("=" * 50)
    print("Flask 天气 API 服务已启动")
    print("=" * 50)
    print("API 端点:")
    print("  GET /api/weather?city=<city>   - 查询当前天气")
    print("  GET /api/forecast?city=<city>  - 查询天气预报")
    print("  GET /api/cities                - 获取城市列表")
    print("=" * 50)
    print("支持的城市：北京、上海、广州、深圳、杭州")
    print("=" * 50)

    app.run(host="0.0.0.0", port=5000, debug=True)
