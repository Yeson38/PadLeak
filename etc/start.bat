@echo off
chcp 65001 >nul


openfiles >nul 2>&1
if %errorlevel% neq 0 (
    pause
    exit /b
)


netsh wlan set hostednetwork mode=allow ssid=FreeWiFi key=12345678


netsh wlan start hostednetwork
if %errorlevel% neq 0 (
    pause
    exit /b
)

for /f "tokens=*" %%i in ('netsh interface show interface ^| findstr "本地连接" ^| findstr "*"') do (
    netsh interface ip set address name="%%i" static 192.168.137.1 255.255.255.0
)


pause