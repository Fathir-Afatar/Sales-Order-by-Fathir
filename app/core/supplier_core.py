# Local Application
from app.constants.config import get_connection

# Add Supplier
def tambah_supplier(data):
    """Inserts a new supplier record into the supplier table.

    Args:
        data (Dict[str, Any]): Dictionary containing supplier fields
            ('nama_supplier', 'alamat', 'no_hp', 'kode_supplier').

    Returns:
        Optional[int]: The primary key ID of the newly inserted supplier row, or
        None if operation fails.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO supplier (nama_supplier, alamat, no_hp, kode_supplier)
                   VALUES (?, ?, ?, ?)
                """, (
                    data.get("nama_supplier"), 
                    data.get("alamat"), 
                    data.get("no_hp"), 
                    data.get("kode_supplier")))
    conn.commit()
    conn.close()

def edit_supplier(id_supplier, data):
    """Updates existing supplier attributes dynamically based on provided dictionary keys.

    Args:
        id_supplier (int): Primary key ID of the supplier to update.
        data (Dict[str, Any]): Dictionary containing fields to update.

    Returns:
        bool: True if records were modified, False if no fields were updated or no
        rows affected.
    """
    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    values = []

    for key in ["nama_supplier", "alamat", "no_hp", "kode_supplier"]:
        if key in data and data[key] is not None:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if not fields:
        conn.close()
        return False #Tidak ada perubahan
    
    query = "UPDATE supplier SET " + ", ".join(fields) + " WHERE id_supplier = ?"
    values.append(id_supplier)

    cursor.execute(query, tuple(values))
    conn.commit()
    conn.close()
    return True

def hapus_supplier(id_supplier):
    """Deletes a supplier record from the database by its primary key ID.

    Args:
        id_supplier (int): Primary key ID of the supplier to delete.

    Returns:
        bool: True if a row was deleted, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM supplier WHERE id_supplier = ?", (id_supplier,))
    conn.commit()
    conn.close()

def semua_supplier():
    """Retrieves all supplier records mapped to dynamic dictionary objects.

    Returns:
        List[Dict[str, Any]]: List of dictionaries representing full supplier
        records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM supplier")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def ambil_supplier():
    """Fetches a simplified list of supplier IDs and names.

    Returns:
        List[Dict[str, Union[int, str]]]: List of dictionaries containing 'id' and
        'nama'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_supplier, nama_supplier FROM supplier")
    result = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "nama": row[1]} for row in result]

