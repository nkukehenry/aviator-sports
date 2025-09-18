@echo off
echo 🚀 Starting Event-Driven WebSocket Server...
echo.
echo Server will start on: http://localhost:5000
echo WebSocket endpoint: ws://localhost:5000/socket.io/
echo.
echo Open these test UIs in your browser:
echo 1. event_driven_test_ui.html (Performance Test UI)
echo 2. enhanced_events_ui.html (Full Events UI)
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
python websocket_main.py

pause
