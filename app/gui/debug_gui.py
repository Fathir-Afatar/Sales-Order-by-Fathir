# Third party
import tkinter as tk
from tkinter import ttk

# Local application
from app.core.debug_core import ambil_log_terakhir
from app.core.debug_core import cek_status_database, cek_status_printer
from app.core.pengaturan_core import simulasi_cetak_nota
from app.translator import _

def buka_debug_gui(parent, set_judul_modul):
    """Build and display the debug and system diagnostic interface frame.

    Constructs a tabbed interface containing options to inspect runtime application
    logs, verify SQLite database health, check USB printer status, and run
    simulations for receipt printing workflows.

    Args:
        parent (tk.Widget): The parent Tkinter container frame.
        set_judul_modul (Callable[[str], None]): Callback function to update the
            active module title label in the parent layout.

    Returns:
        tk.Frame: The main outer container frame holding the debug interface.
    """
    set_judul_modul(_("debug.app_title"))
    frame = tk.Frame(parent, bg="#f4f4f4")
    frame.pack(fill="both", expand=True)

    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Tab Log
    tab_log = tk.Frame(notebook, bg="#f4f4f4")
    notebook.add(tab_log, text= _("debug.tab_log"))

    tab_status = tk.Frame(notebook, bg="#f4f4f4")
    notebook.add(tab_status, text= _("debug.tab_sistem"))

    tab_tes = tk.Frame(notebook, bg="#f4f4f4")
    notebook.add(tab_tes, text= _("debug.tab_tes"))

    status_label = tk.Label(tab_status, text="debug.status_label", bg="#f4f4f4")
    status_label.pack(anchor="w", padx=10, pady=5)

    status_area = tk.Text(tab_status, height=10, bg="#f4f4f4", font=("Courier", 10))
    status_area.pack(fill="x", padx=10)

    log_area = tk.Text(tab_log, bg="#ffffff", font=("Courier", 10))
    log_area.pack(fill="both", expand=True, padx=10, pady=10)

    printer_label = tk.Label(tab_status, text= _("debug.printer_label"), bg="#f4f4f4")
    printer_label.pack(anchor="w", padx=10, pady=5)

    printer_area = tk.Text(tab_status, height=5, bg="#f4f4f4", font=("Courier", 10))
    printer_area.pack(fill="x", padx=10)

    def refresh_printer():
        """Fetch and display the latest application log entries."""
        status = cek_status_printer()
        printer_area.delete("1.0", "end")
        for k, v in status.items():
            printer_area.insert("end", f"{k}: {v}\n")

    def refresh_log():
        """Query USB hardware and display the current printer status key-value pairs."""
        log_area.delete("1.0", "end")
        for line in ambil_log_terakhir():
            log_area.insert("end", line)

    def refresh_status():
        """Query SQLite database health and display table status key-value pairs."""
        status = cek_status_database()
        status_area.delete("1.0", "end")
        for k, v in status.items():
            status_area.insert("end", f"{k}: {v}\n")
    
    tk.Button(tab_status, text=_("debug.btn_tab_status"), command=refresh_status).pack(pady=5)
    refresh_status()

    tk.Button(tab_log, text=_("debug.btn_tab_log"), command=refresh_log).pack(pady=5)

    tk.Button(tab_status, text=_("debug.btn_tab_status_printer"), command=refresh_printer).pack(pady=5)
    refresh_printer()

    tk.Label(tab_tes, text=_("debug.btn_tab_test"), bg="#f4f4f4").pack(pady=5)
    entry_id = tk.Entry(tab_tes)
    entry_id.pack(pady=5)

    hasil_simulasi = tk.Text(tab_tes, height=6, bg="#f4f4f4", font=("Courier", 10))
    hasil_simulasi.pack(fill="x", padx=10, pady=5)

    def jalankan_simulasi():
        """Validate transaction ID input and run the print simulation workflow."""
        transaksi_id = entry_id.get().strip()
        if not transaksi_id.isdigit():
            hasil_simulasi.delete("1.0", "end")
            hasil_simulasi.insert("end", _("debug.err_id_angka") + "\n")
            return
        hasil = simulasi_cetak_nota(int(transaksi_id))
        hasil_simulasi.delete("1.0", "end")
        for k, v in hasil.items():
            hasil_simulasi.insert("end", f"{k}: {v}\n")
    
    tk.Button(tab_tes, text= _("debug.btn_test_simulasi"), command=jalankan_simulasi).pack(pady=5)
    