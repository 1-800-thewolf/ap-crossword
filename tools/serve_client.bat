@echo off
rem Serves the crossword web client to phones on your Wi-Fi.
rem Open the http:// address printed below in Safari/Chrome on your phone.
setlocal
cd /d "%~dp0..\client"
echo On your phone (same Wi-Fi), open one of these:
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /c:"IPv4"') do for /f "tokens=*" %%B in ("%%A") do echo    http://%%B:8123/
echo.
echo If Windows asks about the firewall, allow Private networks.
echo Leave this window open while playing. Ctrl+C to stop.
echo.
py -m http.server 8123
pause
