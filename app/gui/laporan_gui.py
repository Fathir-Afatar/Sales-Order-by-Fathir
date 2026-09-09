# Third-party
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Local application
from app.core.laporan_core import get_ringkasan_laporan, get_histori_transaksi, get_nama_supplier, get_ringkasan_member
from app.translator import _, i18n

def buat_frame_laporan(parent, set_judul_modul):
    """Build and render the comprehensive reporting interface frame.

    Constructs a multi-tab view containing summary cards, date-range filters, and
    data treeviews for sales, purchases, operational expenses, and customer
    member metrics.

    Args:
        parent (tk.Widget): The parent Tkinter container frame.
        set_judul_modul (Callable[[str], None]): Callback function to update the
            active module title label in the parent layout.
    """
    set_judul_modul(_("laporan.set_judul_modul"))

    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True)

    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True)

    tab_laporan = ttk.Frame(notebook)
    tab_penjualan = ttk.Frame(notebook)
    tab_pembelian = ttk.Frame(notebook)
    tab_pengeluaran = ttk.Frame(notebook)
    tab_member = ttk.Frame(notebook)

    notebook.add(tab_laporan, text=_("laporan.tab_laporan"))
    notebook.add(tab_penjualan, text=_("laporan.tab_penjualan"))
    notebook.add(tab_pembelian, text=_("laporan.tab_pembelian"))
    notebook.add(tab_pengeluaran, text=_("laporan.tab_pengeluaran"))
    notebook.add(tab_member, text=_("laporan.tab_member"))

    entry_awal, entry_akhir = build_filter_area(tab_laporan)

    label_penjualan = build_panel(tab_laporan, _("laporan.tab_penjualan"), lambda: notebook.select(tab_penjualan))
    label_pembelian = build_panel(tab_laporan, _("laporan.tab_pembelian"), lambda: notebook.select(tab_pembelian))
    label_pengeluaran = build_panel(tab_laporan, _("laporan.tab_pengeluaran"), lambda: notebook.select(tab_pengeluaran))

    tree_penjualan = build_treeview_with_scroll(tab_penjualan, [_("laporan.tanggal"), _("laporan.total")])
    tree_pembelian = build_treeview_with_scroll(tab_pembelian, [_("laporan.tanggal"), _("laporan.supplier"), _("laporan.total")])
    tree_pengeluaran = build_treeview_with_scroll(tab_pengeluaran, [_("laporan.tanggal"), _("laporan.kategori"), _("laporan.nominal"), _("laporan.keterangan")])
    tree_member = build_treeview_with_scroll(tab_member, [_("laporan.nama"), _("laporan.total_belanja"), _("laporan.kontribusi"), _("laporan.frekuensi")])

    def tampilkan_ringkasan():
        """Fetch report data for the given date range and populate UI elements."""
        awal = entry_awal.get().strip()
        akhir = entry_akhir.get().strip()
        try:
            data= get_ringkasan_laporan(awal, akhir)
            total_penjualan_str = f"{int(data['penjualan']):,}"
            total_pembelian_str = f"{int(data['pembelian']):,}"
            total_pengeluaran_str = f"{int(data['pengeluaran']):,}"

            label_penjualan.config(text=_("laporan.lbl_total_penjualan").format(total=total_penjualan_str))
            label_pembelian.config(text=_("laporan.lbl_total_pembelian").format(total=total_pembelian_str))
            label_pengeluaran.config(text=_("laporan.lbl_total_pengeluaran").format(total=total_pengeluaran_str))
        except Exception as e:
            print(_("laporan.err_laporan"), e)
        
        hist_penjualan = get_histori_transaksi("penjualan", awal, akhir)
        hist_pembelian = get_histori_transaksi("pembelian", awal, akhir)
        hist_pengeluaran = get_histori_transaksi("pengeluaran", awal, akhir)
        data_member = get_ringkasan_member(awal, akhir)

        def format_rupiah(nilai):
            """Format a numerical value as a Indonesian Rupiah currency string.

            Args:
                nilai (Union[int, float, str]): Numeric value to format.

            Returns:
                str: Formatted currency string (e.g., 'Rp 10.000').
            """
            return f"Rp {int(nilai):,}".replace(".", ",")

        for tree in [tree_penjualan, tree_pembelian, tree_pengeluaran]:
            for item in tree.get_children():
                tree.delete(item)
        for item in tree_member.get_children():
            tree_member.delete(item)
        
        for row in hist_penjualan:
            total = format_rupiah(row["total_harga"])
            tanggal = row["tanggal"].split(" ")[0]
            tree_penjualan.insert("", "end", values=(tanggal, total))
        
        for row in hist_pembelian:
            supplier_nama = get_nama_supplier(row["supplier_id"])
            total = format_rupiah(row["total_harga"])
            tree_pembelian.insert("", "end", values=(row["tanggal"], supplier_nama, total))
        
        for row in hist_pengeluaran:
            total = format_rupiah(row["nominal"])
            tree_pengeluaran.insert("", "end", values=(row["tanggal"], row["kategori"], total, row["keterangan"]))

        for row in data_member:
            tree_member.insert("", "end", values=(row["nama"], format_rupiah(row["total_belanja"]), format_rupiah(row["kontribusi"]), row["frekuensi"]))

    filter_frame = entry_awal.master
    tk.Button(filter_frame, text=_("laporan.filter_frame"), command=tampilkan_ringkasan).grid(row=0, column=4, padx=10)

    notebook.select(tab_laporan)

def build_filter_area(parent):
    """Construct date filtering input components with default start/end dates.

    Args:
        parent (tk.Widget): The parent container widget.

    Returns:
        Tuple[tk.Entry, tk.Entry]: Pair containing the start-date entry and
        end-date entry inputs.
    """
    frame = tk.Frame(parent, bg="#f4f4f4")
    frame.pack(pady=10)

    tk.Label(frame, text=_("laporan.tanggal_awal"), bg="#f4f4f4").grid(row=0, column=0)
    entry_awal = tk.Entry(frame)
    entry_awal.insert(0, datetime.now().strftime("%Y-%m-01"))
    entry_awal.grid(row=0, column=1)

    tk.Label(frame, text=_("laporan.tanggal_akhir"), bg="#f4f4f4").grid(row=0, column=2)
    entry_akhir = tk.Entry(frame)
    entry_akhir.insert(0, datetime.now().strftime("%Y-%m-%d"))
    entry_akhir.grid(row=0, column=3)

    return entry_awal, entry_akhir

def build_panel(parent, judul, command):
    """Create a summary card frame displaying totals and a detail button.

    Args:
        parent (tk.Widget): The parent container widget.
        judul (str): The summary title text for the card.
        command (Callable[[], None]): Callback triggered when clicking the detail
            button.

    Returns:
        tk.Label: The dynamic total label component inside the panel.
    """
    panel = tk.LabelFrame(parent, text=judul, padx=10, pady=10, bg="#f4f4f4")
    panel.pack(fill="x", padx=20, pady=5)

    label = tk.Label(panel, text=f"Total {judul}: Rp 0", font=("Segoe UI", 10, "bold"), bg="#f4f4f4")
    label.pack(side="left")

    tk.Button(panel, text=_("laporan.btn_show_detail"), command=command).pack(side="right")

    return label

def build_treeview_with_scroll(parent, kolom):
    """Construct a scrollable Treeview widget for displaying tabular data.

    Args:
        parent (tk.Widget): The parent container widget.
        kolom (List[str]): Header titles for the table columns.

    Returns:
        ttk.Treeview: Configured Treeview instance with attached vertical
        scrollbar.
    """
    container = tk.Frame(parent)
    container.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar_y = tk.Scrollbar(container, orient="vertical")
    scrollbar_y.pack(side="right", fill="y")

    tree = ttk.Treeview(container, columns=kolom, show="headings", yscrollcommand=scrollbar_y.set)
    for col in kolom:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")
    tree.pack(fill="both", expand=True)

    scrollbar_y.config(command=tree.yview)
    return tree

if __name__ == "__main__":
    buat_frame_laporan()
