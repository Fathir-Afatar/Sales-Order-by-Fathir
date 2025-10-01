from app.constants.config import get_connection
conn = get_connection()

# Add Supplier

def tambah_supplier(data):
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

# Edit Supplier

def edit_supplier(id_supplier, data):
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

# Delete Supplier

def hapus_supplier(id_supplier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM supplier WHERE id_supplier = ?", (id_supplier,))
    conn.commit()
    conn.close()

# Take All Supplier

def semua_supplier():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM supplier")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

# Take All Supplier Base on ID

def ambil_supplier():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_supplier, nama_supplier FROM supplier")
    result = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "nama": row[1]} for row in result]

