@echo off
echo 🔍 验证前端运行时错误修复...
echo.

echo 📋 检查关键文件修复...
echo.

:: 检查api.ts是否使用import.meta.env
findstr /c:"import.meta.env" frontend\src\services\api.ts >nul
if %errorlevel% equ 0 (
    echo ✅ api.ts - 已修复为import.meta.env
) else (
    echo ❌ api.ts - 仍然使用process.env
)

:: 检查是否还有process.env的使用
findstr /c:"process.env" frontend\src\services\api.ts >nul
if %errorlevel% equ 0 (
    echo ❌ api.ts - 仍然有process.env引用
) else (
    echo ✅ api.ts - 已清除process.env引用
)

:: 检查thinkingService.ts是否使用正确的导入
findstr /c:"import apiService from" frontend\src\services\thinkingService.ts >nul
if %errorlevel% equ 0 (
    echo ✅ thinkingService.ts - 已修复导入方式
) else (
    echo ❌ thinkingService.ts - 仍然使用旧的导入方式
)

:: 检查vite-env.d.ts是否包含环境变量定义
findstr /c:"REACT_APP_API_URL" frontend\src\vite-env.d.ts >nul
if %errorlevel% equ 0 (
    echo ✅ vite-env.d.ts - 已添加环境变量类型定义
) else (
    echo ❌ vite-env.d.ts - 缺少环境变量类型定义
)

:: 检查package.json构建脚本
findstr /c:"\"build\": \"vite build\"" frontend\package.json >nul
if %errorlevel% equ 0 (
    echo ✅ package.json - 已修复构建脚本
) else (
    echo ❌ package.json - 构建脚本未修复
)

echo.
echo 🚀 验证完成！
echo.
echo 📝 下一步建议：
echo 1. 在frontend目录创建.env文件（可选）
echo 2. 启动前端开发服务器测试: cd frontend && npm run dev
echo 3. 或者测试Docker构建: docker build -t test-frontend:latest ./frontend
echo 4. 推送代码: git add . && git commit -m "fix: resolve process.env runtime error and API service imports" 