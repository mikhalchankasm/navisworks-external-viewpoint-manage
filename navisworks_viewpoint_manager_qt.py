#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Navisworks Viewpoint Manager (Qt/PySide6)
Два дерева: слева список всех точек, справа структура (папки/точки).
Поддержка drag&drop между деревьями и внутри правого дерева.
Экспорт сохраняет внутренний XML точек без изменений, модифицируется только группировка.
"""

from __future__ import annotations

import os
import sys
import uuid
import json
from typing import List, Optional, Dict, Tuple
import re

from PySide6 import QtCore, QtGui, QtWidgets
import xml.etree.ElementTree as ET
from xml.dom import minidom


SUPPORTED_LANGUAGES = ['ru', 'en']

LANGUAGE_STRINGS = {
    'ru': {
        'language.label': 'Язык:',
        'language.ru': 'Русский',
        'language.en': 'Английский',
        'window.title': 'Navisworks Viewpoint Manager (Qt)',
        'toolbar.main': 'Основные команды',
        'data.root_folder': 'Корень',
        'structure_source': 'Структура',
        'checkbox.always_on_top': 'Всегда сверху',
        'labels.bulk_names': 'Имена точек (через пробел):',
        'labels.target_folder': 'В папку:',
        'labels.search': 'Поиск точек:',
        'placeholders.bulk_names': 'Вставьте имена, каждое на новой строке',
        'placeholders.search_names': 'например: 1311 1312 1314 ...',
        'placeholders.search_results': 'Результаты поиска...',
        'placeholders.left_filter': 'Фильтр точек (имя или GUID)',
        'buttons.bulk_move': 'Переместить',
        'buttons.clear': 'Очистить',
        'buttons.search': 'Поиск',
        'buttons.copy_results': 'Копировать результаты',
        'tabs.info': 'Инфо',
        'tabs.log': 'Лог',
        'groups.left': 'Все точки обзора',
        'groups.right': 'Структура организации',
        'tree.headers.name': 'Имя точки',
        'tree.headers.file': 'Имя файла',
        'bulk.separator.label': 'Разделители:',
        'bulk.separator.tab': 'Табуляция ↹',
        'bulk.separator.semicolon': 'Точка с запятой ;',
        'bulk.separator.comma': 'Запятая ,',
        'bulk.separator.space': 'Пробел',
        'bulk.separator.other': 'Другой:',
        'bulk.separator.other_placeholder': 'символ',
        'actions.open': 'Загрузить XML...',
        'actions.export': 'Экспорт XML...',
        'actions.exit': 'Выход',
        'actions.new_folder': 'Создать папку',
        'actions.rename': 'Переименовать',
        'actions.delete': 'Удалить',
        'actions.collapse': 'Свернуть все',
        'actions.about': 'О программе',
        'actions.clear_all': 'Очистить всё',
        'actions.clean_names': 'Очистить счётчики в именах',
        'tooltips.collapse': 'Свернуть все папки в структуре',
        'tooltips.clear_all': 'Очистить все загруженные данные и сбросить форму',
        'tooltips.clean_names': 'Убрать счётчики точек из имён папок (например: "ЛКП (213)" → "ЛКП")',
        'menus.file': 'Файл',
        'menus.edit': 'Правка',
        'menus.language': 'Язык',
        'menus.view': 'Вид',
        'menus.help': 'Справка',
        'dialogs.open_xml.title': 'Выберите XML файлы',
        'dialogs.save_xml.title': 'Сохранить XML',
        'input.create_folder.title': 'Создать папку',
        'input.create_folder.label': 'Имя папки:',
        'input.rename.title': 'Переименовать',
        'input.rename.label': 'Новое имя:',
        'messages.delete.title': 'Удалить',
        'messages.delete.body': 'Удалить выбранные элементы?',
        'messages.error.title': 'Ошибка',
        'messages.success.title': 'Готово',
        'messages.empty.title': 'Пусто',
        'messages.empty.body': 'Нет данных для экспорта',
        'messages.save.success': 'Сохранено: {path}',
        'messages.load.error': 'Не удалось загрузить {path}:\n{error}',
        'messages.load.success': 'Загружено файлов: {count}',
        'about.text': 'Navisworks Viewpoint Manager (Qt)\nДва дерева, drag&drop, экспорт XML.',
        'status.search.all_found': 'Все точки найдены',
        'context.sort_menu': 'Сортировка',
        'context.sort_selected_menu': 'Сортировать выделенные',
        'context.sort.nat_asc': 'По-умному A→Z',
        'context.sort.nat_desc': 'По-умному Z→A',
        'context.sort.guid': 'По GUID',
        'context.sort_selected.nat_asc': 'По-умному A→Z (только выделенные)',
        'context.sort_selected.nat_desc': 'По-умному Z→A (только выделенные)',
        'context.sort_selected.guid': 'По GUID (только выделенные)',
        'info.ready': 'Готов к загрузке XML файлов.',
        'defaults.unnamed_view': 'Безымянная точка',
        'tabs.tasks.general': 'Общая',
        'tabs.tasks.general_placeholder': 'Выберите задачу на соседних вкладках или используйте вкладки ниже.',
        'tabs.tasks.move': 'Перемещение точек',
        'tabs.tasks.search': 'Поиск точек',
    },
    'en': {
        'language.label': 'Language:',
        'language.ru': 'Russian',
        'language.en': 'English',
        'window.title': 'Navisworks Viewpoint Manager (Qt)',
        'toolbar.main': 'Main Toolbar',
        'data.root_folder': 'Root',
        'structure_source': 'Structure',
        'checkbox.always_on_top': 'Always on top',
        'labels.bulk_names': 'Viewpoint names (space-separated):',
        'labels.target_folder': 'To folder:',
        'labels.search': 'Find viewpoints:',
        'placeholders.bulk_names': 'Enter one name per line',
        'placeholders.search_names': 'e.g. 1311 1312 1314 ...',
        'placeholders.search_results': 'Search results...',
        'placeholders.left_filter': 'Filter viewpoints (name or GUID)',
        'buttons.bulk_move': 'Move',
        'buttons.clear': 'Clear',
        'buttons.search': 'Find',
        'buttons.copy_results': 'Copy results',
        'tabs.info': 'Info',
        'tabs.log': 'Log',
        'groups.left': 'All viewpoints',
        'groups.right': 'Destination structure',
        'tree.headers.name': 'Viewpoint name',
        'tree.headers.file': 'File name',
        'bulk.separator.label': 'Separators:',
        'bulk.separator.tab': 'Tab ↹',
        'bulk.separator.semicolon': 'Semicolon ;',
        'bulk.separator.comma': 'Comma ,',
        'bulk.separator.space': 'Space',
        'bulk.separator.other': 'Other:',
        'bulk.separator.other_placeholder': 'char',
        'actions.open': 'Load XML...',
        'actions.export': 'Export XML...',
        'actions.exit': 'Exit',
        'actions.new_folder': 'Create folder',
        'actions.rename': 'Rename',
        'actions.delete': 'Delete',
        'actions.collapse': 'Collapse all',
        'actions.about': 'About',
        'actions.clear_all': 'Clear all',
        'actions.clean_names': 'Clean counters in names',
        'tooltips.collapse': 'Collapse all folders in the structure',
        'tooltips.clear_all': 'Clear all loaded data and reset the form',
        'tooltips.clean_names': 'Remove point counters from folder names (e.g. "LKP (213)" → "LKP")',
        'menus.file': 'File',
        'menus.edit': 'Edit',
        'menus.language': 'Language',
        'menus.view': 'View',
        'menus.help': 'Help',
        'dialogs.open_xml.title': 'Select XML files',
        'dialogs.save_xml.title': 'Save XML',
        'input.create_folder.title': 'Create folder',
        'input.create_folder.label': 'Folder name:',
        'input.rename.title': 'Rename',
        'input.rename.label': 'New name:',
        'messages.delete.title': 'Delete',
        'messages.delete.body': 'Delete selected items?',
        'messages.error.title': 'Error',
        'messages.success.title': 'Done',
        'messages.empty.title': 'Empty',
        'messages.empty.body': 'There is no data to export',
        'messages.save.success': 'Saved: {path}',
        'messages.load.error': 'Failed to load {path}:\n{error}',
        'messages.load.success': 'Files loaded: {count}',
        'about.text': 'Navisworks Viewpoint Manager (Qt)\nTwo trees, drag&drop, XML export.',
        'status.search.all_found': 'All viewpoints found',
        'context.sort_menu': 'Sort',
        'context.sort_selected_menu': 'Sort selected',
        'context.sort.nat_asc': 'Natural A→Z',
        'context.sort.nat_desc': 'Natural Z→A',
        'context.sort.guid': 'By GUID',
        'context.sort_selected.nat_asc': 'Natural A→Z (selected only)',
        'context.sort_selected.nat_desc': 'Natural Z→A (selected only)',
        'context.sort_selected.guid': 'By GUID (selected only)',
        'info.ready': 'Ready to load XML files.',
        'defaults.unnamed_view': 'Untitled viewpoint',
        'tabs.tasks.general': 'Overview',
        'tabs.tasks.general_placeholder': 'Select a task on the neighbouring tabs or use the options below.',
        'tabs.tasks.move': 'Move viewpoints',
        'tabs.tasks.search': 'Find viewpoints',
    },
}


MIME_VIEWS = 'application/x-navis-views-json'


class ViewpointItem:
    """Модельный элемент: папка или точка обзора."""

    def __init__(self, name: str, guid: str, xml_content: str = '', is_folder: bool = False, source_file: str = ''):
        self.name = name
        self.guid = guid
        self.xml_content = xml_content
        self.is_folder = is_folder
        self.source_file = source_file  # Имя файла, из которого загружена точка
        self.children: List['ViewpointItem'] = []
        self.parent: Optional['ViewpointItem'] = None

    def add_child(self, child: 'ViewpointItem') -> None:
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: 'ViewpointItem') -> None:
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def find_by_guid(self, guid: str) -> Optional['ViewpointItem']:
        if self.guid == guid:
            return self
        for c in self.children:
            f = c.find_by_guid(guid)
            if f is not None:
                return f
        return None

    def is_ancestor_of(self, node: 'ViewpointItem') -> bool:
        cur = node.parent
        while cur is not None:
            if cur is self:
                return True
            cur = cur.parent
        return False

    def iter_views(self) -> List['ViewpointItem']:
        out: List[ViewpointItem] = []
        if not self.is_folder:
            out.append(self)
        for c in self.children:
            out.extend(c.iter_views())
        return out


class ViewsTree(QtWidgets.QTreeWidget):
    """Базовый QTreeWidget с удобным доступом к модели (через UserRole)."""

    itemActivatedWithModel = QtCore.Signal(ViewpointItem)
    selectionChangedWithModels = QtCore.Signal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setHeaderHidden(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setUniformRowHeights(True)
        self.setAnimated(True)

    def selected_model_items(self) -> List[ViewpointItem]:
        items = []
        for it in self.selectedItems():
            m = it.data(0, QtCore.Qt.UserRole)
            if isinstance(m, ViewpointItem):
                items.append(m)
        return items


class LeftTree(ViewsTree):
    """Левое дерево: источник точек. Разрешен drag только наружу."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setColumnCount(2)
        self.setHeaderHidden(False)
        header = self.header()
        if header is not None:
            header.setSectionsMovable(True)
            header.setStretchLastSection(True)
            mode_enum = getattr(QtWidgets.QHeaderView, 'ResizeMode', QtWidgets.QHeaderView)
            header.setSectionResizeMode(0, mode_enum.Interactive)
            header.setSectionResizeMode(1, mode_enum.Stretch)
        self.setDragEnabled(True)
        self.setAcceptDrops(False)
        self.setDropIndicatorShown(False)

    def startDrag(self, supportedActions: QtCore.Qt.DropActions) -> None:
        selected = self.selectedItems()
        if not selected:
            return
        guids = []
        for it in selected:
            model: ViewpointItem = it.data(0, QtCore.Qt.UserRole)
            if model and not model.is_folder:
                guids.append(model.guid)
        if not guids:
            return
        mime = QtCore.QMimeData()
        mime.setData(MIME_VIEWS, QtCore.QByteArray(json.dumps({
            'source': 'left',
            'guids': guids,
        }).encode('utf-8')))
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime)
        drag.setPixmap(self.viewport().grab())
        drag.exec(QtCore.Qt.CopyAction)


class RightTree(ViewsTree):
    """Правое дерево: структура. Принимает dnd и из себя, и из левого."""

    requestDropFromLeft = QtCore.Signal(list, object)  # guids, target_model
    requestMoveInside = QtCore.Signal(list, object)    # models, target_model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)

    def startDrag(self, supportedActions: QtCore.Qt.DropActions) -> None:
        selected = self.selectedItems()
        if not selected:
            return
        guids = []
        for it in selected:
            model: ViewpointItem = it.data(0, QtCore.Qt.UserRole)
            if model:
                guids.append(model.guid)
        if not guids:
            return
        mime = QtCore.QMimeData()
        mime.setData(MIME_VIEWS, QtCore.QByteArray(json.dumps({
            'source': 'right',
            'guids': guids,
        }).encode('utf-8')))
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime)
        drag.setPixmap(self.viewport().grab())
        drag.exec(QtCore.Qt.MoveAction)

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().hasFormat(MIME_VIEWS):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e: QtGui.QDragMoveEvent) -> None:
        if e.mimeData().hasFormat(MIME_VIEWS):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        if not e.mimeData().hasFormat(MIME_VIEWS):
            e.ignore()
            return
        data = json.loads(bytes(e.mimeData().data(MIME_VIEWS)).decode('utf-8'))
        source = data.get('source')
        guids = data.get('guids') or []

        pos = e.position().toPoint() if hasattr(e, 'position') else e.pos()
        target_item = self.itemAt(pos)
        target_model = target_item.data(0, QtCore.Qt.UserRole) if target_item else None

        if source == 'left':
            self.requestDropFromLeft.emit(guids, target_model)
            e.acceptProposedAction()
        elif source == 'right':
            # Собрать модели выделенных элементов (по guids)
            self.requestMoveInside.emit(guids, target_model)
            e.acceptProposedAction()
        else:
            e.ignore()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1280, 800)
        
        # Убеждаемся, что окно имеет все необходимые флаги
        self.setWindowFlags(
            QtCore.Qt.Window | 
            QtCore.Qt.WindowTitleHint | 
            QtCore.Qt.WindowSystemMenuHint | 
            QtCore.Qt.WindowMinimizeButtonHint | 
            QtCore.Qt.WindowMaximizeButtonHint | 
            QtCore.Qt.WindowCloseButtonHint
        )

        # Данные
        self.current_language = 'ru'
        self.supported_languages = list(SUPPORTED_LANGUAGES)
        self.root_folder = self._create_root_folder()
        self.source_views_by_guid: Dict[str, ViewpointItem] = {}
        self.toolbar_standard_button_width = 160
        self.toolbar_wide_button_width = 240
        self.toolbar_buttons: List[QtWidgets.QToolButton] = []

        # UI
        self._build_ui()
        self._connect_signals()
        self._apply_translations()
        self._set_info_ready_message()

    # UI
    def _build_ui(self):
        # Actions
        self.toolbar_buttons.clear()
        act_open = QtGui.QAction(self)
        act_open.setShortcut('Ctrl+O')
        act_export = QtGui.QAction(self)
        act_export.setShortcut('Ctrl+S')
        act_exit = QtGui.QAction(self)

        act_new_folder = QtGui.QAction(self)
        act_new_folder.setShortcut('Ctrl+N')
        act_rename = QtGui.QAction(self)
        act_rename.setShortcut('F2')
        act_delete = QtGui.QAction(self)
        act_delete.setShortcut(QtGui.QKeySequence.Delete)

        act_collapse = QtGui.QAction(self)
        act_collapse.setShortcut('Ctrl+L')

        act_about = QtGui.QAction(self)
        
        act_clear_all = QtGui.QAction(self)
        
        act_clean_names = QtGui.QAction(self)

        self.actions = {
            'open': act_open,
            'export': act_export,
            'exit': act_exit,
            'new_folder': act_new_folder,
            'rename': act_rename,
            'delete': act_delete,
            'collapse': act_collapse,
            'about': act_about,
            'clear_all': act_clear_all,
            'clean_names': act_clean_names,
        }
        for key, act in self.actions.items():
            act.setObjectName(f'action_{key}')

        menubar = self.menuBar()
        self.menu_file = menubar.addMenu('')
        self.menu_file.addAction(act_open)
        self.menu_file.addAction(act_export)
        self.menu_file.addSeparator()
        self.menu_file.addAction(act_clear_all)
        self.menu_file.addAction(act_clean_names)
        self.menu_file.addSeparator()
        self.menu_file.addAction(act_exit)

        self.menu_edit = menubar.addMenu('')
        self.menu_edit.addAction(act_new_folder)
        self.menu_edit.addAction(act_rename)
        self.menu_edit.addAction(act_delete)

        self.menu_language = menubar.addMenu('')
        self.language_action_group = QtGui.QActionGroup(self)
        self.language_action_group.setExclusive(True)
        self.language_actions: Dict[str, QtGui.QAction] = {}
        for code in self.supported_languages:
            act_lang = QtGui.QAction(self)
            act_lang.setCheckable(True)
            act_lang.triggered.connect(lambda checked, c=code: self.set_language(c) if checked else None)
            self.language_action_group.addAction(act_lang)
            self.menu_language.addAction(act_lang)
            self.language_actions[code] = act_lang

        self.menu_view = menubar.addMenu('')
        self.menu_view.addAction(act_collapse)

        self.menu_help = menubar.addMenu('')
        self.menu_help.addAction(act_about)

        uniform_menu_style = """
            QMenu {
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 18px;
                min-width: 160px;
            }
        """
        for menu in (self.menu_file, self.menu_edit, self.menu_language, self.menu_view, self.menu_help):
            menu.setStyleSheet(uniform_menu_style)

        self.toolbar = self.addToolBar('')
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.setMovable(False)
        self._add_toolbar_button(act_open)
        self._add_toolbar_button(act_export)
        self._add_toolbar_button(act_new_folder)
        self._add_toolbar_button(act_delete)
        self._add_toolbar_button(act_collapse)
        self._add_toolbar_button(act_clean_names, wide=True)
        self.toolbar.addSeparator()
        self.always_on_top_checkbox = QtWidgets.QCheckBox()
        self.always_on_top_checkbox.setChecked(False)
        self.always_on_top_checkbox.toggled.connect(self.toggle_always_on_top)
        self.toolbar_checkbox_action = self.toolbar.addWidget(self.always_on_top_checkbox)
        self._update_toolbar_button_widths()

        # Центральный виджет
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        
        # Основной layout с галочкой сверху справа
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # Основной горизонтальный layout
        h = QtWidgets.QHBoxLayout()
        h.setContentsMargins(6, 6, 6, 6)
        main_layout.addLayout(h)
        splitter_main = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        # Вкладки задач под основными кнопками
        self.tasks_tab = QtWidgets.QTabWidget()

        general_tab = QtWidgets.QWidget()
        general_layout = QtWidgets.QVBoxLayout(general_tab)
        general_layout.setContentsMargins(12, 12, 12, 12)
        self.general_placeholder_label = QtWidgets.QLabel()
        self.general_placeholder_label.setWordWrap(True)
        self.general_placeholder_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        general_layout.addWidget(self.general_placeholder_label)
        general_layout.addStretch()

        move_tab = QtWidgets.QWidget()
        move_layout = QtWidgets.QVBoxLayout(move_tab)
        move_layout.setContentsMargins(12, 12, 12, 12)
        self.bulk_names_label = QtWidgets.QLabel()
        self.bulk_names_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        move_layout.addWidget(self.bulk_names_label)
        self.bulk_names_edit = QtWidgets.QPlainTextEdit()
        self.bulk_names_edit.setTabChangesFocus(False)
        self.bulk_names_edit.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.bulk_names_edit.setFixedHeight(120)
        move_layout.addWidget(self.bulk_names_edit, 1)

        separator_panel = QtWidgets.QWidget()
        separator_layout = QtWidgets.QHBoxLayout(separator_panel)
        separator_layout.setContentsMargins(0, 0, 0, 0)
        separator_layout.setSpacing(12)
        self.separator_label = QtWidgets.QLabel()
        separator_layout.addWidget(self.separator_label)
        self.separator_checks: Dict[str, QtWidgets.QCheckBox] = {}
        column_layout = QtWidgets.QVBoxLayout()
        column_layout.setSpacing(4)
        for key in ('tab', 'semicolon', 'comma', 'space'):
            check = QtWidgets.QCheckBox()
            self.separator_checks[key] = check
            column_layout.addWidget(check)
        self.other_separator_check = QtWidgets.QCheckBox()
        self.other_separator_check.toggled.connect(self._on_other_separator_toggled)
        column_layout.addWidget(self.other_separator_check)
        column_layout.addStretch(1)
        separator_layout.addLayout(column_layout)
        self.separator_check_labels: Dict[str, QtWidgets.QLabel] = {}
        labels_layout = QtWidgets.QVBoxLayout()
        labels_layout.setSpacing(4)
        for key in ('tab', 'semicolon', 'comma', 'space'):
            label = QtWidgets.QLabel()
            label.setMinimumWidth(140)
            label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.separator_check_labels[key] = label
            labels_layout.addWidget(label)
        other_label_layout = QtWidgets.QHBoxLayout()
        other_label_layout.setContentsMargins(0, 0, 0, 0)
        other_label_layout.setSpacing(4)
        self.other_separator_label = QtWidgets.QLabel()
        other_label_layout.addWidget(self.other_separator_label)
        self.other_separator_edit = QtWidgets.QLineEdit()
        self.other_separator_edit.setMaxLength(1)
        self.other_separator_edit.setFixedWidth(40)
        self.other_separator_edit.setEnabled(False)
        other_label_layout.addWidget(self.other_separator_edit)
        other_label_layout.addStretch(1)
        labels_layout.addLayout(other_label_layout)
        labels_layout.addStretch(1)
        separator_layout.addLayout(labels_layout, 1)
        separator_layout.addStretch(1)
        move_layout.addWidget(separator_panel)
        move_layout.addStretch()

        controls_row = QtWidgets.QHBoxLayout()
        controls_row.setSpacing(6)
        self.target_folder_label = QtWidgets.QLabel()
        controls_row.addWidget(self.target_folder_label)
        self.target_folder_combo = QtWidgets.QComboBox()
        self.target_folder_combo.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.target_folder_combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        controls_row.addWidget(self.target_folder_combo, 1)
        self.bulk_move_btn = QtWidgets.QPushButton()
        controls_row.addWidget(self.bulk_move_btn)
        self.clear_button = QtWidgets.QPushButton()
        controls_row.addWidget(self.clear_button)
        controls_row.addStretch(1)
        move_layout.addLayout(controls_row)

        search_tab = QtWidgets.QWidget()
        search_tab_layout = QtWidgets.QVBoxLayout(search_tab)
        search_tab_layout.setContentsMargins(12, 12, 12, 12)
        search_row = QtWidgets.QHBoxLayout()
        search_row.setSpacing(6)
        self.search_label = QtWidgets.QLabel()
        search_row.addWidget(self.search_label)
        self.search_names_edit = QtWidgets.QLineEdit()
        search_row.addWidget(self.search_names_edit, 1)
        self.search_button = QtWidgets.QPushButton()
        search_row.addWidget(self.search_button)
        self.copy_results_button = QtWidgets.QPushButton()
        search_row.addWidget(self.copy_results_button)
        search_tab_layout.addLayout(search_row)
        self.search_results = QtWidgets.QTextEdit()
        self.search_results.setMaximumHeight(100)
        self.search_results.setReadOnly(True)
        search_tab_layout.addWidget(self.search_results)

        self.tasks_tab_general_index = self.tasks_tab.addTab(general_tab, '')
        self.tasks_tab_move_index = self.tasks_tab.addTab(move_tab, '')
        self.tasks_tab_search_index = self.tasks_tab.addTab(search_tab, '')

        v_main = QtWidgets.QVBoxLayout()
        v_main.setContentsMargins(0, 0, 0, 0)
        container = QtWidgets.QWidget()
        container.setLayout(v_main)
        v_main.addWidget(self.tasks_tab)
        v_main.addWidget(splitter_main, 1)
        h.addWidget(container)

        # Левая панель
        self.left_box = QtWidgets.QGroupBox()
        v_left = QtWidgets.QVBoxLayout(self.left_box)
        # Поиск по точкам
        self.left_filter = QtWidgets.QLineEdit()
        self.left_filter.setClearButtonEnabled(True)
        v_left.addWidget(self.left_filter)
        # Дерево всех точек
        self.left_tree = LeftTree()
        self.left_tree.setHeaderLabels(['', ''])
        v_left.addWidget(self.left_tree)

        # Правая панель: вертикальный сплиттер (структура + информация)
        right_container = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        self.struct_box = QtWidgets.QGroupBox()
        v_struct = QtWidgets.QVBoxLayout(self.struct_box)
        self.right_tree = RightTree()
        v_struct.addWidget(self.right_tree)

        # Панель с вкладками: Инфо и Лог
        self.info_log_tabs = QtWidgets.QTabWidget()
        # Инфо
        self.info_text = QtWidgets.QTextEdit()
        self.info_text.setReadOnly(True)
        info_wrap = QtWidgets.QWidget()
        info_layout = QtWidgets.QVBoxLayout(info_wrap)
        info_layout.setContentsMargins(4, 4, 4, 4)
        info_layout.addWidget(self.info_text)
        self.info_tab_index = self.info_log_tabs.addTab(info_wrap, '')
        # Лог
        self.log_text = QtWidgets.QPlainTextEdit()
        self.log_text.setReadOnly(True)
        log_wrap = QtWidgets.QWidget()
        log_layout = QtWidgets.QVBoxLayout(log_wrap)
        log_layout.setContentsMargins(4, 4, 4, 4)
        log_layout.addWidget(self.log_text)
        self.log_tab_index = self.info_log_tabs.addTab(log_wrap, '')

        right_container.addWidget(self.struct_box)
        right_container.addWidget(self.info_log_tabs)
        right_container.setStretchFactor(0, 3)
        right_container.setStretchFactor(1, 1)

        splitter_main.addWidget(self.left_box)
        splitter_main.addWidget(right_container)
        splitter_main.setStretchFactor(0, 1)
        splitter_main.setStretchFactor(1, 2)

        # Контекстное меню для правого дерева
        self.right_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        if self.current_language in self.language_actions:
            action = self.language_actions[self.current_language]
            action.blockSignals(True)
            action.setChecked(True)
            action.blockSignals(False)

    def _on_other_separator_toggled(self, checked: bool) -> None:
        self.other_separator_edit.setEnabled(checked)
        if not checked:
            self.other_separator_edit.clear()

    def _add_toolbar_button(self, action: QtGui.QAction, *, wide: bool = False) -> QtWidgets.QToolButton:
        button = self._create_toolbar_button(action, wide=wide)
        self.toolbar.addWidget(button)
        self.toolbar_buttons.append(button)
        return button

    def _create_toolbar_button(self, action: QtGui.QAction, *, wide: bool = False) -> QtWidgets.QToolButton:
        button = QtWidgets.QToolButton(self.toolbar)
        button.setDefaultAction(action)
        button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        button.setAutoRaise(False)
        button.setFocusPolicy(QtCore.Qt.NoFocus)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button._wide = wide  # type: ignore[attr-defined]
        object_name = action.objectName() or f'action_{id(action)}'
        button.setObjectName(f'btn_{object_name}')
        button.setStyleSheet(
            "QToolButton { padding: 6px 12px; margin: 2px; border: 1px solid #c8c8c8; "
            "border-radius: 6px; background-color: #f7f7f7; }"
            "QToolButton:hover { background-color: #ececec; border-color: #a0a0a0; }"
            "QToolButton:pressed { background-color: #dcdcdc; border-color: #888888; }"
        )
        button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        button.setMinimumHeight(40)
        return button

    def _update_toolbar_button_widths(self) -> None:
        for button in self.toolbar_buttons:
            wide = bool(getattr(button, '_wide', False))
            width = self.toolbar_wide_button_width if wide else self.toolbar_standard_button_width
            button.setFixedWidth(width)

    def _t(self, key: str, **kwargs) -> str:
        lang_map = LANGUAGE_STRINGS.get(self.current_language, {})
        fallback = LANGUAGE_STRINGS.get('en', {})
        text = lang_map.get(key, fallback.get(key, key))
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text

    def _apply_translations(self) -> None:
        self.setWindowTitle(self._t('window.title'))
        self.toolbar.setWindowTitle(self._t('toolbar.main'))

        for key, action in self.actions.items():
            action.setText(self._t(f'actions.{key}'))
        self.actions['collapse'].setToolTip(self._t('tooltips.collapse'))
        self.actions['clear_all'].setToolTip(self._t('tooltips.clear_all'))
        self.actions['clean_names'].setToolTip(self._t('tooltips.clean_names'))

        self.menu_file.setTitle(self._t('menus.file'))
        self.menu_edit.setTitle(self._t('menus.edit'))
        self.menu_language.setTitle(self._t('menus.language'))
        self.menu_view.setTitle(self._t('menus.view'))
        self.menu_help.setTitle(self._t('menus.help'))

        for code, action in self.language_actions.items():
            action.blockSignals(True)
            action.setText(self._t(f'language.{code}'))
            action.setChecked(code == self.current_language)
            action.blockSignals(False)

        self._update_toolbar_button_widths()
        self.tasks_tab.setTabText(self.tasks_tab_general_index, self._t('tabs.tasks.general'))
        self.tasks_tab.setTabText(self.tasks_tab_move_index, self._t('tabs.tasks.move'))
        self.tasks_tab.setTabText(self.tasks_tab_search_index, self._t('tabs.tasks.search'))
        self.general_placeholder_label.setText(self._t('tabs.tasks.general_placeholder'))

        self.always_on_top_checkbox.setText(self._t('checkbox.always_on_top'))
        self.bulk_names_label.setText(self._t('labels.bulk_names'))
        self.bulk_names_edit.setPlaceholderText(self._t('placeholders.bulk_names'))
        self.target_folder_label.setText(self._t('labels.target_folder'))
        self.bulk_move_btn.setText(self._t('buttons.bulk_move'))
        self.clear_button.setText(self._t('buttons.clear'))
        self.separator_label.setText(self._t('bulk.separator.label'))
        separator_keys = ('tab', 'semicolon', 'comma', 'space')
        for key in separator_keys:
            label = self.separator_check_labels[key]
            label.setText(self._t(f'bulk.separator.{key}'))
        self.other_separator_label.setText(self._t('bulk.separator.other'))
        self.other_separator_edit.setPlaceholderText(self._t('bulk.separator.other_placeholder'))

        self.search_label.setText(self._t('labels.search'))
        self.search_names_edit.setPlaceholderText(self._t('placeholders.search_names'))
        self.search_button.setText(self._t('buttons.search'))
        self.copy_results_button.setText(self._t('buttons.copy_results'))
        self.search_results.setPlaceholderText(self._t('placeholders.search_results'))

        self.left_box.setTitle(self._t('groups.left'))
        self.left_filter.setPlaceholderText(self._t('placeholders.left_filter'))
        self.left_tree.setHeaderLabels([
            self._t('tree.headers.name'),
            self._t('tree.headers.file'),
        ])

        self.struct_box.setTitle(self._t('groups.right'))
        self.info_log_tabs.setTabText(self.info_tab_index, self._t('tabs.info'))
        self.info_log_tabs.setTabText(self.log_tab_index, self._t('tabs.log'))

        # Если в информационном окне было сообщение о готовности — обновим его локализацию
        current_info = self.info_text.toPlainText().strip()
        ready_variants = {LANGUAGE_STRINGS[code].get('info.ready') for code in LANGUAGE_STRINGS}
        if current_info in ready_variants:
            self._set_info_ready_message()

    def set_language(self, lang: str) -> None:
        if lang not in LANGUAGE_STRINGS:
            return
        if lang == self.current_language:
            return
        if lang not in self.supported_languages:
            self.supported_languages.append(lang)
        if lang not in self.language_actions:
            act_lang = QtGui.QAction(self)
            act_lang.setCheckable(True)
            act_lang.triggered.connect(lambda checked, c=lang: self.set_language(c) if checked else None)
            self.language_action_group.addAction(act_lang)
            self.menu_language.addAction(act_lang)
            self.language_actions[lang] = act_lang
        self.current_language = lang
        self.root_folder.name = self._t('data.root_folder')
        self._apply_translations()
        self.refresh_trees()

    def _create_root_folder(self) -> ViewpointItem:
        return ViewpointItem(self._t('data.root_folder'), str(uuid.uuid4()), is_folder=True)

    def _set_info_ready_message(self, force: bool = False) -> None:
        ready_text = self._t('info.ready')
        content = self.info_text.toPlainText().strip()
        if force or not content or content in {LANGUAGE_STRINGS[code].get('info.ready') for code in LANGUAGE_STRINGS}:
            self.info_text.clear()
            self.info_text.append(ready_text)

    def _connect_signals(self):
        self.actions['open'].triggered.connect(self.load_xml_files)
        self.actions['export'].triggered.connect(self.export_xml)
        self.actions['exit'].triggered.connect(self.close)
        self.actions['new_folder'].triggered.connect(self.create_folder)
        self.actions['rename'].triggered.connect(self.rename_selected)
        self.actions['delete'].triggered.connect(self.delete_selected)
        self.actions['collapse'].triggered.connect(self.collapse_all)
        self.actions['about'].triggered.connect(self.show_about)
        self.actions['clear_all'].triggered.connect(self.clear_all_data)
        self.actions['clean_names'].triggered.connect(self.clean_folder_names)

        self.left_tree.itemSelectionChanged.connect(self.on_left_select)
        self.right_tree.itemSelectionChanged.connect(self.on_right_select)
        self.right_tree.customContextMenuRequested.connect(self.on_right_context_menu)

        self.right_tree.requestDropFromLeft.connect(self.on_drop_from_left)
        self.right_tree.requestMoveInside.connect(self.on_move_inside_right)

        # Фильтр левого дерева
        self.left_filter.textChanged.connect(self.apply_left_filter)

        # Массовое перемещение по списку
        self.bulk_move_btn.clicked.connect(self.bulk_move_points)
        self.clear_button.clicked.connect(self.clear_mass_move_form)
        
        # Поиск точек
        self.search_button.clicked.connect(self.search_points)
        self.copy_results_button.clicked.connect(self.copy_search_results)

    # Деревья: наполнение/обновление
    def refresh_trees(self):
        # Сохранить состояние правого дерева (раскрытие и выделение)
        right_state = self._save_right_tree_state()

        # Левое
        self.left_tree.clear()
        # Показываем все уникальные точки: из источника и из структуры
        added: set[str] = set()
        for v in self.all_source_views() + self.root_folder.iter_views():
            if v.guid in added:
                continue
            added.add(v.guid)
            # Создаем элемент с двумя колонками: имя точки и файл
            file_name = v.source_file if v.source_file else self._t('structure_source')
            it = QtWidgets.QTreeWidgetItem([f"👁 {v.name}", file_name])
            it.setData(0, QtCore.Qt.UserRole, v)
            self.left_tree.addTopLevelItem(it)
        # Применить активный фильтр, если есть
        if self.left_filter.text().strip():
            self.apply_left_filter(self.left_filter.text())

        # Автоподбор ширины столбцов после загрузки данных
        if self.left_tree.columnCount() >= 1:
            self.left_tree.resizeColumnToContents(0)
        if self.left_tree.columnCount() >= 2:
            self.left_tree.resizeColumnToContents(1)

        # Правое
        self.right_tree.clear()

        def add_node(parent_qitem: Optional[QtWidgets.QTreeWidgetItem], node: ViewpointItem):
            icon = '📁' if node.is_folder else '👁'
            suffix = f" ({self._count_views(node)})" if node.is_folder else ''
            qitem = QtWidgets.QTreeWidgetItem([f"{icon} {node.name}{suffix}"])
            qitem.setData(0, QtCore.Qt.UserRole, node)
            if parent_qitem is None:
                self.right_tree.addTopLevelItem(qitem)
            else:
                parent_qitem.addChild(qitem)
            for c in node.children:
                add_node(qitem, c)

        add_node(None, self.root_folder)
        # Восстановить раскрытия/выделения
        self._restore_right_tree_state(right_state)

        # Обновить список папок в комбобоксе
        self._refresh_folder_combo()

    def _save_right_tree_state(self) -> dict:
        expanded: set[str] = set()
        selected: set[str] = set()

        def walk(item: QtWidgets.QTreeWidgetItem):
            m: ViewpointItem = item.data(0, QtCore.Qt.UserRole)
            if m:
                # В PySide6 используем состояние самого item
                if item.isExpanded():
                    expanded.add(m.guid)
                if item.isSelected():
                    selected.add(m.guid)
            for i in range(item.childCount()):
                walk(item.child(i))

        for i in range(self.right_tree.topLevelItemCount()):
            walk(self.right_tree.topLevelItem(i))
        return {'expanded': expanded, 'selected': selected}

    def _restore_right_tree_state(self, state: dict) -> None:
        if not state:
            return
        expanded: set[str] = state.get('expanded', set())
        selected: set[str] = state.get('selected', set())

        def walk(item: QtWidgets.QTreeWidgetItem):
            m: ViewpointItem = item.data(0, QtCore.Qt.UserRole)
            if m:
                item.setExpanded(m.guid in expanded)
                item.setSelected(m.guid in selected)
            for i in range(item.childCount()):
                walk(item.child(i))

        for i in range(self.right_tree.topLevelItemCount()):
            walk(self.right_tree.topLevelItem(i))

    def _iter_folders(self, node: ViewpointItem, prefix: str = '') -> List[tuple[str, ViewpointItem]]:
        items: List[tuple[str, ViewpointItem]] = []
        if node.is_folder:
            label = f"{prefix}{node.name}"
            items.append((label, node))
            child_prefix = label + '/' if prefix or node.name else ''
            for c in node.children:
                if c.is_folder:
                    items.extend(self._iter_folders(c, child_prefix))
        return items

    def _refresh_folder_combo(self):
        # Сохраняем выбранный guid
        current_guid = None
        idx = self.target_folder_combo.currentIndex()
        if idx >= 0:
            data = self.target_folder_combo.itemData(idx)
            current_guid = data.guid if isinstance(data, ViewpointItem) else None
        self.target_folder_combo.blockSignals(True)
        self.target_folder_combo.clear()
        # Добавим корень явно
        self.target_folder_combo.addItem(self._t('data.root_folder'), self.root_folder)
        for label, folder in self._iter_folders(self.root_folder):
            if folder is self.root_folder:
                continue
            self.target_folder_combo.addItem(label, folder)
        # Подстроить ширину под контент
        self.target_folder_combo.view().setMinimumWidth(self._calc_combo_popup_width())
        # Восстановим выбор
        if current_guid:
            for i in range(self.target_folder_combo.count()):
                v = self.target_folder_combo.itemData(i)
                if isinstance(v, ViewpointItem) and v.guid == current_guid:
                    self.target_folder_combo.setCurrentIndex(i)
                    break
        self.target_folder_combo.blockSignals(False)

    def _calc_combo_popup_width(self) -> int:
        fm = self.target_folder_combo.fontMetrics()
        maxw = 0
        for i in range(self.target_folder_combo.count()):
            text = self.target_folder_combo.itemText(i)
            maxw = max(maxw, fm.horizontalAdvance(text))
        # Немного запас под рамки/скролл
        return maxw + 32

    def bulk_move_points(self):
        text = (self.bulk_names_edit.text() or '').strip()
        if not text:
            return
        tokens = [t for t in text.split() if t]
        idx = self.target_folder_combo.currentIndex()
        target: ViewpointItem = self.target_folder_combo.itemData(idx) if idx >= 0 else self.root_folder
        if not isinstance(target, ViewpointItem):
            target = self.root_folder
        moved = 0
        missing = []
        already = 0
        before = self._count_views(target)
        # Сформируем быстрый поиск: по структуре по имени (с частичным совпадением)
        structure_views = self.root_folder.iter_views()
        name_to_nodes: Dict[str, List[ViewpointItem]] = {}
        for n in structure_views:
            name_lower = (n.name or '').lower()
            name_to_nodes.setdefault(name_lower, []).append(n)
            # Добавляем также поиск по частичному совпадению
            for part in name_lower.replace('_', ' ').replace('-', ' ').replace('.', ' ').split():
                if part and part != name_lower:
                    name_to_nodes.setdefault(part, []).append(n)
        
        # Поиск в источнике по имени (с частичным совпадением)
        source_by_name: Dict[str, List[ViewpointItem]] = {}
        for v in self.source_views_by_guid.values():
            name_lower = (v.name or '').lower()
            source_by_name.setdefault(name_lower, []).append(v)
            # Добавляем также поиск по частичному совпадению
            for part in name_lower.replace('_', ' ').replace('-', ' ').replace('.', ' ').split():
                if part and part != name_lower:
                    source_by_name.setdefault(part, []).append(v)
        for token in tokens:
            key = token.lower()
            matched = False
            # Сначала ищем в структуре
            for node in name_to_nodes.get(key, []):
                matched = True
                # Если уже в целевой папке — пропускаем
                if node.parent is target:
                    already += 1
                    continue
                # Перемещаем
                if node.parent:
                    node.parent.remove_child(node)
                target.add_child(node)
                moved += 1
            if matched:
                continue
            # Затем ищем в источнике (создаём копии)
            found_src = source_by_name.get(key, [])
            if found_src:
                for src in found_src:
                    # Если точка (GUID) уже где-то в структуре — переместим существующую вместо дублирования
                    exist = self.root_folder.find_by_guid(src.guid)
                    if exist is not None:
                        if exist.parent is target:
                            already += 1
                            continue
                        if exist.parent:
                            exist.parent.remove_child(exist)
                        target.add_child(exist)
                        moved += 1
                    else:
                        # Клонируем в целевую папку
                        clone = ViewpointItem(src.name, src.guid, src.xml_content, False)
                        target.add_child(clone)
                        moved += 1
            else:
                missing.append(token)
        self.refresh_trees()
        after = self._count_views(target)
        msg = f"Массовое перемещение в '{target.name}': перемещено {moved}, уже в папке {already}, было {before}, стало {after}"
        if missing:
            msg += f", не найдены: {', '.join(missing)}"
        self.append_log(msg)

    def clear_mass_move_form(self):
        """Очистить форму массового распределения"""
        self.bulk_names_edit.clear()
        self.target_folder_combo.setCurrentIndex(0)

    def search_points(self):
        """Поиск точек и отображение не найденных"""
        text = (self.search_names_edit.text() or '').strip()
        if not text:
            self.search_results.clear()
            return
            
        tokens = [t for t in text.split() if t]
        not_found = []
        
        # Собираем все точки для поиска
        structure_views = list(self.root_folder.iter_views())
        source_views = list(self.source_views_by_guid.values())
        
        # Создаем словари для быстрого поиска (с частичным совпадением)
        structure_names = set()
        source_names = set()
        
        for v in structure_views:
            name_lower = (v.name or '').lower()
            structure_names.add(name_lower)
            # Добавляем частичные совпадения
            for part in name_lower.replace('_', ' ').replace('-', ' ').replace('.', ' ').split():
                if part:
                    structure_names.add(part)
        
        for v in source_views:
            name_lower = (v.name or '').lower()
            source_names.add(name_lower)
            # Добавляем частичные совпадения
            for part in name_lower.replace('_', ' ').replace('-', ' ').replace('.', ' ').split():
                if part:
                    source_names.add(part)
        
        for token in tokens:
            key = token.lower()
            if key not in structure_names and key not in source_names:
                not_found.append(token)
        
        # Формируем результат
        if not_found:
            result_text = '\n'.join(not_found)
            self.search_results.setText(result_text)
            self.append_log(f"Поиск: найдено {len(tokens) - len(not_found)} из {len(tokens)}, не найдено: {len(not_found)}")
        else:
            self.search_results.setText(self._t('status.search.all_found'))
            self.append_log(f"Поиск: все {len(tokens)} точек найдены")

    def copy_search_results(self):
        """Копировать результаты поиска в буфер обмена"""
        text = self.search_results.toPlainText()
        if text:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(text)
            self.append_log(f"Результаты поиска скопированы в буфер обмена ({len(text.splitlines())} строк)")

    def clear_all_data(self):
        """Очистить все данные и сбросить форму к начальному состоянию"""
        # Очищаем все деревья
        self.left_tree.clear()
        self.right_tree.clear()
        
        # Сбрасываем данные
        self.root_folder = self._create_root_folder()
        self.source_views_by_guid.clear()
        
        # Очищаем формы
        self.bulk_names_edit.clear()
        self.search_names_edit.clear()
        self.search_results.clear()
        self.left_filter.clear()
        
        # Сбрасываем комбобокс папок
        self._refresh_folder_combo()
        
        # Очищаем логи
        self.log_text.clear()
        
        # Обновляем информационную панель
        self._set_info_ready_message(force=True)
        
        self.append_log("Все данные очищены. Форма сброшена к начальному состоянию.")

    def toggle_always_on_top(self, checked: bool):
        """Переключить режим 'поверх окон'"""
        # Используем QTimer для отложенного применения изменений
        # Это минимизирует моргание
        
        def apply_changes():
            # Сохраняем текущую позицию и состояние
            geometry = self.geometry()
            was_maximized = self.isMaximized()
            
            if checked:
                # Устанавливаем флаг поверх окон
                flags = (
                    QtCore.Qt.Window | 
                    QtCore.Qt.WindowTitleHint | 
                    QtCore.Qt.WindowSystemMenuHint | 
                    QtCore.Qt.WindowMinimizeButtonHint | 
                    QtCore.Qt.WindowMaximizeButtonHint | 
                    QtCore.Qt.WindowCloseButtonHint |
                    QtCore.Qt.WindowStaysOnTopHint
                )
                self.append_log("Окно установлено поверх других окон")
            else:
                # Убираем флаг поверх окон
                flags = (
                    QtCore.Qt.Window | 
                    QtCore.Qt.WindowTitleHint | 
                    QtCore.Qt.WindowSystemMenuHint | 
                    QtCore.Qt.WindowMinimizeButtonHint | 
                    QtCore.Qt.WindowMaximizeButtonHint | 
                    QtCore.Qt.WindowCloseButtonHint
                )
                self.append_log("Окно больше не поверх других окон")
            
            # Применяем изменения
            self.setWindowFlags(flags)
            
            # Восстанавливаем состояние
            if was_maximized:
                self.showMaximized()
            else:
                self.setGeometry(geometry)
                self.show()
        
        # Откладываем выполнение на следующий цикл событий
        QtCore.QTimer.singleShot(0, apply_changes)

    def clean_folder_names(self):
        """Очистить счётчики точек из имён папок"""
        cleaned_count = 0
        
        def clean_node(node: ViewpointItem):
            nonlocal cleaned_count
            if node.is_folder and node != self.root_folder:
                # Убираем счётчики в скобках в конце имени
                original_name = node.name
                # Паттерн: пробел + (число) в конце строки
                import re
                cleaned_name = re.sub(r'\s*\(\d+\)\s*$', '', original_name).strip()
                if cleaned_name != original_name:
                    node.name = cleaned_name
                    cleaned_count += 1
                    self.append_log(f"Очищено: '{original_name}' → '{cleaned_name}'")
            
            # Рекурсивно обрабатываем дочерние элементы
            for child in node.children:
                clean_node(child)
        
        clean_node(self.root_folder)
        
        if cleaned_count > 0:
            self.refresh_trees()
            self.append_log(f"Очистка завершена. Обработано папок: {cleaned_count}")
        else:
            self.append_log("Счётчики в именах папок не найдены")

    def apply_left_filter(self, text: str):
        t = (text or '').strip().lower()
        for i in range(self.left_tree.topLevelItemCount()):
            it = self.left_tree.topLevelItem(i)
            m: ViewpointItem = it.data(0, QtCore.Qt.UserRole)
            visible = (not t) or (t in (m.name or '').lower()) or (t in (m.source_file or '').lower()) or (t in (m.guid or '').lower())
            it.setHidden(not visible)

    def _count_views(self, node: ViewpointItem) -> int:
        if not node.is_folder:
            return 1
        total = 0
        for c in node.children:
            total += self._count_views(c)
        return total

    # "Человеческая" сортировка
    @staticmethod
    def _natural_key(name: str):
        # Разбить на группы чисел/не-чисел: ['A', 12, '-', 3]
        parts = re.split(r'(\d+)', name or '')
        key = []
        for p in parts:
            if p.isdigit():
                key.append(int(p))
            else:
                key.append(p.lower())
        return key

    def sort_folder(self, folder: ViewpointItem, mode: str = 'nat_asc'):
        if not folder or not folder.is_folder:
            return
        before = len(folder.children)
        if mode == 'guid':
            folder.children.sort(key=lambda x: (x.is_folder, (x.guid or '').lower()))
        else:
            reverse = (mode == 'nat_desc')
            folder.children.sort(key=lambda x: (x.is_folder, self._natural_key(x.name)), reverse=reverse)
        self.refresh_trees()
        self.append_log(f"Сортировка папки '{folder.name}' ({before} элементов) режим: {mode}")

    def sort_selected_points(self, mode: str = 'nat_asc'):
        items = self.right_tree.selectedItems()
        if not items:
            return
        # Группируем выбранные точки по родителям
        parent_to_children: Dict[ViewpointItem, List[ViewpointItem]] = {}
        for it in items:
            m: ViewpointItem = it.data(0, QtCore.Qt.UserRole)
            if not m or m.is_folder or not m.parent:
                continue
            parent_to_children.setdefault(m.parent, []).append(m)
        for parent, children in parent_to_children.items():
            # Сортируем выбранные внутри родителя, остальные остаются на местах
            indexes = [parent.children.index(ch) for ch in children]
            # Подготовим новый порядок выбранных
            if mode == 'guid':
                sorted_sel = sorted(children, key=lambda x: (x.guid or '').lower())
            else:
                reverse = (mode == 'nat_desc')
                sorted_sel = sorted(children, key=lambda x: self._natural_key(x.name), reverse=reverse)
            # Размещаем по тем же индексам
            for idx, ch in zip(sorted(indexes), sorted_sel):
                parent.children[idx] = ch
        self.refresh_trees()
        self.append_log(f"Сортировка выделенных точек: режим {mode}")

    def all_source_views(self) -> List[ViewpointItem]:
        return list(self.source_views_by_guid.values())

    # Загрузка/парсинг
    def load_xml_files(self):
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, self._t('dialogs.open_xml.title'), filter='XML Files (*.xml)')
        if not paths:
            return
        for p in paths:
            try:
                self._load_xml_file(p)
            except Exception as ex:
                QtWidgets.QMessageBox.critical(self, self._t('messages.error.title'), self._t('messages.load.error', path=p, error=ex))
        self.refresh_trees()
        QtWidgets.QMessageBox.information(self, self._t('messages.success.title'), self._t('messages.load.success', count=len(paths)))

    def _load_xml_file(self, file_path: str):
        loaded_points = []  # Список загруженных точек для лога
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            viewpoints = root.find('.//viewpoints')
            if viewpoints is None:
                self.append_log(f"Ошибка: в файле {os.path.basename(file_path)} не найден элемент viewpoints")
                return

            has_folders = any(ch.tag == 'viewfolder' for ch in viewpoints)
            has_views = any(ch.tag == 'view' for ch in viewpoints)

            if has_folders:
                # Импортируем структуру в правое дерево
                file_name = os.path.basename(file_path)
                folder_points = self._process_viewpoint_elements(viewpoints, self.root_folder, file_name)
                loaded_points.extend(folder_points)
            if has_views:
                # Наполняем левое дерево источником
                for ch in viewpoints:
                    if ch.tag == 'view':
                        name = ch.get('name', self._t('defaults.unnamed_view'))
                        guid = ch.get('guid', str(uuid.uuid4()))
                        xml_content = ET.tostring(ch, encoding='unicode')
                        file_name = os.path.basename(file_path)
                        vp = ViewpointItem(name, guid, xml_content, False, file_name)
                        # Всегда обновляем источник (если guid уже встречался, оставим первый экземпляр)
                        if guid not in self.source_views_by_guid:
                            self.source_views_by_guid[guid] = vp
                            loaded_points.append(name)
            
            # Детальный лог загрузки
            if loaded_points:
                self.append_log(f"Загружен файл: {os.path.basename(file_path)}")
                self.append_log(f"Добавлено точек: {len(loaded_points)}")
                if len(loaded_points) <= 10:
                    # Если точек мало, показываем все
                    self.append_log(f"Точки: {', '.join(loaded_points)}")
                else:
                    # Если много, показываем первые 5 и последние 5
                    first_five = loaded_points[:5]
                    last_five = loaded_points[-5:]
                    self.append_log(f"Точки (первые 5): {', '.join(first_five)}")
                    self.append_log(f"Точки (последние 5): {', '.join(last_five)}")
                    self.append_log(f"... и ещё {len(loaded_points) - 10} точек")
            else:
                self.append_log(f"Загружен файл: {os.path.basename(file_path)} (точки не найдены)")
                
        except ET.ParseError as e:
            self.append_log(f"Ошибка парсинга XML в файле {os.path.basename(file_path)}: {e}")
        except Exception as e:
            self.append_log(f"Ошибка загрузки файла {os.path.basename(file_path)}: {e}")

    def _process_viewpoint_elements(self, parent_element: ET.Element, parent_item: ViewpointItem, source_file: str = ''):
        loaded_points = []
        
        for el in parent_element:
            if el.tag == 'viewfolder':
                name = el.get('name', 'Папка')
                guid = el.get('guid', str(uuid.uuid4()))
                folder = ViewpointItem(name, guid, is_folder=True, source_file=source_file)
                parent_item.add_child(folder)
                folder_points = self._process_viewpoint_elements(el, folder, source_file)
                loaded_points.extend(folder_points)
            elif el.tag == 'view':
                name = el.get('name', 'Точка')
                guid = el.get('guid', str(uuid.uuid4()))
                xml_content = ET.tostring(el, encoding='unicode')
                vp = ViewpointItem(name, guid, xml_content, False, source_file)
                parent_item.add_child(vp)
                loaded_points.append(name)
        
        return loaded_points

    # DnD обработчики
    def on_drop_from_left(self, guids: List[str], target_model: Optional[ViewpointItem]):
        if target_model is not None and not target_model.is_folder:
            target_model = target_model.parent
        if target_model is None:
            target_model = self.root_folder
        # Добавить копии точек (без дубликатов guid в структуре)
        added = 0
        for g in guids:
            src = self.source_views_by_guid.get(g)
            if not src:
                continue
            if self.root_folder.find_by_guid(g) is not None:
                # Уже присутствует где-то в структуре — пропускаем
                continue
            clone = ViewpointItem(src.name, src.guid, src.xml_content, False, src.source_file)
            target_model.add_child(clone)
            added += 1
        self.refresh_trees()
        if added:
            before = self._count_views(target_model)
            # после refresh модель не изменилась, recount
            after = self._count_views(target_model)
            self.append_log(f"Перемещено {added} точек в папку '{target_model.name}'. Было: {before - added}, стало: {after}")

    def on_move_inside_right(self, guids: List[str], target_model: Optional[ViewpointItem]):
        if target_model is not None and not target_model.is_folder:
            target_model = target_model.parent
        if target_model is None:
            target_model = self.root_folder
        # Переместить модели внутри структуры (по выделению правого дерева)
        moving: List[ViewpointItem] = []
        for it in self.right_tree.selectedItems():
            m: ViewpointItem = it.data(0, QtCore.Qt.UserRole)
            if m and m is not self.root_folder:
                moving.append(m)
        # Фильтр: нельзя перемещать папку в собственного потомка
        moved = 0
        before = self._count_views(target_model)
        for node in moving:
            if node is target_model or node.is_ancestor_of(target_model):
                continue
            if node.parent:
                node.parent.remove_child(node)
            target_model.add_child(node)
            moved += 1
        self.refresh_trees()
        if moved:
            after = self._count_views(target_model)
            self.append_log(f"Перемещено {moved} элементов в папку '{target_model.name}'. Было: {before}, стало: {after}")

    def append_log(self, line: str):
        self.log_text.appendPlainText(line)

    def collapse_all(self):
        self.right_tree.collapseAll()

    # Правка
    def create_folder(self):
        name, ok = QtWidgets.QInputDialog.getText(self, self._t('input.create_folder.title'), self._t('input.create_folder.label'))
        if not ok or not name:
            return
        sel = self.right_tree.selectedItems()
        parent_model: Optional[ViewpointItem] = None
        if sel:
            m = sel[0].data(0, QtCore.Qt.UserRole)
            parent_model = m if m.is_folder else m.parent
        if parent_model is None:
            parent_model = self.root_folder
        new_folder = ViewpointItem(name, str(uuid.uuid4()), is_folder=True)
        parent_model.add_child(new_folder)
        self.refresh_trees()

    def delete_selected(self):
        sel = self.right_tree.selectedItems()
        if not sel:
            return
        if QtWidgets.QMessageBox.question(self, self._t('messages.delete.title'), self._t('messages.delete.body')) != QtWidgets.QMessageBox.Yes:
            return
        # Удаляем только из структуры
        for it in sel:
            m: ViewpointItem = it.data(0, QtCore.Qt.UserRole)
            if m is self.root_folder:
                continue
            if m.parent:
                m.parent.remove_child(m)
        self.refresh_trees()

    def rename_selected(self):
        sel = self.right_tree.selectedItems()
        if not sel:
            return
        it = sel[0]
        m: ViewpointItem = it.data(0, QtCore.Qt.UserRole)
        new_name, ok = QtWidgets.QInputDialog.getText(self, self._t('input.rename.title'), self._t('input.rename.label'), text=m.name)
        if ok and new_name:
            m.name = new_name
            self.refresh_trees()

    # Контекстное меню правого дерева
    def on_right_context_menu(self, pos: QtCore.QPoint):
        it = self.right_tree.itemAt(pos)
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.actions['new_folder'])
        sort_menu = menu.addMenu(self._t('context.sort_menu'))
        a_nat_asc = sort_menu.addAction(self._t('context.sort.nat_asc'))
        a_nat_desc = sort_menu.addAction(self._t('context.sort.nat_desc'))
        a_guid = sort_menu.addAction(self._t('context.sort.guid'))
        # Сортировка только выделенных точек
        sort_sel_menu = menu.addMenu(self._t('context.sort_selected_menu'))
        as_nat_asc = sort_sel_menu.addAction(self._t('context.sort_selected.nat_asc'))
        as_nat_desc = sort_sel_menu.addAction(self._t('context.sort_selected.nat_desc'))
        as_guid = sort_sel_menu.addAction(self._t('context.sort_selected.guid'))
        if it is not None:
            menu.addAction(self.actions['rename'])
            menu.addAction(self.actions['delete'])
        chosen = menu.exec(self.right_tree.viewport().mapToGlobal(pos))
        if chosen in (a_nat_asc, a_nat_desc, a_guid):
            # определим контекст (папка или точки)
            folder_model: Optional[ViewpointItem] = None
            items = self.right_tree.selectedItems()
            if items:
                m: ViewpointItem = items[0].data(0, QtCore.Qt.UserRole)
                folder_model = m if m and m.is_folder else (m.parent if m else None)
            if folder_model is None:
                folder_model = self.root_folder
            self.sort_folder(folder_model, mode=('nat_asc' if chosen is a_nat_asc else 'nat_desc' if chosen is a_nat_desc else 'guid'))
        elif chosen in (as_nat_asc, as_nat_desc, as_guid):
            mode = ('nat_asc' if chosen is as_nat_asc else 'nat_desc' if chosen is as_nat_desc else 'guid')
            self.sort_selected_points(mode)

    # Выбор элементов -> показать инфо
    def on_left_select(self):
        models = self.left_tree.selected_model_items()
        self._show_info(models[:1])

    def on_right_select(self):
        models = self.right_tree.selected_model_items()
        self._show_info(models[:1])

    def _show_info(self, models: List[ViewpointItem]):
        if not models:
            self.info_text.clear()
            return
        m = models[0]
        lines = [f"Тип: {'Папка' if m.is_folder else 'Точка обзора'}",
                 f"Имя: {m.name}",
                 f"GUID: {m.guid}"]
        if not m.is_folder and m.xml_content:
            preview = m.xml_content if len(m.xml_content) <= 800 else m.xml_content[:800] + '...'
            lines.append('\nXML:\n' + preview)
        self.info_text.setPlainText('\n'.join(lines))

    # Экспорт
    def export_xml(self):
        if not self.root_folder.children:
            QtWidgets.QMessageBox.warning(self, self._t('messages.empty.title'), self._t('messages.empty.body'))
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, self._t('dialogs.save_xml.title'), filter='XML Files (*.xml)')
        if not path:
            return
        try:
            self._create_export_xml(path)
            QtWidgets.QMessageBox.information(self, self._t('messages.success.title'), self._t('messages.save.success', path=path))
        except Exception as ex:
            QtWidgets.QMessageBox.critical(self, self._t('messages.error.title'), str(ex))

    def _create_export_xml(self, file_path: str):
        exchange = ET.Element('exchange')
        exchange.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        exchange.set('xsi:noNamespaceSchemaLocation',
                     'http://download.autodesk.com/us/navisworks/schemas/nw-exchange-12.0.xsd')
        exchange.set('units', 'm')
        exchange.set('filename', 'merged_viewpoints.nwd')
        exchange.set('filepath', '')

        viewpoints = ET.SubElement(exchange, 'viewpoints')

        def add_node_xml(parent_xml: ET.Element, node: ViewpointItem):
            if node.is_folder:
                # Имя папки + количество точек в скобках
                folder = ET.SubElement(parent_xml, 'viewfolder')
                count = self._count_views(node)
                folder_name = f"{node.name} ({count})"
                folder.set('name', folder_name)
                folder.set('guid', node.guid)
                for c in node.children:
                    add_node_xml(folder, c)
            else:
                if node.xml_content:
                    try:
                        el = ET.fromstring(node.xml_content)
                        el.set('name', node.name)
                        el.set('guid', node.guid)
                        parent_xml.append(el)
                    except ET.ParseError:
                        view = ET.SubElement(parent_xml, 'view')
                        view.set('name', node.name)
                        view.set('guid', node.guid)

        # Добавляем только содержимое корня (не сам корень как папку)
        for c in self.root_folder.children:
            add_node_xml(viewpoints, c)

        rough = ET.tostring(exchange, encoding='unicode')
        xml = minidom.parseString(rough).toprettyxml(indent='  ')
        lines = [ln for ln in xml.split('\n') if ln.strip()]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    # About
    def show_about(self):
        QtWidgets.QMessageBox.information(self, self._t('actions.about'), self._t('about.text'))


def main():
    app = QtWidgets.QApplication(sys.argv)
    # Увеличим базовый шрифт на 1 pt
    font = app.font()
    font.setPointSize(font.pointSize() + 1)
    app.setFont(font)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()


