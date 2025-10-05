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
    frame.pack(fill="both", expand=True)

    # Tabs & Produk

    tab_transaksi, tab_rincian = buat_notebook_penjualan(frame)
    produk_list, produk_display_list = ambil_produk_dan_display()
    form_refs = buat_form_input_penjualan(tab_transaksi, produk_display_list)
    tree, keranjang = buat_keranjang_penjualan(tab_transaksi)

    # Bind search dan pilih produk

    form_refs["produk_entry"].bind("<KeyRelease>", lambda e: filter_produk(form_refs, produk_display_list))
    form_refs["produk_listbox"].bind("<<ListboxSelect>>", lambda e: pilih_produk(form_refs))

    # ------- State Transaksi -----

    state_transaksi = {
        "terakhir_id": None,
        "pembeli": "-",
        "ongkir": 0,
        "total":0
    }
    
    #------Handler Tombol -----------

    def tambah_ke_keranjang():
        tambah_item_ke_keranjang(form_refs, produk_display_list, keranjang, tree)
    
    def simpan_transaksi():
        proses_transaksi(form_refs, keranjang, tree, rincian_tree, state_transaksi, lambda: update_total(form_refs, keranjang))
    
    def hapus_produk():
        hapus_produk_terpilih(tree, keranjang, lambda: update_total(form_refs, keranjang))
    
    def reset_transaksi_gui():
        reset_transaksi(form_refs, keranjang, tree, lambda: update_total(form_refs, keranjang))
    
    def preview_nota_gui():
        preview_nota(
            state_transaksi["terakhir_id"],
            state_transaksi["pembeli"],
            keranjang,
            state_transaksi["total"],
            ongkir=state_transaksi["ongkir"]
        )
    tombol_handlers = {
        "tambah": tambah_ke_keranjang,
        "simpan": simpan_transaksi,
        "hapus": hapus_produk,
        "reset": reset_transaksi_gui,
        "preview": preview_nota_gui
    }

    buat_tombol_penjualan(form_refs["tombol_frame"], tombol_handlers, state_transaksi)

    # ------- Tab Rincian ------

    rincian_tree, detail_frame = buat_tab_rincian(tab_rincian)
    load_transaksi_rincian(rincian_tree)

    tk.Button(detail_frame, text="Lihat Detail", command=lambda: lihat_detail_transaksi(rincian_tree)).grid(row=0, column=0, padx=5)
    tk.Button(detail_frame, text="Cetak Ulang Nota", command=lambda: cetak_ulang_nota(rincian_tree)).grid(row=0, column=1, padx=5)

    tk.Button(form_refs["form_frame"], text="Cek", command=lambda:handler_cek_nama_member(form_refs["member_entry"], form_refs["nama_member_label"])).grid(row=3, columnspan=2, padx=5)

    return frame

def buat_notebook_penjualan(frame):
    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    tab_transaksi = tk.Frame(notebook)
    tab_rincian = tk.Frame(notebook)

    notebook.add(tab_transaksi, text="Transaksi")
    notebook.add(tab_rincian, text="Rincian")
    return tab_transaksi, tab_rincian

def ambil_produk_dan_display():
    produk_list = semua_produk()
    produk_display_list = {
        f"{p['nama_produk']} (ID {p['id_produk']})": p for p in produk_list
    }
    return produk_list, produk_display_list

def buat_form_input_penjualan(tab_transaksi, produk_display_list):
    produk_var = tk.StringVar()
    total_var = tk.StringVar(value="Total: Rp0")

    form_frame = tk.Frame(tab_transaksi)
    form_frame.grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=10)

    tombol_frame = tk.Frame(tab_transaksi)
    tombol_frame.grid(row=1, column=0, columnspan=4, pady=10)

    produk_entry = tk.Entry(form_frame, textvariable=produk_var, width=40)
    produk_entry.grid(row=0, column=1, padx=5)

    produk_listbox = tk.Listbox(form_frame, width=40, height=5)
    produk_listbox.grid(row=1, column=1, padx=5, pady=5)
    produk_listbox.grid_remove()

    jumlah_entry = tk.Entry(form_frame, width=10)
    jumlah_entry.grid(row=2, column=1, sticky="w", padx=5)

    member_entry = tk.Entry(form_frame, width=10)
    member_entry.grid(row=3, column=1, sticky="w", padx=5)

    harga_manual_entry = tk.Entry(form_frame, width=15)
    harga_manual_entry.grid(row=4, column=1, sticky="w", padx=5)

    ongkir_entry = tk.Entry(form_frame, width=15)
    ongkir_entry.grid(row=6, column=1, sticky="w", padx=5)
    
    nama_member_label = tk.Label(form_frame, text="Nama Member:-", font=("Arial", 10), fg="blue")
    nama_member_label.grid(row=3, column=3, padx=5, pady=2, sticky="w")

    tk.Label(form_frame, text="Pilih Produk").grid(row=0, column=0, sticky="w")
    tk.Label(form_frame, text="Jumlah").grid(row=2, column=0, sticky="w")
    tk.Label(form_frame, text="ID Member").grid(row=3, column=0, sticky="w")
    tk.Label(form_frame, text="Harga Manual (Opsional)").grid(row=4, column=0, sticky="w")
    tk.Label(form_frame, text="Ongkos Kirim (opsional)").grid(row=6, column=0, sticky="w")
    tk.Label(form_frame, text="* Kosongkan jika ingin pakai harga default", fg="gray").grid(row=5, column=1, sticky="w")
    tk.Label(form_frame, text="*Kosongkan jika tidak ada ongkir", fg="gray").grid(row=7, column=1, sticky="w")

    return {
        "form_frame": form_frame,
        "produk_var": produk_var,
        "total_var": total_var,
        "produk_entry": produk_entry,
        "produk_listbox": produk_listbox,
        "jumlah_entry": jumlah_entry,
        "member_entry": member_entry,
        "harga_manual_entry": harga_manual_entry,
        "ongkir_entry": ongkir_entry,
        "tombol_frame": tombol_frame,
        "nama_member_label": nama_member_label
    }
    
def buat_keranjang_penjualan(tab_transaksi):
    keranjang_frame = tk.Frame(tab_transaksi)
    keranjang_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

    keranjang_scroll = tk.Scrollbar(keranjang_frame, orient="vertical")
    keranjang_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(keranjang_frame, columns=("Produk", "Jumlah", "Harga", "Subtotal"), show="headings", yscrollcommand=keranjang_scroll.set)
    for col in ("Produk", "Jumlah", "Harga", "Subtotal"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center")
    tree.pack(fill="both", expand=True)

    keranjang_scroll.config(command=tree.yview)
    keranjang = []

    return tree, keranjang

def filter_produk(refs, produk_display_list):
    typed = refs["produk_var"].get().lower()
    listbox = refs["produk_listbox"]
    listbox.delete(0, tk.END)
    matches = [item for item in produk_display_list if typed in item.lower()]
    if matches:
        for item in matches:
            listbox.insert(tk.END, item)
        listbox.grid()
    else:
        listbox.grid_remove()

def pilih_produk(refs):
    listbox = refs["produk_listbox"]
    selection = listbox.curselection()
    if selection:
        selected = listbox.get(selection[0])
        refs["produk_var"].set(selected)
        listbox.delete(0, tk.END)
        listbox.grid_remove()

def tambah_item_ke_keranjang(refs, produk_display_list, keranjang, tree):
    nama_produk_gui = refs["produk_var"].get()
    produk_data = produk_display_list.get(nama_produk_gui)
    if not produk_data:
        messagebox.showerror("Error", "Pilih produk dulu.")
        return
    
    harga_input = refs["harga_manual_entry"].get().strip()
    try:
        harga_satuan = float(harga_input) if harga_input else produk_data["harga_jual"]
    except ValueError:
        messagebox.showerror("Error", "Harga manual harus berupa angka.")
        return

    try:
        jumlah = int(refs["jumlah_entry"].get())
        if jumlah <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Jumlah harus berupa angka positif.")
        return
    
    produk_id = produk_data["id_produk"]
    subtotal = harga_satuan * jumlah

    keranjang.append({
        "produk_id": produk_id,
        "produk_nama": nama_produk_gui,
        "jumlah": jumlah,
        "harga_satuan": harga_satuan,
        "subtotal": subtotal
    })
    print("[DEBUG] Item ditambahkan ke keranjang:", keranjang[-1])

    tree.insert("", tk.END, values=(nama_produk_gui, jumlah, f"Rp {harga_satuan:,.0f}", f"Rp {subtotal:,.0f}"))
    refs["jumlah_entry"].delete(0, tk.END)
    refs["harga_manual_entry"].delete(0, tk.END)
    update_total(refs, keranjang)

def update_total(refs, keranjang):
    total = sum(item["subtotal"] for item in keranjang)
    refs["total_var"].set(f"Total: Rp{total:,.0f}")

def hapus_produk_terpilih(tree, keranjang, update_total_fn):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Hapus Produk", "Pilih baris produk yang ingin dihapus.")
        return
    item_values = tree.item(selected_item)["values"]
    nama_produk = item_values[0]
    jumlah = item_values[1]

    for i, item in enumerate(keranjang):
        if item["produk_nama"] == nama_produk and item["jumlah"] == jumlah:
            keranjang.pop(i)
            break
    tree.delete(selected_item)
    update_total_fn()

def reset_transaksi(refs, keranjang, tree, update_total_fn):
    keranjang.clear()
    tree.delete(*tree.get_children())
    refs["jumlah_entry"].delete(0, tk.END)
    refs["produk_var"].set("")
    refs["member_entry"].delete(0, tk.END)
    update_total_fn

def preview_nota(transaksi_id, pembeli, keranjang, total, status="DRAFT", ongkir=0):
    nota_text = format_nota_thermal(transaksi_id, pembeli, keranjang, total, status=status, ongkir=ongkir)

    preview_window = tk.Toplevel()
    preview_window.title(f"Preview Nota - Transaksi #{transaksi_id}")
    preview_window.geometry("400x500")

    text_area = tk.Text(preview_window, wrap="word", font=("Courier New", 10))
    text_area.insert(tk.END, nota_text)
    text_area.config(state="disabled")
    text_area.pack(fill="both", expand=True, padx=10, pady=10)

    cetak_button = tk.Button(preview_window, text="Cetak ke Printer Thermal", font=("Arial", 10), bg="green", fg="white", command=lambda: cetak_nota_thermal(transaksi_id))
    cetak_button.pack(pady=10)

def proses_transaksi(refs, keranjang, tree, rincian_tree, state_transaksi, update_total_fn):
    ongkir_input = refs["ongkir_entry"].get().strip()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        member_input = refs["member_entry"].get().strip()
        member_id = int(member_input) if member_input.isdigit() else None
        pembeli = get_nama_pembeli(member_id)
        ongkir = float(ongkir_input) if ongkir_input else 0
        total_barang = sum(i["subtotal"] for i in keranjang)
        total = total_barang + ongkir

        transaksi_id = proses_penjualan({
            "member_id": member_id,
            "nama_member": pembeli,
            "daftar_barang": keranjang,
            "ongkos_kirim": ongkir
        })
        state_transaksi.update({
            "terakhir_id": transaksi_id,
            "pembeli": pembeli,
            "ongkir": ongkir,
            "total": total
        })

        simpan_nota_csv(transaksi_id, pembeli, keranjang, total, ongkir)
        preview_nota(transaksi_id, pembeli, keranjang, total, ongkir=ongkir)
        tree.after(100, lambda: load_transaksi_rincian(rincian_tree))
        reset_transaksi(refs, keranjang, tree, update_total_fn)
        messagebox.showinfo("Sukses", f"Transaksi #{transaksi_id} berhasil disimpan")
    
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        conn.close()

def simpan_nota_csv(transaksi_id, pembeli, keranjang, total, ongkir=0):
    nota = format_nota_thermal(transaksi_id, pembeli, keranjang, total, ongkir=ongkir)
    filename = f"nota_{transaksi_id}.txt"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        f.write(nota)
    messagebox.showinfo("Nota", f"Nota transaksi disimpan sebagai {filename}")

LEBAR_BARIS = 42

def format_item_thermal(nama, harga, qty, subtotal, max_width=LEBAR_BARIS):
    lines = []
    if len(nama) <= 30:
        lines.append(f"{nama:<30}{subtotal:>12,.0f}")
    else:
        lines.append(nama[:max_width]) # baris nama penuh

        lines.append(f"{'Subtotal':<30}{f'{subtotal:,.0f}':>12}")
    lines.append(f"{qty} x {f'{harga:,.0f}':>8}")
    return "\n".join(lines) + "\n"
                                   

def format_nota_thermal(transaksi_id, pembeli, items, total, status="DRAFT", ongkir=0, tanggal = None):
    lines = []
    lines.append("=" * LEBAR_BARIS)
    lines.append("KOPANA YOGYAKARTA".center(LEBAR_BARIS))
    lines.append(" Gatak, Selomartani, Kalasan, Sleman".center(LEBAR_BARIS))
    lines.append(" Telp: 0822 2715 4266".center(LEBAR_BARIS))
    lines.append("=" * LEBAR_BARIS)
    lines.append(f"Transaksi : #{transaksi_id}")
    lines.append(f"Tanggal   : {tanggal or datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"Pembeli   : {pembeli}")
    lines.append(f"-" * LEBAR_BARIS)
    lines.append(f"{'Produk':<30} {'Subtotal':>12}")
    lines.append("-" * LEBAR_BARIS)

    for item in items:
        lines.append(format_item_thermal(
            item["produk_nama"],
            item["harga_satuan"],
            item["jumlah"],
            item["subtotal"]
            ))
        
        if item.get("diskon"):
            lines.append(f"{'Diskon':<30}{item['diskon']:>12,.0f}")
        if item.get("catatan"):
            lines.append(f"{'Catatan':<9} {item['catatan'][:LEBAR_BARIS-9]}")
    
    lines.append("-" * LEBAR_BARIS)
    lines.append(f"{'Subtotal':<24}{f'Rp {total - ongkir:,.0f}':>18}")
    lines.append(f"{'Ongkir':<24}{f'Rp {ongkir:,.0f}':>18}")
    lines.append(f"{'Total':<24}{f'Rp {total:,.0f}':>18}")
    lines.append("=" * LEBAR_BARIS)
    lines.append("Terima Kasih".center(LEBAR_BARIS))
    lines.append("=" * LEBAR_BARIS)
    return "\n".join(lines)

def buat_tombol_penjualan(frame, handlers, state_refs):
    tk.Button(frame, text="Tambah ke Keranjang", command=handlers["tambah"]).grid(row=0, column=0, padx=5)
    tk.Button(frame, text="Simpan", command=handlers["simpan"]).grid(row=0, column=1, padx=5)
    tk.Button(frame, text="Hapus Produk", command=handlers["hapus"]).grid(row=0, column=2, padx=5)
    tk.Button(frame, text="Reset", command=handlers["reset"]).grid(row=0, column=3, padx=5)
    tk.Button(frame, text="Preview Nota", command=lambda: handlers["preview"](
        state_refs["transaksi_id"],
        state_refs["pembeli"],
        state_refs["ongkir"],
        state_refs["total"]
    )).grid(row=0, column=4, padx=5)

def buat_treeview_keranjang(frame, scroll):
    tree = ttk.Treeview(frame, columns=("Produk", "Jumlah", "Harga", "Subtotal"), show="headings", height=10, yscrollcommand=scroll.set)
    for col in ("Produk", "Jumlah", "Harga", "Subtotal"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)
    tree.pack(side="left", fill="both", expand=True)
    scroll.config(command=tree.yview)
    return tree

def buat_label_total(frame, total_var):
    label = ttk.Label(frame, textvariable=total_var, font=("Arial", 12, "bold"))
    label.grid(row=3, column=0, columnspan=4, pady=10)
    return label

def buat_tab_rincian(tab_rincian):
    tk.Label(tab_rincian, text="Daftar Transaksi Tersimpan", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)

    tree_frame = tk.Frame(tab_rincian)
    tree_frame.grid(row=1, column=0, padx=10, pady=10)
    
    scroll = tk.Scrollbar(tree_frame, orient="vertical")
    scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(tree_frame, columns=("ID", "Tanggal", "Total", "Status"), show="headings", height=15, yscrollcommand=scroll.set)
    for col in ("ID", "Tanggal", "Total", "Status"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)
    tree.pack(side="left", fill="both", expand=True)
    scroll.config(command=tree.yview)

    detail_frame = tk.Frame(tab_rincian)
    detail_frame.grid(row=2, column=0, pady=10)

    return tree, detail_frame

def get_selected_transaksi_id(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Pilih Transaksi", "Pilih transaksi terlebih dahulu.")
        return None
    item = tree.item(selected[0])
    return item["values"][0]
    
def lihat_detail_transaksi(tree):
    transaksi_id = get_selected_transaksi_id(tree)
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
    
def cetak_ulang_nota(treeview):
    transaksi_id = get_selected_transaksi_id(treeview)
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

def cetak_nota_thermal(transaksi_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()    
    try:
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
    
def cek_nama_member(member_id):
    if not isinstance(member_id, int):
        return "[ID tidak valid]"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama FROM member WHERE id_member = ?", (member_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "[Tidak ditemukan]"

def handler_cek_nama_member(entry_widget, label_widget):
    member_input = entry_widget.get().strip()
    if not member_input.isdigit():
        label_widget.config(text="Nama Member: [ID tidak valid]", fg="red")
        return
    member_id = int(member_input)
    nama = cek_nama_member(member_id)
    warna = "green" if nama not in ["[ID tidak valid]", "[Tidak ditemukan]"] else "red"
    label_widget.config(text=f"Nama Member: {nama}", fg=warna)


if __name__ == "__main__":
    buat_frame_penjualan()