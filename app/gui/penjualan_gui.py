import tkinter as tk
from datetime import datetime
import csv
import sqlite3
import time
#from escpos.printer import Usb
from tkinter import ttk, messagebox, Listbox
from app.core.penjualan_core import proses_penjualan, get_nama_pembeli
from app.core.product_core import semua_produk
from app.constants.config import get_connection
from app.core.member_core import semua_member

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from local_escpos.printer import Usb


transaksi_terakhir = None

def buat_frame_penjualan(parent):
    frame = tk.Frame(parent)

    #------ Notebook Tabs ----
    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    tab_transaksi = tk.Frame(notebook)
    tab_rincian = tk.Frame(notebook)

    notebook.add(tab_transaksi, text="Transaksi")
    notebook.add(tab_rincian, text="Rincian")

    # -----Produk & Jumlah ---
    
    produk_list = semua_produk()
    for p in produk_list:
        print("[DEBUG] ProdukL", p)
    produk_display_list = {f"{p['nama_produk']} (ID {p['id_produk']})": p for p in produk_list}

    produk_var = tk.StringVar()
    total_var = tk.StringVar(value="Total: Rp0")
    keranjang = []

    # ----- Frame Form Input -----

    form_frame = tk.Frame(tab_transaksi)
    form_frame.grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=10)

    tombol_frame = tk.Frame(tab_transaksi)
    tombol_frame.grid(row=1, column=0, columnspan=4, pady=10)

    keranjang_frame = tk.Frame(tab_transaksi)
    keranjang_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

    keranjang_scroll = tk.Scrollbar(keranjang_frame, orient="vertical")
    keranjang_scroll.pack(side="right", fill="y")

    tk.Label(form_frame, text="Pilih Produk").grid(row=0, column=0, sticky="w")
    produk_entry = tk.Entry(form_frame, textvariable=produk_var, width=40)
    produk_entry.grid(row=0, column=1, padx=5)

    produk_listbox = tk.Listbox(form_frame, width=40, height=5)
    produk_listbox.grid(row=1, column=1, padx=5, pady=5)
    produk_listbox.grid_remove()

    tk.Label(form_frame, text="Jumlah").grid(row=2, column=0, sticky="w")
    jumlah_entry = tk.Entry(form_frame, width=10)
    jumlah_entry.grid(row=2, column=1, sticky="w", padx=5)

    tk.Label(form_frame, text="ID Member").grid(row=3, column=0, sticky="w")
    member_entry = tk.Entry(form_frame, width=20)
    member_entry.grid(row=3, column=1, sticky="w", padx=5)

    tk.Label(form_frame, text="Harga Manual (opsional)").grid(row=4, column=0, sticky="w")
    harga_manual_entry = tk.Entry(form_frame, width=15)
    harga_manual_entry.grid(row=4, column=1, sticky="w", padx=5)
    tk.Label(form_frame, text="*Kosongkan jika ingin pakai harga default", fg="gray").grid(row=5, column=1, sticky="w", padx=5)

    tk.Label(form_frame, text="Ongkos Kirim (opsional)").grid(row=6, column=0, sticky="w")
    ongkir_entry = tk.Entry(form_frame, width=15)
    ongkir_entry.grid(row=6, column=1, sticky="w", padx=5)
    tk.Label(form_frame, text="* Kosongkan jika tidak transaksi tanpa ongkir", fg="gray").grid(row=7, column=1, sticky="w")

    # Filter untuk Search
    def filter_produk(event=None):
        typed = produk_var.get().lower()
        produk_listbox.delete(0, tk.END)
        matches = [item for item in produk_display_list if typed in item.lower()]
        if matches:
            for item in matches:
                produk_listbox.insert(tk.END, item)
            produk_listbox.grid() # Tampilkan kembali
        else:
            produk_listbox.grid_remove() # Sembunyikan jika ada hasil 

    def pilih_produk(event=None):
        selection = produk_listbox.curselection()
        if selection:
            selected = produk_listbox.get(selection[0])
            produk_var.set(selected)
            produk_listbox.delete(0, tk.END)
            produk_listbox.grid_remove()

    produk_entry.bind("<KeyRelease>", filter_produk)
    produk_listbox.bind("<<ListboxSelect>>", pilih_produk)

    def tambah_ke_keranjang():
        nama_produk_gui = produk_var.get()
        produk_data = produk_display_list.get(nama_produk_gui)
        if not produk_data:
            messagebox.showerror("Error", "Pilih produk dulu.")
            return
        harga_input = harga_manual_entry.get().strip()
        if harga_input:
            try:
                harga_satuan = float(harga_input)
            except ValueError:
                messagebox.showerror("Error", "Harga manual harus berupa angka.")
                return
        else:
            harga_satuan = produk_data["harga_jual"]
        try:
            jumlah = int(jumlah_entry.get())
            if jumlah <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Jumlah harus berupa angka positif.")
            return
        produk_id = produk_data["id_produk"]
        subtotal = harga_satuan * jumlah
                # Tambah ke Keranjang
        keranjang.append({
            "produk_id": produk_id,
            "produk_nama": nama_produk_gui,
            "jumlah": jumlah,
            "harga_satuan": harga_satuan,
            "subtotal": subtotal
        })
        tree.insert("", tk.END, values=(nama_produk_gui, jumlah, f"Rp {harga_satuan:,.0f}", f"Rp {subtotal:,.0f}"))
        jumlah_entry.delete(0, tk.END)
        harga_manual_entry.delete(0, tk.END)
        update_total()

    def update_total():
        total=sum(item["subtotal"] for item in keranjang)
        ongkir_input = ongkir_entry.get().strip()
        try:
            ongkir = float(ongkir_input) if ongkir_input else 0
        except ValueError:
            ongkir = 0

        total_var.set(f"Total: Rp {total + ongkir:,.0f}")

    def hapus_produk_terpilih():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Hapus Produk", "Pilih baris produk yang ingin dihapus.")
            return
        # Hapus dari Keranjang
        item_values = tree.item(selected_item)["values"]
        nama_produk = item_values[0]
        jumlah = item_values[1]
        # Cari dan hapus dari keranjang
        for i, item in enumerate(keranjang):
            if item["produk_nama"] == nama_produk and item["jumlah"] == jumlah:
                keranjang.pop(i)
                break
        tree.delete(selected_item) # Hapus dari TreeView
        update_total()

    def reset_transaksi():
        keranjang.clear()
        tree.delete(*tree.get_children())
        jumlah_entry.delete(0, tk.END)
        produk_var.set("")
        member_entry.delete(0, tk.END)
        update_total()
    
    transaksi_terakhir = None
    pembeli_terakhir = "-"
    ongkir_terakhir = 0
    total_terakhir = 0

    def preview_nota(transaksi_id, pembeli, ongkir, total):
        nota_text = format_nota_thermal(transaksi_id, pembeli, keranjang, total, status="DRAFT", ongkir=ongkir)

        preview_window = tk.Toplevel()
        preview_window.title(f"Preview Nota - Transaksi #{transaksi_id}")
        preview_window.geometry("400x500")

        text_area = tk.Text(preview_window, wrap="word", font=("Courier New", 10))
        text_area.insert(tk.END, nota_text)
        text_area.config(state="disabled")
        text_area.pack(fill="both", expand=True, padx=10, pady=10)

        cetak_button = tk.Button(preview_window, text="Cetak ke Printer Thermal", font=("Arial", 10), bg="green", fg="white", command=lambda: cetak_nota_thermal(transaksi_id))
        cetak_button.pack(pady=10)

    # Tombol Proses Penjualan

    def proses_transaksi():
        ongkir_input = ongkir_entry.get().strip()
        conn = get_connection()
        cursor = conn.cursor()
        global transaksi_terakhir, pembeli_terakhir, ongkir_terakhir, total_terakhir
        try:
            member_input = member_entry.get().strip()
            member_id = int(member_input) if member_input.isdigit() else None
            pembeli = get_nama_pembeli(member_id, cursor)
            tanggal_transaksi = datetime.now().strftime("%Y-%m-%d")
            ongkir = float(ongkir_input) if ongkir_input else 0
            total_barang = sum(i["subtotal"] for i in keranjang)
            total = total_barang + ongkir
            transaksi_id = proses_penjualan(member_id, keranjang, ongkos_kirim=ongkir, nama_member=pembeli)
            transaksi_terakhir = transaksi_id
            print(f"[DEBUG] transaksi_id :{transaksi_id}")

            print("[DEBUG] Total barang:", total_barang)
            print("[DEBUG] Ongkir dikirim:", ongkir)
            print("[DEBUG] Total Final:", total)
            print("[DEBUG] Pembeli dikirim:", pembeli)
            simpan_nota_csv(transaksi_id, pembeli, ongkir)
            preview_nota(transaksi_id, pembeli, ongkir, total)
            form_frame.after(100, lambda:load_transaksi_rincian(rincian_tree))
            transaksi_terakhir = transaksi_id
            pembeli_terakhir = pembeli
            ongkir_terakhir = ongkir
            total_terakhir = total
            print("[DEBUG] Transaksi berhasil di-commit")
            reset_transaksi()
            messagebox.showinfo("Sukses", f"Transaksi #{transaksi_id} berhasil disimpan")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def simpan_nota_csv(transaksi_id, pembeli, total, ongkir=0):
        pembeli = member_entry.get() or "Tanpa Member"
        total = sum(i["subtotal"] for i in keranjang)
        nota = format_nota_thermal(transaksi_id, pembeli, keranjang, total, ongkir=ongkir)
        filename = f"nota_{transaksi_id}.txt"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            f.write(nota)
        messagebox.showinfo("Nota", f"Nota transaksi disimpan sebagai {filename}")

    LEBAR_BARIS = 42

    def format_item_thermal(nama, harga, qty, subtotal, max_width=LEBAR_BARIS):
        lines = []
        if len(nama) <= 30:
            lines.append(f"{nama:<30}{f'{subtotal:,.0f}'}:>12")
        else:
            lines.append(nama[:max_width]) # baris nama penuh

            lines.append(f"{'Subtotal':<30}{f'{subtotal:,.0f}':>12}")
        lines.append(f"{qty} x {f'{harga:,.0f}':>8}")
        return "\n".join(lines) + "\n"
                                   

    def format_nota_thermal(transaksi_id, pembeli, items, total, status="DRAFT", ongkir=0, tanggal = None):
        nota = ""
        nota += "=" * LEBAR_BARIS + "\n"
        nota += "KOPANA YOGYAKARTA".center(LEBAR_BARIS) + "\n"
        nota += " Gatak, Selomartani, Kalasan, Sleman".center(LEBAR_BARIS) + "\n"
        nota += " Telp: 0822 2715 4266".center(LEBAR_BARIS) + "\n"
        nota += "=" * LEBAR_BARIS + "\n"
        nota += f"Transaksi : #{transaksi_id}\n"
        nota += f"Tanggal   : {tanggal or datetime.now().strftime('%Y-%m-%d')}\n"
        nota += f"Pembeli   : {pembeli}\n"
        nota += "-" * LEBAR_BARIS + "\n"
        nota += f"{'Produk':<30} {'Subtotal':>12}\n"
        nota += "-" * LEBAR_BARIS + "\n"
        for item in items:        
            nama = item["produk_nama"]
            harga = item["harga_satuan"]
            qty = item["jumlah"]
            subtotal = item["subtotal"]
            diskon = item.get("diskon", 0)
            catatan = item.get("catatan", "")

            if len(nama) <= 30:
                nota += f"{nama:<30}{f'{subtotal:,.0f}':>12}\n"
            else:
                nota += f"{nama[:LEBAR_BARIS]}\n"

            # Baris qty x harga
            nota += f"{qty} x {f'{harga:,.0f}'}\n"

            if diskon:
                nota += f"{'Diskon':<30}{f'{diskon:,.0f}':>12}\n"
            if catatan:
                nota += f"{'Catatan':<9} {catatan[:LEBAR_BARIS-9]}\n"
        nota += "-" * LEBAR_BARIS + "\n"
        nota += f"{'Subtotal':<24}{f'Rp {total - ongkir:,.0f}':>18}\n"
        nota += f"{'Ongkir':<24}{f'Rp {ongkir:,.0f}':>18}\n"
        nota += f"{'Total':<24}{f'Rp {total:,.0f}':>18}\n"
        nota += "=" * LEBAR_BARIS + "\n"
        nota += "Terima Kasih".center(LEBAR_BARIS) + "\n"
        nota += "=" * LEBAR_BARIS + "\n"
        return nota

    tk.Button(tombol_frame, text="Tambah ke Keranjang", command=tambah_ke_keranjang).grid(row=0, column=0, padx=5)
    tk.Button(tombol_frame, text="Simpan", command=proses_transaksi).grid(row=0, column=1, padx=5)
    tk.Button(tombol_frame, text="Hapus Produk", command=hapus_produk_terpilih).grid(row=0, column=2, padx=5)
    tk.Button(tombol_frame, text="Reset", command=reset_transaksi).grid(row=0, column=3, padx=5)
    tk.Button(tombol_frame, text="Preview Nota", command=lambda: preview_nota(transaksi_terakhir, pembeli_terakhir, ongkir_terakhir, total_terakhir)).grid(row=0, column=4, padx=5)

    # ---- TreeView Keranjang -----
    tree = ttk.Treeview(keranjang_frame, columns=("Produk", "Jumlah", "Harga", "Subtotal"), show="headings", height=10, yscrollcommand=keranjang_scroll.set)
    for col in ("Produk", "Jumlah", "Harga", "Subtotal"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)
    tree.pack(side="left", fill="both", expand=True)
    keranjang_scroll.config(command=tree.yview)

    # ---- Total Label -----
    total_label = ttk.Label(tab_transaksi, textvariable=total_var, font=("Arial", 12, "bold"))
    total_label.grid(row=3, column=0, columnspan=4, pady=10)
    # ---- Tab Rincian ----
    tk.Label(tab_rincian, text="Daftar Transaksi Tersimpan", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)

    rincian_tree_frame = tk.Frame(tab_rincian)
    rincian_tree_frame.grid(row=1, column=0, padx=10, pady=10)
    
    rincian_scroll = tk.Scrollbar(rincian_tree_frame, orient="vertical")
    rincian_scroll.pack(side="right", fill="y")

    rincian_tree = ttk.Treeview(rincian_tree_frame, columns=("ID", "Tanggal", "Total", "Status"), show="headings", height=15, yscrollcommand=rincian_scroll.set)
    for col in ("ID", "Tanggal", "Total", "Status"):
        rincian_tree.heading(col, text=col)
        rincian_tree.column(col, anchor="center", width=120)

    rincian_tree.pack(side="left", fill="both", expand=True)
    rincian_scroll.config(command=rincian_tree.yview)

    detail_frame = tk.Frame(tab_rincian)
    detail_frame.grid(row=2, column=0, pady=10)

    def get_selected_transaksi_id():
        selected = rincian_tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Transaksi", "Pilih transaksi terlebih dahulu.")
            return None
        item = rincian_tree.item(selected[0])
        return item["values"][0]
    
    def lihat_detail_transaksi():
        transaksi_id = get_selected_transaksi_id()
        if not transaksi_id:
            return
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT nama_produk, jumlah, harga_satuan, diskon, subtotal, catatan FROM detail_penjualan WHERE transaksi_id = ?""", (transaksi_id,))
        items = cursor.fetchall()
        conn.close()

        detail_window = tk.Toplevel()
        detail_window.title(f"Detail Transaksi #{transaksi_id}")
        detail_window.geometry("400x400")

        text_area = tk.Text(detail_window, wrap="word", font=("Courier New", 10))
        text_area.insert(tk.END, f"Detail Transaksi #{transaksi_id}\n\n")
        for item in items:
            nama, qty, harga, diskon, sub, catatan = item
            text_area.insert(tk.END, f"{nama:<18} {qty} Rp {sub:,.0f}\n")
            if diskon:
                text_area.insert(tk.END, f"Diskon: Rp {diskon:,.0f}\n")
            if catatan:
                text_area.insert(tk.END, f" Catatan: {catatan}\n")
            text_area.insert(tk.END, "-"*35 + "\n")

        total_transaksi = sum(item[4] for item in items)
        text_area.insert(tk.END, f"\nTotal Transaksi: Rp {total_transaksi:,.0f}\n")

        text_area.config(state="disabled")
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
    
    def cetak_ulang_nota():
        transaksi_id = get_selected_transaksi_id()
        if not transaksi_id:
            return
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT nama_member, ongkos_kirim, total_harga, status, tanggal FROM transaksi_penjualan WHERE id_transaksi =?""", (transaksi_id,))
        transaksi_info = cursor.fetchone()

        cursor.execute("SELECT nama_produk, jumlah, harga_satuan, diskon, subtotal, catatan FROM detail_penjualan WHERE transaksi_id =?", (transaksi_id,))
        items = cursor.fetchall()
        conn.close()

        pembeli = transaksi_info[0] or "Tanpa Member"
        ongkir = transaksi_info[1] or 0
        total = transaksi_info[2]
        status = transaksi_info[3]
        tanggal = transaksi_info[4]
        item_dicts = [{"produk_nama": i[0], "jumlah": i[1], "harga_satuan":i[2], "diskon": i[3], "subtotal": i[4], "catatan": i[5]} for i in items]
        nota_text = format_nota_thermal(transaksi_id, pembeli, item_dicts, total, status=status, ongkir=ongkir, tanggal=tanggal)
        
        print("[DEBUG] Ongkir dari DB:", transaksi_info[1])
        print("[DEBUG] Nama Member dari DB:", transaksi_info[0])

        preview_window = tk.Toplevel()
        preview_window.title(f"Cetak Ulang Nota #{transaksi_id}")
        preview_window.geometry("400x500")

        text_area = tk.Text(preview_window, wrap="word", font=("Courier New", 10))
        text_area.insert(tk.END, nota_text)
        text_area.config(state="disabled")
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        cetak_button = tk.Button(preview_window, text="Cetak ke Printer Thermal", font=("Arial", 10), bg="green", fg="white", padx=10, pady=5, command=cetak_nota_thermal(transaksi_id))
        cetak_button.pack(pady=10)

    # Ambil Data Transaksi dari Database
    def load_transaksi_rincian(tree_widget):
        global rincian_tree
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
        print("[DEBUG] Jumlah transaksi dimuat:", len(rows))
    tk.Button(detail_frame, text="Lihat Detail", command=lihat_detail_transaksi).grid(row=0, column=0, padx=5)
    tk.Button(detail_frame, text="Cetak Ulang Nota", command=cetak_ulang_nota).grid(row=0, column=1, padx=5)

    # Bisa ditambahkan "Lihat Detail" dan "Cetak Ulang Nota" di sini
    load_transaksi_rincian(rincian_tree)


    def cetak_nota_thermal(transaksi_id):
        try:
            conn = get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Ambil transaksi utama
            cursor.execute("""
                SELECT tanggal, nama_member, total_harga, ongkos_kirim
                FROM transaksi_penjualan
                WHERE id_transaksi = ?
            """, (transaksi_id,))
            transaksi = cursor.fetchone()
            if not transaksi:
                print("[ERROR] Transaksi tidak ditemukan.")
                return
        
            tanggal = transaksi["tanggal"]
            pembeli = transaksi["nama_member"] or "-"
            total = transaksi["total_harga"]
            ongkir = transaksi["ongkos_kirim"]

            # Ambil Detail barang
            cursor.execute("""
                SELECT nama_produk AS produk_nama, jumlah, harga_satuan, subtotal 
                FROM detail_penjualan
                WHERE transaksi_id = ?
            """, (transaksi_id,))
            items = [dict(row) for row in cursor.fetchall()]
            # Format nota pakai yang sudah ada
            nota_str = format_nota_thermal(transaksi_id, pembeli, items, total, ongkir=ongkir, tanggal=tanggal)
            # Kirim ke printer thermal
            try:
                p = Usb(0x28e9, 0x0289) # VendorID dan ProcutID dari printer
                p.open()
                p.text(nota_str)
                p.cut()
                p.close()
                time.sleep(0.5)
                print("[INFO] Nota berhasil dicetak ke printer thermal.")
            except Exception as e:
                print("[ERROR] Gagal mencetak nota:", e)
        finally:
            conn.close()
    

    nama_member_label = tk.Label(form_frame, text="Nama Member:-", font=("Arial", 10), fg="blue")
    nama_member_label.grid(row=3, column=3, padx=5, pady=2, sticky="w")

    def cek_nama_member():
        member_input = member_entry.get().strip()
        if not member_input.isdigit():
            nama_member_label.config(text="Nama Member: [ID tidak valid]", fg="red")
            return
        member_id = int(member_input)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nama FROM member WHERE id_member = ?", (member_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            nama_member_label.config(text=f"Nama Member: {result[0]}", fg="green")
        else:
            nama_member_label.config(text="Nama Member: [Tidak ditemukan]", fg="red")

    tk.Button(form_frame, text="Cek", command=cek_nama_member).grid(row=3, column=2, padx=5)

    frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    buat_frame_penjualan()