# Thir-party
import sqlite3

# Local application
from app.constants.config import get_connection
from app.core.stok_core import catat_log_stok

def get_produk(kode_produk):
    """Retrieves product details by product code.

    Args:
        kode_produk (str): Unique product code to look up.

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing product details or None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_produk, nama_produk, harga_jual FROM produk WHERE kode_produk = ?", (kode_produk,))
    row = cursor.fetchone()
    conn.close()
    columns = ["id", "nama", "harga_jual"]
    return dict(zip(columns, row)) if row else None

def tambah_produk(data):
    """Inserts a new product record into the database.

    Args:
        data (Dict[str, Any]): Product information dictionary containing 'nama',
            'kode_produk', 'kategori_id', 'merk', 'harga_beli', 'harga_jual',
            'stok', and 'berat'.

    Returns:
        bool: True if insertion succeeded, False otherwise.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                   INSERT INTO produk (nama_produk, kode_produk, kategori_id, merk, harga_beli, harga_jual, stok, berat)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (data["nama"], data["kode_produk"], data["kategori_id"], data["merk"], data["harga_beli"], data["harga_jual"], data["stok"], data["berat"]))
        conn.commit()
        return True
    except Exception as e:
        print(f"Gagal tambah produk: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def edit_harga_produk(id_produk, harga_baru):
    """Updates the selling price of a product by ID.

    Args:
        id_produk (int): Target product primary key.
        harga_baru (Union[int, float]): New selling price value.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   UPDATE produk SET harga_jual = ? WHERE id_produk = ?
                """, (harga_baru, id_produk))
    conn.commit()
    conn.close()

def hapus_produk(id_produk):
    """Deletes a product record from the database by ID.

    Args:
        id_produk (int): Target product primary key to delete.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   DELETE FROM produk WHERE id_produk = ?
                """, (id_produk,))
    conn.commit()
    conn.close()

def ambil_produk(id_produk):
    """Fetches a complete product record by ID.

    Args:
        id_produk (int): Primary key ID of the target product.

    Returns:
        Optional[Dict[str, Any]]: Product field dictionary or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT * FROM produk WHERE id_produk = ?
                """, (id_produk,))
    result = cursor.fetchone()
    conn.close()
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, result)) if result else None

def validate_produk_data(harga_beli, harga_jual, stok, berat):
    """Validates numeric input attributes for product creation/update.

    Args:
        harga_beli (Optional[Union[int, float]]): Purchase price value.
        harga_jual (Optional[Union[int, float]]): Selling price value.
        stok (Optional[Union[int, float]]): Stock quantity value.
        berat (Optional[Union[int, float]]): Product weight value.

    Raises:
        ValueError: If any parameter is None or holds a negative number.
    """
    if any(x is None for x in [harga_beli, harga_jual, stok, berat]):
        raise ValueError("Semua nilai numerik wajib diisi.")
    if any (x < 0 for x in [harga_beli, harga_jual, stok, berat]):
        raise ValueError("Nilai tidak boleh negatif")

def log_debug_produk(id_produk, nama, kode, kategori_id, harga_beli, harga_jual, stok, berat):
    """Prints debug info to console before executing product update operations.

    Args:
        id_produk (int): Product primary key ID.
        nama (str): Product name.
        kode (str): Product code.
        kategori_id (int): Category foreign key ID.
        harga_beli (Union[int, float]): Purchase price.
        harga_jual (Union[int, float]): Selling price.
        stok (Union[int, float]): Stock count.
        berat (Union[int, float]): Item weight.
    """
    print("[DEBUG] Menjalankan update_produk dengan:")
    print("ID:", id_produk)
    print("Nama:", nama)
    print("Kode:", kode)
    print("Kategori ID:", kategori_id)
    print("Harga Beli:", harga_beli)
    print("Harga Jual:", harga_jual)
    print("Stok:", stok)
    print("Berat:", berat)

def update_produk(id_produk, nama, kode, kategori_id, merk, harga_beli, harga_jual, stok, berat):
    """Validates product fields and updates database record.

    Args:
        id_produk (int): Target product primary key ID.
        nama (str): Product name.
        kode (str): Product code.
        kategori_id (int): Category foreign key ID.
        merk (str): Brand name string.
        harga_beli (Union[int, float]): Purchase price.
        harga_jual (Union[int, float]): Selling price.
        stok (Union[int, float]): Current stock quantity.
        berat (Union[int, float]): Item weight.

    Returns:
        bool: True if updated successfully, False if validation fails.
    """
    try:
        validate_produk_data(harga_beli, harga_jual, stok, berat)
    except ValueError as e:
        print("[ERROR]", e)
        return False

    log_debug_produk(id_produk, nama, kode, kategori_id, harga_beli, harga_jual, stok, berat)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   UPDATE produk
                   SET nama_produk = ?, kode_produk = ?, kategori_id = ?, merk = ?, harga_beli = ?, harga_jual = ?, stok = ?, berat = ?
                   WHERE id_produk = ?
                """, (nama, kode, kategori_id, merk, harga_beli, harga_jual, stok, berat, id_produk))
    conn.commit()
    conn.close()
    return True

def ubah_stok_dan_catat_log(cursor, produk_id, delta, jenis_perubahan):
    """Adjusts stock quantity within an active database transaction cursor.

    Args:
        cursor (sqlite3.Cursor): Active database transaction cursor.
        produk_id (int): Target product primary key.
        delta (Union[int, float]): Change in quantity (positive or negative).
        jenis_perubahan (str): Description/category of inventory change (e.g.,
            'KELUAR').

    Returns:
        bool: True on successful stock modification.

    Raises:
        ValueError: If product ID is not found.
    """
    cursor.execute("SELECT stok FROM produk WHERE id_produk = ?", (produk_id,))
    result = cursor.fetchone()
    if result is None:
        raise ValueError(f"Produk ID {produk_id} tidak ditemukan.")
    stok_awal = result[0]
    stok_akhir = stok_awal + delta

    cursor.execute("UPDATE produk SET stok = ? WHERE id_produk = ?", (stok_akhir, produk_id))
    catat_log_stok(cursor, produk_id, stok_awal, stok_akhir, jenis_perubahan)
    return True

def semua_produk():
    """Fetches all product records joined with their corresponding category names.

    Returns:
        List[Dict[str, Any]]: List of dictionary representations of products.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """SELECT produk.*, kategori.nama_kategori FROM produk LEFT JOIN kategori ON produk.kategori_id = kategori.id_kategori"""
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.close()

    produk_list = [dict(zip(columns, row)) for row in rows]
    for produk in produk_list:
        print("[DEBUG] Produk:", produk)

    return produk_list

def get_field_by_kode(kode_produk, field):
    """Retrieves a specific field value of a product by its product code.

    Args:
        kode_produk (str): Target product code string.
        field (str): Name of the column field to query.

    Returns:
        Optional[Any]: Field value if found, else None.

    Raises:
        ValueError: If field parameter is not in ALLOWED_PRODUCT_FIELDS whitelist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {field} FROM produk WHERE kode_produk = ?", (kode_produk,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def ambil_daftar_produk():
    """Retrieves a minimal product list containing code, name, and purchase price.

    Returns:
        List[Dict[str, Any]]: List of dictionary representations of products.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT kode_produk, nama_produk, harga_beli FROM produk")
    hasil = cursor.fetchall()
    conn.close()
    return [{"kode_produk": row[0], "nama": row[1], "harga": row[2]} for row in hasil]

def bersihkan_angka(nilai):
    """Cleans currency or formatted text and converts it to float.

    Args:
        nilai (Any): Input string or numeric value to parse.

    Returns:
        Optional[float]: Converted float value, 0.0 if empty, or None on error.
    """
    try:
        if not nilai: return 0.0
        nilai_bersih = str(nilai).replace("Rp", "").replace(",", "").strip()
        return float(nilai_bersih)
    except Exception as e:
        print("[ERROR] Gagal parsing angka:", nilai, e)
        return None

def get_kategori_nama_by_id(id_kategori):
    """Retrieves category name by category ID.

    Args:
        id_kategori (int): Category primary key ID.

    Returns:
        str: Category name or default fallback string if missing.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama_kategori FROM kategori WHERE id_kategori = ?", (id_kategori,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "(Kategori Tidak Ditemukan)"

def ambil_semua_kategori():
    """Retrieves all category names sorted alphabetically.

    Returns:
        List[str]: List of category name strings.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama_kategori FROM kategori ORDER BY nama_kategori ASC")
    hasil = cursor.fetchall()
    conn.close()
    return [row[0] for row in hasil]

def ambil_produk_by_kategori_id(kategori_id):
    """Retrieves products under a specific category ID joined with category name.

    Args:
        kategori_id (int): Foreign key ID of the category.

    Returns:
        List[Dict[str, Any]]: List of matching product record dictionaries.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT produk.*, kategori.nama_kategori 
        FROM 
        produk LEFT JOIN kategori ON produk.kategori_id = kategori.id_kategori 
        WHERE produk.kategori_id = ? """
    cursor.execute(query, (kategori_id,))
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(columns, row)) for row in rows]
            
def tambah_kategori(nama):
    """Inserts a new product category name into the database.

    Args:
        nama (str): Category name string.

    Returns:
        bool: True if created successfully, False on empty input or conflict.
    """
    nama = nama.strip()
    if not nama:
        print("[ERROR] Nama kategori kosong.")
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO kategori (nama_kategori) VALUES (?)", (nama,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_produk_by_id(id_produk):
    """Retrieves product details by ID with standardized key names.

    Args:
        id_produk (int): Primary key ID of target product.

    Returns:
        Optional[Dict[str, Any]]: Product attributes dictionary or None if not
        found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_produk, nama_produk, kode_produk, kategori_id, merk, harga_beli, harga_jual, stok, berat FROM produk WHERE id_produk = ?", (id_produk,))
    row = cursor.fetchone()
    conn.close()

    if row:
        keys = ["id_produk","nama_produk","kode_produk","kategori_produk",
            "merk","harga_beli","harga_jual","stok","berat"]
        return dict(zip(keys, row))
    return None

def get_harga_beli(kode_produk):
    """Helper to retrieve purchase price of a product by product code.

    Args:
        kode_produk (str): Product code to look up.

    Returns:
        Optional[Union[int, float]]: Purchase price value or None.
    """
    return get_field_by_kode(kode_produk, "harga_beli")

def get_kategori_id_by_nama(nama_kategori):
    """Retrieves category ID by category name lookup.

    Args:
        nama_kategori (str): Name of the category.

    Returns:
        Optional[int]: Category ID integer if found, else None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_kategori FROM kategori WHERE nama_kategori = ?", (nama_kategori,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

