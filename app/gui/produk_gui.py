import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from app.core.product_core import tambah_produk, semua_produk,  update_produk, hapus_produk, bersihkan_angka, get_kategori_nama_by_id, ambil_semua_kategori, ambil_produk_by_kategori_id, tambah_kategori, get_produk_by_id, get_kategori_id_by_nama


def buka_form_tambah_produk(parent):
    global entry_nama, entry_kode, entry_kategori, entry_merk
    global entry_harga_beli, entry_harga_jual, entry_stok, entry_berat
    
    form_produk = build_form_produk_window(parent)
    build_form_produk_fields(form_produk)
    build_form_produk_buttons(form_produk)
    center_window(form_produk)

def build_form_produk_window(parent):
    form = tk.Toplevel(parent)
    form.title("Tambah Produk")
    form.geometry("500x400")
    print("[INFO] Membuka form tambah produk...")
    print("[INFO] Form tambah produk selesai dibuat.")
    # konfigurasi kolom agar layout lebih seimbang
    form.grid_columnconfigure(0, weight=1)
    form.grid_columnconfigure(1, weight=2)
    return form

def build_form_produk_fields(form):
    global entry_nama, entry_kode, entry_kategori, entry_merk
    global entry_harga_beli, entry_harga_jual, entry_stok, entry_berat, entries

    kategori_list = ambil_semua_kategori()
    entry_nama = tk.Entry(form)
    entry_kode = tk.Entry(form)
    combo_kategori = ttk.Combobox(form, values=kategori_list, state="readonly")
    combo_kategori.set(kategori_list[0] if kategori_list else "(Belum Ada Kategori)")
    entry_merk = tk.Entry(form)
    entry_harga_beli = tk.Entry(form)
    entry_harga_jual = tk.Entry(form)
    entry_stok = tk.Entry(form)
    entry_berat = tk.Entry(form)

    entries = [entry_nama, entry_kode, combo_kategori, entry_merk, entry_harga_beli, entry_harga_jual, entry_stok, entry_berat]

    labels = ["Nama", "Kode", "Kategori", "Merk", "Harga Beli", "Harga Jual", "Stok", "Berat"]

    for i, (label_text, entry) in enumerate(zip(labels, entries)):
        tk.Label(form, text=label_text).grid(row=i, column=0, padx=(30,10), pady=5, sticky="e")
        entry.grid(row=i, column=1, padx=(10, 30), pady=5, sticky="w")
    print("[INFO] Membuka form tambah produk...")
    print("[INFO] Form tambah produk selesai dibuat.")
    
    tk.Button(form, text="+ Tambah Kategori", command=lambda: build_form_tambah_kategori(form)).grid(row=2, column=2, padx=(0, 10), pady=5)

def build_form_produk_buttons(form):
    def tambah_produk_gui():
        
        global form_produk_aktif
        form_produk_aktif = True
        
        nama_kategori  = entry_kategori.get().strip()
        if nama_kategori == "(Belum Ada Kategori)":
            messagebox.showwarning("Kategori Belum Dipilih", "Silakan tambahkan kategori terlebih dahulu.")
            return

        kategori_id = get_kategori_nama_by_id(nama_kategori)
        if kategori_id is None:
            messagebox.showerror("Kategori Tidak Valid", f"Kategori '{nama_kategori}' tidak ditemukan.")
            print("Debug kategori:", repr(nama_kategori))
            return
        
        try:
            harga_beli = bersihkan_angka(entry_harga_beli.get())
            harga_jual = bersihkan_angka(entry_harga_jual.get())
            stok = int(entry_stok.get().strip())
            berat = float(entry_berat.get().strip())
        except ValueError as e:
            messagebox.showerror("Input Invalid", f"Pastikan semua angka valid: {e}")
            return

        data = {
            "nama" : entry_nama.get().strip(),
            "kode_produk": entry_kode.get().strip(),
            "kategori_id": kategori_id,
            "merk": entry_merk.get().strip(),
            "harga_beli": harga_beli,
            "harga_jual": harga_jual,
            "stok": stok,
            "berat": berat
        }
        print("Data siap ditambahkan:", data)
        if tambah_produk(data):
            messagebox.showinfo("Berhasil", f"Produk'{data['nama']}' berhasil ditambahkan.")
            for entry in entries: entry.delete(0, tk.END)
            refresh_tree()
        else:
            messagebox.showerror("Gagal", "Gagal menambahkan produk.")

    # Tombol Simpan

    tk.Button(form, text="Simpan Produk", command=tambah_produk_gui).grid(row=len(entries), column=0, columnspan=2, pady=20, padx=30)
    tk.Button(form, text="Import dari Excel", command=import_produk_excel).grid(row=len(entries)+1, column=0, columnspan=2, pady=5)

def center_window(form):    # Untuk menengahkan jendela saat input produk
    form.update_idletasks()
    w = form.winfo_width()
    h = form.winfo_height()
    x = (form.winfo_screenmmwidth() // 2) - (w // 10)
    y = (form.winfo_screenheight() // 2) - (h // 2)
    form.geometry(f"+{x}+{y}")

def import_produk_excel():
    file_path = filedialog.askopenfile(filetypes=[("Excel files", ".xlsx")])
    if file_path:
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            nama = row['Nama Produk']
            kategori = row['Kategori']
            harga = row['Harga']
            stok = row['Stok']
            #simpan_produk(nama, kategori, harga, stok)
        refresh_tree

# Untuk Edit Produk, buka form edit, dan update produk

def buka_form_edit_produk(parent):
    global entry_nama, entry_kode, entry_kategori, entry_merk, entry_harga_beli, entry_harga_jual, entry_stok, entry_berat, selected_id
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Tidak Ada Pilihan", "Pilih produk yang ingin diedit di tabel.")
        return

    values = tree.item(selected_item[0], "values")
    selected_id = values[0]
    print("Selected ID:", selected_id)

    produk = get_produk_by_id(selected_id)
    print("[DEBUG] produk:", produk)
    if not produk:
        messagebox.showerror("Produk Tidak Ditemukan", f"Tidak ada produk dengan ID {selected_id}.")
        return
    
    kategori_nama = get_kategori_nama_by_id(produk["kategori_produk"])
    produk["kategori_nama"] = kategori_nama

    print("[DEBUG] Tipe Produk:", type(produk))
    form_edit = tk.Toplevel(parent)
    form_edit.title("Edit Produk")
    form_edit.geometry("500x400")
    form_edit.grid_columnconfigure(0, weight=1)
    form_edit.grid_columnconfigure(1, weight=2)

    entries = build_edit_form_fields(form_edit, produk)
    if len(entries) < 8:
        messagebox.showerror("Error", f"Entry tidak lengkap. Hanya {len(entries)} yang dibuat.")
        return

    tk.Button(form_edit, text="Simpan Perubahan", command=lambda: simpan_perubahan_produk(form_edit, selected_id, entries)).grid(row=len(entries), column=0, columnspan=2, pady=20, padx=30)

def build_edit_form_fields(form, produk):
    labels = ["Nama", "Kode", "Kategori ", "Merk", "Harga Beli", "Harga Jual", "Stok", "Berat"]
    keys = ["nama_produk", "kode_produk", "kategori_nama", "merk", "harga_beli", "harga_jual", "stok", "berat"]
    entries = []
    kategori_list = ambil_semua_kategori()

    for i, (label_text, key) in enumerate(zip(labels, keys)):
        tk.Label(form, text=label_text).grid(row=i, column=0, padx=(30, 10), pady=5, sticky="e")

        if key == "kategori_nama":
            combo = ttk.Combobox(form, values=kategori_list, state="readonly")
            combo.set(produk.get(key, "")) # set nilai awal

            combo.grid(row=i, column=1, padx=(10,30), pady=5, sticky="w")
            entries.append(combo)
        else:
            entry = tk.Entry(form)
            entry.insert(0, str(produk.get(key, "")))
            entry.grid(row=i, column=1, padx=(10,30), pady=5, sticky="w")
            entries.append(entry)
        
    for i, entry in enumerate(entries):
        print(f"[DEBUG] Entry {i}: {entry.get()}")

    return entries

def simpan_perubahan_produk(form, id_produk, entries):
    import traceback
    traceback.print_stack()
    labels = ["Nama", "Kode", "Kategori", "Merk", "Harga Beli", "Harga Jual", "Stok", "Berat"]
    print("[DEBUG] Mulai simpan_perubahan_produk")
    print("[DEBUG] Entry 2 (kategori):", entries[2].get())
    for i, label in enumerate(labels):
        if entries[i].get().strip() == "":
            messagebox.showerror("Input Kosong", f"{label} tidak boleh kosong.")
            return

    try:
        kategori_nama = entries[2].get().strip()
        kategori_id = get_kategori_id_by_nama(kategori_nama)

        if kategori_id is None:
            messagebox.showerror("Kategori Tidak Valid", f"Kategori '{kategori_nama}' tidak ditemukan.")
            return
        print("[DEBUG] kategori_nama:", kategori_nama)
        print("[DEBUG] kategori_id:", kategori_id)
        for i, entry in enumerate(entries):
            print(f"[DEBUG] Entry {i}: '{entry.get().strip()}'")

        data = {
            "nama": entries[0].get().strip(),
            "kode": entries[1].get().strip(),
            "kategori_id": kategori_id,
            "merk": entries[3].get().strip(),
            "harga_beli": bersihkan_angka(entries[4].get()),
            "harga_jual": bersihkan_angka(entries[5].get()),
            "stok": int(entries[6].get().strip()),
            "berat": float(entries[7].get().strip())
        }
    except ValueError as e:
        messagebox.showerror("Input Invalid", f"Pastikan semua angka valid: {e}")
        return

    if data["harga_beli"] is None or data["harga_jual"] is None:
        messagebox.showerror("Input Invalid", "Pastikan harga beli dan jual berupa angka valid.")
        return
    if update_produk_by_id(id_produk, data):
        messagebox.showinfo("Berhasil", f"Produk '{data['nama']}' berhasil diperbarui.")
        form.destroy()
        refresh_tree()
    else:
        messagebox.showerror("Gagal", "Gagal memperbarui produk.")

def update_produk_by_id(id_produk, data):
    try:
        print("[DEBUG] Harga Beli:", data['harga_beli'], type(data['harga_beli']))
        print("[DEBUG] Harga jual:", data['harga_jual'], type(data['harga_jual']))
        for key in ["harga_beli", "harga_jual", "stok", "berat"]:
            if not isinstance(data[key], (int, float)):
                print(f"[ERROR] {key} bukan angka valid:", data[key])
                return False
            
        return update_produk(
            id_produk,
            data['nama'],
            data['kode'],
            data['kategori_id'],
            data['merk'],
            data['harga_beli'],
            data['harga_jual'],
            int(data['stok']),
            float(data['berat'])
        )
    except Exception as e:
        print(f"Error saat update produk: {e}")
        return False

# Untuk hapus produk
def hapus_produk_gui():
    if not selected_id:
        messagebox.showwarning("Tidak Ada Pilihan", "Pilih produk yang akan dihapus di tabel.")
        return
    konfirmasi = messagebox.askyesno("Konfirmasi Hapus", "Yakin ingin menghapus produk ini?")
    if konfirmasi:
        try:
            hapus_produk(selected_id)
            messagebox.showinfo("Dihapus", "Produk berhasil dihapus.")
            refresh_tree()
            for entry in entries: entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Gagal Hapus", str(e))

def format_rupiah(nilai):
    try:
        return f"Rp {int(float(nilai)):,}"
    except (ValueError, TypeError):
        return "Rp 0"

# Main GUI
def buat_frame_produk(parent, set_judul_modul):
    global entry_nama, entry_kode, entry_kategori, entry_merk
    global entry_harga_beli, entry_harga_jual, entry_stok, entry_berat
    global tree, selected_id, entry_filter_kategori
    
    selected_id = None
    frame = tk.Frame(parent, bg="#f4f4f4")
    
    build_kontrol_produk(frame)
    build_form_produk(frame)
    build_filter_produk(frame)
    build_treeview_produk(frame)
    build_footer_produk(frame)

    refresh_tree()
    frame.pack(fill="both", expand=True)
    set_judul_modul("Produk")

def build_kontrol_produk(frame):
    global entry_cari

    frame_kontrol = tk.Frame(frame, bg="#f4f4f4")
    frame_kontrol.pack()

    frame_kontrol_atas = tk.Frame(frame_kontrol, bg="#f4f4f4")
    frame_kontrol_atas.pack()
    tk.Button(frame_kontrol_atas, text="Tambah Produk", command=lambda: buka_form_tambah_produk(frame)).pack()

    frame_kontrol_grid = tk.Frame(frame_kontrol, bg="#f4f4f4")
    frame_kontrol_grid.pack()

    tk.Label(frame_kontrol_grid, text="Nama Produk:").grid(row=0, column=0, padx=5, sticky="e")
    
    # Entry cari
    entry_cari = tk.Entry(frame_kontrol_grid, width=20)
    entry_cari.grid(row=0, column=1, padx=5)
    # Tombol cari  --> hanya nama, Reset Filter
    tk.Button(frame_kontrol_grid, text="Cari", command=cari_produk_nama).grid(row=0, column=2, padx=5)
    tk.Button(frame_kontrol_grid, text="Reset Filter", command=reset_filter).grid(row=0, column=5, padx=5)

def build_form_produk(frame):
    global entry_nama, entry_kode, entry_kategori, entry_merk
    global entry_harga_beli, entry_harga_jual, entry_stok, entry_berat, entries

    # ------ Form Input ----
    frame_form = tk.Frame(frame, bg="#f4f4f4")  # Form Input produk
    frame_form.pack_forget()   # sembunyikan 

    def create_labeled_entry(label):
        tk.Label(frame_form, text=label).pack()
        e = tk.Entry(frame_form)
        e.pack()
        return e
    
    entry_nama = create_labeled_entry("Nama Produk")
    entry_kode = create_labeled_entry("Kode Produk")
    entry_kategori = create_labeled_entry("ID Kategori")
    entry_merk = create_labeled_entry("Merk")
    entry_harga_beli = create_labeled_entry("Harga Beli")
    entry_harga_jual = create_labeled_entry("Harga Jual")
    entry_stok = create_labeled_entry("Stok Awal")
    entry_berat = create_labeled_entry("Berat (Kg)")

    entries = [entry_nama, entry_kode, entry_kategori, entry_merk,
               entry_harga_beli, entry_harga_jual, entry_stok, entry_berat]

def build_filter_produk(frame):
    global entry_filter_kategori
    # Filter Kategori
    frame_filter = tk.Frame(frame, bg="#f4f4f4")
    frame_filter.pack(pady=10)

    tk.Label(frame_filter, text="Nama Kategori:").grid(row=0, column=2, padx=5)

    kategori_list = ambil_semua_kategori()

    entry_filter_kategori = ttk.Combobox(frame_filter, values=kategori_list, state="readonly")
    entry_filter_kategori.grid(row=0, column=3, padx=5)

    tk.Button(frame_filter, text="Terapkan Filter", command=filter_produk_gui).grid(row=0, column=4, padx=5)

def build_treeview_produk(frame):
    global tree

    columns = ("id", "nama", "kode", "kategori", "merk", "harga_beli", "harga_jual", "stok", "berat")
    
    tree_container = tk.Frame(frame)
    tree_container.pack(fill="both", expand=True, padx=10, pady=10)

    scroll_y = ttk.Scrollbar(tree_container, orient="vertical")
    scroll_y.grid(row=0, column=1, sticky="ns")

    scroll_x = ttk.Scrollbar(tree_container, orient="horizontal")
    scroll_x.grid(row=1, column=0, sticky="ew")

    tree = ttk.Treeview(tree_container, columns=columns, show="headings",
                        yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    tree.grid(row=0, column=0, sticky="nsew")

    scroll_y.config(command=tree.yview)
    scroll_x.config(command=tree.xview)

    labels = {
        "nama": "Nama", "kode": "Kode", "kategori": "Kategori", "merk": "Merk",
        "harga_beli": "Harga Beli", "harga_jual": "Harga Jual", "stok": "Stok", "berat": "Berat"
    }
    for col in columns[1:]: # skip "id"
        tree.heading(col, text=labels[col])       

    tree.column("nama", width=150)
    tree.column("kode", width=100)
    tree.column("kategori", width=120)
    tree.column("merk", width=120)
    tree.column("harga_beli", anchor="e", width=100)
    tree.column("harga_jual", anchor="center", width=80)
    tree.column("stok", anchor="center", width=80)
    tree.column("berat", anchor="center", width=80)


    tree.bind("<<TreeviewSelect>>", on_tree_select)

    tree_container.grid_rowconfigure(0, weight=1)
    tree_container.grid_columnconfigure(0, weight=1)

def refresh_tree(kategori=None, nama_produk=None):
    print("[INFO] Memuat ulang daftar produk . . .")
    tree.delete(*tree.get_children())

    for p in semua_produk():
        print("[DEBUG] Produk:", p.get("nama_produk"), " | Kategori:", p.get("nama_kategori", "Kategori tidak tersedia"))
        # Filter Kategori

        if kategori and kategori not in (p.get("nama_kategori") or "").lower():
            continue
        # Filter nama (case-insensitive)
        if nama_produk and nama_produk.lower() not in p["nama_produk"].lower():
            continue
        tree.insert("", tk.END, values=(p["id_produk"], p.get("nama_produk",""), p.get("kode_produk",""), p.get("nama_kategori",""), p.get("merk",""), format_rupiah(p.get("harga_beli",0)), format_rupiah(p.get("harga_jual",0)), p.get("stok",0), p.get("berat",0)))


def filter_produk_gui():
    kategori = entry_filter_kategori.get().strip().lower()
    keyword = entry_cari.get().strip().lower()
    print(f"[INFO] Terapkan filter: Nama = '{keyword}', Kategori = '{kategori}'")
    refresh_tree(kategori=kategori, nama_produk=keyword)

def filter_produk_by_kategori(nama_kategori):
    tree.delete(*tree.get_children())

    if nama_kategori == "Semua":
        produk_list = semua_produk()
    else:
        kategori_id = get_kategori_nama_by_id(nama_kategori)
        produk_list = ambil_produk_by_kategori_id(kategori_id)
    for p in produk_list:
        tree.insert("", tk.END, values=(p["id_produk"], p.get("nama_produk", ""), p.get("kode_produk", ""), nama_kategori, p.get("merk", ""), format_rupiah(p.get("harga_beli", 0)), format_rupiah(p.get("harga_jual", 0)), p.get("stok", 0), p.get("berat",0)))

def cari_produk_nama():
    keyword = entry_cari.get()
    refresh_tree(nama_produk=keyword)


def reset_filter():
    entry_filter_kategori.set("")
    entry_filter_kategori.delete(0, tk.END) # Kosongkan pilihan kategori
    entry_cari.delete(0, tk.END)
    refresh_tree() # Tampilkan semua data
    print("[INFO] Filter direset.")
    
def on_tree_select(event):
    if not buka_form_tambah_produk or not isinstance(buka_form_tambah_produk, tk.Toplevel):
        print("[INFO] Form edit belum aktif.")
        return
    
    try:
        entry_nama.delete(0, tk.END)
    except tk.TclError:
        print("[WARNING] entry_nama sudah tidak aktif atau sudah dihapus.")
        return
    selected = tree.focus()
    if not selected: return
    values = tree.item(selected, 'values')

    entry_nama.delete(0, tk.END)
    entry_nama.insert(0, values[1])
    entry_kode.delete(0, tk.END)
    entry_kode.insert(0, values[2])
    entry_harga_jual.delete(0, tk.END)
    entry_harga_jual.insert(0, values[3])
    entry_stok.delete(0, tk.END)
    entry_stok.insert(0, values[4])


    # ID disimpan untuk edit/delete

    global selected_id
    selected_id = values[0]

form_produk_aktif = False

def build_form_tambah_kategori(parent):
    form_kategori = tk.Toplevel(parent)
    form_kategori.title("Tambah Kategori")
    form_kategori.geometry("300x150")

    tk.Label(form_kategori, text="Nama Kategori").pack(pady=(20, 5))
    entry_nama_kategori = tk.Entry(form_kategori)
    entry_nama_kategori.pack(pady=5)

    def simpan_kategori():
        nama = entry_nama_kategori.get().strip()
        if not nama:
            messagebox.showerror("Error", "nama kategori tidak boleh kosong.")
            return
        if tambah_kategori(nama):
            messagebox.showinfo("Berhasil", f"Kategori '{nama}' berhasil ditambahkan.")
            form_kategori.destroy()
            # Refresh Combobox kategori di form produk jika tersedia
            try:
                kategori_baru = ambil_semua_kategori()
                entry_kategori["values"] = kategori_baru
                entry_kategori.set(nama)
            except:
                print("[WARNING] Tidak bisa refresh Combobox kategori.")
        else:
                messagebox.showerror("Gagal", f"Kategori '{nama}' sudah ada atau gagal ditambahkan.")
    tk.Button(form_kategori, text="Simpan", command=simpan_kategori).pack(pady=10)


def build_footer_produk(frame):

    tk.Button(frame, text="Edit Produk", command=lambda: buka_form_edit_produk(frame)).pack(pady=2)
    tk.Button(frame, text="Hapus Produk", command=hapus_produk_gui).pack(pady=2)

if __name__ == "__main__":
    buat_frame_produk()


#python -m app.gui.produk_gui