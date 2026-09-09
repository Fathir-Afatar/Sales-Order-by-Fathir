# Standard Library
from datetime import datetime

# Third-party
import tkinter as tk
from tkcalendar import Calendar
from tkinter import ttk, messagebox, Toplevel, Button

# Local Application
from app.core.pengeluaran_core import (tambah_pengeluaran, semua_pengeluaran, pengeluaran_bulan_kategori
                                       , pengeluaran_per_bulan, pengeluaran_per_kategori, hapus_pengeluaran
                                       , edit_pengeluaran, bersihkan_angka)
from app.constants.config import get_connection
from app.translator import _, i18n

def open_calendar(entry_widget):
    """Open a modal date picker window and populate the target Entry widget.

    Args:
        entry_widget (ttk.Entry): Target entry widget where selected date string is
            inserted.
    """
    top = Toplevel()
    top.grab_set()
    top.transient(entry_widget.master)

    cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
    cal.pack(padx=10, pady=10)

    def select_date():
        """Extract chosen date from Calendar and update entry field."""
        entry_widget.delete(0, 'end')
        entry_widget.insert(0, cal.get_date())
        top.destroy()
    Button(top, text=_("pengeluaran.btn_top"), command=select_date).pack(pady=5)

def buka_form_tambah_pengeluaran(tampilkan_histori_callback):
    """Display a modal dialog window to input and record new expense transactions.

    Args:
        tampilkan_histori_callback (Callable[[List[Dict[str, Any]]], None]):
            Callback function used to reload the history treeview upon saving.
    """
    form = tk.Toplevel()
    form.title(_("pengeluaran.form_title"))
    form.geometry("400x400")
    form.grab_set()

    # A dictionary for storing Entry objects based on a STATIC KEY (not a language label).
    entries = {}

    # 1. Date input
    ttk.Label(form, text="Tanggal").pack(anchor="w", padx=10, pady=(10))
    tanggal_entry = ttk.Entry(form, width=20)
    tanggal_entry.pack(fill="x", padx=10)
    ttk.Button(form, text="📅", command=lambda: open_calendar(tanggal_entry)).pack(pady=5)
    entries["tanggal"] = tanggal_entry

    # 2. Additional inputs with static keys to prevent mix-ups or misdetection.
    fields = [
        {"key": "nama", "label": _("pengeluaran.nama_pengeluaran")},
        {"key": "kategori", "label": _("pengeluaran.kategori")},
        {"key": "nominal", "label": _("pengeluaran.nominal")},
        {"key": "keterangan", "label": _("pengeluaran.keterangan")}
    ]

    for field in fields:
        ttk.Label(form, text=field["label"]).pack(anchor="w", padx=10, pady=5)
        ent = ttk.Entry(form)
        ent.pack(fill="x", padx=10)
        entries[field["key"]] = ent  # saving according key statis: 'nama', 'nominal', dll.
    
    def simpan():
        """Validate user input, construct record payload, and persist expense data."""
        try:
            # Take data using statis
            tanggal = entries["tanggal"].get().strip()
            nama = entries["nama"].get().strip()
            kategori = entries["kategori"].get().strip()
            keterangan = entries["keterangan"].get().strip()
            
            # Cleaning number
            nominal_raw = entries["nominal"].get().strip()
            nominal = float(nominal_raw)

            if not tanggal or not nama or not kategori or not nominal_raw:
                messagebox.showwarning(_("pengeluaran.validasi"), _("pengeluaran.msg_warning"))
                return
            
            data = {
                "tanggal": tanggal,
                "nama_pengeluaran": nama,
                "nominal": nominal,
                "keterangan": keterangan,
                "kategori": kategori,
            }
            tambah_pengeluaran(data)

            messagebox.showinfo(_("pengeluaran.sukses"), _("pengeluaran.msg_show_info"))
            form.destroy()
            tampilkan_histori_callback(semua_pengeluaran())
        except ValueError:
            messagebox.showerror("Error", _("pengeluaran.msg_show_error_nominal"))

    ttk.Button(form, text=_("pengeluaran.simpan"), command=simpan).pack(pady=20)

def tampilkan_histori(data_pengeluaran):
    """Clear existing tree rows and render the updated set of expense records.

    Args:
        data_pengeluaran (List[Dict[str, Any]]): List of dictionary objects
            representing expense transactions.
    """
    tree.delete(*tree.get_children()) # clear semua isi lama
    for row in data_pengeluaran:
        tree.insert("", "end", values=(
            row["tanggal"],
            row["nama_pengeluaran"],
            row["kategori"],
            f"Rp {float(row['nominal']):,}",
            row["keterangan"]
        ), tags=(row["id_pengeluaran"],)) # row[0] = id_pengeluaran 

def buat_frame_pengeluaran(parent, set_judul_modul):
    """Construct and initialize the primary UI layout for the expense module.

    Args:
        parent (tk.Widget): Parent container widget.
        set_judul_modul (Callable[[str], None]): Callback function to update main
            application header title.
    """
    global tree
    frame = tk.Frame(parent, bg="#f4f4f4")
    
    frame_filter = tk.Frame(frame, bg="#f4f4f4")
    frame_filter.pack(pady=10)

    tk.Label(frame_filter, text=_("pengeluaran.bulan")).pack(side=tk.LEFT, padx=5)
    combo_bulan = ttk.Combobox(frame_filter, values=[
    _("pengeluaran.januari"), _("pengeluaran.februari"), _("pengeluaran.maret"), _("pengeluaran.april"),
    _("pengeluaran.mei"), _("pengeluaran.juni"), _("pengeluaran.juli"), _("pengeluaran.agustus"),
    _("pengeluaran.september"), _("pengeluaran.oktober"), _("pengeluaran.november"), _("pengeluaran.desember")
    ])
    combo_bulan.pack(side=tk.LEFT)
    combo_bulan.set("")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT kategori FROM pengeluaran")
    kategori_list = [row[0] for row in cursor.fetchall()]
    conn.close()

    kategori_list.insert(0, _("pengeluaran.semua"))

    tk.Label(frame_filter, text=_("pengeluaran.kategori")).pack(side=tk.LEFT, padx=5)
    combo_kategori = ttk.Combobox(frame_filter, values=kategori_list, state="readonly")
    combo_kategori.pack(side=tk.LEFT)
    combo_kategori.set(_("pengeluaran.semua"))

    tahun_sekarang = datetime.now().year
    tahun_list = [str(tahun_sekarang - i) for i in range(5)]

    tk.Label(frame_filter, text=_("pengeluaran.tahun")).pack(side=tk.LEFT, padx=5)
    combo_tahun = ttk.Combobox(frame_filter, values=tahun_list, state="readonly")
    combo_tahun.pack(side=tk.LEFT)
    combo_tahun.set(str(datetime.now().year))
    
    def reset_filter():
        """Clear active search parameters and restore default historical view."""
        combo_bulan.set("")
        combo_kategori.set(_("pengeluaran.semua"))
        tampilkan_histori(semua_pengeluaran())
        messagebox.showinfo("Reset",_("pengeluaran.msg_show_info_filter"))

    def apply_filter():
        """Fetch and render filtered records based on current user inputs."""
        bulan_str = combo_bulan.get()
        kategori = combo_kategori.get()
        tahun_str = combo_tahun.get()

        bulan = bulan_str.split(" - ")[0]
        tahun = int(tahun_str) if tahun_str else datetime.now().year
        kategori = kategori.lower() if kategori else "semua"

        if bulan and kategori != "semua":
            data = pengeluaran_bulan_kategori(bulan, tahun, kategori)
        elif bulan and kategori == "semua":
            data = pengeluaran_per_bulan(bulan, tahun)
        elif not bulan and kategori != "semua":
            data = pengeluaran_per_kategori(kategori)
        else:
            data = semua_pengeluaran()
        tampilkan_histori(data)
        for row in data:
            print("Row:", row)
    tk.Button(frame_filter, text=_("pengeluaran.btn_frame_filter"), command= apply_filter).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_filter, text=_("pengeluaran.btn_reset_filter"), command=reset_filter).pack(side=tk.LEFT, padx=5)
    
    # Treeview
    frame_tree = tk.Frame(frame)
    frame_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scroll_x = tk.Scrollbar(frame_tree, orient=tk.HORIZONTAL)
    scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    scroll_y = tk.Scrollbar(frame_tree, orient=tk.VERTICAL)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    tree = ttk.Treeview(frame_tree, columns=(_("pengeluaran.tanggal"), _("pengeluaran.nama"), _("pengeluaran.kategori"), _("pengeluaran.nominal"), _("pengeluaran.keterangan")), show="headings", height=15, xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    scroll_x.config(command=tree.xview)
    scroll_y.config(command=tree.yview)

    for col in (_("pengeluaran.tanggal"), _("pengeluaran.nama"), _("pengeluaran.kategori"), _("pengeluaran.nominal"), _("pengeluaran.keterangan")):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    
    data = semua_pengeluaran()
    tampilkan_histori(data)

    # Tombol edit & hapus
    frame_btn = tk.Frame(frame, bg="#f4f4f4")
    frame_btn.pack(pady=5)

    def hapus_pengeluaran_gui():
        """Prompt for user confirmation and remove selected expense record from DB."""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning(_("pengeluaran.msg_show_warning"))
            return
        id_pengeluaran = tree.item(selected[0])["tags"][0]
        confirm = messagebox.askyesno(_("pengeluaran.msg_ask_yesno"))
        if confirm:
            hapus_pengeluaran(id_pengeluaran)
            apply_filter()

    def edit_pengeluaran_gui():
        """Launch modal form initialized with values of selected entry for modification."""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning(_("pengeluaran.msg_pilih_data"))
            return
        item = tree.item(selected[0])
        values = item["values"]
        id_pengeluaran = tree.item(selected[0])["tags"][0]

        form = tk.Toplevel()
        form.title(_("form_title_edit"))
        form.geometry("400x400")
        form.grab_set()

        labels = [ _("pengeluaran.nama"), _("pengeluaran.kategori"), _("pengeluaran.nominal"), _("pengeluaran.keterangan")]
        entries = {}

        ttk.Label(form, text=(_("pengeluaran.tanggal"))).pack(anchor="w", padx=10, pady=(10))
        tanggal_db = values[0]
        tanggal_entry_edit = ttk.Entry(form, width=20)
        tanggal_entry_edit.insert(0, tanggal_db.split(" ")[0])

        tanggal_entry_edit.pack(fill="x", padx=10)
        Button(form, text="📅", command=lambda: open_calendar(tanggal_entry_edit)).pack(pady=5)
        entries["Tanggal"] = tanggal_entry_edit

        for i, label in enumerate(labels):
            ttk.Label(form, text=label).pack(anchor="w", padx=10, pady=(10 if i == 0 else 5))
            ent = ttk.Entry(form)
            ent.pack(fill="x", padx=10)
            entries[label] = ent
        
        entries["Nama Pengeluaran"].insert(0, values[1])
        entries["Kategori"].insert(0, values[2])
        entries["Nominal"].insert(0, values[3].replace("Rp ","").replace(",",""))
        entries["Keterangan"].insert(0, values[4])

        def simpan_edit():
            """Extract edited details and update record via database persistence function."""
            try:
                tanggal = entries["Tanggal"].get()
                nama = entries["Nama Pengeluaran"].get()
                kategori = entries["Kategori"].get()
                nominal = float(entries["Nominal"].get())
                keterangan = entries["Keterangan"].get()

                data = {
                    "tanggal": tanggal,
                    "nama_pengeluaran": nama,
                    "kategori": kategori,
                    "nominal": nominal,
                    "keterangan": keterangan
                }
                edit_pengeluaran(id_pengeluaran, data)

                messagebox.showinfo(_("pengeluaran.msg_sukses"))
                form.destroy()
                tampilkan_histori(semua_pengeluaran())
            except Exception as e:
                print(_("pengeluaran.msg_error_gui"), e)
                messagebox.showerror(_("pengeluaran.err_gagal_update"))
        ttk.Button(form, text=_("pengeluaran.text_simpan"), command=simpan_edit).pack(pady=20)
    
    tk.Button(frame_btn, text=_("pengeluaran.edit"), command=edit_pengeluaran_gui).pack(side=tk.LEFT, padx=10)
    tk.Button(frame_btn, text=_("pengeluaran.hapus"), command=hapus_pengeluaran_gui).pack(side=tk.LEFT, padx=10)
    tk.Button(frame_btn, text=_("pengeluaran.tambah"), command=lambda:buka_form_tambah_pengeluaran(tampilkan_histori)).pack(side=tk.LEFT, padx=10)
    
    frame.pack(fill="both", expand=True)
    
    set_judul_modul(_("pengeluaran.set_judul_modul"))

if __name__ == "__main__":
    buat_frame_pengeluaran()