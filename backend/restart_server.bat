@echo off
echo Stopping any running Python processes...
taskkill /f /im python.exe 2>nul

echo Starting event-driven WebSocket server...
cd /d "%~dp0"
python websocket_main.py

pause

