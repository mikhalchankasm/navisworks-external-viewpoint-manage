#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для сборки Navisworks Viewpoint Manager в единый exe файл
"""

import subprocess
import sys
import os

def build_exe():
    """Собрать exe файл с помощью PyInstaller"""
    
    # Проверяем, установлен ли PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller не установлен. Устанавливаю...")
        subprocess.run([sys.executable, "-m", "pip", "install", "PyInstaller"])
    
    # Команда для сборки
    cmd = [
        "pyinstaller",
        "--onefile",                    # Создать один exe файл
        "--windowed",                   # Без консоли (GUI приложение)
        "--name=Navisworks Viewpoint Manager",  # Имя exe файла
        "--icon=icon.ico",              # Иконка (если есть)
        "--add-data=requirements.txt;.", # Включить requirements.txt
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
        print("✅ Сборка успешно завершена!")
        print(f"exe файл создан в папке: dist/")
        print(f"Имя файла: Navisworks Viewpoint Manager.exe")
        
        # Показываем размер файла
        exe_path = "dist/Navisworks Viewpoint Manager.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"Размер файла: {size_mb:.1f} МБ")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при сборке: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Сборка Navisworks Viewpoint Manager в exe ===")
    
    # Проверяем наличие основного файла
    if not os.path.exists("navisworks_viewpoint_manager_qt.py"):
        print("❌ Файл navisworks_viewpoint_manager_qt.py не найден!")
        sys.exit(1)
    
    success = build_exe()
    
    if success:
        print("\n🎉 Сборка завершена успешно!")
        print("exe файл находится в папке dist/")
    else:
        print("\n💥 Сборка не удалась!")
        sys.exit(1)
