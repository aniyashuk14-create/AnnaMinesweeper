"""
Игровая логика: обработка кликов, мины, флаги, победа/поражение.
"""
import sys
import random
from typing import Optional, List
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QMessageBox
)
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtCore import Qt
from feature1_ui import MainWindow, MineField, CellButton
from config import CELL_SIZE, COLORS, DEFAULT_ROWS, DEFAULT_COLS, DEFAULT_MINES

class GameCellButton(CellButton):
    def __init__(self, row: int, col: int, field: 'MineFieldGame') -> None:
        super().__init__(row, col)
        self.field = field
        self.setMouseTracking(True)
        self.is_revealed: bool = False
        self.is_flagged: bool = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self.field.toggle_flag(self.row, self.col)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.field.reveal_cell(self.row, self.col)

class MineFieldGame(MineField):
    @staticmethod
    def _count_adjacent_mines(mine_map: List[List[bool]],
                              row: int, col: int,
                              rows: int, cols: int) -> int:
        dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        return sum(mine_map[row+dr][col+dc] for dr, dc in dirs
                   if 0 <= row+dr < rows and 0 <= col+dc < cols)

    def __init__(self, rows: int, cols: int, mines: int,
                 parent: Optional['MainWindowGame'] = None) -> None:
        self.total_mines = mines
        self.mine_map: List[List[bool]] = []
        self.adjacent_mines: List[List[int]] = []
        self._game_over = False
        self.first_click = True
        self.revealed_count = 0
        self.flag_count = 0
        self.main_window = parent
        super().__init__(rows, cols, parent)   # вызовет self.init_ui()

    @property
    def game_over(self) -> bool:
        return self._game_over

    @game_over.setter
    def game_over(self, value: bool) -> None:
        self._game_over = value

    def init_ui(self) -> None:
        old = self.layout()
        if old is not None:
            QWidget().setLayout(old)
        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        self.buttons = []
        for r in range(self.rows):
            row_btns = []
            for c in range(self.cols):
                btn = GameCellButton(r, c, self)
                grid.addWidget(btn, r, c)
                row_btns.append(btn)
            self.buttons.append(row_btns)
        self.setLayout(grid)
        self.setFixedSize(self.cols * CELL_SIZE, self.rows * CELL_SIZE)

    def place_mines(self, safe_row: int, safe_col: int) -> None:
        safe_zone = set()
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                nr, nc = safe_row+dr, safe_col+dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    safe_zone.add((nr, nc))
        candidates = [(r,c) for r in range(self.rows) for c in range(self.cols)
                      if (r,c) not in safe_zone]
        actual = min(self.total_mines, len(candidates))
        self.total_mines = actual
        positions = random.sample(candidates, actual)
        self.mine_map = [[False]*self.cols for _ in range(self.rows)]
        for r,c in positions:
            self.mine_map[r][c] = True
        self._calculate_adjacent()
        if self.main_window:
            self.main_window.update_mine_counter(self.total_mines - self.flag_count)

    def _calculate_adjacent(self) -> None:
        self.adjacent_mines = [[0]*self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                if self.mine_map[r][c]:
                    self.adjacent_mines[r][c] = -1
                else:
                    self.adjacent_mines[r][c] = self._count_adjacent_mines(
                        self.mine_map, r, c, self.rows, self.cols
                    )

    def reveal_cell(self, row: int, col: int, depth: int = 0) -> None:
        if self._game_over or depth > 200:
            return
        if self.first_click:
            self.place_mines(row, col)
            self.first_click = False
            if self.main_window:
                self.main_window.update_mine_counter(self.total_mines - self.flag_count)

        btn = self.buttons[row][col]
        if btn.is_revealed or btn.is_flagged:
            return

        btn.is_revealed = True
        self.revealed_count += 1

        if self.mine_map[row][col]:
            btn.setText("💣")
            btn.setStyleSheet("background-color: red; font-size: 14px;")
            self._game_over = True
            self._reveal_all_mines()
            if self.main_window:
                self.main_window.on_game_over(False)
            return

        adj = self.adjacent_mines[row][col]
        if adj > 0:
            btn.setText(str(adj))
            color = COLORS.get(adj, "black")
            btn.setStyleSheet(f"color: {color}; background-color: #e0e0e0; "
                              f"border: 1px solid #808080; font-weight: bold; font-size: 14px;")
        else:
            btn.setText("")
            btn.setStyleSheet("background-color: #e0e0e0; border: 1px solid #808080;")
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    nr, nc = row+dr, col+dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.reveal_cell(nr, nc, depth+1)

        safe_cells = self.rows * self.cols - self.total_mines
        if self.revealed_count == safe_cells:
            self._game_over = True
            if self.main_window:
                self.main_window.on_game_over(True)

    def toggle_flag(self, row: int, col: int) -> None:
        if self._game_over:
            return
        btn = self.buttons[row][col]
        if btn.is_revealed:
            return
        btn.is_flagged = not btn.is_flagged
        if btn.is_flagged:
            btn.setText("🚩")
            self.flag_count += 1
        else:
            btn.setText("")
            self.flag_count -= 1
        if self.main_window:
            self.main_window.update_mine_counter(self.total_mines - self.flag_count)

    def _reveal_all_mines(self) -> None:
        for r in range(self.rows):
            for c in range(self.cols):
                btn = self.buttons[r][c]
                if self.mine_map[r][c] and not btn.is_flagged:
                    btn.setText("💣")
                elif not self.mine_map[r][c] and btn.is_flagged:
                    btn.setText("❌")

    def reset(self, rows: int, cols: int, mines: int) -> None:
        self.rows = rows
        self.cols = cols
        self.total_mines = mines
        self.first_click = True
        self._game_over = False
        self.revealed_count = 0
        self.flag_count = 0
        self.init_ui()
        self.adjustSize()
        if self.main_window:
            self.main_window.adjust_window_size()
            self.main_window.update_mine_counter(self.total_mines)

class MainWindowGame(MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.field = MineFieldGame(DEFAULT_ROWS, DEFAULT_COLS, DEFAULT_MINES, parent=self)
        self.setCentralWidget(self.field)
        self.field.main_window = self
        self.update_mine_counter(self.field.total_mines)
        self.adjust_window_size()

    def new_game(self) -> None:
        self.field.reset(self.field.rows, self.field.cols, self.field.total_mines)
        self.status_bar.showMessage("Новая игра")

    def set_difficulty(self, rows: int, cols: int, mines: int) -> None:
        self.field.reset(rows, cols, mines)
        self.status_bar.showMessage(f"Сложность изменена")

    def adjust_window_size(self) -> None:
        self.field.adjustSize()
        self.resize(self.field.width() + 20,
                    self.field.height() + self.menuBar().height() + self.statusBar().height() + 50)

    def update_mine_counter(self, count: int) -> None:
        self.mines_label.setText(f"💣 {count}")

    def on_game_over(self, won: bool) -> None:
        if won:
            QMessageBox.information(self, "Поздравляем!", "Вы выиграли!")
        else:
            QMessageBox.critical(self, "Конец игры", "Вы подорвались на мине!")
        self.new_game()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindowGame()
    window.show()
    sys.exit(app.exec())