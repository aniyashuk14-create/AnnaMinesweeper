"""
Тесты игровой логики MineFieldGame.
"""
import sys
import pytest
from PyQt6.QtWidgets import QApplication
from feature2_game import MineFieldGame

app = QApplication(sys.argv)

@pytest.fixture
def field():
    """Создаёт игровое поле 9x9 с 10 минами."""
    f = MineFieldGame(9, 9, 10)
    f.main_window = None  # изолируем от GUI
    return f

def test_initial_state(field):
    assert field.first_click is True
    assert field.game_over is False
    assert field.revealed_count == 0
    assert field.flag_count == 0

def test_place_mines_around_first_click(field):
    field.place_mines(4, 4)
    for r in range(3, 6):
        for c in range(3, 6):
            assert not field.mine_map[r][c], f"Мины не должно быть рядом с первым кликом в ({r},{c})"

def test_adjacent_count(field):
    field.place_mines(0, 0)
    assert field.adjacent_mines[0][0] == 0
    field.mine_map = [[False]*9 for _ in range(9)]
    field.mine_map[0][0] = True
    field._calculate_adjacent()
    assert field.adjacent_mines[1][1] == 1
    assert field.adjacent_mines[0][1] == 1
    assert field.adjacent_mines[2][2] == 0

def test_reveal_cell_safe(field):
    field.place_mines(0, 0)
    field.first_click = False  # имитируем завершённый первый ход
    field.reveal_cell(8, 8)
    btn = field.buttons[8][8]
    assert btn.is_revealed
    assert not field.game_over

def test_lose_on_mine(field):
    field.place_mines(0, 0)          # генерируем мины, исключая (0,0) и соседей
    field.first_click = False        # имитация, что первый ход уже сделан
    field.mine_map[5][5] = True      # теперь принудительно ставим мину в (5,5)
    field.reveal_cell(5, 5)
    assert field.game_over
    assert field.buttons[5][5].text() == "💣"

def test_flag_toggle(field):
    field.place_mines(0, 0)
    field.first_click = False
    field.toggle_flag(0, 8)
    assert field.buttons[0][8].is_flagged
    assert field.buttons[0][8].text() == "🚩"
    field.toggle_flag(0, 8)
    assert not field.buttons[0][8].is_flagged