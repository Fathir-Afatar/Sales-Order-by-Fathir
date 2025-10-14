import tkinter as tk
from tkinter import ttk, messagebox
from app.core.pengaturan_core import(
    ambil_format_nota, simpan_format_nota,
    get_usb_printer_list, simpan_printer_default,
    test_cetak_usb
)

def buka_pengaturan_gui(parent, set_judul_modul):
    set_judul_modul("Pengaturan Nota & Printer")
    frame = tk.Frame(parent, bg="#f4f4f4")
    frame.pack(fill="both", expand=True)

    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Tab 1: Format Nota

    tab_nota = tk.Frame(notebook, bg="#f4f4f4")
    notebook.add(tab_nota, text="Format Nota Thermal")

    config = ambil_format_nota()

    header_label = tk.Label(tab_nota, text="Header Nota:", bg="#f4f4f4")
    header_label.pack(anchor="w", padx=10)
    header_entry = tk.Text(tab_nota, height=3)
    header_entry.insert("1.0", config["header"])
    header_entry.pack(fill="x")

    footer_label = tk.Label(tab_nota, text="Footer Nota:", bg="#f4f4f4")
    footer_label.pack(anchor="w", padx=10)
    footer_entry = tk.Text(tab_nota, height=3)
    footer_entry.insert("1.0", config["footer"])
    footer_entry.pack(fill="x")

    font_label = tk.Label(tab_nota, text="Ukuran Font:", bg="#f4f4f4")
    font_label.pack(anchor="w", padx=10)
    font_size_spin = tk.Spinbox(tab_nota, from_=8, to=20)
    font_size_spin.delete(0, "end")
    font_size_spin.insert(0, config["font_size"])
    font_size_spin.pack()

    def simpan_nota():
        data = {
            "header": header_entry.get("1.0", "end").strip(),
            "footer": footer_entry.get("1.0", "end").strip(),
            "font_size": int(font_size_spin.get()),
            "margin_kiri": 5,
            "margin_kanan": 5,
            "lebar_kertas": "58mm"
        }
        simpan_format_nota(data)
        messagebox.showinfo("Berhasil", "Format nota disimpan.")
    
    tk.Button(tab_nota, text="Simpan Format Nota", command=simpan_nota).pack(pady=5)

    preview_area = tk.Text(tab_nota, height=15, bg="#ffffff", font=("Courier", config["font_size"]))
    preview_area.pack(fill="both", expand=True, padx=10, pady=10)

    def tampilkan_preview():
        preview_area.delete("1.0", "end")
        header = header_entry.get("1.0", "end").strip()
        footer = footer_entry.get("1.0", "end").strip()
        font_size = int(font_size_spin.get())

        #Simulasi isi nota

        isi_nota = f"""
{header.center(32)}

Produk A x2 Rp10.000
Produk B x1 Rp5.000

Total:      Rp25.000

{footer.center(32)}
"""
        preview_area.config(font=("Courier", font_size))
        preview_area.insert("1.0", isi_nota)

    tk.Button(tab_nota, text="Preview Nota", command=tampilkan_preview).pack(pady=5)

    # Tab 2: Printer

    tab_printer = tk.Frame(notebook, bg="#f4f4f4")
    notebook.add(tab_printer, text="Tes & Pengaturan Printer")

    printer_label = tk.Label(tab_printer, text="Pilih Printer USB:", bg="#f4f4f4")
    printer_label.pack(anchor="w", padx=10)
    printer_list = get_usb_printer_list()
    printer_combo = ttk.Combobox(tab_printer, values=printer_list)
    printer_combo.pack()

    def simpan_printer():
        if not printer_combo.get():
            messagebox.showerror("Error", "Pilih printer terlebih dahulu.")
            return
        vendor, product = printer_combo.get().split(":")
        simpan_printer_default(vendor, product)
        messagebox.showinfo("Berhasil", "Printer default disimpan.")
    
    def test_printer():
        if not printer_combo.get():
            messagebox.showerror("Error", "Pilih printer terlebih dahulu.")
            return
        vendor, product = printer_combo.get().split(":")
        success = test_cetak_usb(int(vendor, 16), int(product, 16))
        if success:
            messagebox.showinfo("Sukses", "Tes cetak berhasil.")
        else:
            messagebox.showerror("Gagal", "Tes cetak gagal.")
    
    tk.Button(tab_printer, text="Tes Cetak", command=test_printer).pack(pady=5)
    tk.Button(tab_printer, text="Simpan Printer Default", command=simpan_printer).pack(pady=5)

    return frame

