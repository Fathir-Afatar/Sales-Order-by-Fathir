import tkinter as tk
from tkcalendar import DateEntry, Calendar
print("Berhasil import tkcalendar!")
from tkinter import ttk, messagebox, Toplevel, Entry, Button
from datetime import datetime
from app.core.pengeluaran_core import tambah_pengeluaran, semua_pengeluaran, pengeluaran_bulan_kategori, pengeluaran_per_bulan, pengeluaran_per_kategori, hapus_pengeluaran, edit_pengeluaran
from app.constants.config import get_connection

def open_calendar(entry_widget):
    top = Toplevel()
    top.grab_set()
    top.transient(entry_widget.master)

    cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
    cal.pack(padx=10, pady=10)

    def select_date():
        entry_widget.delete(0, 'end')
        entry_widget.insert(0, cal.get_date())
        top.destroy()
    Button(top, text="Pilih Tanggal", command=select_date).pack(pady=5)

def buka_form_tambah_pengeluaran(tampilkan_histori_callback):
    form = tk.Toplevel()
    form.title("Tambah Pengeluaran")
    form.geometry("400x400")
    form.grab_set()

    entries = {}

    ttk.Label(form, text="Tanggal").pack(anchor="w", padx=10, pady=(10))
    tanggal_entry = ttk.Entry(form, width=20)
    tanggal_entry.pack(fill="x", padx=10)
    Button(form, text="📅", command=lambda:open_calendar(tanggal_entry)).pack(pady=5)
    entries["Tanggal"] = tanggal_entry

    for label in ["Nama Pengeluaran", "Kategori", "Nominal", "Keterangan"]:
        ttk.Label(form, text=label).pack(anchor="w", padx=10, pady=5)
        ent = ttk.Entry(form)
        ent.pack(fill="x", padx=10)
        entries[label] = ent
    
    def simpan():
        try:
            tanggal = entries["Tanggal"].get()
            nama = entries["Nama Pengeluaran"].get()
            nominal = float(entries["Nominal"].get())
            keterangan = entries["Keterangan"].get()
            kategori = entries["Kategori"].get()

            if not tanggal or not nama or not kategori:
                messagebox.showwarning("Validasi", "Tanggal, Nama, dan Kategori wajib diisi.")
                return
            
            data = {
                "tanggal": tanggal,
                "nama_pengeluaran": nama,
                "nominal": nominal,
                "keterangan": keterangan,
                "kategori": kategori,
            }
            tambah_pengeluaran(data)

            messagebox.showinfo("Sukses", "Pengeluaran berhasil ditambahkan.")
            form.destroy()
            tampilkan_histori_callback(semua_pengeluaran())
            print("Data baru:", semua_pengeluaran())
            print("Data yang akan disimpan:", data)
        except ValueError:
            messagebox.showerror("Error", "Nominal harus berupa angka.")
    ttk.Button(form, text="Simpan", command=simpan).pack(pady=20)

def tampilkan_histori(data_pengeluaran):
    tree.delete(*tree.get_children()) # clear semua isi lama
    for row in data_pengeluaran:
        tree.insert("", "end", values=(
            row["tanggal"],
            row["nama_pengeluaran"],
            row["kategori"],
            f"Rp {float(row['nominal']):,}",
            row["keterangan"]
        ), tags=(row["id_pengeluaran"],)) # row[0] = id_pengeluaran 
        print("Data masuk ke Treeview:", len(data_pengeluaran))
        print("Treeview values:", row["tanggal"], row["nama_pengeluaran"], row["kategori"], row["nominal"], row["keterangan"])

def buat_frame_pengeluaran(parent, set_judul_modul):
    global tree
    frame = tk.Frame(parent, bg="#f4f4f4")

    # Filter

    frame_filter = tk.Frame(frame, bg="#f4f4f4")
    frame_filter.pack(pady=10)

    tk.Label(frame_filter, text="Bulan").pack(side=tk.LEFT, padx=5)
    combo_bulan = ttk.Combobox(frame_filter, values=[
    "01 - Januari", "02 - Februari", "03 - Maret", "04 - April",
    "05 - Mei", "06 - Juni", "07 - Juli", "08 - Agustus",
    "09 - September", "10 - Oktober", "11 - November", "12 - Desember"
    ])
    combo_bulan.pack(side=tk.LEFT)
    combo_bulan.set("")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT kategori FROM pengeluaran")
    kategori_list = [row[0] for row in cursor.fetchall()]
    conn.close()

    kategori_list.insert(0, "Semua")

    tk.Label(frame_filter, text="Kategori").pack(side=tk.LEFT, padx=5)
    combo_kategori = ttk.Combobox(frame_filter, values=kategori_list, state="readonly")
    combo_kategori.pack(side=tk.LEFT)
    combo_kategori.set("Semua")

    tahun_sekarang = datetime.now().year
    tahun_list = [str(tahun_sekarang - i) for i in range(5)]

    tk.Label(frame_filter, text="Tahun").pack(side=tk.LEFT, padx=5)
    combo_tahun = ttk.Combobox(frame_filter, values=tahun_list, state="readonly")
    combo_tahun.pack(side=tk.LEFT)
    combo_tahun.set(str(datetime.now().year))
    
    def reset_filter():
        combo_bulan.set("")
        combo_kategori.set("Semua")
        tampilkan_histori(semua_pengeluaran())
        messagebox.showinfo("Filter Direset", "Filter telah dikembalikan ke kondisi awal.")

    def apply_filter():
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
        print("Query filter:", bulan, tahun, kategori)
        print("Filter bulan:", bulan)
        print("Filter tahun", tahun)
        print("Jumlah data:", len(data))
        print("Jumlah data:", len(data))
        for row in data:
            print("Row:", row)
    tk.Button(frame_filter, text="Terapkan Filter", command= apply_filter).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_filter, text="Reset Filter", command=reset_filter).pack(side=tk.LEFT, padx=5)
    
    # Treeview

    frame_tree = tk.Frame(frame)
    frame_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scroll_x = tk.Scrollbar(frame_tree, orient=tk.HORIZONTAL)
    scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    scroll_y = tk.Scrollbar(frame_tree, orient=tk.VERTICAL)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    tree = ttk.Treeview(frame_tree, columns=("Tanggal", "Nama", "Kategori", "Nominal", "Keterangan"), show="headings", height=15, xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    scroll_x.config(command=tree.xview)
    scroll_y.config(command=tree.yview)

    for col in ("Tanggal", "Nama", "Kategori", "Nominal", "Keterangan"):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    
    data = semua_pengeluaran()
    tampilkan_histori(data)

    # Tombol edit & hapus
    frame_btn = tk.Frame(frame, bg="#f4f4f4")
    frame_btn.pack(pady=5)

    def hapus_pengeluaran_gui():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Data", "Silahkan pilih pengeluaran yang ingin dihapus.")
            return
        id_pengeluaran = tree.item(selected[0])["tags"][0]
        confirm = messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data ini?")
        if confirm:
            hapus_pengeluaran(id_pengeluaran)
            apply_filter()

    def edit_pengeluaran_gui():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Data", "Silahkan pilih pengeluaran ingin diedit.")
            return
        item = tree.item(selected[0])
        values = item["values"]
        id_pengeluaran = tree.item(selected[0])["tags"][0]

        form = tk.Toplevel()
        form.title("Edit Pengeluaran")
        form.geometry("400x400")
        form.grab_set()

        labels = ["Nama Pengeluaran", "Kategori", "Nominal", "Keterangan"]
        entries = {}

        ttk.Label(form, text="Tanggal").pack(anchor="w", padx=10, pady=(10))
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

                messagebox.showinfo("Sukses", "Pengeluaran berhasil diupdate.")
                form.destroy()
                tampilkan_histori(semua_pengeluaran())
            except Exception as e:
                print("[ERROR edit_pengeluaran_gui]", e)
                messagebox.showerror("Gagal", "Pengeluaran gagal diupdate.")
        ttk.Button(form, text="Simpan Perubahan", command=simpan_edit).pack(pady=20)
    
    tk.Button(frame_btn, text="Edit", command=edit_pengeluaran_gui).pack(side=tk.LEFT, padx=10)
    tk.Button(frame_btn, text="Hapus", command=hapus_pengeluaran_gui).pack(side=tk.LEFT, padx=10)
    tk.Button(frame_btn, text="Tambah", command=lambda:buka_form_tambah_pengeluaran(tampilkan_histori)).pack(side=tk.LEFT, padx=10)
    
    frame.pack(fill="both", expand=True)
    
    set_judul_modul("Pengeluaran")

if __name__ == "__main__":
    buat_frame_pengeluaran()