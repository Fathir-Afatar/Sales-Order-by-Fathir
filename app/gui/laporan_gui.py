import tkinter as tk
from tkinter import ttk
from datetime import datetime
from app.core.laporan_core import get_ringkasan_laporan

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

if __name__ == "__main__":
    buat_frame_laporan()
