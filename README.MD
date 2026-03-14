# 📝 智能工作日报系统

>  深色主题 | Excel导出 | 零环境焦虑  
> ✨ 专为 Windows 开发者优化 | Python 3.13.3 友好配置

![Python](https://img.shields.io/badge/Python-3.12.3%20(recommended)-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.10.2-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🌟 核心功能
- 🌟 **智能项目选择**：常用项目自动推荐 + 实时搜索
- 📁 **项目分组管理**：支持部门/客户多级分类
- 🎨 **Emoji图标系统**：无需图片资源，跨平台兼容
- 🔍 **全文搜索**：项目名+分组名双关键词搜索
- 📊 **使用统计**：自动记录使用频率，推荐越用越精准

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
├── ProjectDialog.py       # 项目管理对话框
├── requirements.txt       # 精确依赖版本
├── setup_venv.bat         # 环境搭建脚本（⭐ 核心）
├── build_exe.bat          # 一键打包脚本
├── launch_designer.bat    # Designer 启动器（需自行创建）
└── README.md              # 本文件
 ```

## 💡 使用技巧
- 快速选择：在搜索框输入关键词（如"客户"）秒找项目
- 设置常用：在项目管理中勾选"设为常用项目"
- 智能推荐：常用项目会自动出现在顶部推荐区
- 图标选择：点击"🎨 选择图标"从20+ emoji中挑选
- 安全删除：删除项目前会检查是否被日报引用

## 🌈 界面预览
- 主界面：清爽的日报填写表单 + 智能项目选择器
- 项目管理：树形分组 + 表格化项目列表 + 搜索过滤
- 项目编辑：直观的表单 + Emoji图标选择器

## 📌 注意事项
- 首次运行会自动创建 projects.db 数据库文件
- 所有数据保存在本地，无需网络连接
- 支持 Windows/macOS/Linux（需系统支持 emoji 字体）
- 推荐使用 Python 3.9+ 和 PySide6 6.5+

## 🌈 贡献与支持
- 💡 功能建议：提交 Issue 描述需求
- 🐞 Bug 反馈：附截图 + 错误日志
- 🌍 中文优先：所有文档/注释均为中文

## 💌 特别致谢
感谢您选择本项目！