import tkinter as tk
from tkinter import ttk

# Import semua modul GUI

from app.gui.member_gui import buat_frame_member
from app.gui.supplier_gui import buat_frame_supplier
from app.gui.produk_gui import buat_frame_produk
from app.gui.pengeluaran_gui import buat_frame_pengeluaran
from app.gui.pembelian_gui import buat_frame_pembelian
from app.gui.penjualan_gui import buat_frame_penjualan
from app.gui.stok_gui import buat_frame_stok
from app.gui.laporan_gui import buat_frame_laporan

judul_modul_label = None
judul_frame = None
def main():
    root = tk.Tk()
    root.title("POS Pintar by Fathir")
    root.geometry("1200x700")

    # Frame utama: navigasi kiri + konten kanan

    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(side="right", fill="both", expand=True)

    global judul_modul_label, judul_frame
    judul_frame = tk.Frame(main_frame, bg="white")
    judul_frame.pack(fill="x")

    content_frame = tk.Frame(main_frame, bg="white")
    content_frame.pack(side="right", fill="both", expand=True)

    judul_modul_label = tk.Label(judul_frame, text="", font=("Arial", 16, "bold"), bg="white", anchor="center", justify="center")
    judul_modul_label.pack(fill="x", padx=20, pady=(10, 5))

    def set_judul_modul(nama, jumlah=None):
        global judul_modul_label
        teks = f"📌 Modul {nama}"
        if jumlah is not None:
            teks += f" ({jumlah} item)"
        judul_modul_label.config(text=teks)

    def tampilkan_menu_utama():
        for widget in content_frame.winfo_children():
            widget.destroy()
        
        menu_frame = tk.Frame(content_frame, bg="white")
        menu_frame.pack(fill="both", expand=True)

        tk.Label(menu_frame, text="Selamat Datang di POS Pintar by Fathir", font=("Arial", 18, "bold"), bg="white").pack(pady=30)
        tk.Label(menu_frame, text="Silakan Pilih modul dari menu di sebelah kiri.", font=("Arial", 12), bg="white").pack(pady=10)

    # Fungsi untuk menampilkan frame dari modul

    def tampilkan_frame(frame_func):
        for widget in content_frame.winfo_children():
            widget.destroy()

        try:
            frame_func(content_frame, set_judul_modul) # Kirim fungsi ke Modul
        except Exception as e:
            import traceback
            traceback.print_exc()
            tk.messagebox.showerror("Error", f"Gagal load frame: {frame_func.__name__}\n{e}")

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
        tk.Button(main_frame, text=label, font=("Arial", 11), width=20, pady=5,
                  command=lambda f=func:tampilkan_frame(f)).pack(pady=2)

    # Tampilkan default frame

    tampilkan_menu_utama()

    root.mainloop()

if __name__ == "__main__":
    main()

#untuk buat jadi aplikasi
#pyinstaller --noconsole ^
#  --add-data "data/pos.db;data" ^
#  --add-data "local_escpos;local_escpos" ^
#  app_gui.py