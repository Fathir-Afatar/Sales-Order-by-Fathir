from app.constants.config import get_connection
conn = get_connection

def get_detail_transaksi(id_transaksi, tipe):
    print("Mendapatkan detail transaksi untuk tipe:", tipe)
    conn = get_connection()
    conn.row_factory = get_connection.Row # Akses kolom by name

    cursor = conn.cursor()

    if tipe == "penjualan":
        cursor.execute("""
            SELECT nama_produk, jumlah, harga_satuan, subtotal
            FROM detail_penjualan
            WHERE transaksi_id = ?
        """, (id_transaksi,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    elif tipe == "pembelian":
        cursor.execute("""
            SELECT produk_id, qty, harga_beli
            FROM detail_pembelian
            WHERE pembelian_id = ?
        """, (id_transaksi,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    elif tipe == "pengeluaran":
        cursor.execute("""
            SELECT kategori, keterangan, tanggal, nominal
            FROM pengeluaran
            WHERE id_pengeluaran = ?
        """, (id_transaksi,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}
    
    else:
        conn.close()
        return []
    
def get_ringkasan_laporan(tanggal_awal, tanggal_akhir):
    conn = get_connection()
    cursor = conn.cursor()

    # Total Penjualan

    cursor.execute("""
        SELECT SUM(total_harga) FROM transaksi_penjualan
        WHERE DATE(tanggal) BETWEEN DATE(?) AND DATE(?)
    """, (tanggal_awal, tanggal_akhir))
    total_penjualan = cursor.fetchone()[0] or 0

    # Total Pembelian

    cursor.execute("""
        SELECT SUM(total_harga) FROM transaksi_pembelian
        WHERE DATE(tanggal) BETWEEN DATE(?) AND DATE(?)
    """, (tanggal_awal, tanggal_akhir))
    total_pembelian = cursor.fetchone()[0] or 0

    # Total Pengeluaran

    cursor.execute("""
        SELECT SUM(nominal) FROM pengeluaran
        WHERE DATE(tanggal) BETWEEN DATE(?) AND DATE(?)
    """, (tanggal_awal, tanggal_akhir))
    total_pengeluaran = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "penjualan": total_penjualan,
        "pembelian": total_pembelian,
        "pengeluaran": total_pengeluaran
    }


