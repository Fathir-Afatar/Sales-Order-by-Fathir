import tkinter as tk
from tkinter import ttk
import os
import sys
from tkinter import messagebox
import traceback
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

print("[DEBUG] Current dir:", os.getcwd())
print("[DEBUG] pos.db exists:", os.path.exists("data/pos.db"))
print("[DEBUG] capabilities.json exists:", os.path.exists("escpos/capabilities.json"))

    # Validasi file capabilitites.json
import sys
if getattr(sys, 'frozen', False):
    print("[DEBUG] Running from .exe")
else:
    print("[DEBUG] Running from source")
# Import semua modul GUI

from app.gui.member_gui import buat_frame_member
from app.gui.supplier_gui import buat_frame_supplier
from app.gui.produk_gui import buat_frame_produk
from app.gui.pengeluaran_gui import buat_frame_pengeluaran
from app.gui.pembelian_gui import buat_frame_pembelian
from app.gui.penjualan_gui import buat_frame_penjualan
from app.gui.stok_gui import buat_frame_stok
from app.gui.laporan_gui import buat_frame_laporan

def main():
    try:
        root = tk.Tk()
        root.title("POS Pintar by Fathir")
        root.geometry("1200x700")

        # Frame utama: navigasi kiri + konten kanan
        nav_frame = tk.Frame(root, bg="#f0f0f0", width=200)
        nav_frame.pack(side="left", fill="y")

        content_frame = tk.Frame(root, bg="white")
        content_frame.pack(side="right", fill="both", expand=True)

        # Fungsi untuk menampilkan frame dari modul

        def tampilkan_frame(frame_func):
            for widget in content_frame.winfo_children():
                widget.destroy()
            frame_func(content_frame)
    
        # Tombol navigasi vertikal

        tombol_navigasi = [
            ("Member", buat_frame_member),
            ("Supplier", buat_frame_supplier),
            ("Produk", buat_frame_produk),
            ("Pengeluaran", buat_frame_pengeluaran),
            ("Pembelian", buat_frame_pembelian),
            ("Penjualan", buat_frame_penjualan),
            ("Stok", buat_frame_stok),
            ("Laporan", buat_frame_laporan),
        ]

        for label, func in tombol_navigasi:
            tk.Button(nav_frame, text=label, font=("Arial", 11), width=20, pady=5,
                    command=lambda f=func:tampilkan_frame(f)).pack(pady=2)

        # Tampilkan default frame

        tampilkan_frame(buat_frame_penjualan)

        root.mainloop()

    except Exception as e:
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())

if __name__ == "__main__":
    main()