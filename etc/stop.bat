@echo off
chcp 65001 >nul
title 停止WiFi热点

openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 请右键以管理员身份运行此脚本！
    pause
    exit /b
)

echo.
echo 正在停止热点...
netsh wlan stop hostednetwork
echo.
echo 热点已停止。
pause