"""
Кастомные диалоги: завершение игры и ввод произвольной сложности.
"""
import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout,
    QDialogButtonBox, QMessageBox, QApplication, QWidget
)
from PyQt6.QtCore import Qt
from feature3_timer import MainWindowTimer
from config import GameConfig, InvalidConfigError

class GameOverDialog(QDialog):
    def __init__(self, won: bool, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Игра окончена")
        self.setModal(True)
        layout = QVBoxLayout()
        msg = "🎉 Поздравляем! Вы выиграли! 🎉" if won else "💥 Вы подорвались на мине... 💥"
        label = QLabel(msg)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 20px;")
        layout.addWidget(label)

        new_btn = QPushButton("Новая игра")
        new_btn.clicked.connect(self.accept)
        exit_btn = QPushButton("Выход")
        exit_btn.clicked.connect(self.reject)
        layout.addWidget(new_btn)
        layout.addWidget(exit_btn)
        self.setLayout(layout)

class CustomDifficultyDialog(QDialog):
    def __init__(self, current: GameConfig, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Настройка сложности")
        self.setModal(True)
        layout = QVBoxLayout()
        form = QFormLayout()
        self.rows_edit = QLineEdit(str(current.rows))
        self.cols_edit = QLineEdit(str(current.cols))
        self.mines_edit = QLineEdit(str(current.mines))
        form.addRow("Строки (5-30):", self.rows_edit)
        form.addRow("Столбцы (5-30):", self.cols_edit)
        form.addRow("Мины:", self.mines_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _validate_and_accept(self) -> None:
        try:
            rows = int(self.rows_edit.text())
            cols = int(self.cols_edit.text())
            mines = int(self.mines_edit.text())
            config = GameConfig(rows, cols, mines)
            config.validate()
        except (ValueError, InvalidConfigError) as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return
        self.selected_config = config
        self.accept()

class MainWindowDialogs(MainWindowTimer):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Сапёр — кастомные диалоги")

    def _create_menu(self) -> None:
        super()._create_menu()
        menubar = self.menuBar()
        game_menu = menubar.actions()[0].menu()
        game_menu.addSeparator()
        custom_act = game_menu.addAction("Своя сложность...")
        custom_act.triggered.connect(self._show_custom_difficulty)

    def _show_difficulty_menu(self) -> None:
        self._show_custom_difficulty()

    def on_game_over(self, won: bool) -> None:
        self.stop_timer()
        dlg = GameOverDialog(won, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.new_game()
        else:
            self.close()

    def _show_custom_difficulty(self) -> None:
        current = GameConfig(self.field.rows, self.field.cols, self.field.total_mines)
        dlg = CustomDifficultyDialog(current, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            config = dlg.selected_config
            self.set_difficulty(config.rows, config.cols, config.mines)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindowDialogs()
    window.show()
    sys.exit(app.exec())