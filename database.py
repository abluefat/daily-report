# database.py - 增强版数据库（支持分组/搜索/推荐）
import sqlite3
from datetime import datetime
import os


class Database:
    def __init__(self, db_path="projects.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """初始化增强版数据库结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 分组表
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS project_groups
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           name
                           TEXT
                           NOT
                           NULL
                           UNIQUE,
                           parent_id
                           INTEGER,
                           icon
                           TEXT
                           DEFAULT
                           '📁',
                           sort_order
                           INTEGER
                           DEFAULT
                           0,
                           FOREIGN
                           KEY
                       (
                           parent_id
                       ) REFERENCES project_groups
                       (
                           id
                       )
                           )
                       ''')

        # 项目表
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS projects
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           name
                           TEXT
                           NOT
                           NULL
                           UNIQUE,
                           group_id
                           INTEGER,
                           icon
                           TEXT
                           DEFAULT
                           '📌',
                           is_common
                           BOOLEAN
                           DEFAULT
                           0,
                           usage_count
                           INTEGER
                           DEFAULT
                           0,
                           last_used
                           TIMESTAMP,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           updated_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           group_id
                       ) REFERENCES project_groups
                       (
                           id
                       )
                           )
                       ''')

        # 日报表
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS daily_reports
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           date
                           TEXT
                           NOT
                           NULL,
                           project_id
                           INTEGER,
                           task_content
                           TEXT
                           NOT
                           NULL,
                           hours
                           REAL
                           NOT
                           NULL,
                           status
                           TEXT
                           NOT
                           NULL,
                           notes
                           TEXT,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           project_id
                       ) REFERENCES projects
                       (
                           id
                       )
                           )
                       ''')

        # 初始化默认分组（避免空状态）
        cursor.execute("SELECT COUNT(*) FROM project_groups")
        if cursor.fetchone()[0] == 0:
            default_groups = [
                (1, "客户项目", None, "🏢", 1),
                (2, "内部项目", None, "🔧", 2),
                (3, "研发项目", 1, "💻", 3),
                (4, "运维项目", 1, "⚙️", 4),
                (5, "行政事务", 2, "📋", 5),
                (6, "市场活动", 2, "📣", 6)
            ]
            cursor.executemany(
                "INSERT INTO project_groups (id, name, parent_id, icon, sort_order) VALUES (?, ?, ?, ?, ?)",
                default_groups
            )

        # 初始化默认项目
        cursor.execute("SELECT COUNT(*) FROM projects")
        if cursor.fetchone()[0] == 0:
            default_projects = [
                ("客户系统升级", 1, "🚀", 1, 5),
                ("内部工具开发", 2, "🛠️", 1, 8),
                ("需求评审", 3, "📝", 0, 3),
                ("Bug修复", 4, "🐞", 1, 12),
                ("周报整理", 5, "📊", 0, 2),
                ("产品发布会", 6, "🎤", 1, 4)
            ]
            cursor.executemany(
                "INSERT INTO projects (name, group_id, icon, is_common, usage_count) VALUES (?, ?, ?, ?, ?)",
                default_projects
            )

        conn.commit()
        conn.close()

    # ========== 项目管理 ==========
    def get_projects(self, group_id=None, search_text=""):
        """获取项目列表（支持分组过滤+搜索）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
                SELECT p.id, p.name, p.icon, p.is_common, p.usage_count, g.name as group_name
                FROM projects p
                         LEFT JOIN project_groups g ON p.group_id = g.id
                WHERE 1 = 1 \
                """
        params = []

        if group_id:
            query += " AND p.group_id = ?"
            params.append(group_id)

        if search_text:
            query += " AND (p.name LIKE ? OR g.name LIKE ?)"
            like_text = f"%{search_text}%"
            params.extend([like_text, like_text])

        query += " ORDER BY p.is_common DESC, p.usage_count DESC, p.name"
        cursor.execute(query, params)
        projects = cursor.fetchall()
        conn.close()
        return projects

    def get_common_projects(self, limit=5):
        """获取常用项目（按使用频率排序）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT id, name, icon
                       FROM projects
                       WHERE is_common = 1
                          OR usage_count > 0
                       ORDER BY is_common DESC, usage_count DESC, last_used DESC LIMIT ?
                       """, (limit,))
        projects = cursor.fetchall()
        conn.close()
        return projects

    def increment_usage(self, project_id):
        """增加项目使用计数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
                       UPDATE projects
                       SET usage_count = usage_count + 1,
                           last_used   = CURRENT_TIMESTAMP
                       WHERE id = ?
                       """, (project_id,))
        conn.commit()
        conn.close()

    def get_project_by_id(self, project_id):
        """根据ID获取项目名称"""
        if not project_id:
            return "其他"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM projects WHERE id = ?", (project_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "未知项目"

    # ========== 分组管理 ==========
    def get_groups_tree(self):
        """获取分组树形结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT id, name, parent_id, icon, sort_order
                       FROM project_groups
                       ORDER BY sort_order, name
                       """)
        groups = cursor.fetchall()
        conn.close()
        return self._build_tree(groups)

    def _build_tree(self, groups):
        """构建树形结构"""
        tree = []
        group_dict = {g[0]: {"id": g[0], "name": g[1], "parent_id": g[2], "icon": g[3], "children": []} for g in groups}

        for group in groups:
            if group[2] is None:  # 顶级分组
                tree.append(group_dict[group[0]])
            else:
                parent = group_dict.get(group[2])
                if parent:
                    parent["children"].append(group_dict[group[0]])
        return tree

    # ========== 项目CRUD ==========
    def add_project(self, name, group_id=None, icon="📌", is_common=False):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO projects (name, group_id, icon, is_common) VALUES (?, ?, ?, ?)",
                (name, group_id, icon, 1 if is_common else 0)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def update_project(self, project_id, name=None, group_id=None, icon=None, is_common=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if group_id is not None:
            updates.append("group_id = ?")
            params.append(group_id)
        if icon is not None:
            updates.append("icon = ?")
            params.append(icon)
        if is_common is not None:
            updates.append("is_common = ?")
            params.append(1 if is_common else 0)

        if updates:
            params.append(project_id)
            cursor.execute(f"UPDATE projects SET {', '.join(updates)}, updated_at=CURRENT_TIMESTAMP WHERE id = ?",
                           params)
            conn.commit()
        conn.close()
        return True

    def delete_project(self, project_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM daily_reports WHERE project_id = ?", (project_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        conn.close()
        return True

    # ========== 分组CRUD ==========
    def add_group(self, name, parent_id=None, icon="📁", sort_order=0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO project_groups (name, parent_id, icon, sort_order) VALUES (?, ?, ?, ?)",
                (name, parent_id, icon, sort_order)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def update_group(self, group_id, name=None, parent_id=None, icon=None, sort_order=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if parent_id is not None:
            updates.append("parent_id = ?")
            params.append(parent_id)
        if icon is not None:
            updates.append("icon = ?")
            params.append(icon)
        if sort_order is not None:
            updates.append("sort_order = ?")
            params.append(sort_order)

        if updates:
            params.append(group_id)
            cursor.execute(f"UPDATE project_groups SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()
        conn.close()
        return True

    def delete_group(self, group_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 检查是否有子分组或项目
        cursor.execute("SELECT COUNT(*) FROM project_groups WHERE parent_id = ?", (group_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "该分组下存在子分组，无法删除"

        cursor.execute("SELECT COUNT(*) FROM projects WHERE group_id = ?", (group_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "该分组下存在项目，无法删除"

        cursor.execute("DELETE FROM project_groups WHERE id = ?", (group_id,))
        conn.commit()
        conn.close()
        return True, "删除成功"