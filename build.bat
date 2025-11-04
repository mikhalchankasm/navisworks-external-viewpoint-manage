@echo off
echo === Сборка Navisworks Viewpoint Manager в exe ===
echo.

REM Установка PyInstaller если нужно
pip install PyInstaller

REM Сборка exe
pyinstaller --onefile --windowed --name="Navisworks Viewpoint Manager" navisworks_viewpoint_manager_qt.py

echo.
echo Сборка завершена! exe файл находится в папке dist/
pause
