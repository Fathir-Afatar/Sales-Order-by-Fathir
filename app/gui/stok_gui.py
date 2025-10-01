import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.core.stok_core import generate_kartu_stok, get_produk_id_by_nama, get_daftar_nama_barang, cek_log_harian, ambil_log_stok_bulanan, proses_stok_harian
from app.constants.config import get_connection
from app.core.product_core import semua_produk

def build_treeview_stok(parent):
    tree = ttk.Treeview(parent, columns=("Tanggal", "Awal", "Masuk", "Keluar", "Akhir"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=80)
    return tree

def build_treeview_ringkasan(parent):
    tree = ttk.Treeview(parent, columns=("Kode", "Nama Produk", "Stok Awal", "Stok Akhir"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor="w", stretch=True)
    return tree

def ambil_filter_stok(barang_combo, bulan_combo, tahun_combo):
    nama_barang = barang_combo.get()
    bulan_index = bulan_combo.current()
    print("[DEBUG] Filter bulan:", bulan_combo.get())
    print("[DEBUG] Filter tahun:", tahun_combo.get())
    tahun_str = tahun_combo.get()
    if not nama_barang or bulan_index == -1 or not tahun_str:
        return None
    
    bulan = bulan_index + 1
    tahun = int(tahun_str)
    produk_id = get_produk_id_by_nama(nama_barang)
    if produk_id is None:
        return None
    
    return produk_id, bulan, tahun

def isi_treeview_stok(tree, kartu):
    tree.tag_configure("hari_ini", background="#dff0d8", foreground="black")
    tree.delete(*tree.get_children())
    print("[DEBUG] Tipe Treeview:", type(tree))
    print("[DEBUG] Tag hari_ini dikonfigurasi")
    for row in kartu:
        tanggal = row.get("tanggal")
        if row.get("hari_ini"):
            tanggal += " (Hari Ini)"
            tree.insert("", "end", values=(
                tanggal,
                f"{row.get('awal', 0):,}",
                f"{row.get('masuk', 0):,}",
                f"{row.get('keluar', 0):,}",
                f"{row.get('akhir', 0):,}"
            ), tags=("hari_ini",)if row.get("hari_ini") else ())
        else:
            tree.insert("", "end", values=(
                tanggal,
                f"{row.get('awal', 0):,}",
                f"{row.get('masuk', 0):,}",
                f"{row.get('keluar', 0):,}",
                f"{row.get('akhir', 0):,}"
            ))
        if row.get("hari_ini"):
            print("[DEBUG] Baris hari ini:", row)


def buat_frame_stok(parent):
    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True)

    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True)

    build_section_kartu_stok(notebook)
    build_section_ringkasan_stok(notebook)

def build_section_kartu_stok(parent):
    tab_stok = ttk.Frame(parent)
    parent.add(tab_stok, text="Stok")

    filter_frame = tk.Frame(tab_stok)
    filter_frame.pack(pady=10)

    daftar_nama_barang = get_daftar_nama_barang()
    daftar_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    daftar_tahun = ["2025", "2026"] # bisa diganti dengan query log_stok
    
    tk.Label(filter_frame, text="Barang:").grid(row=0, column=0)
    barang_combo = ttk.Combobox(filter_frame, values=daftar_nama_barang)
    barang_combo.grid(row=0, column=1)

    tk.Label(filter_frame, text="Bulan:").grid(row=0, column=2)
    bulan_combo = ttk.Combobox(filter_frame, values=daftar_bulan)
    bulan_combo.grid(row=0, column=3)

    tk.Label(filter_frame, text="Tahun:").grid(row=0, column=4)
    tahun_combo = ttk.Combobox(filter_frame, values=daftar_tahun)
    tahun_combo.grid(row=0, column=5)

    tree_frame = tk.Frame(tab_stok)
    tree_frame.pack(fill="both", expand=True)

    stok_tree = build_treeview_stok(tree_frame)
    stok_tree.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=stok_tree.yview)
    scrollbar.pack(side="right", fill="y")
    stok_tree.config(yscrollcommand=scrollbar.set)

    def tampilkan_kartu_stok():
        hasil = ambil_filter_stok(barang_combo, bulan_combo, tahun_combo)
        if not hasil:
            return
        produk_id, bulan, tahun = hasil
        kartu = generate_kartu_stok(produk_id, bulan, tahun)
        isi_treeview_stok(stok_tree, kartu)
                             
    tk.Button(filter_frame, text="Tampilkan", command=tampilkan_kartu_stok).grid(row=0, column=6, padx=10)

def build_section_ringkasan_stok(parent):
    tab_ringkasan = ttk.Frame(parent)
    parent.add(tab_ringkasan, text="Ringkasan")

    frame_ringkasan = tk.Frame(tab_ringkasan)
    frame_ringkasan.pack(pady=10)

    tk.Label(frame_ringkasan, text="Tanggal:").grid(row=0, column=0)
    tanggal_entry = tk.Entry(frame_ringkasan)
    tanggal_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
    tanggal_entry.grid(row=0, column=1)

    tree_ringkasan = build_treeview_ringkasan(tab_ringkasan)
    tree_ringkasan.pack(fill="both", expand=True)

    def tampilkan_ringkasan():
        bulan = datetime.now().month
        tahun = datetime.now().year
        tampilkan_stok_harian(tree_ringkasan, bulan, tahun)

    def tampilkan_log_harian(treeview, tanggal):
        selected = treeview.focus()
        if not selected:
            messagebox.showinfo("Info", "Pilih produk terlebih dahulu.")
            return
        values = treeview.item(selected)["values"]
        produk_id = values[0]

        conn = get_connection()
        cursor = conn.cursor()
        logs = cek_log_harian(cursor, produk_id, tanggal)
        conn.close()

        if not logs:
            messagebox.showinfo("Info", "Tidak ada log stok untuk tanggal tersebut.")
            return
    
        # Tampilkan di popup

        window = tk.Toplevel(treeview)
        window.title(f"Log Stok Produk #{produk_id} - {tanggal}")
        tree_log = ttk.Treeview(window, columns=("Waktu", "Awal", "Akhir", "Jenis"), show="headings")
        for col in tree_log["columns"]:
            tree_log.heading(col, text=col)
            tree_log.column(col, anchor="center", width=100)
        tree_log.pack(fill="both", expand=True)

        for row in logs:
            tree_log.insert("", "end", values=row)
    
    
    tk.Button(frame_ringkasan, text="Tampilkan Stok Hari Ini", command=tampilkan_ringkasan).grid(row=0, column=2, padx=10)
    tk.Button(frame_ringkasan, text="Audit Log Hari ini", command=lambda: tampilkan_log_harian(tree_ringkasan, tanggal_entry.get().strip())).grid(row=0, column=3, padx=10)

# 
def tampilkan_stok_harian(treeview, bulan, tahun):
    conn = get_connection()
    cursor = conn.cursor()
    produk_list = semua_produk()
    
    treeview.delete(*treeview.get_children())

    hari_ini = datetime.now().day

    for produk in produk_list:
        produk_id = produk["id_produk"]
        nama = produk["nama_produk"]
        logs = ambil_log_stok_bulanan(cursor, produk_id, bulan, tahun)
        stok_harian = proses_stok_harian(logs, bulan, tahun)

        if str(hari_ini) in stok_harian:
            row = stok_harian[str(hari_ini)]
            awal = row["awal"] if row["awal"] is not None else 0
            akhir = row["akhir"] if row["akhir"] is not None else 0
        else:
            awal = akhir = 0
        
        treeview.insert("", "end", values=(produk_id, nama, f"{awal:,}", f"{akhir:,}"))
    
    conn.close()

if __name__ == "__main__":
    buat_frame_stok()