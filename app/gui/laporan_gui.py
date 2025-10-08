import tkinter as tk
from tkinter import ttk
from datetime import datetime
from app.core.laporan_core import get_ringkasan_laporan

def buat_frame_laporan(parent, set_judul_modul):
    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True)

    set_judul_modul("Laporan")

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
    # Frame filter tanggal
    # Frame filter tanggal

    filter_frame = tk.Frame(tab_laporan)
    filter_frame.pack(pady=10)

    tk.Label(filter_frame, text="Dari Tanggal:").grid(row=0, column=0)
    entry_awal = tk.Entry(filter_frame)
    entry_awal.insert(0, datetime.now().strftime("%Y-%m-01")) # default awal bulan
    entry_awal.grid(row=0, column=1)

    tk.Label(filter_frame, text="Sampai Tanggal:").grid(row=0, column=2)
    entry_akhir = tk.Entry(filter_frame)
    entry_akhir.insert(0, datetime.now().strftime("%Y-%m-%d")) # default hari ini
    entry_akhir.grid(row=0, column=3)

    # Panel Penjualan
    
    panel_penjualan = tk.LabelFrame(tab_laporan, text="Penjualan", padx=10, pady=10)
    panel_penjualan.pack(fill="x", padx=20, pady=5)
    label_penjualan = tk.Label(panel_penjualan, text="Total Penjualan: Rp 0", font=("Segoe UI", 10, "bold"))
    label_penjualan.pack(side="left")
    tk.Button(panel_penjualan, text="Tampilkan Detail", command=lambda: notebook.select(tab_penjualan)).pack(side="right")

    # Panel Pembelian

    panel_pembelian = tk.LabelFrame(tab_laporan, text="Pembelian", padx=10, pady=10)
    panel_pembelian.pack(fill="x", padx=20, pady=5)
    label_pembelian = tk.Label(panel_pembelian, text="Total Pembelian: Rp 0", font=("Segoe UI", 10, "bold"))
    label_pembelian.pack(side="left")
    tk.Button(panel_pembelian, text="Tampilkan Detail", command=lambda: notebook.select(tab_pembelian)).pack(side="right")

    # Panel Pengeluaran
    
    panel_pengeluaran = tk.LabelFrame(tab_laporan, text="Pengeluaran", padx=10, pady=10)
    panel_pengeluaran.pack(fill="x", padx=20, pady=5)
    label_pengeluaran = tk.Label(panel_pengeluaran, text="Total Pengeluaran: Rp 0", font=("Segoe UI", 10, "bold"))
    label_pengeluaran.pack(side="left")
    tk.Button(panel_pengeluaran, text="Tampilkan Detail", command=lambda: notebook.select(tab_pengeluaran)).pack(side="right")


    def tampilkan_ringkasan():
        awal = entry_awal.get().strip()
        akhir = entry_akhir.get().strip()
        try:
            data = get_ringkasan_laporan(awal, akhir)
            label_penjualan.config(text=f"Total Penjualan: Rp {int(data['penjualan']):,}")
            label_pembelian.config(text=f"Total Pembelian: Rp {int(data['pembelian']):,}")
            label_pengeluaran.config(text=f"Total Pengeluaran: Rp {int(data['pengeluaran']):,}")
        except Exception as e:
            print("[ERROR] Gagal mengambil laporan:", e)
    tk.Button(filter_frame, text="Tampilkan", command=tampilkan_ringkasan).grid(row=0, column=4, padx=10)

    notebook.select(tab_laporan)

if __name__ == "__main__":
    buat_frame_laporan()
