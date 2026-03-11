# 📝 智能工作日报系统

>  深色主题 | Excel导出 | 零环境焦虑  
> ✨ 专为 Windows 开发者优化 | Python 3.13.3 友好配置

![Python](https://img.shields.io/badge/Python-3.12.3%20(recommended)-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.10.2-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🌟 核心功能
- ✅ **可视化日报管理**：新增/编辑/删除/查询
- ✅ **智能数据库**：SQLite 自动备份到 `%APPDATA%\DailyReport`
- ✅ **Excel 导出**：带格式导出（含状态着色、列宽优化）
- ✅ **深色主题**：护眼设计 + 中文友好字体
- ✅ **状态追踪**：进行中/已完成/已延期 等五种状态
- ✅ **一键打包**：生成独立 exe（无需安装 Python）

---

## ⚠️ 重要环境提示（必读！）
| 项目 | 推荐配置 | 当前项目配置 | 说明 |
|------|------------|----------------|------|
| **Python 版本** | `3.12.3` | `3.13.3` | PySide6 官方认证版本为 3.12.x |
| **虚拟环境** | 纯净隔离 | 已配置 | `setup_venv.bat` 已规避系统包污染 |
| **Designer 位置** | `.venv\Scripts\` | 系统路径 | 详见 [Designer 使用指南](#-qt-designer-使用指南) |

> 💡 **为什么推荐降级到 3.12.3？**  
> - PySide6 6.10.2 官方测试矩阵明确支持 3.12  
> - 避免未来出现隐藏兼容性问题（如信号槽异常）  
> - 企业级项目稳定性首选  
>   
> **降级操作（pyenv-win）**：  
> ```powershell
> pyenv install 3.12.3
> pyenv local 3.12.3  # 仅当前项目生效
> # 重新运行 setup_venv.bat
> ```

---

## 🚀 快速开始（3 步运行）

### 1️⃣ 搭建环境（双击运行）
```cmd
setup_venv.bat
```

✅ 成功标志：
- 控制台显示 ✅ 环境搭建成功！
- 项目目录生成 .venv 文件夹
- 验证 Designer 位置提示

### 2️⃣ 启动应用
```cmd
.venv\Scripts\activate

python main.py
```

### 3️⃣ 首次使用

1. 点击 ➕ 新增日报 填写今日工作 
2. 双击表格行快速编辑 
3. 点击 📤 导出Excel 生成带格式报表

## 📁 项目结构
 ```
daily-report/
├── .venv/                  # 虚拟环境（setup_venv.bat 生成）
├── resources/
│   ├── app.ico            # 应用图标
│   ├── style.qss          # 深色主题样式
│   └── logo.png           # 窗口 Logo
├── database.py            # 增强版数据库（CRUD + Excel导出）
├── main.py                # 主程序（完整 GUI）
├── requirements.txt       # 精确依赖版本
├── setup_venv.bat         # 环境搭建脚本（⭐ 核心）
├── build_exe.bat          # 一键打包脚本
├── launch_designer.bat    # Designer 启动器（需自行创建）
└── README.md              # 本文件
 ```

## 🌈 贡献与支持
- 💡 功能建议：提交 Issue 描述需求
- 🐞 Bug 反馈：附截图 + 错误日志
- 🌍 中文优先：所有文档/注释均为中文

## 💌 特别致谢
感谢您选择本项目！