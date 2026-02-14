@echo off
echo ========================================================
echo   TEJAS - DUAL DOMAIN MODE (Fixed n8n + Random Web)
echo ========================================================

cd /d "C:\Users\shrav\DEV_WORKSPACE\Projects\Tejas\Tejas_AI_Powered_Fake_News_Detection_Application-main"

REM --- 1. Check Docker ---
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop is not running.
    pause
    exit /b
)

REM --- 2. Start Services (Fast) ---
echo.
echo [1/3] Starting Services...
docker compose up -d

REM --- 3. Restart Ngrok ---
echo.
echo [2/3] Starting Dual Tunnels...
taskkill /F /IM ngrok.exe >nul 2>&1
start "" cmd /k ngrok start --all --config=ngrok.yml

REM --- 4. Fetch Random URL ---
echo.
echo [3/3] Fetching Website URL...
timeout /t 5 >nul

set WEB_URL=
for /f "delims=" %%i in ('
curl -s http://127.0.0.1:4040/api/tunnels ^| powershell -Command ^
"$t=$input|ConvertFrom-Json; ($t.tunnels | Where-Object {$_.config.addr -match '8080'}).public_url"
') do set WEB_URL=%%i

echo.
echo ========================================================
echo   SYSTEM IS LIVE!
echo ========================================================
echo.
echo   [1] n8n EDITOR (Fixed):
echo       https://interlacustrine-candace-pleasedly.ngrok-free.dev
echo.
echo   [2] PUBLIC WEBSITE (Random):
echo       %WEB_URL%
echo.
echo ========================================================
echo   Opening Website...

if "%WEB_URL%"=="" (
    echo [WARNING] Could not find Website URL. Check Ngrok window.
) else (
    start "" "%WEB_URL%"
)

pause