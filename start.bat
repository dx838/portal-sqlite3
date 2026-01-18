@echo off
chcp 65001 >nul

echo ======================================
echo Portal��Ŀ�����ű�
echo ======================================
echo.

:: ���Node.js�Ƿ�װ
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ����δ��װNode.js
    echo ���Ȱ�װNode.js 24����߰汾
    pause
    exit /b 1
)

echo �Ѱ�װNode.js��
node --version
echo.

:: ���npm�Ƿ�װ
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ����δ��װnpm
    echo ���Ȱ�װnpm
    pause
    exit /b 1
)

echo �Ѱ�װnpm��
npm --version
echo.

:: ���node_modules�Ƿ����
if not exist "node_modules" (
    echo ���ڰ�װ����...
    npm install
    if %errorlevel% neq 0 (
        echo ���󣺰�װ����ʧ��
        pause
        exit /b 1
    )
    echo ������װ�ɹ�
    echo.
)

:: ����TypeScript����
echo ���ڱ���TypeScript����...
npm run build
if %errorlevel% neq 0 (
    echo ���󣺱���ʧ��
    pause
    exit /b 1
)
echo ����ɹ�

echo.
echo ======================================
echo ����������Ŀ...
echo ���ʵ�ַ��http://localhost:3000
echo ======================================
echo.

:: ������Ŀ
npm run serve

if %errorlevel% neq 0 (
    echo.
    echo ������Ŀ����ʧ��
    pause
    exit /b 1
)

pause
