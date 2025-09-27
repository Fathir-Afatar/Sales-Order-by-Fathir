# Untuk Audit perubahan stok (manual atau otomatis)
# Riwayat histori persediaan barang
# Integrasi nanti ke laporan mingguan/bulanan
from calendar import monthrange
from datetime import datetime
from app.constants.config import get_connection

# Note Stock Changes

def catat_log_stok(cursor, produk_id, stok_awal, stok_akhir, jenis_perubahan):
    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
                   INSERT INTO log_stock(produk_id, tanggal, stok_awal, stok_akhir, jenis_perubahan)
                   VAlUES (?, ?, ?, ?, ?)
                """, (produk_id, tanggal, stok_awal, stok_akhir, jenis_perubahan))

# Retrieve stock history log of a specific product

def histori_stok(produk_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT * FROM log_stock WHERE produk_id = ? ORDER BY tanggal DESC
                """, (produk_id,))
    result = cursor.fetchall()
    conn.close()
    return result

# fungsi catat_log_stok() nanti dipanggil dari proses_penjualan() dan proses_pembelian(), sehingga setiap perubahan stok terekam otomatis

def generate_kartu_stok(produk_id, bulan, tahun):
    # Menghasilkan list harian stok untuk satu barang dalam satu bulan, cocok untuk ditampilkan di GUI Treeview
    conn = get_connection()
    cursor = conn.cursor()

    tanggal_awal = f"{tahun}-{bulan:02d}-01"
    tanggal_akhir = f"{tahun}-{bulan:02d}-{monthrange(tahun, bulan)[1]}"

    cursor.execute("""
        SELECT tanggal, stok_awal, stok_akhir, jenis_perubahan
        FROM log_stock
        WHERE produk_id = ? AND tanggal BETWEEN ? AND ?
        ORDER BY tanggal ASC
    """, (produk_id, tanggal_awal, tanggal_akhir))
    logs = cursor.fetchall()
    conn.close()

    # Inisialisasi per tanggal

    stok_harian = {str(i): {"awal":None, "akhir":None, "masuk": 0, "keluar": 0} for i in range(1, monthrange(tahun, bulan)[1] + 1)}

    for tanggal_str, stok_awal, stok_akhir, jenis in logs:
        hari = str(int(tanggal_str[8:10])) # ambil tanggal (01-31)

        if stok_harian[hari]["awal"] is None:
            stok_harian[hari]["awal"] = stok_awal
        stok_harian[hari]["akhir"] = stok_akhir

        selisih = stok_akhir - stok_awal
        if jenis == "MASUK":
            stok_harian[hari]["masuk"] += abs(selisih)
        elif jenis == "KELUAR":
            stok_harian[hari]["keluar"] += abs(selisih)

    kartu = []    
    for hari in range(1, monthrange(tahun, bulan)[1] + 1):
        h = str(hari)
        kartu.append({
            "tanggal": h,
            "awal": stok_harian[h]["awal"] or 0,
            "masuk": stok_harian[h]["keluar"],
            "akhir": stok_harian[h]["akhir"] or stok_harian[h]["awal"] or 0
        })
    
    return kartu

def get_stok_terakhir(cursor, kode_produk):
    # Ambil stok terakhir dari log, berguna saat validasi penjualan atau pembelian
    cursor.execute("""
        SELECT stok_akhir FROM log_stock
        WHERE produk_id = ?
        ORDER BY tanggal DESC LIMIT 1
    """, (kode_produk,))
    result = cursor.fetchone()
    return result[0] if result else 0

def rekalkulasi_stok(produk_id): 
    # untuk audit ulang stok berdasarkan log, bisa hitung ulang dari stok awal dan semua perubahan.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT stok_awal, stok_akhir FROM log_stock
        WHERE produk_id = ?
        ORDER BY tanggal ASC
    """, (produk_id,))
    logs = cursor.fetchall()
    conn.close()

    if not logs:
        return 0
    return logs[-1][1] # stok_akhir dari log terakhir

def hapus_log_stok(produk_id, tanggal = None):
    # untuk debugging atau rollback manual
    conn = get_connection()
    cursor = conn.cursor()
    if tanggal:
        cursor.execute("DELETE FROM log_stock WHERE produk_id = ? AND tanggal = ?", (produk_id, tanggal))
    else:
        cursor.execute("DELETE FROM log_stock WHERE produk_id = ?", (produk_id,))
    conn.commit()
    conn.close()

def get_produk_id_by_nama(nama_produk):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_produk FROM produk WHERE nama_produk = ?", (nama_produk,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_daftar_nama_barang():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama_produk FROM produk ORDER BY nama_produk ASC")
    result = cursor.fetchall()
    conn.close()
    return [row[0] for row in result]

def get_stok_akhir_semua_produk(tanggal):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id_produk, p.nama_produk,
        (
                   SELECT stok_akhir FROM log_stock ls
                   WHERE ls.produk_id = p.id_produk AND DATE(ls.tanggal) =< DATE(>)
        ) AS stok_akhir
        FROM produk p
        ORDER BY p.nama_produk ASC
    """, (tanggal,))
    result = cursor.fetchall()
    conn.close()

    return [{"id": r[0], "nama":r[1], "stok": r[2] or 0} for r in result]
