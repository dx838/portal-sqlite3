@echo off
chcp 65001 >nul

cd /d %~dp0

echo ======================================
echo Portal项目启动脚本
echo ======================================
echo.

:: 检查Node.js是否安装
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo 系统未安装Node.js
    echo 请先安装Node.js 24或更高版本
    pause
    exit /b 1
)

echo 已安装Node.js版本：
node --version
echo.

:: 检查npm是否安装
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo 系统未安装npm
    echo 请先安装npm
    pause
    exit /b 1
)

echo 已安装npm版本：
npm --version
echo.

:: 检查node_modules是否存在
if not exist "node_modules" (
    echo 正在安装依赖...
    npm install
    if %errorlevel% neq 0 (
        echo 错误：安装依赖失败
        pause
        exit /b 1
    )
    echo 依赖安装成功
    echo.
)

:: 编译TypeScript代码
echo 正在编译TypeScript代码...
npm run build
if %errorlevel% neq 0 (
    echo 错误：编译失败
    pause
    exit /b 1
)
echo 编译成功

echo.
echo ======================================
echo 正在启动项目...
echo 访问地址：http://localhost:3000/portal/
echo ======================================
echo.

:: 启动项目
npm run serve

if %errorlevel% neq 0 (
    echo.
    echo 项目启动失败
    pause
    exit /b 1
)

pause
