from app.constants.config import get_connection
conn = get_connection
import sqlite3

def get_detail_transaksi(id_transaksi, tipe):
    print("Mendapatkan detail transaksi untuk tipe:", tipe)
    conn = get_connection()
    conn.row_factory = sqlite3.Row # Akses kolom by name

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

def get_histori_transaksi(tipe, tanggal_awal, tanggal_akhir):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if tipe == "penjualan":
        cursor.execute("""
            SELECT id_transaksi, tanggal, total_harga
            FROM transaksi_penjualan
            WHERE DATE(tanggal) BETWEEN DATE(?) AND DATE(?)
            ORDER BY tanggal DESC
        """, (tanggal_awal, tanggal_akhir))
        return [dict(row) for row in cursor.fetchall()]
    
    elif tipe == "pembelian":
        cursor.execute("""
            SELECT id_pembelian, tanggal, total_harga, supplier_id
            FROM transaksi_pembelian
            WHERE DATE(tanggal) BETWEEN DATE(?) AND DATE(?)
            ORDER BY tanggal DESC
        """, (tanggal_awal, tanggal_akhir))
        return [dict(row) for row in cursor.fetchall()]

    elif tipe == "pengeluaran":
        cursor.execute("""
            SELECT id_pengeluaran, tanggal, kategori, nominal, keterangan
            FROM Pengeluaran
            WHERE DATE(tanggal) BETWEEN DATE(?) AND DATE(?)
            ORDER BY tanggal DESC
        """, (tanggal_awal, tanggal_akhir))
        return [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return []

def get_nama_supplier(supplier_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama_supplier FROM supplier WHERE id_supplier = ?", (supplier_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else f"ID {supplier_id}"
    
