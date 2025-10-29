@echo off
chcp 65001 > nul
echo ====================================
echo   CrewAI 数据分析 API 服务
echo ====================================
echo.

REM 检查 uvicorn 是否安装
python -c "import uvicorn" > nul 2>&1
if %errorlevel% neq 0 (
    echo uvicorn 未安装，正在安装...
    pip install uvicorn[standard]
    if %errorlevel% neq 0 (
        echo 安装失败，请手动安装: pip install uvicorn[standard]
        pause
        exit /b 1
    )
)

REM 检查依赖
echo 检查 Python 依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败，请检查 requirements.txt
    pause
    exit /b 1
)

echo.
echo API 服务地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo 按 Ctrl+C 停止服务
echo.

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
pause
