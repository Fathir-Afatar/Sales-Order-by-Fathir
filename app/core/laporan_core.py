# Third party
import sqlite3

# Local application
from app.constants.config import get_connection

def get_detail_transaksi(id_transaksi, tipe):
    """Retrieves detailed record item(s) for a specific transaction type.

    Args:
        id_transaksi (int): Unique transaction identifier.
        tipe (str): Type of transaction ('penjualan', 'pembelian', or
            'pengeluaran').

    Returns:
        Union[List[Dict[str, Any]], Dict[str, Any]]: A list of detailed line items
        for sales/purchases, or a single detail dictionary for expenses.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row

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
    """Summarizes total amounts for sales, purchases, and expenses over a date range.

    Args:
        tanggal_awal (str): Start date string (YYYY-MM-DD).
        tanggal_akhir (str): End date string (YYYY-MM-DD).

    Returns:
        Dict[str, float]: Aggregated totals for 'penjualan', 'pembelian', and
        'pengeluaran'.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(total_harga) FROM transaksi_penjualan
        WHERE DATE(tanggal) BETWEEN DATE(?) AND DATE(?)
    """, (tanggal_awal, tanggal_akhir))
    total_penjualan = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM(total_harga) FROM transaksi_pembelian
        WHERE DATE(tanggal) BETWEEN DATE(?) AND DATE(?)
    """, (tanggal_awal, tanggal_akhir))
    total_pembelian = cursor.fetchone()[0] or 0

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
    """Fetches a list of transaction history records for a given type within a date range.

    Args:
        tipe (str): Type of transaction ('penjualan', 'pembelian', or
            'pengeluaran').
        tanggal_awal (str): Start date string (YYYY-MM-DD).
        tanggal_akhir (str): End date string (YYYY-MM-DD).

    Returns:
        List[Dict[str, Any]]: List of matching transaction records sorted by date
        descending.
    """
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
    """Retrieves the supplier's name by ID.

    Args:
        supplier_id (int): Unique identifier of the supplier.

    Returns:
        str: The supplier's name if found, otherwise a default fallback label.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama_supplier FROM supplier WHERE id_supplier = ?", (supplier_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else f"ID {supplier_id}"

def get_ringkasan_member(tanggal_awal, tanggal_akhir):
    """Generates member spending summary along with their profit contribution.

    Args:
        tanggal_awal (str): Start date string (YYYY-MM-DD).
        tanggal_akhir (str): End date string (YYYY-MM-DD).

    Returns:
        List[Dict[str, Any]]: Member records including purchase frequency, total
        spent, and gross profit contribution.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    laba_map = get_laba_member(tanggal_awal, tanggal_akhir)

    cursor.execute("""
        SELECT m.id_member,
                m.nama,
                COUNT(tp.id_transaksi) AS frekuensi,
                SUM(tp.total_harga) AS total_belanja
        FROM member m
        LEFT JOIN transaksi_penjualan tp 
            ON m.id_member = tp.kode_member
            AND DATE(tp.tanggal) BETWEEN DATE(?) AND DATE(?)
        GROUP BY m.id_member
        ORDER BY total_belanja DESC
    """, (tanggal_awal, tanggal_akhir))

    hasil = []
    rows = cursor.fetchall()
    for row in rows:
        print(dict(row))
        id_member = row["id_member"]
        hasil.append({
            "nama": row["nama"],
            "frekuensi": row["frekuensi"],
            "total_belanja": row["total_belanja"] or 0,
            "kontribusi": laba_map.get(id_member, 0)
        })
    conn.close()
    return hasil    

def get_laba_member(tanggal_awal, tanggal_akhir):
    """Calculates total gross profit generated per member within a given date range.

    Args:
        tanggal_awal (str): Start date string (YYYY-MM-DD).
        tanggal_akhir (str): End date string (YYYY-MM-DD).

    Returns:
        Dict[Optional[str], float]: Mapping of member ID to total profit.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tp.kode_member,
                   SUM(dp.subtotal - p.harga_beli * dp.jumlah) AS laba
        FROM transaksi_penjualan tp
        JOIN detail_penjualan dp ON tp.id_transaksi = dp.transaksi_id
        JOIN produk p ON dp.produk_id = p.id_produk
        WHERE DATE(tp.tanggal) BETWEEN DATE(?) AND DATE(?)
        GROUP BY tp.kode_member
    """, (tanggal_awal, tanggal_akhir))
    hasil = {}
    for row in cursor.fetchall():
        hasil[row["kode_member"]] = row["laba"] or 0
    conn.close()
    return hasil