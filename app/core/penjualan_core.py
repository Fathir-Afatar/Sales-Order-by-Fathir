# Standard Library
import csv
import sqlite3

# Third party
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Local application
from app.core.product_core import ubah_stok_dan_catat_log
from app.core.stok_core import catat_log_stok
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
            
            cursor.execute("""
                    INSERT INTO detail_penjualan (transaksi_id, produk_id, nama_produk, jumlah, harga_satuan, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (transaksi_id, item["produk_id"], nama_produk, item["jumlah"], item["harga_satuan"], item["subtotal"]))

            ubah_stok_dan_catat_log(cursor, item["produk_id"], -jumlah, "KELUAR")

            stok_awal = stok # dari SELECT sebelumnya
            stok_akhir = stok_awal - jumlah

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

def cek_stok_minimum(threshold):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_produk, nama_produk, stok FROM produk WHERE stok <= ?", (threshold,))
        return cursor.fetchall()  # List produk dengan stok minim
    finally:
        conn.close()

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

            cursor.execute("SELECT nama_produk, harga_jual, stok FROM produk WHERE id_produk = ?", (produk_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Produk ID {produk_id} tidak ditemukan.")

            nama_produk, harga_jual, stok = result
            if stok < jumlah:
                raise ValueError(f"Stok Produk ID {produk_id} tidak cukup.")
            subtotal = harga_jual * jumlah

            cursor.execute("""
                INSERT INTO detail_penjualan (transaksi_id, produk_id, nama_produk, jumlah, harga_satuan, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)   
            """, (transaksi_id, item["produk_id"], nama_produk, jumlah, harga_jual, subtotal))

            ubah_stok_dan_catat_log(item["produk_id"], -jumlah)
            stok_awal = stok
            stok_akhir = stok_awal - jumlah
            catat_log_stok(cursor, produk_id, stok_awal, stok_akhir, "KELUAR")
        
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] simpan_detail_penjualan {e}")
        raise e
    finally:
        conn.close()

def get_daftar_member():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id_member, nama FROM member ORDER BY nama ASC")
    hasil = cursor.fetchall()
    for row in hasil:
        print(dict(row))
    conn.close()
    return [{"id": row[0], "nama": row[1]} for row in hasil]

def load_transaksi_rincian(tree_widget):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT id_transaksi, tanggal, total_harga 
                    FROM transaksi_penjualan 
                    ORDER BY id_transaksi DESC
    """)
    rows = cursor.fetchall()
    conn.close()
        
    tree_widget.delete(*tree_widget.get_children())
    for row in rows:
        tree_widget.insert("", tk.END, values=(row[0], row[1], f"Rp {row[2]:,.0f}", ""))
    tree_widget.update_idletasks()
        
def cek_nama_member(member_id):
    if not isinstance(member_id, int):
        return "[ID tidak valid]"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama FROM member WHERE id_member = ?", (member_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "[Tidak ditemukan]"

def handler_cek_nama_member(member_var, label_widget, daftar_member):
    nama_input = member_var.get().strip()
    member_id = next((m["id"] for m in daftar_member if m["nama"] == nama_input), None)

    if member_id is None:
        label_widget.config(text = "Nama member: [Tidak ditemukan]", fg= "red")
    else:
        label_widget.config(text=f"Nama Member: {nama_input}", fg="green")

def hitung_total_transaksi(treeview, total_var, ongkir_entry=None):
    total = 0
    for child in treeview.get_children():
        item = treeview.item(child)["values"]
        if len(item) >= 4:
            try:
                subtotal = int(item[3])  # kolom ke-4 = subtotal
                total += subtotal
            except:
                pass

    # Tambahkan ongkir jika ada
    if ongkir_entry:
        try:
            ongkir = float(ongkir_entry.get().strip())
            total += ongkir
        except:
            pass

    total_var.set(f"Total: Rp{total:,}")

def get_selected_transaksi_id(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Pilih Transaksi", "Pilih transaksi terlebih dahulu.")
        return None
    item = tree.item(selected[0])
    return item["values"][0]

def get_detail_transaksi(transaksi_id):
    if not transaksi_id:
        return None, None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nama_member, ongkos_kirim, total_harga, status, tanggal 
        FROM transaksi_penjualan 
        WHERE id_transaksi = ?
    """, (transaksi_id,))
    transaksi_row = cursor.fetchone()

    if not transaksi_row:
        conn.close()
        return None, None

    transaksi_info = {
        "pembeli": transaksi_row[0] or "Tanpa Member",
        "ongkir": transaksi_row[1] or 0,
        "total": transaksi_row[2],
        "status": transaksi_row[3],
        "tanggal": transaksi_row[4]
    }

    cursor.execute("""
        SELECT nama_produk, jumlah, harga_satuan, diskon, subtotal, catatan 
        FROM detail_penjualan 
        WHERE transaksi_id = ?
    """, (transaksi_id,))
    items = cursor.fetchall()
    conn.close()

    item_dicts = [
        {
            "produk_nama": i[0], 
            "jumlah": i[1], 
            "harga_satuan": i[2], 
            "diskon": i[3], 
            "subtotal": i[4], 
            "catatan": i[5]
        } 
        for i in items
    ]

    return transaksi_info, item_dicts

