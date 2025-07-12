@echo off
echo 🔍 验证Docker构建修复...
echo.

echo 📋 检查必要文件...
echo.

:: 检查frontend文件
if exist "frontend\nginx.conf" (
    echo ✅ frontend\nginx.conf - 存在
) else (
    echo ❌ frontend\nginx.conf - 缺失
)

if exist "frontend\Dockerfile" (
    echo ✅ frontend\Dockerfile - 存在
) else (
    echo ❌ frontend\Dockerfile - 缺失
)

:: 检查mobile文件
if exist "mobile\Dockerfile" (
    echo ✅ mobile\Dockerfile - 存在
) else (
    echo ❌ mobile\Dockerfile - 缺失
)

if exist "mobile\package.json" (
    echo ✅ mobile\package.json - 存在
) else (
    echo ❌ mobile\package.json - 缺失
)

:: 检查metaverse文件
if exist "metaverse\Dockerfile" (
    echo ✅ metaverse\Dockerfile - 存在
) else (
    echo ❌ metaverse\Dockerfile - 缺失
)

if exist "metaverse\package.json" (
    echo ✅ metaverse\package.json - 存在
) else (
    echo ❌ metaverse\package.json - 缺失
)

echo.
echo 🔧 检查Dockerfile修复内容...
echo.

:: 检查frontend Dockerfile是否包含npm install
findstr /c:"npm install" frontend\Dockerfile >nul
if %errorlevel% equ 0 (
    echo ✅ frontend\Dockerfile - 已修复为npm install
) else (
    echo ❌ frontend\Dockerfile - 仍然使用npm ci
)

:: 检查mobile Dockerfile是否包含npm install
findstr /c:"npm install" mobile\Dockerfile >nul
if %errorlevel% equ 0 (
    echo ✅ mobile\Dockerfile - 已修复为npm install
) else (
    echo ❌ mobile\Dockerfile - 仍然使用npm ci
)

:: 检查metaverse Dockerfile是否包含npm install
findstr /c:"npm install" metaverse\Dockerfile >nul
if %errorlevel% equ 0 (
    echo ✅ metaverse\Dockerfile - 已修复为npm install
) else (
    echo ❌ metaverse\Dockerfile - 仍然使用npm ci
)

:: 检查frontend是否修复了构建输出目录
findstr /c:"/app/dist" frontend\Dockerfile >nul
if %errorlevel% equ 0 (
    echo ✅ frontend\Dockerfile - 已修复构建输出目录为dist
) else (
    echo ❌ frontend\Dockerfile - 仍然使用build目录
)

echo.
echo 🚀 验证完成！
echo.
echo 📝 接下来的步骤：
echo 1. 启动Docker Desktop
echo 2. 运行测试构建: .\scripts\test-builds.bat
echo 3. 提交代码: git add . && git commit -m "fix: resolve npm ci errors and build output directory issues"
echo 4. 推送代码: git push origin main 