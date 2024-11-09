@echo off
echo Stopping Redis Server...

:: Проверяем права администратора
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Please run as Administrator
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

:: Останавливаем процесс Redis
taskkill /F /IM redis-server.exe 2>NUL
if %ERRORLEVEL% EQU 0 (
    echo Redis server stopped successfully
) else (
    echo Redis server is not running
)

:: Удаляем службу Redis если она существует
sc query Redis >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    sc stop Redis
    sc delete Redis
    echo Redis service removed
)

pause
