@echo off
echo 正在启动智能思维移动应用...
echo.

REM 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Node.js未安装，请先安装Node.js
    pause
    exit /b 1
)

REM 切换到mobile目录
cd /d %~dp0

REM 安装依赖（如果node_modules不存在）
if not exist "node_modules" (
    echo 正在安装依赖...
    npm install
)

REM 启动Metro bundler
echo 正在启动Metro bundler...
echo 请在另一个终端窗口中运行以下命令来启动应用:
echo.
echo   对于Android: npm run android
echo   对于iOS: npm run ios  
echo   对于Web: npm run web
echo.
npm start

pause 