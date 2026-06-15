@echo off
echo Starting Chrome debug mode for AI Assistant...
start \"\" \"C:\Program Files\Google\Chrome\Application\chrome.exe\" --remote-debugging-port=9222 --user-data-dir=\"D:\wechat-bot-chrome-profile\" --no-first-run
echo Chrome started on port 9222
pause
