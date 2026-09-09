# Third-party
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

# Local Application
from app.core.supplier_core import semua_supplier, tambah_supplier, edit_supplier, hapus_supplier
from app.translator import _, i18n

def buat_frame_supplier(parent, set_judul_modul):
    """Construct main UI layout frame and controls for the supplier module.

    Args:
        parent (tk.Tk): Parent Tkinter container.
        set_judul_modul (Callable[[str], None]): Callback function to update title bar text.
    """
    frame = tk.Frame(parent, bg="#f4f4f4")

    frame_top = tk.Frame(frame, bg="#f4f4f4")
    frame_top.pack(pady=10)

    frame_treeview = tk.Frame(frame, bg="#f4f4f4")
    frame_treeview.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(frame_treeview, columns=("id", "nama", "alamat", "no_hp"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("nama", text=_("supplier.nama_supplier"))
    tree.heading("alamat", text=_("supplier.alamat"))
    tree.heading("no_hp", text=_("supplier.no_hp"))
    tree.column("id", width=50)
    tree.column("nama", width=200)
    tree.column("alamat", width=250)
    tree.column("no_hp", width=150)

    scroll_y = ttk.Scrollbar(frame_treeview, orient="vertical", command=tree.yview)
    scroll_x = ttk.Scrollbar(frame_treeview, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    tk.Button(frame_top, text=_("supplier.btn_tambah"), command=lambda: buka_form_tambah_supplier(tree, frame)).pack(side="left", padx=5)
    tk.Button(frame_top, text=_("supplier.btn_import"), command= lambda: import_supplier_excel(tree)).pack(side="left", padx=5)

    tk.Label(frame_top, text=_("supplier.lbl_cari_nama")).pack(side="left", padx=5)
    entry_nama = tk.Entry(frame_top)
    entry_nama.pack(side="left", padx=5)
    tk.Button(frame_top, text=_("supplier.lbl_cari"), command=lambda: filter_supplier(tree, entry_nama)).pack(side="left", padx=5)
    tk.Button(frame_top, text="Reset", command=lambda: refresh_tree(tree)).pack(side="left", padx=5)

    tree.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")

    frame_treeview.grid_rowconfigure(0, weight=1)
    frame_treeview.grid_columnconfigure(0, weight=1)

    frame_bottom = tk.Frame(frame, bg="#f4f4f4")
    frame_bottom.pack(pady=10)

    tk.Button(frame_bottom, text=_("supplier.btn_hapus"), command=lambda: hapus_supplier_gui(tree)).pack(side="left", padx=5)
    tk.Button(frame_bottom, text=_("supplier.btn_edit"), command=lambda: buka_form_edit_supplier(tree, frame)).pack(side="left", padx=5)

    refresh_tree(tree)
    frame.pack(fill="both", expand=True)

    set_judul_modul(_("supplier.set_judul_modul"))

def import_supplier_excel(tree):
    """Parse supplier records from an Excel or CSV file and insert into the database.

    Args:
        tree (ttk.Treeview): Target Treeview instance to refresh after import.
    """
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.csv")])
    if not file_path:
        return
    try:
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)

        required_columns = {"Nama Supplier", "Alamat", "No HP"}
        if not required_columns.issubset(df.columns):
            messagebox.showerror("supplier.err_format", f"Madatory column: {', '.join(required_columns)}")
            return
        count = 0
        for _, row in df.iterrows():
            try:
                data = {
                    "nama_supplier": row["Nama Supplier"],
                    "alamat": row["Alamat"],
                    "no_hp": row["No HP"],
                    "kode_supplier": None
                }
                tambah_supplier(data)
                count += 1
            except Exception as e:
                print("[ERROR] Failed to add supplier:", row["Nama Supplier"], "-", e)
        
        messagebox.showinfo("[ERROR] Import failed:", f"{count} Supplier successfully added.")
        refresh_tree(tree)
    except Exception as e:
        print("[ERROR] Import failed:", e)
        messagebox.showerror("Import Failed", str(e))

def refresh_tree(tree):
    """Fetch all suppliers from database and populate Treeview rows.

    Args:
        tree (ttk.Treeview): Target Treeview table to clear and repopulate.
    """
    tree.delete(*tree.get_children())
    for s in semua_supplier():
        tree.insert("", tk.END, values=(s["id_supplier"], s["nama_supplier"], s["alamat"], s["no_hp"]))

def buka_form_tambah_supplier(tree, parent):
    """Launch a pop-up Toplevel dialog for creating new supplier records.

    Args:
        tree (ttk.Treeview): Target Treeview instance to refresh after saving.
        parent (tk.Widget): Parent Tkinter window container.
    """
    form = tk.Toplevel(parent)
    form.title(_("supplier.form_title"))
    form.geometry("300x300")

    labels = [_("supplier.nama"), _("supplier.alamat"), _("supplier.no_hp")]
    entries = []

    for i, label in enumerate(labels):
        tk.Label(form, text=label).grid(row=i, column=0, padx=20, pady=5, sticky="e")
        entry = tk.Entry(form)
        entry.grid(row=i, column=1, padx=20, pady=5, sticky="w")
        entries.append(entry)
    
    def simpan():
        """Save new supplier entry to database."""
        nama = entries[0].get().strip()
        alamat = entries[1].get().strip()
        no_hp = entries[2].get().strip()

        if not nama:
            messagebox.showerror("Error", _("supplier.err_nama_supplier"))
            return
        
        data = {"nama_supplier": nama,
                "alamat": alamat,
                "no_hp": no_hp}
        tambah_supplier(data)
        messagebox.showinfo(_("supplier.berhasil"), f"Supplier '{nama}' added.")
        form.destroy()
        refresh_tree(tree)
    tk.Button(form, text=_("supplier.simpan"), command=simpan).grid(row=3, column=0, columnspan=2, pady=20)

def hapus_supplier_gui(tree):
    """Delete selected supplier row in Treeview from database.

    Args:
        tree (ttk.Treeview): Source Treeview table.
    """
    selected = tree.selection()
    if not selected:
        messagebox.showwarning(_("supplier.pilih_supplier"), _("supplier.warr_pilih_supplier"))
        return

    supplier_id = tree.item(selected[0])["values"][0]
    hapus_supplier(supplier_id)
    messagebox.showinfo(_("supplier.berhasil"), _("supplier.info_berhasil"))
    refresh_tree(tree)

def buka_form_edit_supplier(tree, parent):
    """Launch a pop-up Toplevel dialog for editing selected supplier details.

    Args:
        tree (ttk.Treeview): Source Treeview containing selected supplier record.
        parent (tk.Widget): Parent Tkinter window container.
    """
    selected = tree.selection()
    if not selected:
        messagebox.showwarning(_("supplier.pilih_supplier"), _("supplier.warr_pilih_supplier"))
        return

    values = tree.item(selected[0])["values"]
    id_supplier, nama_awal, alamat_awal, no_hp_awal = values[:4]

    form = tk.Toplevel(parent)
    form.title(_("supplier.form_edit"))
    form.geometry("300x300")

    labels = [_("supplier.nama"), _("supplier.alamat"), _("supplier.no_hp")]
    entries = []

    for i, (label, value) in enumerate(zip(labels, [nama_awal, alamat_awal, no_hp_awal])):
        tk.Label(form, text=label).grid(row=i, column=0, padx=20, pady=5, sticky="e")
        entry = tk.Entry(form)
        entry.insert(0, value)
        entry.grid(row=i, column=1, padx=20, pady=5, sticky="w")
        entries.append(entry)
    
    def simpan():
        """Save updated supplier data to database."""
        nama = entries[0].get().strip()
        alamat = entries[1].get().strip()
        no_hp = entries[2].get().strip()

        if not nama:
            messagebox.showerror("Error", _("supplier.err_nama_supplier"))
            return
        
        data = {
            "nama_supplier": nama,
            "alamat": alamat,
            "no_hp": no_hp
        }
        edit_supplier(id_supplier, data)
        messagebox.showinfo(_("supplier.berhasil"), f"Supplier '{nama}' successfully updated.")
        refresh_tree(tree)
        form.destroy()
    
    tk.Button(form, text=_("supplier.btn_simpan"), command=simpan).grid(row=3, column=0, columnspan=2, pady=20)

def filter_supplier(tree, entry_nama):
    """Filter Treeview rows by searching supplier name keyword.

    Args:
        tree (ttk.Treeview): Target Treeview table to display results.
        entry_nama (tk.Entry): Entry widget containing user search keyword.
    """
    keyword = entry_nama.get().strip().lower()
    tree.delete(*tree.get_children())
    for s in semua_supplier():
        if keyword in s["nama_supplier"].lower():
            row_values = list(s.values())
            tree.insert("", tk.END, values=row_values)

if __name__ == "__main__":
    buat_frame_supplier()