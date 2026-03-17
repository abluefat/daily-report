# main.py - 智能日报系统 v2.1 (含历史记录+导出)
import csv
import os
import sqlite3
import sys
from datetime import datetime

from PySide6.QtCore import Qt, QSize, QDate
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QDateEdit, QTextEdit, QDoubleSpinBox, QComboBox, QPushButton,
    QMessageBox, QLineEdit, QListWidget, QListWidgetItem, QDialog,
    QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QTabWidget, QFileDialog, QGroupBox,
    QStatusBar
)

from ProjectDialog import ProjectDialog
from database import Database


class DailyReportApp(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.selected_project_id = None
        self.init_ui()
        self.load_common_projects()
        self.load_history_reports()  # 初始化加载历史记录

    def init_ui(self):
        self.setWindowTitle("智能日报系统")
        self.setGeometry(100, 100, 1000, 700)

        # 居中窗口
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        self.setStyleSheet("""
            QWidget {
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #e9ecef;
                color: #495057;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
                color: white;
                font-weight: bold;
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
                font-weight: bold;
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
            QPushButton#exportBtn {
                background-color: #9C27B0;
                padding: 10px 20px;
                font-size: 15px;
            }
            QPushButton#exportBtn:hover {
                background-color: #7B1FA2;
            }
            QPushButton#refreshBtn {
                background-color: #FF9800;
            }
            QPushButton#refreshBtn:hover {
                background-color: #F57C00;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #4CAF50;
                box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
            }
            QTableWidget {
                background-color: white;
                gridline-color: #eee;
                border-radius: 4px;
            }
            QTableWidget::item:selected {
                background-color: #e8f5e9;
                color: #1b5e20;
            }
            QGroupBox {
                font-weight: bold;
                color: #1976d2;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QStatusBar {
                background-color: #f1f8e9;
                color: #33691e;
                font-weight: bold;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 创建标签页
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Microsoft YaHei", 11))

        # ============ 标签页1：新增日报 ============
        self.new_report_tab = self.create_new_report_tab()
        self.tabs.addTab(self.new_report_tab, "📝 新增日报")

        # ============ 标签页2：历史日报 ============
        self.history_tab = self.create_history_tab()
        self.tabs.addTab(self.history_tab, "📚 历史记录")

        main_layout.addWidget(self.tabs)

        # 状态栏
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("✅ 系统就绪 | 智能推荐已启用 | 数据自动保存")
        self.status_bar.setStyleSheet("QStatusBar::item {border: none;}")
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)

    # ========== 新增日报标签页 ==========
    def create_new_report_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 20, 25, 20)

        # 标题
        title_label = QLabel("✨ 快速创建今日工作日报")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title_label.setStyleSheet("color: #1976d2; margin-bottom: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        subtitle = QLabel("选择项目 → 填写任务 → 保存完成（支持常用项目智能推荐）")
        subtitle.setStyleSheet("color: #6c757d; font-size: 13px; margin-bottom: 15px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # 日期选择
        date_layout = QHBoxLayout()
        date_label = QLabel("🗓️ 日期:")
        date_label.setFixedWidth(80)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setStyleSheet("padding: 10px; font-size: 15px;")
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit, 1)
        layout.addLayout(date_layout)

        # 项目选择（增强版）
        project_layout = QVBoxLayout()
        project_label = QLabel("📌 项目选择:")
        project_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))

        # 智能搜索框
        self.project_search = QLineEdit()
        self.project_search.setPlaceholderText("🔍 搜索项目（输入关键词）...")
        self.project_search.textChanged.connect(self.filter_projects)
        self.project_search.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                border-width: 2px;
            }
        """)

        # 项目列表
        self.project_list = QListWidget()
        self.project_list.setIconSize(QSize(28, 28))
        self.project_list.itemClicked.connect(self.select_project)
        self.project_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 15px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 12px 10px;
                border-bottom: 1px solid #f5f5f5;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                font-weight: bold;
                border-left: 3px solid #2196F3;
            }
            QListWidget::item:hover {
                background-color: #f9f9f9;
            }
        """)

        # 按钮区域
        btn_layout = QHBoxLayout()
        self.manage_btn = QPushButton("📁 项目管理")
        self.manage_btn.setObjectName("manageBtn")
        self.manage_btn.setMinimumHeight(40)
        self.manage_btn.clicked.connect(self.open_project_manager)
        self.clear_btn = QPushButton("↺ 清除选择")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self.clear_project_selection)
        btn_layout.addWidget(self.manage_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.clear_btn)

        project_layout.addWidget(project_label)
        project_layout.addWidget(self.project_search)
        project_layout.addWidget(self.project_list, 1)
        project_layout.addLayout(btn_layout)
        layout.addLayout(project_layout)

        # 任务内容
        task_layout = QHBoxLayout()
        task_label = QLabel("✏️ 任务内容:")
        task_label.setFixedWidth(100)
        self.task_text = QTextEdit()
        self.task_text.setPlaceholderText("请输入详细任务内容（必填）...\n• 建议分点描述\n• 包含关键成果/进展")
        self.task_text.setMinimumHeight(120)
        self.task_text.setStyleSheet("font-size: 15px; padding: 10px;")
        task_layout.addWidget(task_label)
        task_layout.addWidget(self.task_text, 1)
        layout.addLayout(task_layout)

        # 耗时和状态
        hour_status_layout = QHBoxLayout()

        hour_label = QLabel("⏱️ 耗时(小时):")
        hour_label.setFixedWidth(110)
        self.hour_spin = QDoubleSpinBox()
        self.hour_spin.setRange(0.5, 24)
        self.hour_spin.setSingleStep(0.5)
        self.hour_spin.setValue(8.0)
        self.hour_spin.setFixedWidth(120)
        self.hour_spin.setStyleSheet("font-size: 15px; padding: 5px;")

        status_label = QLabel("📊 状态:")
        status_label.setFixedWidth(70)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["已完成", "进行中", "已延期", "待确认", "已取消"])
        self.status_combo.setCurrentText("进行中")
        self.status_combo.setFixedWidth(150)
        self.status_combo.setStyleSheet("font-size: 15px; padding: 5px;")

        hour_status_layout.addWidget(hour_label)
        hour_status_layout.addWidget(self.hour_spin)
        hour_status_layout.addSpacing(30)
        hour_status_layout.addWidget(status_label)
        hour_status_layout.addWidget(self.status_combo)
        hour_status_layout.addStretch()
        layout.addLayout(hour_status_layout)

        # 备注
        note_layout = QHBoxLayout()
        note_label = QLabel("💬 备注:")
        note_label.setFixedWidth(100)
        self.note_text = QTextEdit()
        self.note_text.setPlaceholderText("可选：补充说明、遇到的问题、明日计划等...")
        self.note_text.setMaximumHeight(90)
        self.note_text.setStyleSheet("font-size: 14px; padding: 8px;")
        note_layout.addWidget(note_label)
        note_layout.addWidget(self.note_text, 1)
        layout.addLayout(note_layout)

        # 按钮区域
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 保存日报")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.save_btn.setStyleSheet("background-color: #43A047; font-size: 16px;")
        self.save_btn.clicked.connect(self.save_report)

        self.cancel_btn = QPushButton("❌ 取消")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setFont(QFont("Microsoft YaHei", 12))
        self.cancel_btn.clicked.connect(lambda: self.clear_form())

        button_layout.addStretch()
        button_layout.addWidget(self.save_btn, 1)
        button_layout.addWidget(self.cancel_btn, 1)
        layout.addLayout(button_layout)

        # 底部提示
        footer_label = QLabel(
            "💡 提示：常用项目会根据使用频率智能推荐 | 项目管理中可设置常用项目 | 所有数据本地存储安全可靠")
        footer_label.setStyleSheet(
            "color: #546e7a; font-size: 12px; margin-top: 8px; padding: 8px; background-color: #e8f5e9; border-radius: 4px;")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setWordWrap(True)
        layout.addWidget(footer_label)

        widget.setLayout(layout)
        return widget

    # ========== 历史日报标签页 ==========
    def create_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 15, 20, 15)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("📊 历史工作日报记录")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title_label.setStyleSheet("color: #1565C0;")
        title_label.setAlignment(Qt.AlignLeft)
        title_layout.addWidget(title_label)

        # 导出按钮（右侧）
        self.export_btn = QPushButton("📤 导出为CSV")
        self.export_btn.setObjectName("exportBtn")
        self.export_btn.setMinimumHeight(45)
        self.export_btn.setIcon(QIcon.fromTheme("document-save"))
        self.export_btn.clicked.connect(self.export_reports)
        title_layout.addStretch()
        title_layout.addWidget(self.export_btn)
        layout.addLayout(title_layout)

        # 筛选区域
        filter_group = QGroupBox("🔍 筛选条件")
        filter_layout = QGridLayout()
        filter_layout.setSpacing(15)

        # 日期范围
        date_label = QLabel("日期范围:")
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setCalendarPopup(True)
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setCalendarPopup(True)

        # 项目筛选
        project_filter_label = QLabel("项目:")
        self.project_filter_combo = QComboBox()
        self.project_filter_combo.addItem("🔄 全部项目", -2)  # -2: 全部
        self.project_filter_combo.addItem("📎 其他（未指定）", -1)  # -1: 未指定项目
        # 加载项目列表
        self.load_project_filter_combo()
        self.project_filter_combo.currentIndexChanged.connect(self.on_filter_changed)

        # 状态筛选
        status_label = QLabel("状态:")
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItem("🔄 全部状态", "")
        self.status_filter_combo.addItems(["已完成", "进行中", "已延期", "待确认", "已取消"])
        self.status_filter_combo.currentIndexChanged.connect(self.on_filter_changed)

        # 搜索框
        search_label = QLabel("关键词:")
        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText("搜索任务内容或备注...")
        self.history_search.textChanged.connect(self.on_search_changed)
        self.history_search.setStyleSheet("padding: 8px; font-size: 14px;")

        # 刷新按钮
        self.refresh_btn = QPushButton("🔄 刷新列表")
        self.refresh_btn.setObjectName("refreshBtn")
        self.refresh_btn.setMinimumHeight(35)
        self.refresh_btn.clicked.connect(self.load_history_reports)

        # 添加到网格
        filter_layout.addWidget(date_label, 0, 0)
        filter_layout.addWidget(self.start_date, 0, 1)
        filter_layout.addWidget(QLabel("至"), 0, 2)
        filter_layout.addWidget(self.end_date, 0, 3)
        filter_layout.addWidget(project_filter_label, 1, 0)
        filter_layout.addWidget(self.project_filter_combo, 1, 1, 1, 3)
        filter_layout.addWidget(status_label, 2, 0)
        filter_layout.addWidget(self.status_filter_combo, 2, 1, 1, 3)
        filter_layout.addWidget(search_label, 3, 0)
        filter_layout.addWidget(self.history_search, 3, 1, 1, 2)
        filter_layout.addWidget(self.refresh_btn, 3, 3)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # 历史记录表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "日期", "项目", "任务内容", "耗时(小时)", "状态", "备注", "创建时间"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.history_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
                gridline-color: #eee;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #1976d2;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #4CAF50;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e8f5e9;
                color: #1b5e20;
            }
        """)
        self.history_table.doubleClicked.connect(self.view_report_detail)
        layout.addWidget(self.history_table, 1)

        # 底部状态
        self.record_count_label = QLabel("📌 共 0 条记录 | 双击查看详情")
        self.record_count_label.setStyleSheet("font-weight: bold; color: #1976d2; padding: 5px;")
        layout.addWidget(self.record_count_label)

        widget.setLayout(layout)
        return widget

    # ========== 历史记录相关方法 ==========
    def load_project_filter_combo(self):
        """加载项目筛选下拉框"""
        # 清除除前两项外的所有项目
        while self.project_filter_combo.count() > 2:
            self.project_filter_combo.removeItem(2)

        projects = self.db.get_all_projects_for_combo()
        for pid, name, icon, group_name in projects:
            display_text = f"{icon} {name}"
            if group_name:
                display_text += f" ({group_name})"
            self.project_filter_combo.addItem(display_text, pid)

    def on_filter_changed(self):
        """筛选条件变化时刷新列表"""
        self.load_history_reports()

    def on_search_changed(self, text):
        """搜索框变化（防抖处理）"""
        # 简单实现：直接刷新（实际项目可加 QTimer 防抖）
        self.load_history_reports()

    def load_history_reports(self):
        """加载历史日报记录"""
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        project_id = self.project_filter_combo.currentData()
        status = self.status_filter_combo.currentData()
        keyword = self.history_search.text().strip()

        # 处理特殊项目ID
        if project_id == -2:  # 全部项目
            project_id = None
        elif project_id == -1:  # 未指定项目
            project_id = "IS_NULL"

        reports = self.db.get_reports(
            start_date=start,
            end_date=end,
            project_id=project_id,
            status=status,
            keyword=keyword
        )

        # 清空表格
        self.history_table.setRowCount(0)

        # 填充数据
        for row_idx, report in enumerate(reports):
            self.history_table.insertRow(row_idx)

            # ID
            id_item = QTableWidgetItem(str(report[0]))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row_idx, 0, id_item)

            # 日期
            date_item = QTableWidgetItem(report[1])
            date_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row_idx, 1, date_item)

            # 项目（处理NULL）
            project_display = report[6] if report[6] else "📎 其他"
            project_icon = report[7] if report[7] else "📎"
            project_item = QTableWidgetItem(f"{project_icon} {project_display}")
            self.history_table.setItem(row_idx, 2, project_item)

            # 任务内容
            task_item = QTableWidgetItem(report[2])
            task_item.setToolTip(report[2])
            self.history_table.setItem(row_idx, 3, task_item)

            # 耗时
            hour_item = QTableWidgetItem(f"{report[3]:.1f}")
            hour_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row_idx, 4, hour_item)

            # 状态（带颜色）
            status_item = QTableWidgetItem(report[4])
            status_item.setTextAlignment(Qt.AlignCenter)
            # 状态颜色映射
            status_colors = {
                "已完成": "#2E7D32",
                "进行中": "#1565C0",
                "已延期": "#C62828",
                "待确认": "#5D4037",
                "已取消": "#757575"
            }
            if report[4] in status_colors:
                status_item.setForeground(QColor(status_colors[report[4]]))
                status_item.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
            self.history_table.setItem(row_idx, 5, status_item)

            # 备注
            note_item = QTableWidgetItem(report[5] if report[5] else "-")
            note_item.setToolTip(report[5] if report[5] else "")
            self.history_table.setItem(row_idx, 6, note_item)

            # 创建时间（简化显示）
            created_time = report[8].split()[1] if report[8] else ""
            time_item = QTableWidgetItem(created_time)
            time_item.setTextAlignment(Qt.AlignCenter)
            time_item.setForeground(QColor("#6c757d"))
            self.history_table.setItem(row_idx, 7, time_item)

        # 更新记录数
        count = len(reports)
        self.record_count_label.setText(f"📌 共 {count} 条记录 | 双击表格行查看详情")

        # 调整行高
        self.history_table.resizeRowsToContents()
        self.status_bar.showMessage(f"✅ 已加载 {count} 条日报记录 | 筛选范围: {start} 至 {end}", 3000)

    def view_report_detail(self, index):
        """双击查看详情"""
        row = index.row()
        report_id = int(self.history_table.item(row, 0).text())
        date = self.history_table.item(row, 1).text()
        project = self.history_table.item(row, 2).text().replace("📎 ", "")
        task = self.history_table.item(row, 3).text()
        hours = self.history_table.item(row, 4).text()
        status = self.history_table.item(row, 5).text()
        notes = self.history_table.item(row, 6).text() if self.history_table.item(row, 6).text() != "-" else ""

        detail_text = f"""
            📅 日期: {date}
            📌 项目: {project}
            ✏️ 任务内容:
            {task}
            
            ⏱️ 耗时: {hours} 小时
            📊 状态: {status}
            💬 备注:
            {notes if notes else '无'}
        """.strip()

        QMessageBox.information(
            self,
            f"📋 日报详情 (ID: {report_id})",
            detail_text
        )

    def export_reports(self):
        """导出日报为CSV"""
        if self.history_table.rowCount() == 0:
            QMessageBox.warning(self, "⚠️ 导出提示", "当前无数据可导出！\n请先筛选或刷新数据。")
            return

        # 获取当前筛选的数据
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        project_id = self.project_filter_combo.currentData()
        status = self.status_filter_combo.currentData()
        keyword = self.history_search.text().strip()

        if project_id == -2:
            project_id = None
        elif project_id == -1:
            project_id = "IS_NULL"

        reports = self.db.get_reports(
            start_date=start,
            end_date=end,
            project_id=project_id,
            status=status,
            keyword=keyword
        )

        if not reports:
            QMessageBox.warning(self, "⚠️ 导出提示", "筛选条件下无数据可导出！")
            return

        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "📤 保存日报数据",
            f"工作日报_{start}_至_{end}.csv",
            "CSV Files (*.csv);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # 确保文件扩展名
            if not file_path.endswith('.csv'):
                file_path += '.csv'

            # 写入CSV（UTF-8-BOM 避免Excel乱码）
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                # 写入标题
                writer.writerow([
                    "ID", "日期", "项目", "任务内容", "耗时(小时)",
                    "状态", "备注", "创建时间"
                ])
                # 写入数据
                for report in reports:
                    writer.writerow([
                        report[0],  # ID
                        report[1],  # 日期
                        report[6] if report[6] else "其他",  # 项目名
                        report[2],  # 任务内容
                        f"{report[3]:.1f}",  # 耗时
                        report[4],  # 状态
                        report[5] if report[5] else "",  # 备注
                        report[8]  # 创建时间
                    ])

            # 成功提示
            file_size = os.path.getsize(file_path) / 1024  # KB
            QMessageBox.information(
                self,
                "✅ 导出成功",
                f"日报数据已成功导出！\n\n"
                f"📁 保存路径: {file_path}\n"
                f"📊 记录数量: {len(reports)} 条\n"
                f"💾 文件大小: {file_size:.1f} KB\n\n"
                f"💡 提示: 用Excel/WPS打开可自动识别中文"
            )
            self.status_bar.showMessage(f"📤 导出成功: {os.path.basename(file_path)} | {len(reports)}条记录", 5000)

        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ 导出失败",
                f"导出过程中发生错误:\n{str(e)}\n\n"
                f"请检查:\n• 文件是否被占用\n• 磁盘空间是否充足\n• 是否有写入权限"
            )
            self.status_bar.showMessage(f"❌ 导出失败: {str(e)}", 5000)

    def load_common_projects(self):
        """加载常用项目（智能推荐）"""
        self.project_list.clear()

        # 添加标题
        title_item = QListWidgetItem("⭐ 常用项目（根据使用频率智能推荐）")
        title_item.setForeground(QColor("#1976d2"))
        title_item.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        title_item.setFlags(Qt.NoItemFlags)
        title_item.setBackground(QColor("#e3f2fd"))
        title_item.setSizeHint(QSize(0, 35))
        self.project_list.addItem(title_item)

        # 获取常用项目
        projects = self.db.get_common_projects(limit=10)

        if not projects:
            empty_item = QListWidgetItem("📭 暂无常用项目，添加项目后会自动推荐")
            empty_item.setForeground(QColor("#999"))
            empty_item.setFlags(Qt.NoItemFlags)
            empty_item.setSizeHint(QSize(0, 30))
            self.project_list.addItem(empty_item)
        else:
            for pid, name, icon in projects:
                item = QListWidgetItem(f"  {icon}  {name}")
                item.setData(Qt.UserRole, pid)
                item.setToolTip(f"项目ID: {pid}\n点击选择此项目")
                item.setFont(QFont("Microsoft YaHei", 12))
                self.project_list.addItem(item)

        # 添加分隔线
        sep = QListWidgetItem("─" * 60)
        sep.setFlags(Qt.NoItemFlags)
        sep.setForeground(QColor("#e0e0e0"))
        sep.setSizeHint(QSize(0, 12))
        self.project_list.addItem(sep)

        # 添加提示
        hint_item = QListWidgetItem("💡 在搜索框输入关键词查找更多项目 | 点击「📁 项目管理」添加/管理项目")
        hint_item.setForeground(QColor("#546e7a"))
        hint_item.setFont(QFont("Microsoft YaHei", 10))
        hint_item.setFlags(Qt.NoItemFlags)
        hint_item.setSizeHint(QSize(0, 28))
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
        title_item.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        title_item.setFlags(Qt.NoItemFlags)
        title_item.setBackground(QColor("#ffebee"))
        title_item.setSizeHint(QSize(0, 35))
        self.project_list.addItem(title_item)

        # 获取搜索结果
        projects = self.db.get_projects(search_text=text)

        if not projects:
            empty_item = QListWidgetItem("📭 未找到匹配的项目")
            empty_item.setForeground(QColor("#999"))
            empty_item.setFlags(Qt.NoItemFlags)
            empty_item.setSizeHint(QSize(0, 30))
            self.project_list.addItem(empty_item)
        else:
            for pid, name, icon, _, _, group_name in projects:
                display_text = f"  {icon}  {name}"
                if group_name:
                    display_text += f"  <{group_name}>"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, pid)
                item.setToolTip(f"分组: {group_name or '未分组'}\nID: {pid}")
                item.setFont(QFont("Microsoft YaHei", 12))
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
                self.project_list.item(i).setForeground(QColor("#333"))
            item.setBackground(QColor("#c8e6c9"))
            item.setForeground(QColor("#1b5e20"))
            item.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))

    def clear_project_selection(self):
        """清除项目选择"""
        self.selected_project_id = None
        self.project_search.clear()
        self.load_common_projects()
        QMessageBox.information(self, "📌 提示", "已清除项目选择")

    def open_project_manager(self):
        """打开项目管理对话框"""
        dialog = ProjectDialog(self.db, self)
        if dialog.exec() == QDialog.Accepted:
            # 重新加载项目（两个标签页都需要）
            current_text = self.project_search.text()
            if current_text:
                self.filter_projects(current_text)
            else:
                self.load_common_projects()
            # 刷新历史记录页的项目筛选下拉框
            self.load_project_filter_combo()
            # 刷新历史记录（因为项目可能变化）
            self.load_history_reports()
            self.status_bar.showMessage("✅ 项目列表已更新", 2000)

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
                "未选择项目，是否继续保存到「其他」类别？\n（可在项目管理中设置常用项目）",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # 保存到数据库
        try:
            conn = sqlite3.connect("projects.db")
            cursor = conn.cursor()
            # 使用本地时间戳
            local_created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                           INSERT INTO daily_reports (date, project_id, task_content, hours, status, notes, created_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?)
                           ''', (date_str, self.selected_project_id, task_content, hours, status, notes, local_created_at))
            conn.commit()
            conn.close()

            # 重置表单（保留日期为今天）
            self.task_text.clear()
            self.note_text.clear()
            self.hour_spin.setValue(8.0)
            self.status_combo.setCurrentText("进行中")
            self.clear_project_selection()

            # 刷新历史记录（切换到历史标签页并刷新）
            self.tabs.setCurrentIndex(1)
            self.load_history_reports()

            QMessageBox.information(
                self, "✅ 保存成功",
                f"日报已成功保存！\n\n"
                f"📅 日期: {date_str}\n"
                f"📌 项目: {self.db.get_project_by_id(self.selected_project_id) if self.selected_project_id else '其他'}\n"
                f"⏱️ 耗时: {hours} 小时\n\n"
                f"💡 已自动切换到「历史记录」标签页查看"
            )

            self.status_bar.showMessage(
                f"✅ 新增日报成功 | 项目: {self.db.get_project_by_id(self.selected_project_id) if self.selected_project_id else '其他'} | 耗时: {hours}h",
                4000)

        except Exception as e:
            QMessageBox.critical(self, "❌ 保存失败", f"发生错误：{str(e)}\n\n请检查数据库是否被占用")
            self.status_bar.showMessage(f"❌ 保存失败: {str(e)}", 5000)

    def clear_form(self):
        """清空表单"""
        reply = QMessageBox.question(
            self, "🧹 清空表单",
            "确定要清空当前填写内容吗？\n（已保存的数据不受影响）",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.task_text.clear()
            self.note_text.clear()
            self.hour_spin.setValue(8.0)
            self.status_combo.setCurrentText("进行中")
            self.clear_project_selection()
            self.status_bar.showMessage("🧹 表单已清空", 2000)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用属性
    app.setApplicationName("智能日报系统")
    app.setOrganizationName("DailyReport")
    app.setApplicationVersion("2.1")

    # 高DPI支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 创建并显示窗口
    window = DailyReportApp()
    window.show()

    sys.exit(app.exec())