from app.constants.config import get_connection

def reset_database():
    conn = get_connection()
    cursor = conn.cursor()

    tables = [
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
        "user"
    ]
    
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
        print(f"[INFO] Data di tabel '{table}' telah dihapus.")
    
    conn.commit()
    conn.close()
    print("[✅] Database berhasil dibersihkan tanpa mengubah struktur.")

if __name__ == "__main__":
    reset_database()


#python -m app.utils.reset_db