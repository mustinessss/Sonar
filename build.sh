#!/bin/bash
echo "========================================"
echo " Сборка SonarRadar (Linux / macOS)"
echo "========================================"

echo ""
echo "[1/3] Установка зависимостей..."
pip install pyserial pyinstaller --quiet || { echo "ОШИБКА: pip не найден"; exit 1; }

echo ""
echo "[2/3] Сборка исполняемого файла..."
pyinstaller radar.spec --noconfirm --clean || { echo "ОШИБКА: сборка не удалась"; exit 1; }

echo ""
echo "[3/3] Готово!"
echo "Файл: dist/SonarRadar"
