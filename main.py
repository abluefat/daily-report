# main.py - 完整增强版日报系统
import sys
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QDateEdit, QTextEdit, QDoubleSpinBox, QComboBox, QPushButton,
    QMessageBox, QLineEdit, QListWidget, QListWidgetItem, QDialog,
    QFormLayout, QCheckBox, QGridLayout, QDialogButtonBox, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QIcon
from database import Database
from ProjectDialog import ProjectDialog


class DailyReportApp(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.selected_project_id = None
        self.init_ui()
        self.load_common_projects()

    def init_ui(self):
        self.setWindowTitle("📅 智能日报系统 v2.0")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QWidget {
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                background-color: #4CAF50;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton#cancelBtn {
                background-color: #f44336;
            }
            QPushButton#cancelBtn:hover {
                background-color: #e53935;
            }
            QPushButton#manageBtn {
                background-color: #2196F3;
            }
            QPushButton#manageBtn:hover {
                background-color: #1e88e5;
            }
            QLineEdit, QTextEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #4CAF50;
                box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("📝 新增工作日报")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_label.setStyleSheet("color: #1976d2; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 日期选择
        date_layout = QHBoxLayout()
        date_label = QLabel("🗓️ 日期:")
        date_label.setFixedWidth(80)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(datetime.now().date())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit, 1)
        main_layout.addLayout(date_layout)

        # 项目选择（增强版）
        project_layout = QVBoxLayout()
        project_label = QLabel("📌 项目选择:")
        project_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))

        # 智能搜索框
        self.project_search = QLineEdit()
        self.project_search.setPlaceholderText("🔍 搜索项目（输入关键词）...")
        self.project_search.textChanged.connect(self.filter_projects)
        self.project_search.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #e0e0e0;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)

        # 项目列表
        self.project_list = QListWidget()
        self.project_list.setIconSize(QSize(24, 24))
        self.project_list.itemClicked.connect(self.select_project)
        self.project_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f5f5f5;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                font-weight: bold;
            }
            QListWidget::item:hover {
                background-color: #f9f9f9;
            }
        """)

        # 按钮区域
        btn_layout = QHBoxLayout()
        self.manage_btn = QPushButton("📁 项目管理")
        self.manage_btn.setObjectName("manageBtn")
        self.manage_btn.clicked.connect(self.open_project_manager)
        self.clear_btn = QPushButton("↺ 清除选择")
        self.clear_btn.clicked.connect(self.clear_project_selection)
        btn_layout.addWidget(self.manage_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.clear_btn)

        project_layout.addWidget(project_label)
        project_layout.addWidget(self.project_search)
        project_layout.addWidget(self.project_list)
        project_layout.addLayout(btn_layout)
        main_layout.addLayout(project_layout)

        # 任务内容
        task_layout = QHBoxLayout()
        task_label = QLabel("✏️ 任务内容:")
        task_label.setFixedWidth(80)
        self.task_text = QTextEdit()
        self.task_text.setPlaceholderText("请输入详细任务内容（必填）...")
        self.task_text.setMinimumHeight(100)
        task_layout.addWidget(task_label)
        task_layout.addWidget(self.task_text, 1)
        main_layout.addLayout(task_layout)

        # 耗时和状态
        hour_status_layout = QHBoxLayout()

        hour_label = QLabel("⏱️ 耗时(小时):")
        hour_label.setFixedWidth(100)
        self.hour_spin = QDoubleSpinBox()
        self.hour_spin.setRange(0.5, 24)
        self.hour_spin.setSingleStep(0.5)
        self.hour_spin.setValue(1.0)
        self.hour_spin.setFixedWidth(100)

        status_label = QLabel("📊 状态:")
        status_label.setFixedWidth(60)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["已完成", "进行中", "已延期", "待确认", "已取消"])
        self.status_combo.setCurrentText("进行中")

        hour_status_layout.addWidget(hour_label)
        hour_status_layout.addWidget(self.hour_spin)
        hour_status_layout.addSpacing(20)
        hour_status_layout.addWidget(status_label)
        hour_status_layout.addWidget(self.status_combo)
        hour_status_layout.addStretch()
        main_layout.addLayout(hour_status_layout)

        # 备注
        note_layout = QHBoxLayout()
        note_label = QLabel("💬 备注:")
        note_label.setFixedWidth(80)
        self.note_text = QTextEdit()
        self.note_text.setPlaceholderText("可选：补充说明、遇到的问题等...")
        self.note_text.setMaximumHeight(80)
        note_layout.addWidget(note_label)
        note_layout.addWidget(self.note_text, 1)
        main_layout.addLayout(note_layout)

        # 按钮区域
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 保存日报")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        self.save_btn.clicked.connect(self.save_report)

        self.cancel_btn = QPushButton("❌ 取消")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.clicked.connect(self.close)

        button_layout.addStretch()
        button_layout.addWidget(self.save_btn, 1)
        button_layout.addWidget(self.cancel_btn, 1)
        main_layout.addLayout(button_layout)

        # 底部提示
        footer_label = QLabel("💡 提示：常用项目会根据使用频率智能推荐 | 项目管理中可设置常用项目")
        footer_label.setStyleSheet("color: #666; font-size: 12px; margin-top: 10px;")
        footer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer_label)

        self.setLayout(main_layout)

    def load_common_projects(self):
        """加载常用项目（智能推荐）"""
        self.project_list.clear()

        # 添加标题
        title_item = QListWidgetItem("⭐ 常用项目（根据使用频率智能推荐）")
        title_item.setForeground(QColor("#1976d2"))
        title_item.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        title_item.setFlags(Qt.NoItemFlags)
        title_item.setBackground(QColor("#e3f2fd"))
        title_item.setSizeHint(QSize(0, 30))
        self.project_list.addItem(title_item)

        # 获取常用项目
        projects = self.db.get_common_projects(limit=8)

        if not projects:
            empty_item = QListWidgetItem("📭 暂无常用项目，添加项目后会自动推荐")
            empty_item.setForeground(QColor("#999"))
            empty_item.setFlags(Qt.NoItemFlags)
            self.project_list.addItem(empty_item)
        else:
            for pid, name, icon in projects:
                item = QListWidgetItem(f"  {icon}  {name}")
                item.setData(Qt.UserRole, pid)
                item.setToolTip(f"项目ID: {pid}\n点击选择此项目")
                item.setFont(QFont("Microsoft YaHei", 11))
                self.project_list.addItem(item)

        # 添加分隔线
        sep = QListWidgetItem("─" * 50)
        sep.setFlags(Qt.NoItemFlags)
        sep.setForeground(QColor("#e0e0e0"))
        sep.setSizeHint(QSize(0, 10))
        self.project_list.addItem(sep)

        # 添加提示
        hint_item = QListWidgetItem("💡 在搜索框输入关键词查找更多项目 | 点击「📁 项目管理」添加新项目")
        hint_item.setForeground(QColor("#666"))
        hint_item.setFont(QFont("Microsoft YaHei", 9))
        hint_item.setFlags(Qt.NoItemFlags)
        hint_item.setSizeHint(QSize(0, 25))
        self.project_list.addItem(hint_item)

    def filter_projects(self, text):
        """实时搜索项目"""
        if not text.strip():
            self.load_common_projects()
            return

        self.project_list.clear()

        # 添加搜索标题
        title_item = QListWidgetItem(f"🔍 搜索结果：'{text}'")
        title_item.setForeground(QColor("#d32f2f"))
        title_item.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        title_item.setFlags(Qt.NoItemFlags)
        title_item.setBackground(QColor("#ffebee"))
        title_item.setSizeHint(QSize(0, 30))
        self.project_list.addItem(title_item)

        # 获取搜索结果
        projects = self.db.get_projects(search_text=text)

        if not projects:
            empty_item = QListWidgetItem("📭 未找到匹配的项目")
            empty_item.setForeground(QColor("#999"))
            empty_item.setFlags(Qt.NoItemFlags)
            self.project_list.addItem(empty_item)
        else:
            for pid, name, icon, _, _, group_name in projects:
                display_text = f"  {icon}  {name}"
                if group_name:
                    display_text += f"  <{group_name}>"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, pid)
                item.setToolTip(f"分组: {group_name or '未分组'}\nID: {pid}")
                item.setFont(QFont("Microsoft YaHei", 11))
                self.project_list.addItem(item)

    def select_project(self, item):
        """选择项目"""
        project_id = item.data(Qt.UserRole)
        if project_id:
            self.selected_project_id = project_id
            # 增加使用计数（用于智能推荐）
            self.db.increment_usage(project_id)
            # 高亮显示选中项
            for i in range(self.project_list.count()):
                self.project_list.item(i).setBackground(QColor("white"))
            item.setBackground(QColor("#c8e6c9"))
            item.setForeground(QColor("#1b5e20"))

    def clear_project_selection(self):
        """清除项目选择"""
        self.selected_project_id = None
        self.project_search.clear()
        self.load_common_projects()
        QMessageBox.information(self, "提示", "已清除项目选择")

    def open_project_manager(self):
        """打开项目管理对话框"""
        dialog = ProjectDialog(self.db, self)
        if dialog.exec() == QDialog.Accepted:
            # 重新加载项目
            current_text = self.project_search.text()
            if current_text:
                self.filter_projects(current_text)
            else:
                self.load_common_projects()

    def save_report(self):
        """保存日报"""
        # 获取数据
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        task_content = self.task_text.toPlainText().strip()
        hours = self.hour_spin.value()
        status = self.status_combo.currentText()
        notes = self.note_text.toPlainText().strip()

        # 验证必填项
        if not task_content:
            QMessageBox.warning(self, "⚠️ 验证失败", "任务内容不能为空！")
            return

        if not self.selected_project_id:
            reply = QMessageBox.question(
                self, "❓ 项目未选择",
                "未选择项目，是否继续保存到「其他」类别？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # 保存到数据库
        try:
            conn = sqlite3.connect("projects.db")
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO daily_reports (date, project_id, task_content, hours, status, notes)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ''', (date_str, self.selected_project_id, task_content, hours, status, notes))
            conn.commit()
            conn.close()

            # 重置表单（保留日期为今天）
            self.task_text.clear()
            self.note_text.clear()
            self.hour_spin.setValue(1.0)
            self.status_combo.setCurrentText("进行中")
            self.clear_project_selection()

            QMessageBox.information(
                self, "✅ 保存成功",
                f"日报已保存！\n日期：{date_str}\n项目：{self.db.get_project_by_id(self.selected_project_id) if self.selected_project_id else '其他'}\n耗时：{hours}小时"
            )

        except Exception as e:
            QMessageBox.critical(self, "❌ 保存失败", f"发生错误：{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用属性
    app.setApplicationName("智能日报系统")
    app.setOrganizationName("DailyReport")

    # 创建并显示窗口
    window = DailyReportApp()
    window.show()

    sys.exit(app.exec())