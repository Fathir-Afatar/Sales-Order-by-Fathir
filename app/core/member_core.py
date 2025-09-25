from app.constants.config import get_connection

# Utility: Format hasil query ke dict

def format_row(columns, row):
    return dict(zip(columns, row))

# Add New Member

def tambah_member(nama, alamat=None, nomor=None, tipe=None, ranting=None, kode_member=None):
    if not nama or not kode_member:
        raise ValueError("Nama dan kode member wajib diisi.")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO member (nama, alamat, no_hp, tipe, ranting, kode_member)
                   VALUES (?, ?, ?, ?, ?, ?)
                   """, (nama, alamat, nomor, tipe, ranting, kode_member))
    conn.commit()
    conn.close()

# Update Member Data

def update_member(id_member, nama, nomor, alamat, tipe, ranting, kode_member):
    if not id_member or not nama or not kode_member:
        raise ValueError("ID, Nama, dan Kode Member wajib diisi.")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   UPDATE member
                   SET nama = ?, no_hp=?, alamat = ?, tipe = ?, ranting = ?, kode_member = ?
                   WHERE id_member = ?
                """, (nama, nomor, alamat, tipe, ranting, kode_member, id_member))
    print("[DEBUG] UPDATE query berhasil? Rows affected:", cursor.rowcount)
    conn.commit()
    conn.close()

# Delete Member

def hapus_member(id_member):
    print("[DEBUG] SQL Dijalankan")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM member WHERE id_member = ?", (id_member,))
    conn.commit()
    conn.close()

# Take All Member

def semua_member():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_member, nama, no_hp, alamat, tipe, ranting, kode_member FROM member")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.close()
    return [format_row(columns, row) for row in rows]

# Retrieved Member Based on ID

def ambil_by_kode_member(kode_member):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_member, nama, no_hp, alamat, tipe, ranting, kode_member
        FROM member
        WHERE kode_member = ?
    """, (kode_member,))
    row = cursor.fetchone()
    columns = [columns[0] for col in cursor.description]
    conn.close()
    return format_row(columns, row) if row else None

# Cari Member

def cari_member(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_member, nama, no_hp, alamat, tipe, ranting, kode_member
        FROM member
        WHERE nama LIKE ? OR no_hp LIKE ?
        """, (f'%{keyword}%', f'%{keyword}%'))
    hasil = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.close()
    return [format_row(columns, row) for row in hasil]

def semua_member_dropdown():
    return [f"{m['id_member']} - {m['nama']}" for m in semua_member]