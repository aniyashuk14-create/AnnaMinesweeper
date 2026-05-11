"""
Модуль таймера, стартующего при первом клике.
"""
import sys
from typing import Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from feature2_game import MainWindowGame, MineFieldGame
from config import DEFAULT_ROWS, DEFAULT_COLS, DEFAULT_MINES

class MineFieldTimer(MineFieldGame):
    def __init__(self, rows: int, cols: int, mines: int,
                 parent: Optional['MainWindowTimer'] = None) -> None:
        super().__init__(rows, cols, mines, parent)
        self._first_click_callback: Optional[callable] = None

    def set_first_click_callback(self, callback: callable) -> None:
        self._first_click_callback = callback

    def reveal_cell(self, row: int, col: int, depth: int = 0) -> None:
        was_first = self.first_click
        super().reveal_cell(row, col, depth)
        if was_first and not self.first_click and self._first_click_callback:
            self._first_click_callback()

class MainWindowTimer(MainWindowGame):
    def __init__(self) -> None:
        super().__init__()
        self.field = MineFieldTimer(DEFAULT_ROWS, DEFAULT_COLS, DEFAULT_MINES, parent=self)
        self.setCentralWidget(self.field)
        self.field.main_window = self
        self.field.set_first_click_callback(self.start_timer)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer)
        self.elapsed_seconds = 0
        self.update_timer_label()

    def start_timer(self) -> None:
        if not self.timer.isActive():
            self.elapsed_seconds = 0
            self.timer.start(1000)

    def _update_timer(self) -> None:
        self.elapsed_seconds += 1
        self.update_timer_label()

    def update_timer_label(self) -> None:
        self.timer_label.setText(f"⏱ {self.elapsed_seconds:03d}")

    def stop_timer(self) -> None:
        self.timer.stop()

    def new_game(self) -> None:
        self.stop_timer()
        self.elapsed_seconds = 0
        self.update_timer_label()
        super().new_game()

    def set_difficulty(self, rows: int, cols: int, mines: int) -> None:
        self.stop_timer()
        self.elapsed_seconds = 0
        self.update_timer_label()
        super().set_difficulty(rows, cols, mines)

    def on_game_over(self, won: bool) -> None:
        self.stop_timer()
        super().on_game_over(won)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindowTimer()
    window.show()
    sys.exit(app.exec())