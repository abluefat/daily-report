# ProjectDialog.py - 完整项目管理对话框
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTreeWidget,
    QTreeWidgetItem, QTableWidget, QTableWidgetItem, QPushButton,
    QMessageBox, QComboBox, QCheckBox, QGridLayout, QDialogButtonBox,
    QHeaderView, QListWidget, QListWidgetItem, QSplitter, QAbstractItemView, QWidget, QFormLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor
import sqlite3


class ProjectDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("📁 项目管理中心")
        self.setGeometry(200, 100, 850, 600)
        self.setStyleSheet("""
            QDialog {
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                background-color: #2196F3;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #1e88e5;
            }
            QPushButton:pressed {
                background-color: #1976d2;
            }
            QPushButton#deleteBtn {
                background-color: #f44336;
            }
            QPushButton#deleteBtn:hover {
                background-color: #e53935;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTreeWidget, QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
        """)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 标题
        title_label = QLabel("📁 项目管理中心")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title_label.setStyleSheet("color: #1976d2; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 搜索项目/分组:")
        search_label.setFixedWidth(120)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词快速查找项目或分组...")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.setStyleSheet("padding: 10px; font-size: 14px;")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # 分组树 + 项目列表（左右布局）
        content_splitter = QSplitter(Qt.Horizontal)

        # 左侧：分组树
        group_widget = QWidget()
        group_layout = QVBoxLayout(group_widget)
        group_layout.addWidget(QLabel("📂 项目分组结构:"))
        self.group_tree = QTreeWidget()
        self.group_tree.setHeaderHidden(True)
        self.group_tree.setColumnCount(1)
        self.group_tree.itemClicked.connect(self.on_group_selected)
        self.group_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f5f5f5;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        group_layout.addWidget(self.group_tree)
        content_splitter.addWidget(group_widget)
        content_splitter.setStretchFactor(0, 1)

        # 右侧：项目列表
        project_widget = QWidget()
        project_layout = QVBoxLayout(project_widget)
        project_layout.addWidget(QLabel("📌 项目列表:"))

        # 项目表格
        self.project_table = QTableWidget()
        self.project_table.setColumnCount(5)
        self.project_table.setHorizontalHeaderLabels(["ID", "图标", "项目名称", "所属分组", "常用"])
        self.project_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.project_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.project_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.project_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.project_table.setColumnWidth(1, 50)
        self.project_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.project_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.project_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f5f5f5;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        project_layout.addWidget(self.project_table)

        # 按钮区域
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ 新增项目")
        self.add_btn.setMinimumHeight(35)
        self.edit_btn = QPushButton("✏️ 编辑项目")
        self.edit_btn.setMinimumHeight(35)
        self.delete_btn = QPushButton("🗑️ 删除项目")
        self.delete_btn.setObjectName("deleteBtn")
        self.delete_btn.setMinimumHeight(35)
        self.close_btn = QPushButton("✅ 完成")
        self.close_btn.setMinimumHeight(35)
        self.close_btn.setStyleSheet("background-color: #4CAF50;")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)

        project_layout.addLayout(btn_layout)
        content_splitter.addWidget(project_widget)
        content_splitter.setStretchFactor(1, 2)

        main_layout.addWidget(content_splitter)
        self.setLayout(main_layout)

        # 连接信号
        self.add_btn.clicked.connect(self.add_project)
        self.edit_btn.clicked.connect(self.edit_project)
        self.delete_btn.clicked.connect(self.delete_project)
        self.close_btn.clicked.connect(self.accept)

        # 初始禁用按钮
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.project_table.itemSelectionChanged.connect(self.on_project_selected)

    def load_data(self):
        """加载分组树和项目列表"""
        self.load_groups()
        self.load_projects()

    def load_groups(self):
        """加载分组树"""
        self.group_tree.clear()
        groups = self.db.get_groups_tree()

        def add_to_tree(parent_item, items):
            for item in items:
                tree_item = QTreeWidgetItem([f"{item['icon']} {item['name']}"])
                tree_item.setData(0, Qt.UserRole, item['id'])
                if parent_item:
                    parent_item.addChild(tree_item)
                else:
                    self.group_tree.addTopLevelItem(tree_item)
                if item['children']:
                    add_to_tree(tree_item, item['children'])

        add_to_tree(None, groups)
        self.group_tree.expandAll()

    def load_projects(self, group_id=None, search_text=""):
        """加载项目列表（支持过滤）"""
        self.project_table.setRowCount(0)
        projects = self.db.get_projects(group_id, search_text)

        for row_idx, (pid, name, icon, is_common, usage, group_name) in enumerate(projects):
            self.project_table.insertRow(row_idx)

            # ID列
            id_item = QTableWidgetItem(str(pid))
            id_item.setData(Qt.UserRole, pid)
            self.project_table.setItem(row_idx, 0, id_item)

            # 图标列
            icon_item = QTableWidgetItem(icon)
            icon_item.setFont(QFont("Segoe UI Emoji", 14))
            icon_item.setTextAlignment(Qt.AlignCenter)
            self.project_table.setItem(row_idx, 1, icon_item)

            # 名称列
            name_item = QTableWidgetItem(name)
            name_item.setFont(QFont("Microsoft YaHei", 11))
            self.project_table.setItem(row_idx, 2, name_item)

            # 分组列
            group_item = QTableWidgetItem(group_name or "未分组")
            self.project_table.setItem(row_idx, 3, group_item)

            # 常用列
            common_item = QTableWidgetItem("⭐" if is_common else "")
            common_item.setTextAlignment(Qt.AlignCenter)
            common_item.setForeground(QColor("#FFD700") if is_common else QColor("#ccc"))
            self.project_table.setItem(row_idx, 4, common_item)

        # 设置表格样式
        self.project_table.resizeRowsToContents()

    def on_group_selected(self, item):
        """分组选择事件"""
        group_id = item.data(0, Qt.UserRole)
        self.load_projects(group_id=group_id, search_text=self.search_input.text())

    def on_search_changed(self, text):
        """搜索框变化事件"""
        current_group = None
        selected = self.group_tree.currentItem()
        if selected:
            current_group = selected.data(0, Qt.UserRole)
        self.load_projects(group_id=current_group, search_text=text)

    def on_project_selected(self):
        """项目选择变化"""
        has_selection = len(self.project_table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    def add_project(self):
        """新增项目"""
        dialog = ProjectEditDialog(self.db, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_projects()
            QMessageBox.information(self, "✅ 成功", "项目添加成功！")

    def edit_project(self):
        """编辑项目"""
        row = self.project_table.currentRow()
        if row < 0:
            return
        project_id = int(self.project_table.item(row, 0).text())
        dialog = ProjectEditDialog(self.db, project_id, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_projects()
            QMessageBox.information(self, "✅ 成功", "项目更新成功！")

    def delete_project(self):
        """删除项目"""
        row = self.project_table.currentRow()
        if row < 0:
            return
        project_id = int(self.project_table.item(row, 0).text())
        project_name = self.project_table.item(row, 2).text()

        reply = QMessageBox.question(
            self, "⚠️ 确认删除",
            f"确定要删除项目「{project_name}」？\n\n注意：\n• 已关联的日报将保留，但项目显示为'已删除'\n• 此操作不可恢复",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.db.delete_project(project_id):
                self.load_projects()
                QMessageBox.information(self, "✅ 成功", "项目已删除！")
            else:
                QMessageBox.warning(self, "❌ 失败", "该项目已被日报引用，无法删除！\n请先处理关联的日报记录。")


class ProjectEditDialog(QDialog):
    """项目编辑对话框"""

    def __init__(self, db, project_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.project_id = project_id
        self.setWindowTitle("✏️ 编辑项目" if project_id else "➕ 新增项目")
        self.setModal(True)
        self.setup_ui()
        if project_id:
            self.load_project_data()

    def setup_ui(self):
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 项目名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入项目名称（必填）")
        self.name_input.setStyleSheet("padding: 10px; font-size: 14px;")
        layout.addRow("📌 项目名称:", self.name_input)

        # 分组选择
        self.group_combo = QComboBox()
        self.load_groups()
        self.group_combo.setStyleSheet("padding: 8px; font-size: 14px;")
        layout.addRow("📂 所属分组:", self.group_combo)

        # 图标选择
        icon_layout = QHBoxLayout()
        self.icon_input = QLineEdit("📌")
        self.icon_input.setFixedWidth(60)
        self.icon_input.setFont(QFont("Segoe UI Emoji", 16))
        self.icon_input.setStyleSheet("padding: 5px; text-align: center; font-size: 16px;")
        self.icon_btn = QPushButton("🎨 选择图标")
        self.icon_btn.clicked.connect(self.select_icon)
        icon_layout.addWidget(self.icon_input)
        icon_layout.addWidget(self.icon_btn)
        icon_layout.addStretch()
        layout.addRow("🎨 项目图标:", icon_layout)

        # 常用项目
        self.common_check = QCheckBox("设为常用项目（在日报中优先显示）")
        self.common_check.setStyleSheet("font-size: 14px;")
        layout.addRow("", self.common_check)

        # 按钮
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setStyleSheet("background-color: #4CAF50; font-size: 14px; font-weight: bold;")
        self.cancel_btn = QPushButton("❌ 取消")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.setStyleSheet("background-color: #f44336; font-size: 14px;")

        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow("", btn_layout)

        self.setLayout(layout)
        self.setMinimumWidth(450)

        # 连接信号
        self.save_btn.clicked.connect(self.save_project)
        self.cancel_btn.clicked.connect(self.reject)

    def load_groups(self):
        """加载分组到下拉框"""
        self.group_combo.addItem("未分组", None)
        groups = self.db.get_groups_tree()

        def add_to_combo(items, prefix=""):
            for item in items:
                self.group_combo.addItem(f"{prefix}{item['icon']} {item['name']}", item['id'])
                if item['children']:
                    add_to_combo(item['children'], prefix + "  ")

        add_to_combo(groups)

    def load_project_data(self):
        """加载项目数据（编辑模式）"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, group_id, icon, is_common FROM projects WHERE id = ?", (self.project_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            name, group_id, icon, is_common = result
            self.name_input.setText(name)
            # 设置分组
            for i in range(self.group_combo.count()):
                if self.group_combo.itemData(i) == group_id:
                    self.group_combo.setCurrentIndex(i)
                    break
            self.icon_input.setText(icon)
            self.common_check.setChecked(bool(is_common))

    def select_icon(self):
        """emoji图标选择器"""
        icons = [
            "📌", "🚀", "🛠️", "📝", "🐞", "📊", "💡", "🎯", "🔧", "⚙️",
            "💻", "📱", "🌐", "🔒", "👥", "🎨", "📚", "🔬", "🌱", "🚀"
        ]
        dialog = QDialog(self)
        dialog.setWindowTitle("🎨 选择项目图标")
        dialog.setModal(True)
        layout = QGridLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)

        for i, icon in enumerate(icons):
            btn = QPushButton(icon)
            btn.setFont(QFont("Segoe UI Emoji", 18))
            btn.setFixedSize(50, 50)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    background-color: white;
                }
                QPushButton:hover {
                    background-color: #e3f2fd;
                    border-color: #2196F3;
                }
            """)
            btn.clicked.connect(lambda _, ic=icon: self.set_icon(ic, dialog))
            layout.addWidget(btn, i // 5, i % 5)

        dialog.setLayout(layout)
        dialog.exec()

    def set_icon(self, icon, dialog):
        self.icon_input.setText(icon)
        dialog.accept()

    def save_project(self):
        """保存项目"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "⚠️ 验证失败", "项目名称不能为空！")
            return

        group_id = self.group_combo.currentData()
        icon = self.icon_input.text()
        is_common = self.common_check.isChecked()

        if self.project_id:
            self.db.update_project(self.project_id, name, group_id, icon, is_common)
        else:
            if not self.db.add_project(name, group_id, icon, is_common):
                QMessageBox.warning(self, "❌ 失败", f"项目名称 '{name}' 已存在！")
                return

        self.accept()