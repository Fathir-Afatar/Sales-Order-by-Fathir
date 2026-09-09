# Third-party
from datetime import datetime

# Local application
from app.core.product_core import ubah_stok_dan_catat_log
from app.core.stok_core import get_stok_terakhir
from app.constants.config import get_connection

def tambah_pembelian(supplier_id: str, daftar_barang:list):
    """Records a new purchase transaction along with its itemized details and stock updates.

    Args:
        supplier_id (Union[int, str]): Unique identifier of the supplier.
        daftar_barang (List[Dict[str, Any]]): List of items containing
            'kode_produk', 'qty', and 'harga_beli'.

    Returns:
        Union[int, bool]: Created purchase transaction ID on success, or False on
        failure.
    """
    if not daftar_barang:
        print("[ERROR] Daftar barang kosong.")
        return False

    for item in daftar_barang:
        if item["qty"] <= 0 or item["harga_beli"] <= 0:
            print(f"[ERROR] Item tidak valid: {item}")
            return False
    tanggal = datetime.now().strftime("%Y-%m-%d")
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        total_harga = sum(item["qty"] * item["harga_beli"] for item in daftar_barang)

        cursor.execute("""
                INSERT INTO transaksi_pembelian (supplier_id, tanggal, total_harga)
                       VALUES (?, ?, ?)
                       """, (supplier_id, tanggal, total_harga))
        pembelian_id = cursor.lastrowid

        for item in daftar_barang:
            cursor.execute("""
                           INSERT INTO detail_pembelian (pembelian_id, kode_produk, qty, harga_beli)
                           VALUES (?, ?, ?, ?)
                           """, (pembelian_id, item["kode_produk"], item["qty"], item["harga_beli"]))
        
            cursor.execute("SELECT id_produk FROM produk WHERE kode_produk = ?", (item["kode_produk"],))
            result = cursor.fetchone()
            if not result:
                print(f"[ERROR] Produk dengan kode'{item['kode_produk']}' tidak ditemukan.")
                continue
        
            produk_id = result[0]
            ubah_stok_dan_catat_log(cursor, produk_id, item["qty"], "MASUK")

        conn.commit()
        print(f"[INFO] Pembelian berhasil disimpan. ID: {pembelian_id}")
        return pembelian_id

    except Exception as e:
        print(f"[ERROR] Gagal menyimpan pembelian: {e}")
        if conn:
            conn.rollback()
        return False
    
    finally:
        if conn:
            conn.close()

def get_histori_pembelian():
    """Retrieves purchase transaction history with supplier details.

    Returns:
        List[Tuple[int, str, str, float]]: Records containing 'id_pembelian',
        'tanggal', 'nama_supplier', and 'total_harga'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tp.id_pembelian, tp.tanggal, s.nama_supplier, tp.total_harga
        FROM transaksi_pembelian tp
        JOIN supplier s ON tp.supplier_id = s.id_supplier
        ORDER BY tp.tanggal DESC    
    """)
    hasil = cursor.fetchall()
    conn.close()
    return hasil

def get_pembelian(pembelian_id):
    """Retrieves items for a specific purchase transaction ID.

    Args:
        pembelian_id (int): Primary key of the purchase transaction.

    Returns:
        List[Tuple[str, int, float]]: List of records containing 'kode_produk',
        'qty', and 'harga_beli'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT kode_produk, qty, harga_beli
        FROM detail_pembelian
        WHERE pembelian_id = ?
    """, (pembelian_id,))
    hasil = cursor.fetchall()
    conn.close()
    return hasil

def validasi_keranjang(daftar_barang):
    """Validates if a shopping cart/item list has valid quantities and prices.

    Args:
        daftar_barang (List[Dict[str, Any]]): List of item dictionaries to
            validate.

    Returns:
        bool: True if valid and non-empty, False otherwise.
    """
    if not daftar_barang:
        return False
    for item in daftar_barang:
        if item["qty"] <= 0 or item["harga_beli"] <= 0:
            return False
    return True

def get_pembelian_untuk_koreksi(pembelian_id):
    """Fetches purchase data structured for correction interfaces.

    Args:
        pembelian_id (int): Primary key of the purchase transaction.

    Returns:
        Dict[str, Any]: Dictionary containing 'header' and 'detail' transaction
        data.
    """
    header = get_histori_pembelian()
    detail = get_histori_pembelian()
    return {"header":header, "detail": detail}

def hapus_pembelian(pembelian_id):
    """Deletes a purchase transaction, reverses stock adjustments, and logs the change.

    Args:
        pembelian_id (int): Primary key of the purchase transaction to delete.

    Returns:
        bool: True if deletion succeeded, False otherwise.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT kode_produk, qty FROM detail_pembelian
            WHERE pembelian_id = ?
        """, (pembelian_id,))

        detail = cursor.fetchall()

        for kode_produk, qty in detail:
            ubah_stok_dan_catat_log(kode_produk, -qty, "PEMBATALAN")

        cursor.execute("DELETE FROM detail_pembelian WHERE pembelian_id = ?", (pembelian_id,))
        cursor.execute("DELETE FROM transaksi_pembelian WHERE id_pembelian = ?", (pembelian_id,))
        conn.commit()
        print(f"[INFO] Transaksi pembelian {pembelian_id} berhasil dihapus.")
        return True
    except Exception as e:
        print(f"[ERROR] gagal menghapus pembelian: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_detail_pembelian(pembelian_id):
    """Retrieves line items for a given purchase ID.

    Args:
        pembelian_id (int): Primary key of the purchase transaction.

    Returns:
        List[Tuple[str, int, float]]: Records containing 'kode_produk', 'qty', and
        'harga_beli'.
    """
    conn = get_connection()
    cursor= conn.cursor()
    cursor.execute("""
        SELECT kode_produk, qty, harga_beli
        FROM detail_pembelian
        WHERE pembelian_id = ?
    """, (pembelian_id,))
    hasil = cursor.fetchall()
    conn.close()
    return hasil

def update_pembelian(pembelian_id, hasil_koreksi):
    """Updates transaction items and recalculates total price for an existing purchase.

    Args:
        pembelian_id (int): Primary key of the purchase transaction to update.
        hasil_koreksi (List[Dict[str, Any]]): Updated list of item dictionaries.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM detail_pembelian WHERE pembelian_id = ?", (pembelian_id,))

    for item in hasil_koreksi:
        cursor.execute("""
            INSERT INTO detail_pembelian (pembelian_id, kode_produk, qty, harga_beli)
            VALUES (?, ?, ?, ?)   
        """, (
            pembelian_id,
            item["kode_produk"],
            item["qty"],
            item["harga_beli"]
        ))
        total_baru = sum(item["qty"] * item["harga_beli"] for item in hasil_koreksi)
        cursor.execute("UPDATE transaksi_pembelian SET total_harga = ? WHERE id_pembelian = ?", (total_baru, pembelian_id))
    conn.commit()
    conn.close()

def hitung_total_keranjang(daftar_barang):
    """Calculates total sum of all item subtotals in a shopping cart list.

    Args:
        daftar_barang (List[Dict[str, Any]]): List of item dictionaries with 'qty'
            and 'harga_beli'.

    Returns:
        float: Grand total amount.
    """
    return sum(item["qty"] * item["harga_beli"] for item in daftar_barang)

def ambil_supplier_nama(supplier_id):
    """Fetches a supplier's name given their supplier ID.

    Args:
        supplier_id (Union[int, str]): Unique identifier of the supplier.

    Returns:
        str: Supplier name if found, or '-' as fallback.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama FROM supplier WHERE id = ?", (supplier_id,))
    hasil = cursor.fetchone()
    conn.close()
    return hasil [0] if hasil else "-"

def get_produk_nama(kode_produk):
    """Retrieves a product's name by its product code.

    Args:
        kode_produk (str): Unique stock-keeping code of the product.

    Returns:
        str: Product name if found, or '-' as fallback.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama_produk FROM produk WHERE kode_produk = ?", (kode_produk,))
    hasil = cursor.fetchone()
    conn.close()
    return hasil[0] if hasil else "-"