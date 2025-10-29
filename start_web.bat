@echo off
chcp 65001 > nul
echo ====================================
echo   CrewAI 数据分析系统 - Web 前端
echo ====================================
echo.
echo 正在启动 Web 服务器...
echo.
echo 浏览器访问: http://localhost:8080
echo.
echo 按 Ctrl+C 停止服务
echo.
echo ====================================
echo.

cd web
python -m http.server 8080
