# Standard Library
from datetime import datetime

# Local application
from app.constants.config import get_connection

def tambah_pengeluaran(data):
    """Inserts a new expense record into the database.

    Args:
        data (Dict[str, Any]): Dictionary containing expense fields such as
            'tanggal', 'nama_pengeluaran', 'nominal', 'keterangan', and 'kategori'.

    Raises:
        ValueError: If nominal is not a numeric type or category is missing/empty.
    """
    tanggal = data.get("tanggal") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cursor = conn.cursor()
    if not isinstance(data.get("nominal"), (int, float)):
        raise ValueError("Nominal harus berupa angka")
    if not data.get("kategori"):
        raise ValueError("Kategori tidak boleh kosong")
    try:
        cursor.execute("""
                   INSERT INTO pengeluaran (tanggal, nama_pengeluaran, nominal, keterangan, kategori)
                   VALUES (?, ?, ?, ?, ?)
                """, (tanggal,
                      data.get("nama_pengeluaran"),
                      data.get("nominal"),
                      data.get("keterangan"),
                      data.get("kategori")))
        conn.commit()
    except Exception as e:
        print("[ERROR] Gagal simpan pengeluaran:", e)
    finally:
        conn.close()

def semua_pengeluaran(limit = None):
    """Retrieves all expense records ordered by date descending.

    Args:
        limit (Optional[int]): Maximum number of records to return. Defaults to
            None.

    Returns:
        List[Dict[str, Any]]: List of expense record dictionaries.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM pengeluaran ORDER BY tanggal DESC"
    if limit:
        query += f" LIMIT {limit}"
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.commit()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def pengeluaran_per_bulan(bulan: str, tahun: int):
    """Retrieves expenses filtered by month and year.

    Args:
        bulan (str): Two-digit month string (e.g., '01', '12').
        tahun (Union[int, str]): Year value (e.g., 2026 or '2026').

    Returns:
        List[Dict[str, Any]]: List of matching expense records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM pengeluaran
        WHERE strftime('%m', tanggal) = ?
        AND strftime ('%Y', tanggal) = ?
    """, (bulan, str(tahun)))
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.commit()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def pengeluaran_per_kategori(kategori: str):
    """Retrieves expenses filtered by category name.

    Args:
        kategori (str): Category name to filter by.

    Returns:
        List[Dict[str, Any]]: List of matching expense records ordered by date
        descending.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM pengeluaran
        WHERE kategori = ?
        ORDER BY tanggal DESC
    """, (kategori,))
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.commit()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def pengeluaran_bulan_kategori(bulan: str, tahun: int, kategori:str):
    """Retrieves expenses filtered by month, year, and category.

    Args:
        bulan (str): Two-digit month string.
        tahun (Union[int, str]): Year value.
        kategori (str): Category name to filter by.

    Returns:
        List[Dict[str, Any]]: List of matching expense records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM pengeluaran
        WHERE strftime ('%m', tanggal) = ?
        AND strftime('%Y', tanggal) = ?
        AND kategori = ?
    """, (bulan, str(tahun), kategori))
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.commit()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def total_pengeluaran_kategori(kategori: str):
    """Calculates total expense sum for a specific category.

    Args:
        kategori (str): Target category name.

    Returns:
        float: Summed nominal amount or 0.0 if no records found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM (nominal) FROM pengeluaran
        WHERE kategori = ?
    """,(kategori,))
    total = cursor.fetchone()[0]
    return total or 0

def hapus_pengeluaran(id_pengeluaran: int):
    """Deletes an expense record by its unique ID.

    Args:
        id_pengeluaran (int): Primary key ID of the expense record to delete.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pengeluaran WHERE id_pengeluaran =?", (id_pengeluaran,))
    conn.commit()
    conn.close()

def edit_pengeluaran(id_pengeluaran, data):
    """Updates an existing expense record by ID.

    Args:
        id_pengeluaran (int): Primary key ID of the record to edit.
        data (Dict[str, Any]): Updated dictionary with keys 'tanggal',
            'nama_pengeluaran', 'kategori', 'nominal', and 'keterangan'.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        UPDATE pengeluaran
        SET tanggal = ?, nama_pengeluaran = ?, kategori = ?, nominal = ?, keterangan = ?
        WHERE id_pengeluaran = ?
    """
    cursor.execute(query, (
        data.get("tanggal"),
        data.get("nama_pengeluaran"),
        data.get("kategori"),
        data.get("nominal"),
        data.get("keterangan"),
        id_pengeluaran
    )) 
    conn.commit()
    conn.close()

def bersihkan_angka(teks):
    """Sanitizes currency text string into a standardized numeric format string.

    Args:
        teks (str): Input currency string (e.g., 'Rp 50.000,00').

    Returns:
        str: Cleaned string ready for numerical parsing (e.g., '50000.00').
    """
    teks = teks.replace("Rp", "").replace(" ", "").replace(".", "")
    teks = teks.replace(",", ".")
    return teks
