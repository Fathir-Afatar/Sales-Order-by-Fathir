# Third-party
import tkinter as tk
import pandas as pd
from tkinter import ttk, messagebox, filedialog

# Local Application
from app.core.member_core import tambah_member, semua_member, update_member, hapus_member
from app.translator import _, i18n

def refresh_tree():
    """Refresh and repopulate the member Treeview widget with current data."""
    tree.delete(*tree.get_children())
    for row in semua_member():
        tree.insert("", tk.END, iid=row["id_member"], values=(
            row["id_member"],row["kode_member"], row["nama"], row["no_hp"], row["alamat"], row["tipe"], row["ranting"]
        ))

        print(f"[DEBUG] tree inserted: ID = {row['id_member']}, values ={(row['kode_member'], row['nama'], row['no_hp'], row['alamat'], row['tipe'], row['ranting'])}")

def update_filter_dropdowns():
    """Extract distinct member types and branch categories to refresh filter dropdowns."""
    all_member = semua_member()
    tipe_values = sorted(set([
        d["tipe"] for d in all_member
        if d.get("tipe") not in [None, ""]
    ]))
    if not tipe_values:
        tipe_values = ["(Tidak ada data)"]

    ranting_values = sorted(set([
        d["ranting"] for d in all_member
        if d.get("ranting") not in [None, ""]
    ]))
    if not ranting_values:
        ranting_values = ["(Tidak ada data)"]
    combo_tipe['values'] = tipe_values
    combo_ranting['values'] = ranting_values


def tambah_member_gui():
    """Launch a top-level popup dialog to manually register a new member."""
    popup = tk.Toplevel()
    popup.title(_("member.pop_title"))
    popup.geometry("400x400")
    frame_form = tk.Frame(popup)
    frame_form.pack(padx=10, pady=10)

    def create_entry(label):
        """Create and pack a labeled entry field inside the form frame.

        Args:
            label (str): Text description for the input field label.

        Returns:
            tk.Entry: Configured entry widget.
        """
        tk.Label(frame_form, text=label).pack(anchor='w')
        entry = tk.Entry(frame_form)
        entry.pack(fill='x')
        return entry
    
    entry_kode_member = create_entry(_("member.entry_kode"))
    entry_nama = create_entry(_("member.entry_nama"))
    entry_nomor = create_entry(_("member.entry_no_hp"))
    entry_alamat = create_entry(_("member.entry_alamat"))
    entry_tipe = create_entry(_("member.entry_tipe"))
    entry_ranting = create_entry(_("member.entry_ranting"))

    entries = [entry_nama, entry_nomor, entry_alamat, entry_tipe, entry_ranting, entry_kode_member]

    def simpan_member():
        """Extract entry values, persist the new member, and refresh UI components."""
        nama = entry_nama.get()
        alamat = entry_alamat.get()
        nomor = entry_nomor.get()
        tipe = entry_tipe.get()
        ranting = entry_ranting.get()
        kode_member = entry_kode_member.get()
    
        try:
            tambah_member(nama=nama, alamat=alamat, nomor=nomor, tipe=tipe, ranting=ranting, kode_member=kode_member)
            messagebox.showinfo(_("member.berhasil"), f"Member '{nama}' successfully added.")
            for entry in entries: entry.delete(0, tk.END)
            refresh_tree()
            update_filter_dropdowns()
        except Exception as e:
            messagebox.showerror(_("member.gagal"), str(e))

    tk.Button(popup, text=_("member.simpan"), command=simpan_member).pack(pady=10)

def import_member_excel():
    """Import member records from an external Excel (.xlsx) or CSV file."""
    filepath = filedialog.askopenfilename(
        title=(("member.title_pilih")),
        filetypes=[("Excel Files", "*.xlsx *.csv")]
    )
    if not filepath:
        return
    try:
        if filepath.endswith(".xlsx"):
            df = pd.read_excel(filepath)
        else:
            df = pd.read_csv(filepath)
        required_columns = {"Kode Member", "Nama", "Nomor HP", "Tipe Member", "Ranting"}
        if not required_columns.issubset(df.columns):
            messagebox.showerror(_("member.err_kolom"), f"Mandatory column: {', '.join(required_columns)}")
            return
        count = 0
        for _, row in df.iterrows():
            try:
                tambah_member(
                    nama = row["Nama"],
                    nomor=row["Nomor HP"],
                    alamat=row["Alamat"],
                    tipe=row["Tipe Member"],
                    ranting = row["Ranting"],
                    kode_member=row["Kode Member"]

                )
                count += 1
            except Exception as e:
                print("[ERROR] Failed to add:", row["Nama"], "-", e)
        
        messagebox.showinfo("Import Complete", f"{count} Member successfully added.")
        refresh_tree()
        update_filter_dropdowns()

    except Exception as e:
        print("[ERROR] Import failed:", e)
        messagebox.showerror("Import Failed", str(e))

def on_tree_select(event):
    """Handle the Treeview selection event and populate mapped form input fields.

    Args:
        event (tk.Event): Tkinter selection event instance.
    """
    global selected_id
    selected_id = tree.focus()
    values = tree.item(selected_id)["values"]

    if not selected_id:
        return
    column_order = ["kode_member", "nama", "no_hp", "alamat", "tipe", "ranting"]

    for i, col in enumerate(column_order):
        if col in entry_map:
            entry_map[col].delete(0, tk.END)
            if i < len(values):
                entry_map[col].insert(0, values[i])

def edit_member_gui(parent):
    """Launch a top-level popup dialog to modify selected member details.

    Args:
        parent (tk.Widget): Parent container widget for the popup modal.
    """
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning(_("member.warning_pilih"))
        return
    values = tree.item(selected_item)["values"]
    if not values or len(values) < 6:
        return

    popup = tk.Toplevel(parent)
    popup.title(_("member.pop_edit"))
    popup.geometry("400x400")

    def create_entry(label, value):
        """Create a pre-filled entry input widget inside the popup dialog.

        Args:
            label (str): Label string describing the entry purpose.
            value (Any): Initial value to insert into the input field.

        Returns:
            tk.Entry: Populated entry widget instance.
        """
        tk.Label(popup, text=label).pack(anchor='w')
        entry = tk.Entry(popup)
        entry.insert(0, value)
        entry.pack(fill='x')
        return entry
    
    entry_kode_member = create_entry(_("member.entry_kode"), values[1])
    entry_nama = create_entry(_("member.entry_nama"), values[2])
    entry_nomor = create_entry(_("member.entry_no_hp"), values[3])
    entry_alamat = create_entry(_("member.entry_alamat"), values[4])
    entry_tipe = create_entry(_("member.entry_alamat"), values[5])
    entry_ranting = create_entry(_("member.entry_ranting"), values[6])

    def simpan_perubahan():
        """Save modified member details to the database and close the modal."""
        try:
            update_member(selected_item,
                          entry_nama.get(),
                          entry_nomor.get(),
                          entry_alamat.get(),
                          entry_tipe.get(),
                          entry_ranting.get(),
                          entry_kode_member.get()
            )
            messagebox.showinfo(_("member.msg_sukses"), _("member.msg_perbarui"))
            refresh_tree()
            popup.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(popup, text=_("member.btn_simpan"), command=simpan_perubahan).pack(pady=5)
    tk.Button(popup, text=_("member.batal"), command=popup.destroy).pack()

def hapus_member_gui():
    """Delete the currently selected member record following user confirmation."""
    if not selected_id:
        messagebox.showwarning(_("member.warr_pilih_member"))
        return
    if messagebox.askyesno(_("member.msg_hapus"), _("member.msg_ask_yesno")):
        try:
            hapus_member(selected_id)
            messagebox.showinfo("Info", _("member.msg_berhasil_hapus"))
            refresh_tree()
        except Exception as e:
            messagebox.showerror(_("member.err_gagal_hapus"), str(e))

def buat_frame_member(parent, set_judul_modul):
    """Build and render the main member management module interface.

    Constructs the member toolbar, dynamic category filter controls, search input
    area, data grid treeview, and action buttons for editing/deleting records.

    Args:
        parent (tk.Widget): The parent Tkinter container frame.
        set_judul_modul (Callable[[str], None]): Callback function to update the
            active module title label in the application shell.
    """
    global window, entry_map, entry_nama, entry_nomor, entry_alamat, entry_tipe, entry_ranting 
    global tree, entries, selected_id, entry_kode_member
    global entry_search, combo_tipe, combo_ranting
    entry_map = {}
    selected_id = None
    frame = tk.Frame(parent, bg="#f4f4f4")

    build_header(frame)
    build_filter_area(frame)
    build_search_area(frame)
    build_treeview(frame)
    build_footer(frame)

    refresh_tree()
    frame.pack(fill="both", expand=True)

    set_judul_modul(_("member.set_judul_modul"))

def build_header(frame):
    """Construct the top action header containing creation and import buttons.

    Args:
        frame (tk.Frame): Parent container frame.
    """
    frame_header = tk.Frame(frame, bg="#f4f4f4")
    frame_header.pack(pady=10)
    tk.Button(frame_header, text=_("member.btn_tambah"), command=tambah_member_gui).pack(side=tk.LEFT, padx=6)
    tk.Button(frame_header, text=_("member.btn_import"), command=import_member_excel).pack(side=tk.LEFT, padx=6)

def build_filter_area(frame):
    """Construct the dropdown filtering bar for member type and branch categories.

    Args:
        frame (tk.Frame): Parent container frame.
    """
    global combo_tipe, combo_ranting
        
    frame_filter = tk.Frame(frame, bg="#f4f4f4")
    frame_filter.pack(pady=10)

    all_member = semua_member()

    tipe_values = sorted(set([d["tipe"] for d in all_member if d.get("tipe") not in [None, ""]]))
    if not tipe_values: tipe_values = ["(Tidak ada data)"]

    ranting_values = sorted(set([
        d["ranting"] for d in all_member 
        if d.get("ranting") not in [None, ""]
        ]))
    if not ranting_values: ranting_values = ["(Tidak ada data)"]

    tk.Label(frame_filter, text=_("member.lbl_filter_tipe")).pack(side='left')
    combo_tipe = ttk.Combobox(frame_filter, values=tipe_values)
    combo_tipe.pack(side='left', padx=5)

    tk.Label(frame_filter, text=_("member.lbl_filter_ranting")).pack(side='left')
    combo_ranting = ttk.Combobox(frame_filter, values=ranting_values)
    combo_ranting.pack(side='left', padx=5)

    def reset_filter():
        """Clear combobox selections and reset the treeview to display all records."""
        combo_tipe.set("")
        combo_ranting.set("")
        refresh_tree()

    def filter_data():
        """Filter member records based on selected type and branch criteria."""
        tipe_selected = combo_tipe.get()
        ranting_selected = combo_ranting.get()
        hasil = [d for d in all_member if
                (tipe_selected == '' or d["tipe"] == tipe_selected) and
                (ranting_selected == '' or d["ranting"] == ranting_selected)]
        
        tree.delete(*tree.get_children())
        for row in hasil:
            tree.insert("", tk.END, iid=row["id_member"], values=(row["id_member"],
                row["kode_member"], row["nama"], row["no_hp"], row["alamat"], row["tipe"], row["ranting"]
            ))

    tk.Button(frame_filter, text=_("member.btn_reset"), command=reset_filter).pack(side=tk.LEFT, padx=4)        
    tk.Button(frame_filter, text="Filter", command=filter_data).pack(side='left', padx=5)

def build_search_area(frame):
    """Construct the keyword search panel for querying member records.

    Args:
        frame (tk.Frame): Parent container frame.
    """
    global entry_search

    frame_search = tk.Frame(frame, bg="#f4f4f4")
    frame_search.pack(pady=5)

    tk.Label(frame_search, text=_("member.lbl_search"), bg="#f4f4f4").pack(side=tk.LEFT)
    entry_search = tk.Entry(frame_search, width=30)
    entry_search.pack(side=tk.LEFT, padx=4)

    def cari_member_gui():
        """Execute keyword search and update the treeview with matching results."""
        keyword = entry_search.get()
        if not keyword.strip():
            messagebox.showwarning(_("member.warr_kosong"), _("member.warr_kata_kunci"))
            return
        from app.core.member_core import cari_member
        hasil = cari_member(keyword)
        tree.delete(*tree.get_children())
        for row in hasil:
            tree.insert("", tk.END, iid=row["id_member"], values=(row["id_member"],
                row["kode_member"], row["nama"], row["no_hp"], row["alamat"], row["tipe"], row["ranting"] 
            ))

    tk.Button(frame_search, text=_("member.cari"), command=lambda: cari_member_gui()).pack(side=tk.LEFT, padx=4)

def build_treeview(frame):
    """Construct the scrollable Treeview table displaying member data rows.

    Args:
        frame (tk.Frame): Parent container frame.
    """
    global tree
   
    columns = ("id_member", "kode_member", "nama", "no_hp", "alamat", "tipe", "ranting", )
    column_labels = {
        "id_member": "ID",
        "kode_member": _("member.entry_kode"),
        "nama": _("member.entry_nama"),
        "no_hp": _("member.entry_no_hp"),
        "alamat": _("member.entry_alamat"),
        "tipe": _("member.entry_tipe"),
        "ranting": _("member.entry_ranting"),

    }
    frame_treeview = tk.Frame(frame)
    frame_treeview.pack(fill="both", expand=True, padx=10, pady=10)    
    frame_treeview.grid_rowconfigure(0, weight=1)
    frame_treeview.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(frame_treeview, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=column_labels[col])
        tree.column(col, width=130) 
    
    scroll_y = ttk.Scrollbar(frame_treeview, orient="vertical", command=tree.yview)
    scroll_x = ttk.Scrollbar(frame_treeview, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)  
    
    tree.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")

    tree.bind("<<TreeviewSelect>>", on_tree_select)

def build_footer(frame):
    """Construct the bottom control bar containing edit and delete buttons.

    Args:
        frame (tk.Frame): Parent container frame.
    """
    frame_footer = tk.Frame(frame, bg="#f4f4f4")
    frame_footer.pack(pady=10)

    tk.Button(frame_footer, text=_("member.btn_edit"), command=lambda: edit_member_gui(frame)).pack(side=tk.LEFT, padx=8)
    tk.Button(frame_footer, text=_("member.btn_hapus"), command=hapus_member_gui).pack(side=tk.LEFT, padx=8)

    refresh_tree()
    frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    buat_frame_member()


#python -m app.gui.member_gui
