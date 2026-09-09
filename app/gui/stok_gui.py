# Third-party
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Local Application
from app.core.stok_core import (generate_kartu_stok, get_produk_id_by_nama, 
                                get_daftar_nama_barang, cek_log_harian, 
                                ambil_log_stok_bulanan, proses_stok_harian)
from app.constants.config import get_connection
from app.core.product_core import semua_produk
from app.translator import _, i18n

def build_treeview_stok(parent):
    """Construct and format the stock card Treeview component.

    Args:
        parent (tk.Widget): Parent GUI container widget.

    Returns:
        ttk.Treeview: Configured Treeview widget for stock movement display.
    """
    tree = ttk.Treeview(parent, columns=(_("stok.tanggal"), _("stok.awal"), _("stok.masuk"), 
                                         _("stok.keluar"), _("stok.akhir")), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=80)
    return tree

def build_treeview_ringkasan(parent):
    """Construct and format the stock summary Treeview component.

    Args:
        parent (tk.Widget): Parent GUI container widget.

    Returns:
        ttk.Treeview: Configured Treeview widget for stock summary display.
    """
    tree = ttk.Treeview(parent, columns=(_("stok.kode"), _("stok.nama_produk"), 
                                         _("stok.stok_awal"), _("stok.stok_akhir")), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, anchor="w", stretch=True)
    return tree

def ambil_filter_stok(barang_combo, bulan_combo, tahun_combo):
    """Extract and validate parameters from stock filter dropdowns.

    Args:
        barang_combo (ttk.Combobox): Product selector Combobox.
        bulan_combo (ttk.Combobox): Month selector Combobox.
        tahun_combo (ttk.Combobox): Year selector Combobox.

    Returns:
        Optional[Tuple[Any, int, int]]: Tuple containing (product_id, month,
        year) if valid, otherwise None.
    """
    nama_barang = barang_combo.get()
    bulan_index = bulan_combo.current()
    tahun_str = tahun_combo.get()
    if not nama_barang or bulan_index == -1 or not tahun_str:
        return None
    
    bulan = bulan_index + 1
    tahun = int(tahun_str)
    produk_id = get_produk_id_by_nama(nama_barang)
    if produk_id is None:
        return None
    
    return produk_id, bulan, tahun

def isi_treeview_stok(tree, kartu):
    """Populate stock card Treeview rows with formatted stock transaction records.

    Args:
        tree (ttk.Treeview): Target Treeview instance.
        kartu (List[Dict[str, Any]]): List of stock movement record dictionaries.
    """
    tree.tag_configure("hari_ini", background="#dff0d8", foreground="black")
    tree.delete(*tree.get_children())
    for row in kartu:
        tanggal = row.get("tanggal")
        if row.get("hari_ini"):
            tanggal += " (Hari Ini)"
            tree.insert("", "end", values=(
                tanggal,
                f"{row.get('awal', 0):,}",
                f"{row.get('masuk', 0):,}",
                f"{row.get('keluar', 0):,}",
                f"{row.get('akhir', 0):,}"
            ), tags=("hari_ini",)if row.get("hari_ini") else ())
        else:
            tree.insert("", "end", values=(
                tanggal,
                f"{row.get('awal', 0):,}",
                f"{row.get('masuk', 0):,}",
                f"{row.get('keluar', 0):,}",
                f"{row.get('akhir', 0):,}"
            ))

def buat_frame_stok(parent, set_judul_modul):
    """Build primary stock management view inside a Notebook container.

    Args:
        parent (tk.Tk): Parent Tkinter container.
        set_judul_modul (Callable[[str], None]): Callback function to set module
            title.
    """
    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True)

    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True)

    build_section_kartu_stok(notebook)
    build_section_ringkasan_stok(notebook)

    set_judul_modul("Stok")

def build_section_kartu_stok(parent):
    """Build the stock card view section within the provided notebook tab.

    Args:
        parent (ttk.Notebook): Parent Notebook container.
    """
    tab_stok = ttk.Frame(parent)
    parent.add(tab_stok, text="Stok")

    filter_frame = tk.Frame(tab_stok)
    filter_frame.pack(pady=10)

    daftar_nama_barang = get_daftar_nama_barang()
    daftar_bulan = [_("stok.januari"), _("stok.februari"), _("stok.maret"), _("stok.april")
                    , _("stok.mei"), _("stok.juni"), _("stok.juli"), _("stok.agustus")
                    , _("stok.september"), _("stok.oktober"), _("stok.november"), _("stok.desember")]
    daftar_tahun = ["2025", "2026", "2027", "2028"]
    
    tk.Label(filter_frame, text=_("stok.barang")).grid(row=0, column=0)
    barang_combo = ttk.Combobox(filter_frame, values=daftar_nama_barang)
    barang_combo.grid(row=0, column=1)

    tk.Label(filter_frame, text=_("stok.bulan")).grid(row=0, column=2)
    bulan_combo = ttk.Combobox(filter_frame, values=daftar_bulan)
    bulan_combo.grid(row=0, column=3)

    tk.Label(filter_frame, text=_("stok.tahun")).grid(row=0, column=4)
    tahun_combo = ttk.Combobox(filter_frame, values=daftar_tahun)
    tahun_combo.grid(row=0, column=5)

    tree_frame = tk.Frame(tab_stok)
    tree_frame.pack(fill="both", expand=True)

    stok_tree = build_treeview_stok(tree_frame)
    stok_tree.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=stok_tree.yview)
    scrollbar.pack(side="right", fill="y")
    stok_tree.config(yscrollcommand=scrollbar.set)

    def tampilkan_kartu_stok():
        """Fetch filter inputs and load generated stock card into Treeview."""
        hasil = ambil_filter_stok(barang_combo, bulan_combo, tahun_combo)
        if not hasil:
            return
        produk_id, bulan, tahun = hasil
        kartu = generate_kartu_stok(produk_id, bulan, tahun)
        isi_treeview_stok(stok_tree, kartu)
                             
    tk.Button(filter_frame, text=_("stok.btn_tampilkan"), command=tampilkan_kartu_stok).grid(row=0, column=6, padx=10)

def build_section_ringkasan_stok(parent):
    """Build stock summary section within notebook container.

    Args:
        parent (ttk.Notebook): Parent Notebook container.
    """
    tab_ringkasan = ttk.Frame(parent)
    parent.add(tab_ringkasan, text=_("stok.tab_ringkasan"))

    frame_ringkasan = tk.Frame(tab_ringkasan)
    frame_ringkasan.pack(pady=10)

    tk.Label(frame_ringkasan, text=_("stok.tanggal_frame")).grid(row=0, column=0)
    tanggal_entry = tk.Entry(frame_ringkasan)
    tanggal_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
    tanggal_entry.grid(row=0, column=1)

    tree_ringkasan = build_treeview_ringkasan(tab_ringkasan)
    tree_ringkasan.pack(fill="both", expand=True)

    def tampilkan_ringkasan():
        """Trigger daily stock update visualization for current month/year."""
        bulan = datetime.now().month
        tahun = datetime.now().year
        tampilkan_stok_harian(tree_ringkasan, bulan, tahun)

    def tampilkan_log_harian(treeview, tanggal):
        """Open modal window displaying detailed daily stock transaction logs.

        Args:
            treeview (ttk.Treeview): Source Treeview table.
            tanggal (str): Date string filter formatted as 'YYYY-MM-DD'.
        """
        selected = treeview.focus()
        if not selected:
            messagebox.showinfo(_("stok.box_info"), _("stok.pilih_produk"))
            return
        values = treeview.item(selected)["values"]
        produk_id = values[0]

        conn = get_connection()
        cursor = conn.cursor()
        logs = cek_log_harian(cursor, produk_id, tanggal)
        conn.close()

        if not logs:
            messagebox.showinfo(_("stok.box_info"), (_("stok.tidak_ada_log")))
            return
    
        window = tk.Toplevel(treeview)
        window.title(f"Log Stok Produk #{produk_id} - {tanggal}")
        tree_log = ttk.Treeview(window, columns=(_("stok.waktu"), _("stok.awal")
                                                 , _("stok.akhir"), _("stok.jenis")), show="headings")
        for col in tree_log["columns"]:
            tree_log.heading(col, text=col)
            tree_log.column(col, anchor="center", width=100)
        tree_log.pack(fill="both", expand=True)

        for row in logs:
            tree_log.insert("", "end", values=row)
    
    tk.Button(frame_ringkasan, text=_("stok.btn_tampilkan_ringkasan")
              , command=tampilkan_ringkasan).grid(row=0, column=2, padx=10)
    tk.Button(frame_ringkasan, text=_("stok.btn_log_harian")
              , command=lambda: tampilkan_log_harian(tree_ringkasan, tanggal_entry.get()
                                                     .strip())).grid(row=0, column=3, padx=10)

def tampilkan_stok_harian(treeview, bulan, tahun):
    """Fetch monthly stock logs from database and insert aggregated daily stock summary.

    Args:
        treeview (ttk.Treeview): Target Treeview instance.
        bulan (int): Target month index (1-12).
        tahun (int): Target year.
    """
    conn = get_connection()
    cursor = conn.cursor()
    produk_list = semua_produk()
    
    treeview.delete(*treeview.get_children())

    hari_ini = datetime.now().day

    for produk in produk_list:
        produk_id = produk["id_produk"]
        nama = produk["nama_produk"]
        logs = ambil_log_stok_bulanan(cursor, produk_id, bulan, tahun)
        stok_harian = proses_stok_harian(logs, bulan, tahun)

        if str(hari_ini) in stok_harian:
            row = stok_harian[str(hari_ini)]
            awal = row["awal"] if row["awal"] is not None else 0
            akhir = row["akhir"] if row["akhir"] is not None else 0
        else:
            awal = akhir = 0
        
        treeview.insert("", "end", values=(produk_id, nama, f"{awal:,}", f"{akhir:,}"))
    
    conn.close()

if __name__ == "__main__":
    buat_frame_stok()