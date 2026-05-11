"""Точка входа."""
import sys
from PyQt6.QtWidgets import QApplication
from feature6_records import MainWindowRecords

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindowRecords()
    window.show()
    sys.exit(app.exec())