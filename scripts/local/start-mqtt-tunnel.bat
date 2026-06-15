@echo off
REM === {AI_NAME} MQTT SSH 隧道启动器 ===
REM 建立本地到云端的 MQTT 加密通道 (Clash 不会拦截 SSH)

set SSH_KEY=%USERPROFILE%\.ssh\cloud_{project_name}
set CLOUD_HOST=<YOUR_SERVER_IP>
set LOCAL_PORT=1885

echo ========================================
echo   {AI_NAME} MQTT SSH 隧道
echo   %LOCAL_PORT% --^> %CLOUD_HOST%:1883
echo ========================================
echo.

REM 检查是否已有隧道
netstat -an | findstr ":%LOCAL_PORT% " | findstr "LISTENING" >nul
if %ERRORLEVEL%==0 (
    echo [警告] 端口 %LOCAL_PORT% 已被占用，可能在运行中
    echo 如需重启，请先关掉占用的进程，或修改 LOCAL_PORT
    pause
    exit /b 0
)

echo 正在建立隧道...
ssh -N -L %LOCAL_PORT%:localhost:1883 -i "%SSH_KEY%" -o StrictHostKeyChecking=no -o ServerAliveInterval=60 <YOUR_SSH_USER>@%CLOUD_HOST%

echo.
echo 隧道已断开。
pause
