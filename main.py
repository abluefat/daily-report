import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, QDateEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog,
    QHeaderView, QAbstractItemView, QDialog, QDialogButtonBox
)
from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QColor
from database import Database
import datetime


# 加载样式表（如果存在）
def load_stylesheet():
    style_path = os.path.join(os.path.dirname(__file__), "resources", "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


class EditDialog(QDialog):
    """编辑日报对话框"""

    def __init__(self, report_data=None, parent=None):
        super().__init__(parent)
        self.report_data = report_data
        self.setWindowTitle("✏️ 编辑日报" if report_data else "✏️ 新增日报")
        self.setModal(True)
        self.resize(600, 400)
        self.setup_ui()
        if report_data:
            self.load_data(report_data)

    def setup_ui(self):
        layout = QVBoxLayout()

        # 日期
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("📅 日期:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        layout.addLayout(date_layout)

        # 项目
        project_layout = QHBoxLayout()
        project_layout.addWidget(QLabel("📦 项目:"))
        self.project_combo = QComboBox()
        self.project_combo.addItems(["客户系统升级", "内部工具开发", "需求评审", "Bug修复", "其他"])
        project_layout.addWidget(self.project_combo)
        project_layout.addStretch()
        layout.addLayout(project_layout)

        # 任务内容
        layout.addWidget(QLabel("📝 任务内容:"))
        self.task_edit = QTextEdit()
        self.task_edit.setPlaceholderText("请输入详细工作内容...")
        layout.addWidget(self.task_edit)

        # 耗时+状态
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(QLabel("⏱️ 耗时(小时):"))
        self.hours_edit = QLineEdit("2.5")
        bottom_layout.addWidget(self.hours_edit)

        bottom_layout.addWidget(QLabel("  状态:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["进行中", "已完成", "已延期", "待确认", "已取消"])
        bottom_layout.addWidget(self.status_combo)
        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)

        # 备注
        layout.addWidget(QLabel("💬 备注:"))
        self.notes_edit = QLineEdit()
        layout.addWidget(self.notes_edit)

        # 按钮
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("❌ 取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self, data):
        """加载现有数据"""
        self.date_edit.setDate(QDate.fromString(data[1], "yyyy-MM-dd"))
        self.project_combo.setCurrentText(data[2] or "")
        self.task_edit.setPlainText(data[3])
        self.hours_edit.setText(str(data[4] or "0"))
        self.status_combo.setCurrentText(data[5])
        self.notes_edit.setText(data[6] or "")

    def get_data(self):
        """获取输入数据"""
        return (
            self.date_edit.date().toString("yyyy-MM-dd"),
            self.project_combo.currentText(),
            self.task_edit.toPlainText().strip(),
            float(self.hours_edit.text() or 0),
            self.status_combo.currentText(),
            self.notes_edit.text().strip()
        )


class DailyReportApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
        self.load_history()

    def init_ui(self):
        # 窗口设置
        self.setWindowTitle("📝 智能工作日报系统")
        self.resize(1100, 750)

        # 设置图标（如果存在）
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "app.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # 主窗口部件
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # =============== 顶部按钮区 ===============
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ 新增日报")
        self.add_btn.clicked.connect(self.add_report)
        self.edit_btn = QPushButton("✏️ 编辑选中")
        self.edit_btn.clicked.connect(self.edit_selected)
        self.delete_btn = QPushButton("🗑️ 删除选中")
        self.delete_btn.clicked.connect(self.delete_selected)
        self.export_btn = QPushButton("📤 导出Excel")
        self.export_btn.clicked.connect(self.export_excel)

        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.export_btn]:
            btn.setMinimumHeight(35)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.export_btn)
        main_layout.addLayout(btn_layout)

        # =============== 历史记录表格 ===============
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels(
            ["ID", "日期", "项目", "任务内容", "耗时", "状态", "备注", "创建时间"]
        )
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止直接编辑
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setColumnWidth(0, 50)  # ID
        self.history_table.setColumnWidth(1, 100)  # 日期
        self.history_table.setColumnWidth(2, 120)  # 项目
        self.history_table.setColumnWidth(3, 350)  # 任务内容
        self.history_table.setColumnWidth(4, 70)  # 耗时
        self.history_table.setColumnWidth(5, 80)  # 状态
        self.history_table.setColumnWidth(6, 150)  # 备注
        self.history_table.setColumnWidth(7, 150)  # 创建时间
        main_layout.addWidget(self.history_table)

        # 状态栏
        self.statusBar().showMessage("✅ 系统就绪 | 双击表格行可快速编辑")

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 双击编辑
        self.history_table.itemDoubleClicked.connect(self.edit_selected)

    def load_history(self, rows=None):
        """加载日报数据到表格"""
        if rows is None:
            rows = self.db.get_all_reports(limit=200)

        self.history_table.setRowCount(len(rows))
        status_colors = {
            "已完成": "#28a745", "进行中": "#ffc107",
            "已延期": "#dc3545", "待确认": "#17a2b8", "已取消": "#6c757d"
        }

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item_text = str(value) if value is not None else ""
                item = QTableWidgetItem(item_text)

                # 状态列着色
                if col_idx == 5 and item_text in status_colors:
                    item.setForeground(QColor("white"))
                    item.setBackground(QColor(status_colors[item_text]))
                    item.setTextAlignment(Qt.AlignCenter)

                # ID和耗时列居中
                if col_idx in [0, 4]:
                    item.setTextAlignment(Qt.AlignCenter)

                self.history_table.setItem(row_idx, col_idx, item)

        self.statusBar().showMessage(f"✅ 已加载 {len(rows)} 条日报记录")

    def add_report(self):
        """新增日报"""
        dialog = EditDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data[2]:  # 任务内容为空
                QMessageBox.warning(self, "⚠️ 警告", "任务内容不能为空！")
                return

            success, result = self.db.save_report(*data)
            if success:
                QMessageBox.information(self, "✅ 成功", f"日报保存成功！ID: {result}")
                self.load_history()
            else:
                QMessageBox.critical(self, "❌ 失败", f"保存失败:\n{result}")

    def edit_selected(self):
        """编辑选中行"""
        selected = self.history_table.selectedItems()
        if not selected:
            QMessageBox.information(self, "💡 提示", "请先选择要编辑的日报行")
            return

        row = selected[0].row()
        report_id = int(self.history_table.item(row, 0).text())
        # 获取完整数据（从数据库）
        all_reports = self.db.get_all_reports(limit=1000)
        target_report = None
        for r in all_reports:
            if r[0] == report_id:
                target_report = r
                break

        if not target_report:
            QMessageBox.warning(self, "⚠️ 警告", "未找到该日报记录")
            return

        dialog = EditDialog(report_data=target_report, parent=self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data[2]:
                QMessageBox.warning(self, "⚠️ 警告", "任务内容不能为空！")
                return

            success = self.db.update_report(report_id, *data)
            if success:
                QMessageBox.information(self, "✅ 成功", "日报更新成功！")
                self.load_history()
            else:
                QMessageBox.critical(self, "❌ 失败", "更新失败，请重试")

    def delete_selected(self):
        """删除选中行"""
        selected = self.history_table.selectedItems()
        if not selected:
            QMessageBox.information(self, "💡 提示", "请先选择要删除的日报行")
            return

        row = selected[0].row()
        report_id = int(self.history_table.item(row, 0).text())
        report_date = self.history_table.item(row, 1).text()
        task_preview = self.history_table.item(row, 3).text()[:20] + "..."

        reply = QMessageBox.question(
            self, "❓ 确认删除",
            f"确定要删除以下日报吗？\n\n📅 日期: {report_date}\n📝 任务: {task_preview}",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = self.db.delete_report(report_id)
            if success:
                QMessageBox.information(self, "✅ 成功", "日报已删除")
                self.load_history()
            else:
                QMessageBox.critical(self, "❌ 失败", "删除失败，请重试")

    def export_excel(self):
        """导出Excel"""
        path, _ = QFileDialog.getSaveFileName(
            self, "💾 保存Excel",
            f"工作日报_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        if not path:
            return

        try:
            # 获取当前表格数据（避免重新查询）
            rows = []
            for row in range(self.history_table.rowCount()):
                row_data = []
                for col in range(8):
                    item = self.history_table.item(row, col)
                    row_data.append(item.text() if item else "")
                rows.append(row_data)

            success, error = self.db.export_to_excel(rows, path)
            if success:
                QMessageBox.information(
                    self, "✅ 导出成功",
                    f"Excel文件已保存！\n📁 {path}\n\n共导出 {len(rows)} 条记录"
                )
            else:
                QMessageBox.critical(self, "❌ 导出失败", f"错误:\n{error}")
        except Exception as e:
            QMessageBox.critical(self, "❌ 错误", f"导出过程出错:\n{str(e)}")


if __name__ == "__main__":
    # 设置环境变量（解决中文路径问题）
    os.environ["QT_QPA_PLATFORM"] = "windows"

    app = QApplication(sys.argv)

    # 设置全局字体（中文友好）
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    # 应用样式表
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    window = DailyReportApp()
    window.show()
    sys.exit(app.exec())