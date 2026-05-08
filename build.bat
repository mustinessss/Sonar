@echo off
echo ========================================
echo  Сборка SonarRadar.exe
echo ========================================

echo.
echo [1/3] Установка зависимостей...
pip install pyserial pyinstaller --quiet
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: не удалось установить зависимости.
    echo Убедитесь что Python установлен и доступен в PATH.
    pause
    exit /b 1
)

echo.
echo [2/3] Сборка исполняемого файла...
pyinstaller radar.spec --noconfirm --clean
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: сборка не удалась.
    pause
    exit /b 1
)

echo.
echo [3/3] Готово!
echo Файл: dist\SonarRadar.exe
echo.
pause
