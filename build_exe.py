#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для сборки Navisworks Viewpoint Manager в единый exe файл
"""

import subprocess
import sys
import os
import io

# Настройка кодировки для Windows консоли
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from version import __version__
except ImportError:
    __version__ = "1.0.0"

def build_exe():
    """Собрать exe файл с помощью PyInstaller"""
    
    # Проверяем, установлен ли PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller не установлен. Устанавливаю...")
        subprocess.run([sys.executable, "-m", "pip", "install", "PyInstaller"])
    
    # Имя exe файла с версией
    exe_name = f"Navisworks Viewpoint Manager v{__version__}"
    
    # Команда для сборки
    cmd = [
        "pyinstaller",
        "--onefile",                    # Создать один exe файл
        "--windowed",                   # Без консоли (GUI приложение)
        f"--name={exe_name}",           # Имя exe файла с версией
        "--icon=icon.ico",              # Иконка (если есть)
        "--add-data=requirements.txt;.", # Включить requirements.txt
        "--add-data=version.py;.",      # Включить version.py
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui", 
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=xml.etree.ElementTree",
        "--hidden-import=xml.dom.minidom",
        "--hidden-import=uuid",
        "--hidden-import=os",
        "--hidden-import=re",
        "--hidden-import=json",
        "navisworks_viewpoint_manager_qt.py"
    ]
    
    # Удаляем параметр с иконкой, если файла нет
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    print("Сборка exe файла...")
    print(f"Команда: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("[OK] Сборка успешно завершена!")
        print(f"exe файл создан в папке: dist/")
        print(f"Имя файла: {exe_name}.exe")
        print(f"Версия: {__version__}")
        
        # Показываем размер файла
        exe_path = f"dist/{exe_name}.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"Размер файла: {size_mb:.1f} МБ")
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка при сборке: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Сборка Navisworks Viewpoint Manager в exe ===")
    
    # Проверяем наличие основного файла
    if not os.path.exists("navisworks_viewpoint_manager_qt.py"):
        print("[ERROR] Файл navisworks_viewpoint_manager_qt.py не найден!")
        sys.exit(1)
    
    success = build_exe()
    
    if success:
        print("\n[SUCCESS] Сборка завершена успешно!")
        print("exe файл находится в папке dist/")
    else:
        print("\n[FAILED] Сборка не удалась!")
        sys.exit(1)
