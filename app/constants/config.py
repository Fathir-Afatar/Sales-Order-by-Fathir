import os
import sys
import sqlite3

def get_database_path():
    if getattr(sys, 'frozen', False):
        # Saat dijalankan dari hasil build PyInstaller
        base_path = sys._MEIPASS
    else:
        # Saat dijalankan dari source code
        base_path = os.path.abspath(".")
    # Arahkan ke folder data/pos.db
    return os.path.join(base_path, "data", "pos.db")

def get_connection():
    db_path = get_database_path()
    return sqlite3.connect(db_path)

# Digunakan oleh semua modul core untuk koneksi database