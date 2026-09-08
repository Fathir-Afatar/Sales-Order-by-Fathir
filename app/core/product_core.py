# Thir-party
import sqlite3

# Local application
from app.constants.config import get_connection
from app.core.stok_core import catat_log_stok

def get_produk(kode_produk):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_produk, nama_produk, harga_jual FROM produk WHERE kode_produk = ?", (kode_produk,))
    row = cursor.fetchone()
    conn.close()
    columns = ["id", "nama", "harga_jual"]
    return dict(zip(columns, row)) if row else None

def tambah_produk(data):
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   UPDATE produk SET harga_jual = ? WHERE id_produk = ?
                """, (harga_baru, id_produk))
    conn.commit()
    conn.close()

def hapus_produk(id_produk):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   DELETE FROM produk WHERE id_produk = ?
                """, (id_produk,))
    conn.commit()
    conn.close()

def ambil_produk(id_produk):
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
    if any(x is None for x in [harga_beli, harga_jual, stok, berat]):
        raise ValueError("Semua nilai numerik wajib diisi.")
    if any (x < 0 for x in [harga_beli, harga_jual, stok, berat]):
        raise ValueError("Nilai tidak boleh negatif")

def log_debug_produk(id_produk, nama, kode, kategori_id, harga_beli, harga_jual, stok, berat):
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {field} FROM produk WHERE kode_produk = ?", (kode_produk,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def ambil_daftar_produk():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT kode_produk, nama_produk, harga_beli FROM produk")
    hasil = cursor.fetchall()
    conn.close()
    return [{"kode_produk": row[0], "nama": row[1], "harga": row[2]} for row in hasil]

def bersihkan_angka(nilai):
    try:
        if not nilai: return 0.0
        nilai_bersih = str(nilai).replace("Rp", "").replace(",", "").strip()
        return float(nilai_bersih)
    except Exception as e:
        print("[ERROR] Gagal parsing angka:", nilai, e)
        return None

def get_kategori_nama_by_id(id_kategori):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama_kategori FROM kategori WHERE id_kategori = ?", (id_kategori,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "(Kategori Tidak Ditemukan)"

def ambil_semua_kategori():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama_kategori FROM kategori ORDER BY nama_kategori ASC")
    hasil = cursor.fetchall()
    conn.close()
    return [row[0] for row in hasil]

def ambil_produk_by_kategori_id(kategori_id):
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
    return get_field_by_kode(kode_produk, "harga_beli")

def get_kategori_id_by_nama(nama_kategori):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_kategori FROM kategori WHERE nama_kategori = ?", (nama_kategori,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

