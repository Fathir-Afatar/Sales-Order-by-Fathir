# Third party
import sqlite3
from typing import List

# Local application
from app.constants.config import get_connection


ALLOWED_TABLES: List[str] = [
    "Pengeluaran",
    "detail_pembelian",
    "detail_penjualan",
    "kategori",
    "log_harga_beli_harga_jual",
    "log_stock",
    "member",
    "produk",
    "sqlite_sequence",
    "supplier",
    "transaksi_pembelian",
    "transaksi_penjualan",
    "user",
]


def reset_database():
  """Truncates all data from specified database tables without dropping structures.

  Disables foreign key constraints temporarily to allow cascade-free deletion,
  clears sequence counters, and commits changes atomically within a
  transaction.

  Returns:
      bool: True if reset succeeded, False if an error occurred during transaction.
  """
  conn: sqlite3.Connection = get_connection()
  cursor: sqlite3.Cursor = conn.cursor()

  try:
    cursor.execute("PRAGMA foreign_keys = OFF;")

    for table in ALLOWED_TABLES:
      if table in ALLOWED_TABLES:
        cursor.execute(f"DELETE FROM {table}")
        print(f"[INFO] Data di tabel '{table}' telah dihapus.")

    cursor.execute("PRAGMA foreign_keys = ON;")

    conn.commit()
    print("[✅] Database berhasil dibersihkan tanpa mengubah struktur.")
    return True

  except sqlite3.Error as e:
    conn.rollback()
    print(f"[ERROR] Gagal mereset database: {e}")
    return False

  finally:
    conn.close()

if __name__ == "__main__":
  reset_database()

#python -m app.utils.reset_db