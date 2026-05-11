"""
Профилирование основных операций игры.
"""
import sys
import cProfile
import pstats
import io
from PyQt6.QtWidgets import QApplication
from feature2_game import MineFieldGame

def profile_place_and_reveal():
    field = MineFieldGame(16, 16, 40)
    field.place_mines(8, 8)
    field.reveal_cell(0, 0)

def profile_large_field():
    field = MineFieldGame(30, 30, 99)
    field.place_mines(15, 15)
    for r in range(30):
        for c in range(30):
            if not field.buttons[r][c].is_revealed and not field.mine_map[r][c]:
                field.reveal_cell(r, c)
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)

    pr = cProfile.Profile()
    pr.enable()

    profile_place_and_reveal()
    profile_large_field()

    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(20)
    print(s.getvalue())

    try:
        with open("profile_results.txt", "w") as f:
            f.write(s.getvalue())
        print("profile_results.txt записан успешно.")
    except Exception as e:
        print(f"Ошибка при записи файла: {e}")

    app.quit()