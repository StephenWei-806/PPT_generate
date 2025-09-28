@echo off
setlocal enabledelayedexpansion

REM 前端构建脚本 - Windows版本
REM 用于本地开发和生产部署

echo === PPT生成器前端构建脚本 ===

REM 获取脚本目录
set "SCRIPT_DIR=%~dp0"
set "FRONTEND_DIR=%SCRIPT_DIR%"
set "BACKEND_STATIC_DIR=%SCRIPT_DIR%\..\backend\static\frontend"

REM 检查Node.js和npm
where node >nul 2>nul
if errorlevel 1 (
    echo 错误: 未找到Node.js，请先安装Node.js 16+
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo 错误: 未找到npm，请先安装npm
    exit /b 1
)

for /f "tokens=1 delims=." %%a in ('node --version') do (
    set "NODE_MAJOR=%%a"
    set "NODE_MAJOR=!NODE_MAJOR:v=!"
)

if !NODE_MAJOR! LSS 16 (
    echo 警告: Node.js版本过低 ^(!NODE_MAJOR!^)，推荐使用16+
)

echo Node.js版本: 
node --version
echo npm版本: 
npm --version

REM 进入前端目录
cd /d "%FRONTEND_DIR%"

REM 1. 清理旧文件
echo 1. 清理旧的构建文件...
if exist "dist" rmdir /s /q "dist"
if exist "%BACKEND_STATIC_DIR%" rmdir /s /q "%BACKEND_STATIC_DIR%"

REM 2. 安装依赖
echo 2. 安装npm依赖...
if not exist "node_modules" (
    echo 首次安装依赖...
    npm install
) else (
    echo 更新依赖...
    npm ci
)

if errorlevel 1 (
    echo 错误: npm依赖安装失败
    exit /b 1
)

REM 3. 构建生产版本
echo 3. 构建生产版本...
set NODE_ENV=production
npm run build:production

if errorlevel 1 (
    echo 错误: 构建失败
    exit /b 1
)

REM 4. 验证构建结果
echo 4. 验证构建结果...
if exist "%BACKEND_STATIC_DIR%" (
    echo ✓ 构建成功！文件输出到: %BACKEND_STATIC_DIR%
    
    echo.
    echo 构建文件列表:
    dir /s "%BACKEND_STATIC_DIR%"
    
    REM 检查关键文件
    if exist "%BACKEND_STATIC_DIR%\index.html" (
        echo ✓ index.html 存在
    ) else (
        echo ✗ index.html 缺失
        exit /b 1
    )
    
    if exist "%BACKEND_STATIC_DIR%\assets" (
        echo ✓ assets 目录存在
    ) else (
        echo ✗ assets 目录缺失
        exit /b 1
    )
    
) else (
    echo ✗ 构建失败！输出目录不存在
    exit /b 1
)

REM 5. 生成部署信息
echo 5. 生成部署信息...
for /f "tokens=2 delims= " %%i in ('date /t') do set BUILD_DATE=%%i
for /f "tokens=1 delims= " %%i in ('time /t') do set BUILD_TIME=%%i

REM 尝试获取git哈希
for /f "tokens=*" %%i in ('git rev-parse --short HEAD 2^>nul') do set BUILD_HASH=%%i
if "!BUILD_HASH!"=="" set BUILD_HASH=unknown

REM 生成构建信息JSON
(
echo {
echo   "buildTime": "%BUILD_DATE% %BUILD_TIME%",
echo   "buildHash": "%BUILD_HASH%",
echo   "nodeVersion": "$(node --version)",
echo   "npmVersion": "$(npm --version)",
echo   "environment": "production"
echo }
) > "%BACKEND_STATIC_DIR%\build-info.json"

echo ✓ 部署信息已生成

echo.
echo === 构建完成 ===
echo 构建时间: %BUILD_DATE% %BUILD_TIME%
echo 提交哈希: %BUILD_HASH%
echo 输出目录: %BACKEND_STATIC_DIR%
echo.
echo 下一步:
echo 1. 将 backend/ 目录上传到服务器
echo 2. 运行部署脚本: sudo ./deploy.sh
echo 3. 访问: http://101.245.71.8/PPT_generate/
echo.

pause