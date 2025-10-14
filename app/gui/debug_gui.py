import tkinter as tk
from tkinter import ttk
from app.core.debug_core import ambil_log_terakhir
from app.core.debug_core import cek_status_database, cek_status_printer
from app.core.pengaturan_core import simulasi_cetak_nota

def buka_debug_gui(parent, set_judul_modul):
    set_judul_modul("Debug")
    frame = tk.Frame(parent, bg="#f4f4f4")
    frame.pack(fill="both", expand=True)

    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Tab Log

    tab_log = tk.Frame(notebook, bg="#f4f4f4")
    notebook.add(tab_log, text="Log Sistem")

    tab_status = tk.Frame(notebook, bg="#f4f4f4")
    notebook.add(tab_status, text="Status Sistem")

    tab_tes = tk.Frame(notebook, bg="#f4f4f4")
    notebook.add(tab_tes, text="Tes Cetak")

    status_label = tk.Label(tab_status, text="Status Database:", bg="#f4f4f4")
    status_label.pack(anchor="w", padx=10, pady=5)

    status_area = tk.Text(tab_status, height=10, bg="#f4f4f4", font=("Courier", 10))
    status_area.pack(fill="x", padx=10)

    log_area = tk.Text(tab_log, bg="#ffffff", font=("Courier", 10))
    log_area.pack(fill="both", expand=True, padx=10, pady=10)

    printer_label = tk.Label(tab_status, text="Status Printer:", bg="#f4f4f4")
    printer_label.pack(anchor="w", padx=10, pady=5)

    printer_area = tk.Text(tab_status, height=5, bg="#f4f4f4", font=("Courier", 10))
    printer_area.pack(fill="x", padx=10)

    def refresh_printer():
        status = cek_status_printer()
        printer_area.delete("1.0", "end")
        for k, v in status.items():
            printer_area.insert("end", f"{k}: {v}\n")

    def refresh_log():
        log_area.delete("1.0", "end")
        for line in ambil_log_terakhir():
            log_area.insert("end", line)

    def refresh_status():
        status = cek_status_database()
        status_area.delete("1.0", "end")
        for k, v in status.items():
            status_area.insert("end", f"{k}: {v}\n")
    
    tk.Button(tab_status, text="Refresh Status", command=refresh_status).pack(pady=5)
    refresh_status()

    tk.Button(tab_log, text="Refresh Log", command=refresh_log).pack(pady=5)

    tk.Button(tab_status, text="Refresh Printer", command=refresh_printer).pack(pady=5)
    refresh_printer()

    tk.Label(tab_tes, text="ID transaksi untuk Simulasi:", bg="#f4f4f4").pack(pady=5)
    entry_id = tk.Entry(tab_tes)
    entry_id.pack(pady=5)

    hasil_simulasi = tk.Text(tab_tes, height=6, bg="#f4f4f4", font=("Courier", 10))
    hasil_simulasi.pack(fill="x", padx=10, pady=5)

    def jalankan_simulasi():
        transaksi_id = entry_id.get().strip()
        if not transaksi_id.isdigit():
            hasil_simulasi.delete("1.0", "end")
            hasil_simulasi.insert("end", "ID Transaksi harus berupa angka.\n")
            return
        hasil = simulasi_cetak_nota(int(transaksi_id))
        hasil_simulasi.delete("1.0", "end")
        for k, v in hasil.items():
            hasil_simulasi.insert("end", f"{k}: {v}\n")
    
    tk.Button(tab_tes, text="Simulasi Cetak Nota", command=jalankan_simulasi).pack(pady=5)
    