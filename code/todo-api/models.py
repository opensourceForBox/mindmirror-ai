"""
数据模型模块
定义 Todo 数据模型和数据库操作
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any


def get_db_connection(db_path: str = 'todos.db') -> sqlite3.Connection:
    """获取数据库连接

    Args:
        db_path: 数据库文件路径

    Returns:
        sqlite3 连接对象
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = 'todos.db') -> None:
    """初始化数据库，创建表结构

    Args:
        db_path: 数据库文件路径
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


class Todo:
    """Todo 数据模型类"""

    def __init__(self, db_path: str = 'todos.db'):
        """初始化 Todo 模型

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        init_db(db_path)

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将数据库行转换为字典

        Args:
            row: 数据库行

        Returns:
            包含 todo 数据的字典
        """
        return {
            'id': row['id'],
            'title': row['title'],
            'description': row['description'],
            'completed': bool(row['completed']),
            'created_at': row['created_at']
        }

    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有待办事项

        Returns:
            包含所有 todo 的列表
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM todos ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_dict(row) for row in rows]

    def get_by_id(self, todo_id: int) -> Optional[Dict[str, Any]]:
        """根据 ID 获取单个待办事项

        Args:
            todo_id: 待办事项 ID

        Returns:
            待办事项字典，不存在则返回 None
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_dict(row)
        return None

    def create(self, title: str, description: str = '', completed: bool = False) -> Dict[str, Any]:
        """创建新的待办事项

        Args:
            title: 标题
            description: 描述
            completed: 是否完成

        Returns:
            新创建的待办事项字典
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)',
            (title, description, completed)
        )
        conn.commit()
        todo_id = cursor.lastrowid

        # 获取刚创建的记录
        cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
        row = cursor.fetchone()
        conn.close()

        return self._row_to_dict(row)

    def update(self, todo_id: int, title: Optional[str] = None,
               description: Optional[str] = None,
               completed: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        """更新待办事项

        Args:
            todo_id: 待办事项 ID
            title: 新标题（可选）
            description: 新描述（可选）
            completed: 新完成状态（可选）

        Returns:
            更新后的待办事项字典，不存在则返回 None
        """
        # 检查记录是否存在
        existing = self.get_by_id(todo_id)
        if not existing:
            return None

        # 构建更新字段
        updates = []
        values = []

        if title is not None:
            updates.append('title = ?')
            values.append(title)
        if description is not None:
            updates.append('description = ?')
            values.append(description)
        if completed is not None:
            updates.append('completed = ?')
            values.append(completed)

        if not updates:
            return existing

        values.append(todo_id)
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE todos SET {', '.join(updates)} WHERE id = ?",
            values
        )
        conn.commit()

        # 获取更新后的记录
        cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
        row = cursor.fetchone()
        conn.close()

        return self._row_to_dict(row)

    def delete(self, todo_id: int) -> bool:
        """删除待办事项

        Args:
            todo_id: 待办事项 ID

        Returns:
            删除成功返回 True，记录不存在返回 False
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
