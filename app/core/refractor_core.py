# Third-party
from datetime import datetime

# Local application
from app.constants.config import get_connection

conn = get_connection()

# Get_product untuk ambil detail produk dari DB
def ambil_produk(identifier, by_kode:True):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT id_produk, nama_produk, harga_jual, stok FROM produk WHERE kode_produk WHERE {} = ?", format(
        "kode_produk" if by_kode else "id_produk"
    )
    cursor.execute(query, (identifier,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id_produk": row[0],
            "nama": row [1],
            "harga": row[2],
            "stok": row [3]
        }
    return None

# Fungsi kurangi stok produk
def kurang_stok(id_produk, jumlah):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE produk SET stok = stok - ? WHERE id_produk = ?", (jumlah, id_produk))
    conn.commit()
    conn.close()

# Fungsi Simpan transaksi penjualan
def simpan_transaksi(nama_member, keranjang, total, waktu, voucher_kode=None):
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Save Transaction
    cursor.execute("""
                   INSERT INTO transaksi_penjualan (nama_member, total_harga, waktu, voucher)
                   VALUES (?, ?, ?, ?)
                """, (nama_member, total, waktu, voucher_kode))
    id_transaksi = cursor.lastrowid

    # 2. Save transaction details + update stock

    for item in keranjang:
        cursor.execute("""
                       INSERT INTO detail_penjualan (transaksi_id, produk_id, nama_produk, jumlah, harga_satuan, subtotal)
                       VALUES (?, ?, ?, ?)
                    """,(
                        id_transaksi, item["id_produk"], item["nama"], item["jumlah"],
                        item["harga"], item["jumlah"], * item["harga"]
                    ))
        kurang_stok(item["id_produk"], item["jumlah"])

    conn.commit()
    conn.close()
    return id_transaksi

# Validasi Voucher
def cek_voucher(kode, nama_member):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT nilai FROM voucher
                   WHERE kode = ? AND status 'aktif' AND nama_member = ?
""", (kode, nama_member))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0] # nilai potongan
    return 0