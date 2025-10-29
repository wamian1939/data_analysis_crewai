@echo off
chcp 65001 > nul
echo ====================================
echo   CrewAI 数据分析系统 - 一键启动
echo ====================================
echo.
echo 正在启动 API 和 Web 服务...
echo.

:: 启动 API 服务（新窗口）
echo [1/2] 启动 API 服务...
start "CrewAI API" cmd /k "chcp 65001 > nul && python api/main.py"

:: 等待 API 启动
timeout /t 5 /nobreak > nul

:: 启动 Web 服务（新窗口）
echo [2/2] 启动 Web 前端...
start "CrewAI Web" cmd /k "chcp 65001 > nul && cd web && python -m http.server 8080"

:: 等待服务启动
timeout /t 3 /nobreak > nul

echo.
echo ====================================
echo   启动完成！
echo ====================================
echo.
echo API 文档: http://localhost:8000/docs
echo Web 界面: http://localhost:8080
echo.
echo 按任意键打开浏览器...
pause > nul

:: 打开浏览器
start http://localhost:8080

echo.
echo 提示: 关闭两个命令窗口即可停止服务
echo.
