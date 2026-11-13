@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul && (py -3 dot2_cues.py list) || (python dot2_cues.py list)
pause
