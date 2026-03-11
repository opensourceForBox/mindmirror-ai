"""
Flask 应用入口
Todo API 服务主程序
"""
from flask import Flask

from routes import todo_bp


def create_app() -> Flask:
    """创建并配置 Flask 应用

    Returns:
        配置好的 Flask 应用实例
    """
    app = Flask(__name__)

    # 配置 JSON 编码
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSON_AS_ASCII'] = False

    # 注册 Blueprint
    app.register_blueprint(todo_bp)

    return app


# 创建应用实例
app = create_app()


if __name__ == '__main__':
    # 启动开发服务器
    app.run(debug=True, host='0.0.0.0', port=5000)
