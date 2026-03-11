"""
路由模块
定义 Todo API 的所有端点
"""
from flask import Blueprint, request, jsonify
from models import Todo

# 创建 Blueprint
todo_bp = Blueprint('todos', __name__, url_prefix='/todos')

# 初始化 Todo 模型
todo_model = Todo()


@todo_bp.route('', methods=['GET'])
def get_all_todos():
    """获取所有待办事项

    Returns:
        JSON 格式的待办事项列表
    """
    todos = todo_model.get_all()
    return jsonify(todos), 200


@todo_bp.route('/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """获取单个待办事项

    Args:
        todo_id: 待办事项 ID

    Returns:
        JSON 格式的待办事项，不存在则返回 404
    """
    todo = todo_model.get_by_id(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo), 200


@todo_bp.route('', methods=['POST'])
def create_todo():
    """创建新的待办事项

    Request Body:
        {
            "title": "标题（必填）",
            "description": "描述（可选）",
            "completed": false（可选，默认 false）
        }

    Returns:
        JSON 格式的新建待办事项，参数错误返回 400
    """
    data = request.get_json()

    # 验证必填字段
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    title = data.get('title')
    description = data.get('description', '')
    completed = data.get('completed', False)

    # 验证字段类型
    if not isinstance(title, str):
        return jsonify({'error': 'Title must be a string'}), 400
    if not isinstance(description, str):
        return jsonify({'error': 'Description must be a string'}), 400
    if not isinstance(completed, bool):
        return jsonify({'error': 'Completed must be a boolean'}), 400

    todo = todo_model.create(title, description, completed)
    return jsonify(todo), 201


@todo_bp.route('/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """更新待办事项

    Args:
        todo_id: 待办事项 ID

    Request Body:
        {
            "title": "新标题（可选）",
            "description": "新描述（可选）",
            "completed": true/false（可选）
        }

    Returns:
        JSON 格式的更新后待办事项，不存在返回 404
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 验证字段类型
    if 'title' in data and not isinstance(data['title'], str):
        return jsonify({'error': 'Title must be a string'}), 400
    if 'description' in data and not isinstance(data['description'], str):
        return jsonify({'error': 'Description must be a string'}), 400
    if 'completed' in data and not isinstance(data['completed'], bool):
        return jsonify({'error': 'Completed must be a boolean'}), 400

    todo = todo_model.update(
        todo_id,
        title=data.get('title'),
        description=data.get('description'),
        completed=data.get('completed')
    )

    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404

    return jsonify(todo), 200


@todo_bp.route('/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """删除待办事项

    Args:
        todo_id: 待办事项 ID

    Returns:
        成功返回 204，不存在返回 404
    """
    if todo_model.delete(todo_id):
        return '', 204
    return jsonify({'error': 'Todo not found'}), 404
