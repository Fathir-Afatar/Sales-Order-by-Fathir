from datetime import datetime
import csv

from app.core.product_core import get_field_by_kode, ubah_stok_dan_catat_log
from app.core.stok_core import catat_log_stok, get_stok_terakhir
from app.constants.config import get_connection
conn = get_connection()

# ── Hitung Total Penjualan ──
def hitung_total_penjualan(daftar_barang, cursor):
    total = 0
    for item in daftar_barang:
        cursor.execute("SELECT harga_jual FROM produk WHERE id_produk = ?", (item["produk_id"],))
        harga = cursor.fetchone()
        if harga:
            total += harga[0] * item["jumlah"]
    return total

# ── Proses Penjualan ──
def proses_penjualan(member_id, daftar_barang, ongkos_kirim=0, voucher=0, metode_bayar="", nama_member=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        total = hitung_total_penjualan(daftar_barang, cursor) + ongkos_kirim
        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Simpan transaksi utama
        metode_bayar = "-"
        status = "DRAFT"
        catatan = "-"
        print("[DEBUG] metode_bayar:", repr(metode_bayar))
        print("[DEBUG] catatan:", repr(catatan))
        print("[DEBUg] Nilai yang dikirim ke INSERT:")
        print(tanggal, member_id, nama_member, total, ongkos_kirim, voucher, metode_bayar, catatan, status)
        print("[DEBUG] Jumlah nilai:", len((tanggal, member_id, nama_member, total, ongkos_kirim, voucher, metode_bayar, catatan, status)))
        print("[DEBUG] Tipe masing-masing nilai:")
        for val in (tanggal, member_id, nama_member, total, ongkos_kirim, voucher, metode_bayar, catatan, status):
            print(type(val), val)
        cursor.execute("""
            INSERT INTO transaksi_penjualan (tanggal, kode_member, nama_member, total_harga, ongkos_kirim, voucher, metode_bayar, catatan, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tanggal, member_id, nama_member, total, ongkos_kirim, voucher, metode_bayar, catatan, status))
        transaksi_id = cursor.lastrowid

        # Simpan detail transaksi + kurangi stok
        for item in daftar_barang:
            cursor.execute("SELECT nama_produk, harga_jual, stok FROM produk WHERE id_produk = ?", (item["produk_id"],))
            data = cursor.fetchone()
            if data:
                nama_produk, harga_jual, stok = data
                jumlah = item["jumlah"]
                if stok < jumlah:
                    conn.close()
                    raise ValueError(f"Stok Produk ID {item['produk_id']} tidak cukup.")

                print("[DEBUG] Detail item:", item)
                print("[DEBUG] Nilai detail:", transaksi_id, item.get("produk_id"), nama_produk, jumlah, harga_jual, harga_jual * jumlah)
                print("[DEBUG] Jumlah Nilai:", len((transaksi_id, item.get("produk_id"), nama_produk, jumlah, harga_jual, harga_jual * jumlah)))
                cursor.execute("""
                    INSERT INTO detail_penjualan (transaksi_id, produk_id, nama_produk, jumlah, harga_satuan, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (transaksi_id, item["produk_id"], nama_produk, jumlah, harga_jual, harga_jual * jumlah))

                ubah_stok_dan_catat_log(item["produk_id"], -jumlah)

                # Ambil stok sebelum update
                stok_awal = stok # dari SELECT sebelumnya
                stok_akhir = stok_awal - jumlah

                # Catat log stok keluar
                catat_log_stok(cursor, item["produk_id"], stok_awal, stok_akhir, "KELUAR")

        print("DEBUG proses_penjualan")
        print("Total belanja:", total)
        print("Jumlah item:", len(daftar_barang))     
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
        return transaksi_id

def get_nama_pembeli(member_id, cursor):
    if not member_id:
        return "Tanpa Member"
    cursor.execute("SELECT nama FROM member WHERE id_member = ?", (member_id,))
    result = cursor.fetchone()
    return result[0] if result else "Tanpa Member"

# ── Cek Produk Stok Rendah ──
def cek_stok_minimum(threshold, cursor):
    cursor.execute("SELECT id_produk, nama_produk, stok FROM produk WHERE stok <= ?", (threshold,))
    return cursor.fetchall()  # List produk dengan stok minim

# ── Simpan Nota Penjualan ke CSV ──
def simpan_nota_penjualan_csv(transaksi_id, daftar_barang, total, path="nota.csv"):
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Produk", "Jumlah", "Harga Satuan", "Subtotal"])
        for item in daftar_barang:
            subtotal = item["jumlah"] * item["harga_satuan"]
            writer.writerow([item["nama_produk"], item["jumlah"], item["harga_satuan"], subtotal])
        writer.writerow(["", "", "Total", total])

def simpan_detail_penjualan(transaksi_id, item_list):
    conn = get_connection()
    cursor = conn.cursor()

    for item in item_list:
        harga_jual = item["harga_jual"]
        jumlah = item["jumlah"]
        nama_produk = item["nama_produk"]
        subtottal = harga_jual * jumlah
        cursor.execute("""
                INSERT INTO detail_penjualan (transaksi_id, produk_id, nama_produk, jumlah, harga_satuan, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)   
        """, (transaksi_id, item["produk_id"], nama_produk, jumlah, harga_jual, subtottal))
        ubah_stok_dan_catat_log(item["produk_id"], -jumlah)
    conn.commit()
    conn.close()
