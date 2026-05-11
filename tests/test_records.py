"""
Тесты для модуля records.py (хранение рекордов).
"""
import json
import os
import tempfile
from records import RecordStore

def test_add_and_retrieve_record():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        path = f.name
    try:
        store = RecordStore(path)
        store.add_record("beginner 9x9 10m", 120)
        store.add_record("beginner 9x9 10m", 60)
        store.add_record("beginner 9x9 10m", 90)

        top = store.get_top("beginner 9x9 10m", 10)
        assert len(top) == 3
        assert top[0]["time"] == 60   # сортировка по возрастанию
        assert top[1]["time"] == 90
        assert top[2]["time"] == 120
        assert "date" in top[0]
    finally:
        os.unlink(path)

def test_clear_records():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        path = f.name
    try:
        store = RecordStore(path)
        store.add_record("expert 16x30 99m", 200)
        store.clear_all()
        assert store.get_top("expert 16x30 99m") == []
        with open(path) as f:
            data = json.load(f)
        assert data == {}
    finally:
        os.unlink(path)

def test_multiple_difficulties():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        path = f.name
    try:
        store = RecordStore(path)
        store.add_record("custom 12x14 20m", 45)
        store.add_record("custom 12x14 10m", 55)
        diffs = store.get_all_difficulties()
        assert "custom 12x14 20m" in diffs
        assert "custom 12x14 10m" in diffs
    finally:
        os.unlink(path)