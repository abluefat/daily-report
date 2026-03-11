@echo off
echo ========================================
echo    📦 智能日报系统 - 一键打包工具
echo ========================================
echo.

:: 检查虚拟环境
if not exist ".venv\Scripts\activate.bat" (
    echo [!] 错误：未检测到虚拟环境！请先运行 setup_venv.bat
    pause
    exit /b 1
)

:: 激活环境
call .venv\Scripts\activate

:: 安装打包工具
echo [1/3] 安装打包工具...
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet

:: 创建dist目录
if not exist "dist" mkdir dist

:: 打包命令（优化参数）
echo [2/3] 开始打包...（约需2-5分钟）
pyinstaller ^
  --name="DailyReport" ^
  --windowed ^
  --icon="resources\app.ico" ^
  --add-data "resources;resources" ^
  --hidden-import=openpyxl.cell ^
  --hidden-import=openpyxl.styles ^
  --hidden-import=openpyxl.utils ^
  --exclude-module matplotlib ^
  --exclude-module numpy ^
  --clean ^
  --noconfirm ^
  main.py

:: 复制资源文件（备用方案）
if exist "dist\DailyReport\resources" (
    echo [3/3] 资源文件已包含
) else (
    echo [3/3] 复制资源文件...
    xcopy /E /I /Y "resources" "dist\DailyReport\resources" >nul 2>&1
)

:: 完成提示
echo.
echo ========================================
echo    ✅ 打包成功！
echo ========================================
echo  📁 生成位置: dist\DailyReport\
echo  💡 双击运行: dist\DailyReport\DailyReport.exe
echo  🌐 分发建议: 压缩整个 DailyReport 文件夹（约50MB）
echo ========================================
pause