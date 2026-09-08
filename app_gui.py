# Standard Library
import os
import sys

# Third-party
import tkinter as tk
from tkinter import messagebox

# Local Application
from app.gui.member_gui import buat_frame_member
from app.gui.supplier_gui import buat_frame_supplier
from app.gui.produk_gui import buat_frame_produk
from app.gui.pengeluaran_gui import buat_frame_pengeluaran
from app.gui.pembelian_gui import buat_frame_pembelian
from app.gui.penjualan_gui import buat_frame_penjualan
from app.gui.stok_gui import buat_frame_stok
from app.gui.laporan_gui import buat_frame_laporan
from app.gui.pengaturan_gui import buka_pengaturan_gui
from app.gui.debug_gui import buka_debug_gui
from app.translator import _, i18n

judul_modul_label = None
judul_frame = None
modul_aktif_sekarang = None  # Menyimpan fungsi modul yang sedang dibuka


def main():
  global judul_modul_label, judul_frame, modul_aktif_sekarang

  root = tk.Tk()
  root.title(_("app_gui.app_title"))
  root.geometry("1000x600")

  # --- SIDEBAR NAVIGASI (KIRI) ---
  sidebar_frame = tk.Frame(root, bg="#f0f0f0", width=200)
  sidebar_frame.pack(side="left", fill="y")

  # --- KONTEN UTAMA (KANAN) ---
  main_frame = tk.Frame(root, bg="white")
  main_frame.pack(side="right", fill="both", expand=True)

  judul_frame = tk.Frame(main_frame, bg="white")
  judul_frame.pack(fill="x")

  content_frame = tk.Frame(main_frame, bg="white")
  content_frame.pack(fill="both", expand=True)

  judul_modul_label = tk.Label(
      judul_frame,
      text="",
      font=("Arial", 16, "bold"),
      bg="white",
      anchor="center",
      justify="center",
  )
  judul_modul_label.pack(fill="x", padx=20, pady=(10, 5))

  def set_judul_modul(nama, jumlah=None):
    global judul_modul_label
    teks = f"📌 {_('app_gui.lbl_module')} {nama}"
    if jumlah is not None:
      teks += f" ({jumlah} item)"
    judul_modul_label.config(text=teks)

  # --- FUNGSI MEREFRESH SELURUH UI BILA BAHASA BERUBAH ---
  def refresh_app_ui():
    root.title(_("app_gui.app_title"))
    render_sidebar()  # Redraw tombol navigasi dengan bahasa baru

    # Redraw halaman yang sedang aktif
    if modul_aktif_sekarang is None:
      tampilkan_menu_utama()
    else:
      tampilkan_frame(modul_aktif_sekarang)

  def tampilkan_menu_utama():
    global modul_aktif_sekarang
    modul_aktif_sekarang = None
    set_judul_modul(_("app_gui.menu_dashboard"))

    for widget in content_frame.winfo_children():
      widget.destroy()

    menu_frame = tk.Frame(content_frame, bg="white")
    menu_frame.pack(fill="both", expand=True)

    footer_frame = tk.Frame(content_frame, bg="white")
    footer_frame.pack(side="bottom", fill="x", pady=20)

    tk.Label(
        menu_frame,
        text=_("app_gui.msg_welcome"),
        font=("Arial", 18, "bold"),
        bg="white",
    ).pack(pady=30)

    tk.Label(
        menu_frame, text=_("app_gui.msg_select_module"), font=("Arial", 12), bg="white"
    ).pack(pady=10)

    footer_center_frame = tk.Frame(footer_frame, bg="white")
    footer_center_frame.pack(anchor="center")

    lbl_copy = tk.Label(
        footer_center_frame,
        text="© 2025 Fathir Afatar • v2.0 • ",
        font=("Arial", 9),
        fg="#555555",
        bg="white",
    )
    lbl_copy.pack(side="left")

    lbl_license = tk.Label(
        footer_center_frame,
        text="MIT License",
        font=("Arial", 9, "underline"),
        fg="#0066cc",
        bg="white",
        cursor="hand2",
    )
    lbl_license.pack(side="left")
    lbl_license.bind("<Button-1>", lambda e: show_license())

  def tampilkan_frame(frame_func):
    global modul_aktif_sekarang
    modul_aktif_sekarang = frame_func

    for widget in content_frame.winfo_children():
      widget.destroy()

    try:
      # Jika yang dibuka adalah Pengaturan, kirimkan callback refresh_app_ui
      if frame_func == buka_pengaturan_gui:
        frame_func(content_frame, set_judul_modul, refresh_app_ui)
      else:
        frame_func(content_frame, set_judul_modul)
    except Exception as e:
      import traceback

      traceback.print_exc()
      messagebox.showerror(
          _("app_gui.msg_error"), f"Gagal load frame: {frame_func.__name__}\n{e}"
      )

  # --- RENDER TOMBOL NAVIGASI DENGAN TERJEMAHAN DYNAMIS ---
  def render_sidebar():
    for widget in sidebar_frame.winfo_children():
      widget.destroy()

    tombol_navigasi = [
        (_("app_gui.nav_member"), buat_frame_member),
        (_("app_gui.nav_supplier"), buat_frame_supplier),
        (_("app_gui.nav_product"), buat_frame_produk),
        (_("app_gui.nav_expense"), buat_frame_pengeluaran),
        (_("app_gui.nav_purchase"), buat_frame_pembelian),
        (_("app_gui.nav_sale"), buat_frame_penjualan),
        (_("app_gui.nav_stock"), buat_frame_stok),
        (_("app_gui.nav_report"), buat_frame_laporan),
        (_("app_gui.nav_settings"), buka_pengaturan_gui),
        (_("app_gui.nav_debug"), buka_debug_gui),
    ]

    for label, func in tombol_navigasi:
      tk.Button(
          sidebar_frame,
          text=label,
          font=("Arial", 11),
          width=18,
          pady=5,
          command=lambda f=func: tampilkan_frame(f),
      ).pack(pady=2, padx=5)

  def get_license_path(filename="LICENSE"):
    if getattr(sys, "frozen", False):
      base_path = os.path.dirname(sys.executable)
    else:
      base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

  def show_license():
    license_path = get_license_path("LICENSE")
    try:
      with open(license_path, "r", encoding="utf-8") as file:
        license_text = file.read()
      messagebox.showinfo("MIT License", license_text)
    except FileNotFoundError:
      messagebox.showerror(
          _("app_gui.msg_error"), f"File LICENSE not found:\n{license_path}"
      )
    except Exception as e:
      messagebox.showerror(
          _("app_gui.msg_error"), f"Failed to open license file:\n{str(e)}"
      )

  # Inisialisasi Tampilan Awal
  render_sidebar()
  tampilkan_menu_utama()

  root.mainloop()

if __name__ == "__main__":
  main()

#untuk buat jadi aplikasi
#pyinstaller --noconsole ^
#  --add-data "data/pos.db;data" ^
#  --add-data "local_escpos;local_escpos" ^
#  app_gui.py