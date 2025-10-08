import tkinter as tk
from tkinter import ttk
from datetime import datetime
from app.core.laporan_core import get_ringkasan_laporan, get_histori_transaksi, get_nama_supplier

def buat_frame_laporan(parent, set_judul_modul):
    set_judul_modul("Laporan")

    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True)

    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True)

    tab_laporan = ttk.Frame(notebook)
    tab_penjualan = ttk.Frame(notebook)
    tab_pembelian = ttk.Frame(notebook)
    tab_pengeluaran = ttk.Frame(notebook)

    notebook.add(tab_laporan, text="Laporan")
    notebook.add(tab_penjualan, text="Penjualan")
    notebook.add(tab_pembelian, text="Pembelian")
    notebook.add(tab_pengeluaran, text="Pengeluaran")

    # Build Filter Tanggal
    entry_awal, entry_akhir = build_filter_area(tab_laporan)

    # Build Panel Ringkasan
    label_penjualan = build_panel(tab_laporan, "Penjualan", lambda: notebook.select(tab_penjualan))
    label_pembelian = build_panel(tab_laporan, "Pembelian", lambda: notebook.select(tab_pembelian))
    label_pengeluaran = build_panel(tab_laporan, "Pengeluaran", lambda: notebook.select(tab_pengeluaran))

    tree_penjualan = build_treeview_laporan(tab_penjualan, ["Tanggal", "Total"])
    tree_pembelian = build_treeview_laporan(tab_pembelian, ["Tanggal", "Supplier", "Total"])
    tree_pengeluaran = build_treeview_laporan(tab_pengeluaran, ["Tanggal", "Kategori", "Nominal", "Keterangan"])

    # Tombol tampilkan
    def tampilkan_ringkasan():
        awal = entry_awal.get().strip()
        akhir = entry_akhir.get().strip()
        try:
            data= get_ringkasan_laporan(awal, akhir)
            label_penjualan.config(text=f"Total Penjualan: Rp {int(data['penjualan']):,}")
            label_pembelian.config(text=f"Total Pembelian: Rp {int(data['pembelian']):,}")
            label_pengeluaran.config(text=f"Total Pengeluaran: Rp {int(data['pengeluaran']):,}")
        except Exception as e:
            print("[ERROR] Gagal mengambil laporan:", e)
        
        hist_penjualan = get_histori_transaksi("penjualan", awal, akhir)
        hist_pembelian = get_histori_transaksi("pembelian", awal, akhir)
        hist_pengeluaran = get_histori_transaksi("pengeluaran", awal, akhir)

        def format_rupiah(nilai):
            return f"Rp {int(nilai):,}".replace(".", ",")

        # Kosongkan dulu
        for tree in [tree_penjualan, tree_pembelian, tree_pengeluaran]:
            for item in tree.get_children():
                tree.delete(item)
        
        # Isi ulang
        
        for row in hist_penjualan:
            total = format_rupiah(row["total_harga"])
            tanggal = row["tanggal"].split(" ")[0]
            tree_penjualan.insert("", "end", values=(tanggal, total))
        
        for row in hist_pembelian:
            supplier_nama = get_nama_supplier(row["supplier_id"])
            total = format_rupiah(row["total_harga"])
            tree_pembelian.insert("", "end", values=(row["tanggal"], supplier_nama, total))
        
        for row in hist_pengeluaran:
            total = format_rupiah(row["nominal"])
            tree_pengeluaran.insert("", "end", values=(row["tanggal"], row["kategori"], total, row["keterangan"]))
    
    # Tombol tampilkan di filter

    filter_frame = entry_awal.master
    tk.Button(filter_frame, text="Tampilkan", command=tampilkan_ringkasan).grid(row=0, column=4, padx=10)

    notebook.select(tab_laporan)

# Komponen : Filter Area
def build_filter_area(parent):
    frame = tk.Frame(parent, bg="#f4f4f4")
    frame.pack(pady=10)

    tk.Label(frame, text="Dari Tanggal:", bg="#f4f4f4").grid(row=0, column=0)
    entry_awal = tk.Entry(frame)
    entry_awal.insert(0, datetime.now().strftime("%Y-%m-01"))
    entry_awal.grid(row=0, column=1)

    tk.Label(frame, text="Sampai Tanggal:", bg="#f4f4f4").grid(row=0, column=2)
    entry_akhir = tk.Entry(frame)
    entry_akhir.insert(0, datetime.now().strftime("%Y-%m-%d"))
    entry_akhir.grid(row=0, column=3)

    return entry_awal, entry_akhir

# Komponen: Panel Ringkasan
def build_panel(parent, judul, command):
    panel = tk.LabelFrame(parent, text=judul, padx=10, pady=10, bg="#f4f4f4")
    panel.pack(fill="x", padx=20, pady=5)

    label = tk.Label(panel, text=f"Total {judul}: Rp 0", font=("Segoe UI", 10, "bold"), bg="#f4f4f4")
    label.pack(side="left")

    tk.Button(panel, text="Tampilkan Detail", command=command).pack(side="right")

    return label

def build_treeview_laporan(parent, kolom):
    tree = ttk.Treeview(parent, columns=kolom, show="headings")
    for col in kolom:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=10)
    return tree



if __name__ == "__main__":
    buat_frame_laporan()
