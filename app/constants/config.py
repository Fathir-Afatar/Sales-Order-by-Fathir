# Standard Library
import os
import sys
import sqlite3

def get_database_path():
    """Retrieve the absolute path to the SQLite database file.

    Detects the current execution environment: if running within a PyInstaller
    executable bundle, it directs to the PyInstaller temporary directory
    (`sys._MEIPASS`). Otherwise, it builds the path relative to the current working
    directory.

    Returns:
        str: Absolute path to the 'data/pos.db' file.
    """
    if getattr(sys, 'frozen', False):
        # Saat dijalankan dari hasil build PyInstaller
        base_path = sys._MEIPASS
    else:
        # Saat dijalankan dari source code
        base_path = os.path.abspath(".")
    # Arahkan ke folder data/pos.db
    return os.path.join(base_path, "data", "pos.db")

def get_connection():
    """Establish and return a connection to the SQLite database.

    Returns:
        sqlite3.Connection: SQLite connection object configured with a 10-second
        timeout.
    """
    db_path = get_database_path()
    return sqlite3.connect(db_path,timeout=10)

# Digunakan oleh semua modul core untuk koneksi database