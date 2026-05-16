"""
Модуль рекордов (фича 6): сохранение, отображение, очистка.
"""
import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from feature5_qss import MainWindowQSS
from feature4_dialogs import GameOverDialog
from records import RecordStore

TOP_LIMIT_WIN_DIALOG = 20
TOP_LIMIT_ALL_RECORDS = 20

class WinRecordsDialog(QDialog):
    def __init__(self, elapsed: int, difficulty: str, store: RecordStore,
                 parent: Optional[QWidget] = None, limit: int = TOP_LIMIT_WIN_DIALOG) -> None:
        super().__init__(parent)
        self.setWindowTitle("Победа!")
        self.setModal(True)
        layout = QVBoxLayout()
        layout.setSpacing(10)
        label = QLabel(f"🎉 Вы выиграли за {elapsed} сек. 🎉")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(label)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["№", "Время", "Дата"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        top = store.get_top(difficulty, limit)
        table.setRowCount(len(top))
        for i, rec in enumerate(top, start=1):
            table.setItem(i-1, 0, QTableWidgetItem(str(i)))
            time_item = QTableWidgetItem(str(rec["time"]))
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(i-1, 1, time_item)
            date_item = QTableWidgetItem(rec.get("date", ""))
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(i-1, 2, date_item)

        layout.addWidget(table)
        btn_new = QPushButton("Новая игра")
        btn_new.clicked.connect(self.accept)
        btn_exit = QPushButton("Выход")
        btn_exit.clicked.connect(self.reject)
        layout.addWidget(btn_new)
        layout.addWidget(btn_exit)
        self.setLayout(layout)

class MainWindowRecords(MainWindowQSS):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Сапёр — Рекорды")
        self.record_store = RecordStore()
        self._game_over_processed = False

        menubar = self.menuBar()
        records_menu = menubar.addMenu("Рекорды")
        show_action = QAction("Показать таблицу рекордов", self)
        show_action.triggered.connect(self._show_all_records)
        records_menu.addAction(show_action)
        records_menu.addSeparator()
        clear_action = QAction("Очистить все рекорды", self)
        clear_action.triggered.connect(self._clear_records)
        records_menu.addAction(clear_action)

    def _get_current_difficulty(self) -> str:
        r, c, m = self.field.rows, self.field.cols, self.field.total_mines
        if r == 9 and c == 9 and m == 10:
            return "beginner 9x9 10m"
        elif r == 16 and c == 16 and m == 40:
            return "intermediate 16x16 40m"
        elif r == 16 and c == 30 and m == 99:
            return "expert 16x30 99m"
        else:
            return f"custom {r}x{c} {m}m"

    def on_game_over(self, won: bool) -> None:
        if self._game_over_processed:
            return
        self._game_over_processed = True
        self.stop_timer()
        if won:
            diff = self._get_current_difficulty()
            self.record_store.add_record(diff, self.elapsed_seconds)
            QTimer.singleShot(0, lambda: self._show_win_dialog(diff))
        else:
            QTimer.singleShot(0, self._show_loss_dialog)

    def _show_win_dialog(self, difficulty: str) -> None:
        dlg = WinRecordsDialog(self.elapsed_seconds, difficulty, self.record_store, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            QTimer.singleShot(0, self._start_new_game)
        else:
            self.close()

    def _show_loss_dialog(self) -> None:
        dlg = GameOverDialog(False, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            QTimer.singleShot(0, self._start_new_game)
        else:
            self.close()

    def _start_new_game(self) -> None:
        self._game_over_processed = False
        self.new_game()

    def new_game(self) -> None:
        self._game_over_processed = False
        super().new_game()

    def set_difficulty(self, rows: int, cols: int, mines: int) -> None:
        self._game_over_processed = False
        super().set_difficulty(rows, cols, mines)

    def _show_all_records(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Рекорды")
        layout = QVBoxLayout()
        diffs = self.record_store.get_all_difficulties()
        if not diffs:
            layout.addWidget(QLabel("Нет сохранённых результатов."))
        else:
            for diff in diffs:
                layout.addWidget(QLabel(f"Сложность: {diff}"))
                table = QTableWidget()
                table.setColumnCount(3)
                table.setHorizontalHeaderLabels(["№", "Время", "Дата"])
                table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                top = self.record_store.get_top(diff, TOP_LIMIT_ALL_RECORDS)
                table.setRowCount(len(top))
                for i, rec in enumerate(top, start=1):
                    table.setItem(i-1, 0, QTableWidgetItem(str(i)))
                    table.setItem(i-1, 1, QTableWidgetItem(str(rec["time"])))
                    table.setItem(i-1, 2, QTableWidgetItem(rec.get("date", "")))
                layout.addWidget(table)
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)
        dialog.setLayout(layout)
        dialog.exec()

    def _clear_records(self) -> None:
        confirm = QMessageBox.question(
            self, "Подтверждение",
            "Вы действительно хотите удалить все рекорды?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.record_store.clear_all()
            QMessageBox.information(self, "Готово", "Все рекорды удалены.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindowRecords()
    window.show()
    sys.exit(app.exec())