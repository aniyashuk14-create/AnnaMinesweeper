"""
Меню «Вид» с выбором тем QSS.
"""
import sys
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt6.QtGui import QAction
from feature4_dialogs import MainWindowDialogs

QSS_STANDARD = ""
QSS_DARK = """
QMainWindow { background-color: #2b2b2b; }
QToolBar { background-color: #3c3c3c; border: none; }
QStatusBar { background-color: #3c3c3c; color: #aaaaaa; }
QMenuBar { background-color: #3c3c3c; color: #aaaaaa; }
QMenuBar::item:selected { background: #555555; }
QMenu { background-color: #3c3c3c; color: #aaaaaa; }
QMenu::item:selected { background: #555555; }
QPushButton { background-color: #4a4a4a; border: 1px solid #5a5a5a; color: #dddddd; }
QPushButton:hover { background-color: #5a5a5a; }
QPushButton:pressed { background-color: #6a6a6a; }
QLabel { color: #cccccc; }
QDialog { background-color: #2b2b2b; color: #cccccc; }
QLineEdit { background-color: #4a4a4a; color: #dddddd; border: 1px solid #5a5a5a; }
"""
QSS_COLORFUL = """
QMainWindow { background-color: #f0f0d0; }
QToolBar { background-color: #e0d8b0; border: none; }
QStatusBar { background-color: #e0d8b0; color: #333333; }
QMenuBar { background-color: #e0d8b0; color: #333333; }
QMenuBar::item:selected { background: #c8b878; }
QMenu { background-color: #e0d8b0; color: #333333; }
QMenu::item:selected { background: #c8b878; }
QPushButton { background-color: #c0c0a0; border: 1px solid #808060; font-weight: bold; color: #333333; }
QPushButton:hover { background-color: #d0d0b0; }
QLabel { color: #333333; }
QDialog { background-color: #f0f0d0; color: #333333; }
QLineEdit { background-color: #c0c0a0; border: 1px solid #808060; color: #333333; }
"""

class MainWindowQSS(MainWindowDialogs):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Сапёр — QSS темы")
        self._apply_theme(QSS_COLORFUL)

    def _create_menu(self) -> None:
        super()._create_menu()
        menubar = self.menuBar()
        view_menu = menubar.addMenu("Вид")
        for name, qss in [("Стандартная", QSS_STANDARD), ("Тёмная", QSS_DARK), ("Цветная", QSS_COLORFUL)]:
            action = QAction(name, self)
            action.triggered.connect(lambda _, t=qss: self._apply_theme(t))
            view_menu.addAction(action)
        view_menu.addSeparator()
        load_action = QAction("Загрузить из файла...", self)
        load_action.triggered.connect(self._load_theme_file)
        view_menu.addAction(load_action)

    def _apply_theme(self, qss: str) -> None:
        QApplication.instance().setStyleSheet(qss)

    def _load_theme_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Выберите QSS", "", "QSS Files (*.qss);;All Files (*)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._apply_theme(f.read())
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindowQSS()
    window.show()
    sys.exit(app.exec())