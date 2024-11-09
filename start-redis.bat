@echo off
echo Starting Redis Server...

:: Проверяем, запущен ли уже Redis
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Redis is already running
    exit /b
)

:: Останавливаем существующий процесс Redis если есть
call redis-kill.bat

:: Ждем 2 секунды
timeout /t 2 /nobreak

:: Запускаем Redis напрямую без конфигурационного файла
"C:\Program Files\Redis\redis-server.exe"

echo Redis server started