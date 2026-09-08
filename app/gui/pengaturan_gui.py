# Third-party
import tkinter as tk
from tkinter import ttk, messagebox

# Local application
from app.core.pengaturan_core import(
    ambil_format_nota, simpan_format_nota,
    get_usb_printer_list, simpan_printer_default,
    test_cetak_usb
)
from app.translator import _, i18n

def buka_pengaturan_gui(parent, set_judul_modul, refresh_app_ui=None):
  # Menggunakan _() agar judul modul menyesuaikan bahasa aktif
  set_judul_modul(_("pengaturan.set_title"))

  frame = tk.Frame(parent, bg="#f4f4f4")
  frame.pack(fill="both", expand=True)

  notebook = ttk.Notebook(frame)
  notebook.pack(fill="both", expand=True, padx=10, pady=10)

  tab_nota = tk.Frame(notebook, bg="#f4f4f4")
  notebook.add(tab_nota, text=_("pengaturan.tab_receipt_format"))

  config = ambil_format_nota()

  header_label = tk.Label(
      tab_nota, text=_("pengaturan.lbl_header_receipt"), bg="#f4f4f4"
  )
  header_label.pack(anchor="w", padx=10)
  header_entry = tk.Text(tab_nota, height=3)
  header_entry.insert("1.0", config["header"])
  header_entry.pack(fill="x")

  footer_label = tk.Label(
      tab_nota, text=_("pengaturan.lbl_footer_receipt"), bg="#f4f4f4"
  )
  footer_label.pack(anchor="w", padx=10)
  footer_entry = tk.Text(tab_nota, height=3)
  footer_entry.insert("1.0", config["footer"])
  footer_entry.pack(fill="x")

  font_label = tk.Label(tab_nota, text=_("pengaturan.lbl_font_size"), bg="#f4f4f4")
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
        "lebar_kertas": "58mm",
    }
    simpan_format_nota(data)
    messagebox.showinfo(_("pengaturan.msg_success"), _("pengaturan.msg_receipt_saved"))

  tk.Button(tab_nota, text=_("pengaturan.btn_save_receipt"), command=simpan_nota).pack(
      pady=5
  )

  preview_area = tk.Text(
      tab_nota, height=15, bg="#ffffff", font=("Courier", config["font_size"])
  )
  preview_area.pack(fill="both", expand=True, padx=10, pady=10)

  def tampilkan_preview():
    preview_area.delete("1.0", "end")
    header = header_entry.get("1.0", "end").strip()
    footer = footer_entry.get("1.0", "end").strip()
    font_size = int(font_size_spin.get())

    isi_nota = f"""
{header.center(32)}

Produk A x2 Rp10.000
Produk B x1 Rp5.000

Total:      Rp25.000

{footer.center(32)}
"""
    preview_area.config(font=("Courier", font_size))
    preview_area.insert("1.0", isi_nota)

  tk.Button(tab_nota, text=_("pengaturan.btn_preview"), command=tampilkan_preview).pack(
      pady=5
  )

  # ==========================================
  # TAB 2: PRINTER
  # ==========================================
  tab_printer = tk.Frame(notebook, bg="#f4f4f4")
  notebook.add(tab_printer, text=_("pengaturan.tab_printer_settings"))

  printer_label = tk.Label(tab_printer, text=_("pengaturan.lbl_select_usb"), bg="#f4f4f4")
  printer_label.pack(anchor="w", padx=10)
  printer_list = get_usb_printer_list()
  printer_combo = ttk.Combobox(tab_printer, values=printer_list)
  printer_combo.pack()

  def simpan_printer():
    if not printer_combo.get():
      messagebox.showerror(_("pengaturan.msg_error"), _("pengaturan.err_select_printer"))
      return
    vendor, product = printer_combo.get().split(":")
    simpan_printer_default(vendor, product)
    messagebox.showinfo(_("pengaturan.msg_success"), _("pengaturan.msg_printer_saved"))

  def test_printer():
    if not printer_combo.get():
      messagebox.showerror(_("pengaturan.msg_error"), _("pengaturan.err_select_printer"))
      return
    vendor, product = printer_combo.get().split(":")
    success = test_cetak_usb(int(vendor, 16), int(product, 16))
    if success:
      messagebox.showinfo(_("pengaturan.msg_success"), _("pengaturan.msg_print_success"))
    else:
      messagebox.showerror(_("pengaturan.msg_error"), _("pengaturan.err_print_failed"))

  tk.Button(tab_printer, text=_("pengaturan.btn_test_print"), command=test_printer).pack(
      pady=5
  )
  tk.Button(
      tab_printer, text=_("pengaturan.btn_save_printer"), command=simpan_printer
  ).pack(pady=5)

  # ==========================================
  # TAB 3: BAHASA / LANGUAGE (TAMBAHAN BARU)
  # ==========================================
  tab_lang = tk.Frame(notebook, bg="#f4f4f4")
  notebook.add(tab_lang, text=_("pengaturan.tab_language"))

  lbl_choose = tk.Label(
      tab_lang,
      text=_("pengaturan.lbl_select_language"),
      bg="#f4f4f4",
      font=("Arial", 10, "bold"),
  )
  lbl_choose.pack(anchor="w", padx=15, pady=(15, 5))

  # Pilihan Bahasa dengan RadioButton
  lang_var = tk.StringVar(value=i18n.current_lang)

  rb_id = tk.Radiobutton(
      tab_lang,
      text="Bahasa Indonesia",
      variable=lang_var,
      value="id",
      bg="#f4f4f4",
  )
  rb_id.pack(anchor="w", padx=25, pady=2)

  rb_en = tk.Radiobutton(
      tab_lang,
      text="English",
      variable=lang_var,
      value="en",
      bg="#f4f4f4",
  )
  rb_en.pack(anchor="w", padx=25, pady=2)

  def ubah_bahasa():
    pilihan = lang_var.get()
    i18n.set_language(pilihan)

    messagebox.showinfo(_("pengaturan.msg_success"), _("pengaturan.msg_lang_changed"))

    if refresh_app_ui:
      refresh_app_ui()

  btn_apply_lang = tk.Button(
      tab_lang,
      text=_("pengaturan.btn_apply_language"),
      command=ubah_bahasa,
      bg="#007acc",
      fg="white",
      font=("Arial", 9, "bold"),
  )
  btn_apply_lang.pack(anchor="w", padx=15, pady=15)

  return frame