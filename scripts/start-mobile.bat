@echo off
echo 正在启动智能思维移动应用...
echo.

cd mobile

REM 检查依赖
if not exist "node_modules" (
    echo 正在安装依赖...
    npm install
)

echo.
echo 移动应用已配置完成！
echo.
echo 可用的启动选项:
echo   1. npm start          - 启动Metro bundler
echo   2. npm run web        - 启动Web版本 (推荐)
echo   3. npm run android    - 启动Android版本
echo   4. npm run ios        - 启动iOS版本
echo.

REM 启动web版本
echo 正在启动Web版本...
npm run web

pause 