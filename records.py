"""
Хранилище рекордов в JSON.
"""
import json
import os
from datetime import datetime
from typing import Dict, List

DEFAULT_RECORDS_FILE = "records.json"

class RecordStore:
    def __init__(self, filepath: str = DEFAULT_RECORDS_FILE) -> None:
        self.filepath = filepath
        self._data: Dict[str, List[dict]] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._data = {}
        else:
            self._data = {}

    def _save(self) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def add_record(self, difficulty: str, time_seconds: int) -> None:
        record = {
            "time": time_seconds,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self._data.setdefault(difficulty, []).append(record)
        self._data[difficulty].sort(key=lambda x: x["time"])
        self._data[difficulty] = self._data[difficulty][:200]
        self._save()

    def get_top(self, difficulty: str, limit: int = 10) -> List[dict]:
        return self._data.get(difficulty, [])[:limit]

    def get_all_difficulties(self) -> List[str]:
        return list(self._data.keys())

    def clear_all(self) -> None:
        self._data = {}
        self._save()