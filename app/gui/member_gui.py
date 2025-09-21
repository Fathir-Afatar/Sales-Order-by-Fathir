import tkinter as tk
from tkinter import ttk, messagebox
from app.core.member_core import tambah_member, semua_member, update_member, hapus_member


def refresh_tree():
    print("[DEBUG] refresh_tree dipangil")
    print("[DEBUG] refresh_tree aktif oleh", __name__)
    tree.delete(*tree.get_children())
    for m in semua_member():
        tree.insert("", tk.END, iid=m["id_member"], values=(
            m["id_member"],m["kode_member"], m["nama"], m["no_hp"], m["alamat"], m["tipe"], m["ranting"]
        ))
    print(f"[DEBUG] tree inserted: ID = {m['id_member']}, values ={(m['kode_member'], m['nama'], m['no_hp'], m['alamat'], m['tipe'], m['ranting'])}")

def update_filter_dropdowns():
    all_member = semua_member()
    tipe_values = sorted(set([d["tipe"] for d in all_member]))
    ranting_values = sorted(set([d["ranting"] for d in all_member]))
    combo_tipe['values'] = tipe_values
    combo_ranting['values'] = ranting_values


def tambah_member_gui():
    popup = tk.Toplevel()
    popup.title("Tambah Member")
    popup.geometry("400x400")
    frame_form = tk.Frame(popup)
    frame_form.pack(padx=10, pady=10)

    def create_entry(label):
        tk.Label(frame_form, text=label).pack(anchor='w')
        entry = tk.Entry(frame_form)
        entry.pack(fill='x')
        return entry
    
    # Entry fields
    
    entry_kode_member = create_entry("Kode Member")
    entry_nama = create_entry("Nama")
    entry_nomor = create_entry("Nomor HP")
    entry_alamat = create_entry("Alamat")
    entry_tipe = create_entry("Tipe Member")
    entry_ranting = create_entry("Ranting")

    entries = [entry_nama, entry_nomor, entry_alamat, entry_tipe, entry_ranting, entry_kode_member]

    def simpan_member():
        nama = entry_nama.get()
        alamat = entry_alamat.get()
        nomor = entry_nomor.get()
        tipe = entry_tipe.get()
        ranting = entry_ranting.get()
        kode_member = entry_kode_member.get()
    
        try:
            tambah_member(nama=nama, alamat=alamat, nomor=nomor, tipe=tipe, ranting=ranting, kode_member=kode_member)
            messagebox.showinfo("Berhasil", f"Member '{nama}' berhasil ditambahkan.")
            for entry in entries: entry.delete(0, tk.END)
            print("[DEBUG] refresh_tree aktif oleh", __name__)
            refresh_tree()
            update_filter_dropdowns()
        except Exception as e:
            print("[ERROR]", e) #
            messagebox.showerror("Gagal", str(e))
    
    print("[DEBUG] ISi dropdown tipe:", combo_tipe['values'])
    print("[DEBUG] Isi dropdown ranting:", combo_ranting['values'])
    tk.Button(popup, text="Simpan", command=simpan_member).pack(pady=10)


def on_tree_select(event):
    global selected_id
    selected_id = tree.focus()
    values = tree.item(selected_id)["values"]
    print("[DEBUG] values", values)
    print("[DEBUG] len values", len(values))

    if not selected_id:
        print("[DEBUG] Tidak ada baris yang dipilih")
        return

    column_order = ["kode_member", "nama", "no_hp", "alamat", "tipe", "ranting"]

    for i, col in enumerate(column_order):
        if col in entry_map:
            entry_map[col].delete(0, tk.END)
            if i < len(values):
                entry_map[col].insert(0, values[i])

    print("[DEBUG]",selected_id)
    print("[DEBUG] entry_map keys:", entry_map.keys())

def edit_member_gui(parent):
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Pilih Member yang ingin diedit.")
        return
    values = tree.item(selected_id)["values"]
    if not values or len(values) < 6:
        print("[DEBUG] Tidak ada data valid.")
        return

    popup = tk.Toplevel(parent)
    popup.title("EDIT Member")
    popup.geometry("400x400")

    def create_entry(label, value):
        tk.Label(popup, text=label).pack(anchor='w')
        entry = tk.Entry(popup)
        entry.insert(0, value)
        entry.pack(fill='x')
        return entry
    
    entry_kode_member = create_entry("Kode Member", values[0])
    entry_nama = create_entry("Nama", values[1])
    entry_nomor = create_entry("Nomor HP", values[2])
    entry_alamat = create_entry("Alamat", values[3])
    entry_tipe = create_entry("Tipe Member", values[4])
    entry_ranting = create_entry("Ranting", values[5])

    def simpan_perubahan():
        try:
            update_member(selected_item,
                          entry_nama.get(),
                          entry_nomor.get(),
                          entry_alamat.get(),
                          entry_tipe.get(),
                          entry_ranting.get(),
                          entry_kode_member.get()
            )
            messagebox.showinfo("Edit Sukses", "Data Member Berhasil diperbarui.")
            refresh_tree()
            popup.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    # Tombol di jendela edit

    tk.Button(popup, text="Simpan Perubahan", command=simpan_perubahan).pack(pady=5)
    tk.Button(popup, text="Batal", command=popup.destroy).pack()


def hapus_member_gui():
    print("[DEBUG]hapus", selected_id)
    if not selected_id:
        messagebox.showwarning("Pilih member yang ingin dihapus.")
        return
    if messagebox.askyesno("Hapus Member", "Yakin ingin menghapus member ini?"):
        try:
            hapus_member(selected_id)
            messagebox.showinfo("Info", "Member berhasil dihapus.")
            print("[DEBUG] refresh_tree aktif oleh", __name__)
            refresh_tree()
        except Exception as e:
            messagebox.showerror("Gagal Hapus", str(e))

def buat_frame_member(parent):
    global window, entry_map, entry_nama, entry_nomor, entry_alamat, entry_tipe, entry_ranting 
    global tree, entries, selected_id, entry_kode_member
    global entry_search, combo_tipe, combo_ranting
    entry_map = {}
    selected_id = None
    frame = tk.Frame(parent, bg="#f4f4f4")

    # Header dan Tombol Aksi

    frame_header = tk.Frame(frame, bg="#f4f4f4")
    frame_header.pack(pady=10)
    tk.Button(frame_header, text="Tambah Member", command=tambah_member_gui).pack(side=tk.LEFT, padx=6)

    # _______________ Filter Area
    def reset_filter():
        combo_tipe.set("")
        combo_ranting.set("")
        print("[DEBUG] refresh_tree aktif oleh", __name__)
        refresh_tree()  # Tampikan semua member

    def build_filter_gui():
        global combo_tipe, combo_ranting
        
        frame_filter = tk.Frame(frame, bg="#f4f4f4")
        frame_filter.pack(pady=10)

        all_member = semua_member()
        # Ambil data unik
        tipe_values = sorted(set([d["tipe"] for d in all_member]))
        ranting_values = sorted(set([d["ranting"] for d in all_member]))

        # Dropdown Tipe

        tk.Label(frame_filter, text="Filter Tipe").pack(side='left')
        combo_tipe = ttk.Combobox(frame_filter, values=tipe_values)
        combo_tipe.pack(side='left', padx=5)

        # Dropdown Ranting

        tk.Label(frame_filter, text="Filter Ranting").pack(side='left')
        combo_ranting = ttk.Combobox(frame_filter, values=ranting_values)
        combo_ranting.pack(side='left', padx=5)

        #tk.Button(frame_header, text="Terapkan Filter", command=lambda: filter_member()).pack(side=tk.LEFT, padx=6)
        tk.Button(frame_filter, text="Reset Filter", command=reset_filter).pack(side=tk.LEFT, padx=4)

        def filter_data():
            tipe_selected = combo_tipe.get()
            ranting_selected = combo_ranting.get()
            hasil = [d for d in all_member if
                     (tipe_selected == '' or d["tipe"] == tipe_selected) and
                     (ranting_selected == '' or d["ranting"] == ranting_selected)]
        
            tree.delete(*tree.get_children())
            for m in hasil:
                tree.insert("", tk.END, iid=m["id_member"], values=(
                m["kode_member"], m["nama"], m["no_hp"], m["alamat"], m["tipe"], m["ranting"]
            ))
        
        tk.Button(frame_filter, text="Filter", command=filter_data).pack(side='left', padx=5)
    build_filter_gui()

    # ______________ Pencarian Nama

    frame_search = tk.Frame(frame, bg="#f4f4f4")
    frame_search.pack(pady=5)

    tk.Label(frame_search, text="Cari Nama Member:", bg="#f4f4f4").pack(side=tk.LEFT)
    entry_search = tk.Entry(frame_search, width=30)
    entry_search.pack(side=tk.LEFT, padx=4)
    tk.Button(frame_search, text="Cari", command=lambda: cari_member_gui()).pack(side=tk.LEFT, padx=4)

    # ____________ Treeview Daftar Member
   
    columns = ("id_member", "kode_member", "nama", "nomor", "alamat", "tipe", "ranting", )
    column_labels = {
        "id_member": "ID",
        "kode_member": "Kode Member",
        "nama": "Nama",
        "nomor": "Nomor HP",
        "alamat": "Alamat",
        "tipe": "Tipe Member",
        "ranting": "Ranting",

    }
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=column_labels[col])
        tree.column(col, width=130)    
    tree.pack(fill="both", expand=True, pady=10)
    tree.bind("<<TreeviewSelect>>", on_tree_select)

    def cari_member_gui():
        keyword = entry_search.get()
        if not keyword.strip():
            messagebox.showwarning("Pencarian Kosong", "Masukkan kata kunci nama member.")
            return
        from app.core.member_core import cari_member
        hasil = cari_member(keyword)
        tree.delete(*tree.get_children())
        for m in hasil:
            tree.insert("", tk.END, iid=m["id_member"], values=(
                m["kode_member"], m["nama"], m["no_hp"], m["alamat"], m["tipe"], m["ranting"] 
            ))

    # Filter Tipe dan Ranting

    def filter_member():
        frame_filter = tk.Frame(window)
        frame_filter.pack(pady=10)
        tipe = combo_tipe.get()
        ranting = combo_ranting.get()
        filtered = [
            m for m in semua_member()
            if (tipe == "" or m["tipe"] == tipe) and
                (ranting == "" or m["ranting"] == ranting)
        ]
        tree.delete(*tree.get_children())
        for m in filtered:
            tree.insert("", tk.END, iid=m["id_member"], values=(
                m["kode_member"], m["nama"], m["no_hp"], m["alamat"], m["tipe"], m["ranting"]
            ))

        
    # _________ Tombol Bawah Edit & Hapus

    frame_footer = tk.Frame(frame, bg="#f4f4f4")
    frame_footer.pack(pady=10)

    tk.Button(frame_footer, text="Edit Member", command=lambda: edit_member_gui(frame)).pack(side=tk.LEFT, padx=8)
    tk.Button(frame_footer, text="Hapus Member", command=hapus_member_gui).pack(side=tk.LEFT, padx=8)
    
    refresh_tree()
    print("[DEBUG] data awal", semua_member())
    frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    buat_frame_member()


#python -m app.gui.member_gui
