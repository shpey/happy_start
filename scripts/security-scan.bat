@echo off
echo ========================================
echo       智能思维平台 - 安全扫描
echo ========================================
echo.

:: 设置颜色
color 0A

:: 检查Node.js是否已安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 请先安装 Node.js
    pause
    exit /b 1
)

:: 检查npm是否已安装
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 请先安装 npm
    pause
    exit /b 1
)

echo [INFO] 开始安全扫描...
echo.

:: 1. 扫描前端依赖漏洞
echo ========================================
echo       前端依赖安全扫描
echo ========================================
cd frontend
if exist package.json (
    echo [INFO] 扫描前端依赖漏洞...
    npm audit --audit-level moderate
    if %errorlevel% neq 0 (
        echo [WARNING] 发现前端依赖安全问题
        echo [INFO] 尝试自动修复...
        npm audit fix
    ) else (
        echo [SUCCESS] 前端依赖无安全问题
    )
) else (
    echo [WARNING] 前端 package.json 文件不存在
)
cd ..
echo.

:: 2. 扫描后端依赖漏洞
echo ========================================
echo       后端依赖安全扫描  
echo ========================================
cd backend
if exist requirements.txt (
    echo [INFO] 检查 Python 安全工具...
    pip show safety >nul 2>&1
    if %errorlevel% neq 0 (
        echo [INFO] 安装 Python 安全扫描工具...
        pip install safety bandit
    )
    
    echo [INFO] 扫描 Python 依赖漏洞...
    safety check -r requirements.txt
    if %errorlevel% neq 0 (
        echo [WARNING] 发现后端依赖安全问题
    ) else (
        echo [SUCCESS] 后端依赖无安全问题
    )
    
    echo [INFO] 扫描代码安全问题...
    bandit -r . -x tests/ -f txt
    if %errorlevel% neq 0 (
        echo [WARNING] 发现代码安全问题
    ) else (
        echo [SUCCESS] 代码安全检查通过
    )
) else (
    echo [WARNING] 后端 requirements.txt 文件不存在
)
cd ..
echo.

:: 3. 扫描移动应用依赖
echo ========================================
echo       移动应用依赖安全扫描
echo ========================================
cd mobile
if exist package.json (
    echo [INFO] 扫描移动应用依赖漏洞...
    npm audit --audit-level moderate
    if %errorlevel% neq 0 (
        echo [WARNING] 发现移动应用依赖安全问题
        echo [INFO] 尝试自动修复...
        npm audit fix
    ) else (
        echo [SUCCESS] 移动应用依赖无安全问题
    )
) else (
    echo [WARNING] 移动应用 package.json 文件不存在
)
cd ..
echo.

:: 4. Docker 安全扫描
echo ========================================
echo       Docker 镜像安全扫描
echo ========================================
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker 未安装，跳过镜像安全扫描
) else (
    echo [INFO] 扫描 Docker 镜像安全问题...
    
    :: 检查是否有 Dockerfile
    if exist Dockerfile (
        echo [INFO] 构建并扫描主 Dockerfile...
        docker build -t intelligent-thinking-security-scan .
        
        :: 使用 docker scout 扫描（如果可用）
        docker scout version >nul 2>&1
        if %errorlevel% equ 0 (
            echo [INFO] 使用 Docker Scout 扫描镜像...
            docker scout cves intelligent-thinking-security-scan
        ) else (
            echo [INFO] Docker Scout 不可用，使用基础安全检查...
            docker run --rm -v "%cd%":/app node:18-alpine sh -c "cd /app && npm list --depth=0"
        )
    ) else (
        echo [WARNING] 主 Dockerfile 不存在
    )
    
    :: 扫描前端 Dockerfile
    if exist frontend/Dockerfile (
        echo [INFO] 扫描前端 Dockerfile...
        docker build -f frontend/Dockerfile -t frontend-security-scan ./frontend/
    )
    
    :: 扫描后端 Dockerfile  
    if exist backend/Dockerfile (
        echo [INFO] 扫描后端 Dockerfile...
        docker build -f backend/Dockerfile -t backend-security-scan ./backend/
    )
)
echo.

:: 5. 环境变量和配置文件检查
echo ========================================
echo       配置文件安全检查
echo ========================================
echo [INFO] 检查敏感文件...

:: 检查是否有敏感文件暴露
if exist .env (
    echo [WARNING] 发现 .env 文件，请确保不要提交到版本控制
)

if exist backend/.env (
    echo [WARNING] 发现 backend/.env 文件，请确保不要提交到版本控制
)

if exist frontend/.env (
    echo [WARNING] 发现 frontend/.env 文件，请确保不要提交到版本控制
)

if exist mobile/.env (
    echo [WARNING] 发现 mobile/.env 文件，请确保不要提交到版本控制
)

:: 检查.gitignore文件
if exist .gitignore (
    findstr /C:".env" .gitignore >nul 2>&1
    if %errorlevel% neq 0 (
        echo [WARNING] .gitignore 中未包含 .env 文件
    ) else (
        echo [SUCCESS] .gitignore 配置正确
    )
) else (
    echo [WARNING] 缺少 .gitignore 文件
)

echo.

:: 6. 生成安全扫描报告
echo ========================================
echo       生成安全扫描报告
echo ========================================
set REPORT_FILE=security-scan-report-%date:~0,4%%date:~5,2%%date:~8,2%-%time:~0,2%%time:~3,2%%time:~6,2%.txt
echo [INFO] 生成安全扫描报告: %REPORT_FILE%

echo 智能思维平台 - 安全扫描报告 > %REPORT_FILE%
echo 扫描时间: %date% %time% >> %REPORT_FILE%
echo ================================== >> %REPORT_FILE%
echo. >> %REPORT_FILE%

:: 添加依赖扫描结果到报告
echo 前端依赖扫描: >> %REPORT_FILE%
cd frontend
if exist package.json (
    npm audit --audit-level moderate >> ../%REPORT_FILE% 2>&1
)
cd ..

echo. >> %REPORT_FILE%
echo 后端依赖扫描: >> %REPORT_FILE%
cd backend
if exist requirements.txt (
    safety check -r requirements.txt >> ../%REPORT_FILE% 2>&1
)
cd ..

echo. >> %REPORT_FILE%
echo 配置文件检查: >> %REPORT_FILE%
if exist .env echo 发现 .env 文件 >> %REPORT_FILE%
if exist backend/.env echo 发现 backend/.env 文件 >> %REPORT_FILE%
if exist frontend/.env echo 发现 frontend/.env 文件 >> %REPORT_FILE%
if exist mobile/.env echo 发现 mobile/.env 文件 >> %REPORT_FILE%

echo.
echo ========================================
echo       安全扫描完成
echo ========================================
echo [SUCCESS] 安全扫描报告已生成: %REPORT_FILE%
echo [INFO] 请查看报告并修复发现的安全问题
echo.

pause 