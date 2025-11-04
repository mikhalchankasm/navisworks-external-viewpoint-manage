# Сборка Navisworks Viewpoint Manager в exe

## Быстрая сборка (Windows)

1. **Запусти `build.bat`** - двойной клик по файлу
2. Дождись завершения сборки
3. exe файл будет в папке `dist/`

## Ручная сборка

### 1. Установка PyInstaller
```bash
pip install PyInstaller
```

### 2. Сборка exe файла
```bash
pyinstaller --onefile --windowed --name="Navisworks Viewpoint Manager" navisworks_viewpoint_manager_qt.py
```

### 3. Результат
- exe файл: `dist/Navisworks Viewpoint Manager.exe`
- Размер: ~50-80 МБ (зависит от версии Python и PySide6)

## Дополнительные опции

### С иконкой (если есть icon.ico):
```bash
pyinstaller --onefile --windowed --icon=icon.ico --name="Navisworks Viewpoint Manager" navisworks_viewpoint_manager_qt.py
```

### С очисткой временных файлов:
```bash
pyinstaller --onefile --windowed --clean --name="Navisworks Viewpoint Manager" navisworks_viewpoint_manager_qt.py
```

### С дополнительными скрытыми импортами:
```bash
pyinstaller --onefile --windowed --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --hidden-import=PySide6.QtWidgets --name="Navisworks Viewpoint Manager" navisworks_viewpoint_manager_qt.py
```

## Структура файлов после сборки

```
NW_vp_master/
├── navisworks_viewpoint_manager_qt.py    # Исходный код
├── build_exe.py                          # Скрипт сборки
├── build.bat                             # Быстрая сборка для Windows
├── dist/
│   └── Navisworks Viewpoint Manager.exe  # Готовый exe файл
└── build/                                # Временные файлы (можно удалить)
```

## Примечания

- exe файл содержит все необходимые библиотеки
- Не требует установки Python на целевом компьютере
- Запускается на любом Windows 10/11
- Первый запуск может быть медленнее (распаковка)
