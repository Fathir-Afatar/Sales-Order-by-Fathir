import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Import Modular Core

from app.core.product_core import get_produk
from app.core.member_core import semua_member

# Untuk embedded ke GUI

import tkinter as tk

def tambah_ke_keranjang():
    kode = entry_kode_produk.get()
    jumlah = entry_jumlah.get()
    try:
        produk = get_produk(kode)
        if not produk:
            messagebox.showerror("Produk tidak ditemukan", f"Kode '{kode}' tidak valid.")
            return
        keranjang.append({
            "produk_id": produk["id"],
            "produk_nama": produk["nama"],
            "jumlah": int(jumlah),
            "harga_satuan": int(produk["harga_jual"])
        })
        refresh_keranjang()
    except Exception as e:
        messagebox.showerror("Error Tambah Produk", str(e))

def refresh_keranjang():
    tree_keranjang.delete(*tree_keranjang.get_children())
    total = 0
    for item in keranjang:
        subtotal = item["jumlah"] * item["harga_satuan"]
        tree_keranjang.insert("", tk.END, values=(
            item["produk_id"], item["produk_nama"], item["jumlah"], item["harga_satuan"], subtotal
        ))
        total += subtotal
    label_total.config(text=f"Total: Rp {total:,}")
    global grand_total
    grand_total = total

def main():
    global entry_kode_produk, entry_jumlah, tree_keranjang, label_total, keranjang, grand_total, combo_member, entry_voucher
    keranjang = []
    grand_total = 0

    root = tk.Tk()
    root.title("Transaksi Penjualan - POS Pintar")
    root.geometry("700x650")

    # Member
    tk.Label(root, text="Pilih Member (Opsional)").pack()
    member_list = [m["nama"] for m in semua_member()]
    combo_member = ttk.Combobox(root, values=member_list)
    combo_member.pack()

    # Produk
    tk.Label(root, text="Kode Produk").pack()
    entry_kode_produk = tk.Entry(root)
    entry_kode_produk.pack()

    tk.Label(root, text="Jumlah").pack()
    entry_jumlah = tk.Entry(root)
    entry_jumlah.pack()

    tk.Button(root, text="Tambah ke Keranjang", command=tambah_ke_keranjang).pack(pady=5)

    # Keranjang
    tree_keranjang = ttk.Treeview(root, columns=("id", "nama", "jumlah", "harga", "subtotal"), show="headings")
    for col in ("id", "nama", "jumlah", "harga", "subtotal"):
        tree_keranjang.heading(col, text=col.capitalize())
    tree_keranjang.pack(pady=10)

    # Voucher
    tk.Label(root, text="Kode Voucher (jika ada)").pack()
    entry_voucher = tk.Entry(root)
    entry_voucher.pack()

    # Total & Simpan
    label_total = tk.Label(root, text="Total: Rp 0")
    label_total.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()