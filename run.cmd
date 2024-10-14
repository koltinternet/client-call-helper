@echo off

for /f "tokens=2 delims=:" %%a in ('chcp') do set /a codepage=%%a
if not %codepage% == 65001 (
	chcp 65001
)

rem Запускает main.py в виртуальном окружении
if "%VIRTUAL_ENV%" == "" (
    echo Активация виртуального окружения
	call venv\Scripts\activate.bat
)

echo Запуск программы
py main.py
