from datetime import datetime
import csv

from app.core.product_core import get_field_by_kode, ubah_stok_dan_catat_log
from app.core.stok_core import catat_log_stok, get_stok_terakhir
from app.constants.config import get_connection
conn = get_connection()

# ── Hitung Total Penjualan ──
def hitung_total_penjualan(daftar_barang):
    total = 0
    for item in daftar_barang:
        total += item["harga_satuan"] * item["jumlah"]
    return total

# ── Proses Penjualan ──
def proses_penjualan(data):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        daftar_barang = data.get("daftar_barang", [])
        member_id = data.get("member_id", "")
        nama_member = data.get("nama_member", "Tanpa Member")
        ongkos_kirim = data.get("ongkos_kirim", 0)
        voucher = data.get("voucher", 0)
        metode_bayar = data.get("metode_bayar", "-")
        catatan = data.get("catatan", "-")
        status = data.get("status", "DRAFT")

        total = hitung_total_penjualan(daftar_barang) + ongkos_kirim

        # Simpan transaksi utama
        cursor.execute("""
            INSERT INTO transaksi_penjualan (
                tanggal, kode_member, nama_member, total_harga, 
                ongkos_kirim, voucher, metode_bayar, catatan, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tanggal, member_id, nama_member, total, ongkos_kirim, voucher, metode_bayar, catatan, status))
        transaksi_id = cursor.lastrowid

        # Simpan detail transaksi + kurangi stok
        for item in daftar_barang:
            produk_id = item["produk_id"]
            jumlah = item["jumlah"]

            cursor.execute("SELECT nama_produk, harga_jual, stok FROM produk WHERE id_produk = ?", (item["produk_id"],))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Produk ID {produk_id} tidak ditemukan.")
            
            nama_produk, harga_jual, stok = result
            if stok < jumlah:
                raise ValueError(f"Stok Produk ID {produk_id} tidak cukup.")
            
            #subtotal = harga_jual * jumlah
            print("[DEBUG] Keys item:", list(item.keys()))
            print("[DEBUG] Simpan detail:", item)
            print("[DEBUG] Nama produk dari DB:", nama_produk)
            cursor.execute("""
                    INSERT INTO detail_penjualan (transaksi_id, produk_id, nama_produk, jumlah, harga_satuan, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (transaksi_id, item["produk_id"], nama_produk, item["jumlah"], item["harga_satuan"], item["subtotal"]))

            ubah_stok_dan_catat_log(cursor, item["produk_id"], -jumlah, "KELUAR")

                # Ambil stok sebelum update
            stok_awal = stok # dari SELECT sebelumnya
            stok_akhir = stok_awal - jumlah

                # Catat log stok keluar
            catat_log_stok(cursor, item["produk_id"], stok_awal, stok_akhir, "KELUAR")
   
        conn.commit()
        return transaksi_id

    except Exception as e:
        conn.rollback()
        print("[ERROR proses_penjualan]", e)
        raise e
    finally:
        conn.close()

def get_nama_pembeli(member_id):
    if not member_id:
        return "Tanpa Member"
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nama FROM member WHERE id_member = ?", (member_id,))
        result = cursor.fetchone()
        return result[0] if result else "Tanpa Member"
    finally:
        conn.close()

# ── Cek Produk Stok Rendah ──
def cek_stok_minimum(threshold):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_produk, nama_produk, stok FROM produk WHERE stok <= ?", (threshold,))
        return cursor.fetchall()  # List produk dengan stok minim
    finally:
        conn.close()

# ── Simpan Nota Penjualan ke CSV ──
def simpan_nota_penjualan_csv(transaksi_id, daftar_barang, total, path="nota.csv"):
    try:
        with open(path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Produk", "Jumlah", "Harga Satuan", "Subtotal"])
            for item in daftar_barang:
                subtotal = item["jumlah"] * item["harga_satuan"]
                writer.writerow([item["nama_produk"], item["jumlah"], item["harga_satuan"], subtotal])
            writer.writerow(["", "", "Total", total])
        print(f"[INFO] Nota transaksi {transaksi_id} berhasil disimpan ke {path}")
    except Exception as e:
        print(f"[ERROR] simpan_nota_penjualan_csv {e}")
        raise e

def simpan_detail_penjualan(transaksi_id, item_list):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for item in item_list:
            produk_id = item["produk_id"]
            jumlah = item["jumlah"]

            # Ambil data produk
            cursor.execute("SELECT nama_produk, harga_jual, stok FROM produk WHERE id_produk = ?", (produk_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Produk ID {produk_id} tidak ditemukan.")

            nama_produk, harga_jual, stok = result
            if stok < jumlah:
                raise ValueError(f"Stok Produk ID {produk_id} tidak cukup.")
            subtotal = harga_jual * jumlah
            # Simpan detail penjualan
            cursor.execute("""
                INSERT INTO detail_penjualan (transaksi_id, produk_id, nama_produk, jumlah, harga_satuan, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)   
            """, (transaksi_id, item["produk_id"], nama_produk, jumlah, harga_jual, subtotal))
            # Update stok dan log
            ubah_stok_dan_catat_log(item["produk_id"], -jumlah)
            stok_awal = stok
            stok_akhir = stok_awal - jumlah
            catat_log_stok(cursor, produk_id, stok_awal, stok_akhir, "KELUAR")
        
            print(f"[INFO] Produk {nama_produk} ({produk_id}) dikurangi {jumlah}. Stok: {stok_awal} -> {stok_akhir}")
        
        conn.commit()
        print(f"[INFO] Detail penjualan untuk transaksi {transaksi_id} berhasil disimpan.")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] simpan_detail_penjualan {e}")
        raise e
    finally:
        conn.close()
