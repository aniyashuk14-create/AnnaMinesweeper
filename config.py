"""
Конфигурация игры «Сапёр».
Содержит константы, dataclass параметров и собственные исключения.
"""
from dataclasses import dataclass

CELL_SIZE: int = 30
DEFAULT_ROWS: int = 9
DEFAULT_COLS: int = 9
DEFAULT_MINES: int = 10

COLORS: dict[int, str] = {
    1: "#0000FF", 2: "#008000", 3: "#FF0000", 4: "#000080",
    5: "#800000", 6: "#008080", 7: "#000000", 8: "#808080"
}

@dataclass
class GameConfig:
    rows: int = DEFAULT_ROWS
    cols: int = DEFAULT_COLS
    mines: int = DEFAULT_MINES

    def validate(self) -> None:
        if not (5 <= self.rows <= 30 and 5 <= self.cols <= 30):
            raise InvalidConfigError("Размеры поля должны быть от 5 до 30.")
        if not (1 <= self.mines < self.rows * self.cols):
            raise InvalidConfigError(
                f"Количество мин должно быть от 1 до {self.rows * self.cols - 1}."
            )

class InvalidConfigError(ValueError):
    pass

class TooManyMinesError(RuntimeError):
    pass