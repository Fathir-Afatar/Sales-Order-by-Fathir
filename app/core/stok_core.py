# Standard Library
from calendar import monthrange
from datetime import datetime

# Local application
from app.constants.config import get_connection

def catat_log_stok(cursor, produk_id, stok_awal, stok_akhir, jenis_perubahan):
    """Inserts a stock movement entry into the stock log table.

    Args:
        cursor (sqlite3.Cursor): Active database transaction cursor.
        produk_id (int): Primary key ID of the product.
        stok_awal (Union[int, float]): Initial stock level before movement.
        stok_akhir (Union[int, float]): Final stock level after movement.
        jenis_perubahan (str): Movement type (e.g., 'MASUK', 'KELUAR').
    """
    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
                   INSERT INTO log_stock(produk_id, tanggal, stok_awal, stok_akhir, jenis_perubahan)
                   VALUES (?, ?, ?, ?, ?)
                """, (produk_id, tanggal, stok_awal, stok_akhir, jenis_perubahan))

def histori_stok(cursor, produk_id):
    """Retrieves full historical stock log records for a given product.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
        produk_id (int): Primary key ID of the product.

    Returns:
        List[Tuple[Any, ...]]: Tuple list of stock log records ordered by date
        descending.
    """
    cursor.execute("""
                   SELECT * FROM log_stock WHERE produk_id = ? ORDER BY tanggal DESC
                """, (produk_id,))
    return cursor.fetchall()

def ambil_log_stok_bulanan(cursor, produk_id, bulan, tahun):
    """Fetches stock logs within a specific month and year range.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
        produk_id (int): Primary key ID of the product.
        bulan (int): Month number (1-12).
        tahun (int): Four-digit year integer.

    Returns:
        List[Tuple[str, Union[int, float], Union[int, float], str]]: List of log
        records containing (tanggal, stok_awal, stok_akhir, jenis_perubahan).
    """
    tanggal_awal = f"{tahun}-{bulan:02d}-01"
    tanggal_akhir = f"{tahun}-{bulan:02d}-{monthrange(tahun, bulan)[1]}"
    cursor.execute("""
        SELECT tanggal, stok_awal, stok_akhir, jenis_perubahan
        FROM log_stock
        WHERE produk_id = ? AND DATE(tanggal) BETWEEN ? AND ?
        ORDER BY tanggal ASC
    """, (produk_id, tanggal_awal, tanggal_akhir))
    return cursor.fetchall()

def proses_stok_harian(logs, bulan, tahun):
    """Aggregates monthly log records into daily stock statistics dictionary.

    Args:
        logs (List[Tuple[str, Union[int, float], Union[int, float], str]]): Log
            records.
        bulan (int): Target month.
        tahun (int): Target year.

    Returns:
        Dict[str, Dict[str, Any]]: Map of day numbers to daily stock metrics.
    """
    hari_ini = datetime.now().day
    stok_harian = {
        str(i): {"awal": None, "akhir":None, "masuk":0, "keluar": 0,  "hari_ini": i == hari_ini} for i in range(1, monthrange(tahun, bulan)[1] + 1)
    }

    for tanggal_str, stok_awal, stok_akhir, jenis in logs:
        jenis =str(jenis).strip().upper()
        hari = str(datetime.strptime(tanggal_str, "%Y-%m-%d %H:%M:%S").day)
        if stok_harian[hari]["awal"] is None:
            stok_harian[hari]["awal"] = stok_awal
        stok_harian[hari]["akhir"] = stok_akhir
        if jenis == "MASUK":
            stok_harian[hari]["masuk"] += stok_akhir - stok_awal
        elif jenis == "KELUAR":
            stok_harian[hari]["keluar"] += stok_awal - stok_akhir
        else:
            print(f"[DEBUG] Hari {hari} | Awal: {stok_awal} | Akhir: {stok_akhir} | Jenis: {jenis}")
            print(f"[DEBUG] Masuk: {stok_harian[hari]['masuk']} | Keluar : {stok_harian[hari]['keluar']}")
            print(f"[DEBUG] Jenis perubahan:", repr(jenis))
    return stok_harian

def bentuk_kartu_stok(stok_harian, bulan, tahun):
    """Formats daily aggregated stock dictionary into a structured stock card list.

    Args:
        stok_harian (Dict[str, Dict[str, Any]]): Daily aggregated stock map.
        bulan (int): Target month.
        tahun (int): Target year.

    Returns:
        List[Dict[str, Any]]: Formatted list of daily stock card entries.
    """
    kartu = []
    for hari in range(1, monthrange(tahun, bulan)[1] + 1):
        h = str(hari)
        kartu.append({
            "tanggal": h,
            "awal": stok_harian[h]["awal"] if stok_harian[h]["awal"] is not None else 0,
            "masuk": stok_harian[h]["masuk"],
            "keluar": stok_harian[h]["keluar"] if stok_harian[h]["keluar"] is not None else 0,
            "akhir": stok_harian[h]["akhir"] if stok_harian[h]["akhir"] is not None else stok_harian[h]["awal"]or 0
        })
    return kartu

def generate_kartu_stok(produk_id, bulan, tahun):
    """Generates a complete monthly stock card report for a product.

    Args:
        produk_id (int): Primary key ID of the product.
        bulan (int): Target month.
        tahun (int): Target year.

    Returns:
        List[Dict[str, Any]]: Generated stock card data list.
    """
    conn = get_connection()
    cursor = conn.cursor()
    logs = ambil_log_stok_bulanan(cursor, produk_id, bulan, tahun)
    conn.close()

    for log in logs:
        print("[DEBUG] Log:", log)

    stok_harian = proses_stok_harian(logs, bulan, tahun)
    return bentuk_kartu_stok(stok_harian, bulan, tahun)

def get_stok_terakhir(cursor, kode_produk):
    """Gets the latest stock count recorded in stock log for a product.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
        produk_id (Union[int, str]): Primary key ID or code of product.

    Returns:
        int: Latest stock count integer or 0 if no record exists.
    """
    cursor.execute("""
        SELECT stok_akhir FROM log_stock
        WHERE produk_id = ?
        ORDER BY tanggal DESC LIMIT 1
    """, (kode_produk,))
    result = cursor.fetchone()
    return int(result[0]) if result and result[0] is not None else 0

def rekalkulasi_stok(cursor, produk_id): 
    """Recalculates stock based on chronological stock log entries.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
        produk_id (int): Target product primary key.

    Returns:
        Union[int, float]: Final recalculated stock value or 0 if logs are empty.
    """
    cursor.execute("""
        SELECT stok_awal, stok_akhir FROM log_stock
        WHERE produk_id = ?
        ORDER BY tanggal ASC
    """, (produk_id,))
    logs = cursor.fetchall()

    if not logs:
        return 0
    return logs[-1][1]

def hapus_log_stok(cursor, produk_id, tanggal = None):
    """
    Deprecated. This function no longer use.
    """
    if tanggal:
        cursor.execute("DELETE FROM log_stock WHERE produk_id = ? AND tanggal = ?", (produk_id, tanggal))
    else:
        cursor.execute("DELETE FROM log_stock WHERE produk_id = ?", (produk_id,))
    return cursor.fetchall()

def get_produk_id_by_nama(nama_produk):
    """Retrieves product ID by searching product name.

    Args:
        nama_produk (str): Target product name string.

    Returns:
        Optional[int]: Product primary key ID if found, else None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_produk FROM produk WHERE nama_produk = ?", (nama_produk,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_daftar_nama_barang():
    """Fetches list of all product names ordered alphabetically.

    Returns:
        List[str]: Alphabetically ordered product names.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama_produk FROM produk ORDER BY nama_produk ASC")
    result = cursor.fetchall()
    conn.close()
    return [row[0] for row in result]

def get_stok_akhir_semua_produk(tanggal):
    """Retrieves last recorded stock count for all products up to a specific date.

    Args:
        tanggal (str): Date threshold string formatted as 'YYYY-MM-DD'.

    Returns:
        List[Dict[str, Any]]: List of dictionary containing 'id', 'nama', and
        'stok'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        tanggal = str(tanggal).strip()
        datetime.strptime(tanggal, "%Y-%m-%d")
    except ValueError as e:
        print("[ERROR] Format tanggal tidak valid:", tanggal)
        return []
    except Exception as e:
        print("[ERROR] Kesalahan lain saat validasi tanggal:", e)
        return []

    cursor.execute("""
        SELECT p.id_produk, p.nama_produk,
        (
                   SELECT stok_akhir FROM log_stock ls
                   WHERE ls.produk_id = p.id_produk AND DATE(ls.tanggal) <= DATE(?)
                   ORDER BY ls.tanggal DESC LIMIT 1
        ) AS stok_akhir
        FROM produk p
        ORDER BY p.nama_produk ASC
    """, (tanggal,))
    result = cursor.fetchall()
    conn.close()

    return [{"id": r[0], "nama":r[1], "stok": r[2] or 0} for r in result]

def cek_log_harian(cursor, produk_id, tanggal):
    """Retrieves stock log movements for a product on a specific date.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
        produk_id (int): Primary key ID of the product.
        tanggal (str): Date prefix string (e.g., 'YYYY-MM-DD').

    Returns:
        List[Tuple[str, Union[int, float], Union[int, float], str]]: List of log
        records.
    """
    tanggal = str(tanggal).strip()
    cursor.execute("""
        SELECT tanggal, stok_awal, stok_akhir, jenis_perubahan
        FROM log_stock
        WHERE produk_id = ? AND tanggal LIKE ?
    """, (produk_id, f"{tanggal}%"))
    return cursor.fetchall()
