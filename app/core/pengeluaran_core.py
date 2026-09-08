# Standard Library
from datetime import datetime

# Local application
from app.constants.config import get_connection

def tambah_pengeluaran(data):
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM (nominal) FROM pengeluaran
        WHERE kategori = ?
    """,(kategori,))
    total = cursor.fetchone()[0]
    return total or 0

def hapus_pengeluaran(id_pengeluaran: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pengeluaran WHERE id_pengeluaran =?", (id_pengeluaran,))
    conn.commit()
    conn.close()

def edit_pengeluaran(id_pengeluaran, data):
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
    teks = teks.replace("Rp", "").replace(" ", "").replace(".", "")
    teks = teks.replace(",", ".")
    return teks
