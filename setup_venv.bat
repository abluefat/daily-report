@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    🌟 智能工作日报系统 - 环境搭建工具
echo    ✅ 专为 Python 3.13.3 优化 | 隔离系统包
echo ========================================
echo.

:: 检查是否在项目根目录
if not exist "requirements.txt" (
    echo [!] 错误：请将本脚本放在项目根目录（需包含 requirements.txt）
    echo      当前路径: %CD%
    pause
    exit /b 1
)

:: 检查 Python 版本（友好提示）
python --version | findstr /C:"3.13" >nul
if errorlevel 1 (
    echo [⚠️] 检测到非 3.13 版本 Python，建议使用 3.12.3 获得最佳兼容性
    echo      当前:
    python --version
    echo      详细说明见 README.md 第 3 节
    timeout /t 3 >nul
)

:: 清理旧环境（关键！避免系统包污染）
echo [1/5] 🔥 清理旧虚拟环境...
if exist ".venv" (
    rmdir /s /q ".venv" 2>nul
    if errorlevel 1 (
        echo [!] 警告：.venv 目录被占用，请关闭 PyCharm/VSCode 后重试
        pause
        exit /b 1
    )
)
pip cache purge >nul 2>&1
del /f /q "distutils-precedence.pth" 2>nul

:: 创建纯净虚拟环境（关键参数：不继承系统包）
echo [2/5] 🌱 创建隔离虚拟环境（--without-pip 确保纯净）...
python -m venv .venv --without-pip --prompt "daily-report"
if errorlevel 1 (
    echo [❌] 虚拟环境创建失败！请检查：
    echo       1. 是否以管理员身份运行
    echo       2. Python 路径是否包含空格（建议安装到无空格路径）
    pause
    exit /b 1
)

:: 激活环境并安装工具链
echo [3/5] 🛠️  激活环境并安装 pip/setuptools...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [❌] 激活虚拟环境失败！
    pause
    exit /b 1
)

:: 安装兼容版 pip（Python 3.13 需 pip≥24.0）
python -m ensurepip --default-pip >nul 2>&1
python -m pip install --upgrade pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=1000
if errorlevel 1 (
    echo [❌] pip 安装失败！尝试手动安装：
    echo       .venv\Scripts\python.exe -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
    pause
    exit /b 1
)

:: 安装项目依赖（关键：指定源+超时）
echo [4/5] 📦 安装项目依赖（PySide6 6.10.2 + openpyxl）...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=1000 --no-cache-dir
if errorlevel 1 (
    echo.
    echo [⚠️] 依赖安装部分失败！常见原因：
    echo       • 网络波动 → 重新运行本脚本
    echo       • 杀毒软件拦截 → 临时关闭后重试
    echo       • 磁盘空间不足 → 检查 C 盘剩余空间
    echo.
    echo [💡] 尝试单独安装 PySide6：
    echo       pip install PySide6==6.10.2 -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=1000
    pause
    exit /b 1
)

:: 验证 Designer 位置（解决核心痛点）
echo [5/5] 🔍 验证 Qt Designer 位置...
where designer >nul 2>&1
if errorlevel 1 (
    echo.
    echo [❗] 未在虚拟环境中找到 designer.exe
    echo      ✅ 解决方案（任选其一）：
    echo        1️⃣ 直接使用系统 Designer：
    echo           "D:\Develop File\Python\pyenv-win\versions\3.13.3\Scripts\designer.exe"
    echo.
    echo        2️⃣ 配置 PyCharm External Tools（推荐）：
    echo           Settings → Tools → External Tools → 添加 designer.exe 路径
    echo.
    echo        3️⃣ 创建启动器（复制下方命令到 launch_designer.bat）：
    echo           @echo off
    echo           start "" "D:\Develop File\Python\pyenv-win\versions\3.13.3\Scripts\designer.exe"
    echo.
) else (
    for /f "tokens=*" %%i in ('where designer') do set DESIGNER_PATH=%%i
    echo      ✅ Designer 位置: %DESIGNER_PATH%
    echo      💡 使用方法：
    echo         • 命令行输入: designer
    echo         • PyCharm 右键 .ui 文件 → Open With → Qt Designer
)

:: 最终提示
echo.
echo ========================================
echo    ✅ 环境搭建成功！
echo ========================================
echo  📌 下一步操作：
echo      1. 运行: .venv\Scripts\activate ^&^& python main.py
echo      2. 设计界面: 双击 launch_designer.bat（需自行创建）
echo      3. 打包发布: 运行 build_exe.bat
echo.
echo  ⚠️  Python 3.13.3 兼容性提示：
echo      • 当前配置可运行，但 PySide6 官方认证版本为 3.12.x
echo      • 长期开发建议: pyenv local 3.12.3 重建环境（见 README.md）
echo ========================================
pause