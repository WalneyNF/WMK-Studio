@echo off
setlocal
cd /d "%~dp0"
echo WMK Data Studio / SQLite
echo Abra http://127.0.0.1:3366/
python "%~dp0tools\wmk-data-studio\server.py" --port 3366
if errorlevel 1 (
 echo Verifique se Python esta instalado e se a porta 3366 esta livre.
 pause
)
