"""
Базовый интерфейс: главное окно, меню, тулбар, сетка.
"""
import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar, QMenuBar, QMenu,
    QWidget, QGridLayout, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QSize
from config import CELL_SIZE, DEFAULT_ROWS, DEFAULT_COLS

class CellButton(QPushButton):
    def __init__(self, row: int, col: int) -> None:
        super().__init__()
        self.row = row
        self.col = col
        self.setFixedSize(CELL_SIZE, CELL_SIZE)
        self.setStyleSheet("QPushButton { background-color: #c0c0c0; border: 1px solid #808080; }")

class MineField(QWidget):
    def __init__(self, rows: int = DEFAULT_ROWS, cols: int = DEFAULT_COLS,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.rows = rows
        self.cols = cols
        self.buttons: list[list[CellButton]] = []
        self.init_ui()

    def init_ui(self) -> None:
        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.buttons = []
        for r in range(self.rows):
            row_btns = []
            for c in range(self.cols):
                btn = CellButton(r, c)
                btn.clicked.connect(lambda _, r=r, c=c: self._on_cell_click(r, c))
                layout.addWidget(btn, r, c)
                row_btns.append(btn)
            self.buttons.append(row_btns)
        self.setLayout(layout)
        self.setFixedSize(self.cols * CELL_SIZE, self.rows * CELL_SIZE)

    def _on_cell_click(self, row: int, col: int) -> None:
        print(f"Click ({row}, {col})")

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Сапёр")
        self.field = MineField(DEFAULT_ROWS, DEFAULT_COLS, parent=self)
        self.setCentralWidget(self.field)
        self._create_toolbar()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к игре")
        self._create_menu()
        self._adjust_size()

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Основная")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        new_action = QAction("Новая игра", self)
        new_action.triggered.connect(self.new_game)
        toolbar.addAction(new_action)

        diff_action = QAction("Сложность", self)
        diff_action.triggered.connect(self._show_difficulty_menu)
        toolbar.addAction(diff_action)

        toolbar.addSeparator()
        self.mines_label = QLabel("💣 10")
        self.timer_label = QLabel("⏱ 000")
        toolbar.addWidget(self.mines_label)
        toolbar.addWidget(self.timer_label)

    def _create_menu(self) -> None:
        menubar = self.menuBar()
        game_menu = menubar.addMenu("Игра")

        new_action = QAction("Новая игра", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_game)
        game_menu.addAction(new_action)

        game_menu.addSeparator()
        diff_menu = QMenu("Сложность", self)
        for name, r, c, m in [("Новичок (9×9, 10 м)", 9, 9, 10),
                              ("Любитель (16×16, 40 м)", 16, 16, 40),
                              ("Профессионал (30×16, 99 м)", 16, 30, 99)]:
            action = QAction(name, self)
            action.triggered.connect(lambda _, r=r, c=c, m=m: self.set_difficulty(r, c, m))
            diff_menu.addAction(action)
        game_menu.addMenu(diff_menu)

        game_menu.addSeparator()
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        game_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Помощь")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def new_game(self) -> None:
        print("New game stub")

    def set_difficulty(self, rows: int, cols: int, mines: int) -> None:
        print(f"Difficulty {rows}x{cols}, {mines} mines")

    def _show_difficulty_menu(self) -> None:
        print("Use menu")

    def _adjust_size(self) -> None:
        self.resize(self.field.width() + 20,
                    self.field.height() + self.menuBar().height() + self.statusBar().height() + 50)

    def _show_about(self) -> None:
        QMessageBox.about(self, "О Сапёре", "Сапёр на PyQt6\nВерсия 1.0\nСоздатель: Ящук Анна Б05-523")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())