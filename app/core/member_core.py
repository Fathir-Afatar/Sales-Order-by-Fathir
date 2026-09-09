# Local application
from app.constants.config import get_connection

def format_row(columns, row):
    """Maps table columns and row values into a dictionary.

    Args:
        columns (Sequence[str]): Sequence of database column names.
        row (Sequence[Any]): Database row values corresponding to the columns.

    Returns:
        Dict[str, Any]: A dictionary mapping column names to row values.
    """
    return dict(zip(columns, row))

def tambah_member(nama, alamat=None, nomor=None, tipe=None, ranting=None, kode_member=None):
    """Inserts a new member record into the database.

    Args:
        nama (str): Full name of the member.
        alamat (Optional[str]): Home address. Defaults to None.
        nomor (Optional[str]): Contact/phone number. Defaults to None.
        tipe (Optional[str]): Member classification type. Defaults to None.
        ranting (Optional[str]): Branch/sub-unit assignment. Defaults to None.
        kode_member (Optional[str]): Unique member code.

    Raises:
        ValueError: If `nama` or `kode_member` is empty/None.
    """
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

def update_member(id_member, nama, nomor, alamat, tipe, ranting, kode_member):
    """Updates an existing member record in the database.

    Args:
        id_member (int): Primary key ID of the member to update.
        nama (str): Updated full name.
        nomor (Optional[str]): Updated phone number.
        alamat (Optional[str]): Updated address.
        tipe (Optional[str]): Updated member classification.
        ranting (Optional[str]): Updated branch assignment.
        kode_member (str): Updated unique member code.

    Raises:
        ValueError: If `id_member`, `nama`, or `kode_member` is missing.
    """
    if not id_member or not nama or not kode_member:
        raise ValueError("ID, Nama, dan Kode Member wajib diisi.")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   UPDATE member
                   SET nama = ?, no_hp=?, alamat = ?, tipe = ?, ranting = ?, kode_member = ?
                   WHERE id_member = ?
                """, (nama, nomor, alamat, tipe, ranting, kode_member, id_member))
    conn.commit()
    conn.close()

def hapus_member(id_member):
    """Deletes a member record from the database by ID.

    Args:
        id_member (int): Primary key ID of the member to delete.
    """
    print("[DEBUG] SQL Dijalankan")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM member WHERE id_member = ?", (id_member,))
    conn.commit()
    conn.close()

def semua_member():
    """Fetches all member records from the database.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing all member
        records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_member, nama, no_hp, alamat, tipe, ranting, kode_member FROM member")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.close()
    return [format_row(columns, row) for row in rows]

def ambil_by_kode_member(kode_member):
    """Retrieves a single member record by unique member code.

    Args:
        kode_member (str): Unique member code to query.

    Returns:
        Optional[Dict[str, Any]]: Member record dictionary if found, otherwise
        None.
    """
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

def cari_member(keyword):
    """Searches member records by matching name or phone number keyword.

    Args:
        keyword (str): Search string to match against name or phone number.

    Returns:
        List[Dict[str, Any]]: List of member dictionaries matching the keyword.
    """
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
    """Generates formatted strings for populating UI dropdown selection items.

    Returns:
        List[str]: Formatted string list in 'ID - Nama' format.
    """
    return [f"{m['id_member']} - {m['nama']}" for m in semua_member]