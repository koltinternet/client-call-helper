@echo off

rem Переключает кодировку вывода командной строки
rem на используемую Windows, для поддержки
rem кириллицы, если эта кодировка не используется
rem по умолчанию.
for /f "tokens=2 delims=:" %%a in ('chcp') do set /a codepage=%%a
if not %codepage% == 65001 (
	chcp 65001
)

set conemu_url=https://github.com/Maximus5/ConEmu/releases
set python_exe=https://www.python.org/downloads/

where ConEmu64.exe >nul 2>&1 || (
	echo Не обнаружен консольный эмулятор ConEmu. Открывается браузер со страницей скачивания ...
	echo %conemu_url%
    start %conemu_url%
	
	echo Установите эмулятор и заново выполните этот скрипт.
	echo Нажмите любую клавишу чтобы продолжить.
    pause >nul
    exit 
)

where python >nul 2>&1 || (
    echo Интерпретатор Python не установлен. Открывается браузер со страницей скачивания ...
	echo %python_exe%
    start %python_exe%
	
	echo Установите интерпретатор Python и заново выполните этот скрипт.
	echo Нажмите любую клавишу чтобы продолжить.
    pause >nul
    exit
)

echo Создание виртуального окружения ...
py -m venv venv

echo Активация виртуального окружения ...
call venv\Scripts\activate.bat

echo Upgrade pip ...
py -m pip install --upgrade pip

echo Установка зависимостей ...
pip install -r requirements.txt
