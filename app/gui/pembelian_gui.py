# Third-party
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog

# Local application
from app.core.pembelian_core import tambah_pembelian, get_detail_pembelian, get_histori_pembelian, update_pembelian, get_produk_nama
from app.core.supplier_core import ambil_supplier
from app.core.product_core import ambil_daftar_produk, bersihkan_angka
from app.constants.config import get_connection
from app.translator import _, i18n

def buat_frame_pembelian(parent, set_judul_modul):
    frame = tk.Frame(parent, bg="#f4f4f4")
    combo_supplier, supplier_map = build_supplier_section(frame)
    tree_input, entry_cari, reset_pencarian = build_produk_section(frame)
    tree_histori = build_histori_pembelian(frame)
    buka_konfirmasi_pembelian = setup_btn_simpan_pembelian(combo_supplier, tree_input, supplier_map, frame, tree_histori)

    setup_btn_lihat_detail(tree_histori, frame)

    btn_simpan = tk.Button(frame, text=_("pembelian.btn_simpan"), command=buka_konfirmasi_pembelian)
    btn_simpan.pack(pady=5)

    frame.pack(fill="both", expand=True)
    
    set_judul_modul(_("pembelian.set_judul_modul"))

def build_supplier_section(frame):
    font_normal = ("Segoe UI", 10)

    frame_supplier = tk.Frame(frame)
    frame_supplier.pack(fill="x", padx=10, pady=5)

    supplier_data = ambil_supplier()
    supplier_map = {sup["nama"]: sup["id"] for sup in supplier_data}
    
    tk.Label(frame_supplier, text=_("pembelian.lbl_frame_supplier"), font=font_normal).pack(side="left")
    combo_supplier = ttk.Combobox(frame_supplier, values=list(supplier_map.keys()), state="readonly")
    combo_supplier.pack(side="left", padx=5)

    return combo_supplier, supplier_map

def build_produk_section(frame):
    font_normal = ("Segoe UI", 10)

    frame_input = tk.Frame(frame)
    frame_input.pack(fill="both", expand=True, padx=10, pady=5)
    
    tk.Label(frame_input, text=_("pembelian.lbl_frame_input"), font=font_normal).pack(anchor="w")

    frame_search = tk.Frame(frame_input)
    frame_search.pack(pady=5)

    frame_input_scroll = tk.Frame(frame_input)
    frame_input_scroll.pack(fill="both", expand=True)

    entry_cari = tk.Entry(frame_search, width=30)
    entry_cari.pack(side="left", pady=(0, 5))
    entry_cari.insert(0, _("pembelian.lbl_entry_cari"))

    scroll_produk = tk.Scrollbar(frame_input_scroll, orient="vertical")
    tree_input = ttk.Treeview(frame_input_scroll, columns=(_("pembelian.pilih"), _("pembelian.kode"), _("pembelian.nama"), _("pembelian.jumlah"), _("pembelian.harga")), show="headings", yscrollcommand=scroll_produk.set)
    scroll_produk.config(command=tree_input.yview)

    produk_list = ambil_daftar_produk()
    tampilkan_produk(tree_input, produk_list)

    reset_pencarian = setup_pencarian_produk(entry_cari, tree_input, produk_list)
    btn_reset = tk.Button(frame_search, text="🔄 Reset", command=lambda:reset_pencarian())
    btn_reset.pack(side="left")
    
    for col in (_("pembelian.pilih"), _("pembelian.kode"), _("pembelian.nama"), _("pembelian.jumlah"), _("pembelian.harga")):
        tree_input.heading(col, text=col if col != "Pilih" else "✔")
        tree_input.column(col, width=40 if col == "Pilih" else 120, anchor="center")
    
    tree_input.pack(side="left", fill="both", expand=True)
    scroll_produk.pack(side="right", fill="y")

    entry_cari.bind("<FocusIn>", lambda e: entry_cari.delete(0, "end"))
    entry_cari.bind("<Key>", lambda e: filter_produk(entry_cari.get())) 
    btn_reset.config(command=lambda: tampilkan_produk(tree_input, produk_list))
    tree_input.bind("<Button-1>", lambda e: toogle_pilih(e, tree_input))
    tree_input.bind("<Double-1>", lambda e: tambah_produk(e, tree_input))

    return tree_input, entry_cari, reset_pencarian

def build_histori_section(frame):
    font_normal= ("Segoe UI", 10)
    frame_histori = tk.Frame(frame)
    frame_histori.pack(fill="both", expand=True, padx=10, pady=5)

    tk.Label(frame_histori, text=_("pembelian.lbl_frame_histori"), font=font_normal).pack(anchor="w")
    frame_histori_scroll =  tk.Frame(frame_histori)
    frame_histori_scroll.pack(fill="both", expand=True)

    scroll_histori = tk.Scrollbar(frame_histori_scroll, orient="vertical")
    tree_histori = ttk.Treeview(frame_histori_scroll, columns=(_("pembelian.id"), _("pembelian.tanggal"), _("pembelian.supplier"), _("pembelian.total")), show="headings", yscrollcommand=scroll_histori.set)
    for col in (_("pembelian.id"), _("pembelian.tanggal"), _("pembelian.supplier"), _("pembelian.total")):
        tree_histori.heading(col, text=col)
        tree_histori.column(col, anchor="center", width=100)
    
    scroll_histori.config(command=tree_histori.yview)
    tree_histori.pack(side="left", fill="both", expand=True)
    scroll_histori.pack(side="right", fill="y")

    return tree_histori

def tampilkan_produk(tree, list_produk):
    tree.delete(*tree.get_children())
    for p in list_produk:
        try:
            harga_format = f"Rp {int(float(p.get('harga', 0))):,}"
        except:
            harga_format = "Rp -"
        tree.insert("", "end", values=("", p.get("kode_produk", "-"), p.get("nama", "-"), p.get("jumlah", 0), harga_format))

def filter_produk(keyword, tree, produk_list):
    keyword = keyword.lower()
    if not keyword or keyword == _("pembelian.lbl_entry_cari"):
        tampilkan_produk(produk_list)
        return
        
    hasil = [p for p in produk_list if keyword in p["kode_produk"].lower() or keyword in p["nama"].lower()]
    tampilkan_produk(tree, hasil)

def toogle_pilih(event, tree):
    item_id = tree.identify_row(event.y)
    col = tree.identify_column(event.x)
    if not item_id or col != "#1": # Pastikan klik di kolom "Pilih"
        return
    values = tree.item(item_id)["values"]
    values[0] = "✔" if values[0] == "" else ""
    tree.item(item_id, values=values)

def build_interaksi_pembelian(entry_cari, frame, tree_input, combo_supplier, produk_list, supplier_map):
    setup_pencarian_produk(entry_cari, tree_input, produk_list)
    setup_edit_jumlah(tree_input)
    setup_konfirmasi_pembelian(frame, tree_input, combo_supplier, supplier_map)

def setup_pencarian_produk(entry_cari, tree_input, produk_list):
    def reset_pencarian():
        entry_cari.delete(0, "end") # Kosongkan kotak pencarian
        tampilkan_produk(produk_list)
    entry_cari.delete(0, "end")
    tampilkan_produk(tree_input, produk_list)
    return reset_pencarian

def setup_edit_jumlah(tree_input):    
    # Edit Jumlah (dual click)
    def edit_jumlah(event):
        item_id = tree_input.focus()
        if not item_id:
            return
        current = tree_input.item(item_id)["values"]
        if len(current) < 5:
            return
        nama_produk = current[2]
        try:
            jumlah_sekarang = int(current[3])
        except:
            jumlah_sekarang = 0
        jumlah_baru = simpledialog.askinteger(_("pembelian.simpledialog"), _("pembelian.jumlah_baru").format(nama=nama_produk), initialvalue=jumlah_sekarang, minvalue=0)
        if jumlah_baru is not None:
            current[3] = jumlah_baru
            tree_input.item(item_id, values=current)
        if current[0] != "✔":
            messagebox.showinfo(_("pembelian.info"), _("pembelian.lbl_centang"))
            return
    tree_input.bind("<Double-1>", edit_jumlah)

def setup_konfirmasi_pembelian(frame, tree_input, combo_supplier, supplier_map):
    def ambil_produk_terpilih():
        hasil = []
        for item_id in tree_input.get_children():
            values = tree_input.item(item_id)["values"]
            if values[0] == "✔" and int(values[3]) > 0:
                hasil.append({"kode_produk":values[1], "nama":values[2], "qty":int(values[3]), "harga_beli":int(bersihkan_rupiah(values[4]))})
        return hasil  

    def buka_konfirmasi_pembelian():
        produk_terpilih = ambil_produk_terpilih()
        if not produk_terpilih:
            messagebox.showinfo_("pembelian.info"), _("pembelian.lbl_tidak_dipilih")
            return
        
        supplier_nama = combo_supplier.get()
        if not supplier_nama:
            messagebox.showinfo(_("pembelian.info"), _("pembelian.lbl_pilih_supplier"))
            return
        
        window = tk.Toplevel(frame, bg="lightyellow")
        window.title(_("pembelian.lbl_window"))
        window.geometry("500x400")
        
        tk.Label(window, text=f"Supplier: {supplier_nama}", font=("Segoe UI", 10, "bold")).pack(pady=5)
        
        frame_produk = tk.Frame(window)
        frame_produk.pack(fill="both", expand=True)

        frame_total = tk.Frame(window)
        frame_total.pack(fill="x", pady=5)

        scroll_konfirmasi = ttk.Scrollbar(frame_produk, orient="vertical")
        tree_konfirmasi = ttk.Treeview(frame_produk, columns=(_("pembelian.kode"), _("pembelian.nama"), _("pembelian.qty"), _("pembelian.harga"), _("pembelian.subtotal")), show="headings", yscrollcommand=scroll_konfirmasi.set)
        scroll_konfirmasi.config(command=tree_konfirmasi.yview)

        for col in (_("pembelian.kode"), _("pembelian.nama"), _("pembelian.qty"), _("pembelian.harga"), _("pembelian.subtotal")):
            tree_konfirmasi.heading(col, text=col)
            tree_konfirmasi.column(col, anchor="center", width=100)
        
        tree_konfirmasi.pack(side="left", fill="both", expand=True)
        scroll_konfirmasi.pack(side="right", fill="y")

        total = 0
        for item in produk_terpilih:
            try :
                harga_format = f"Rp {int(float(item.get('harga_beli', 0))):,}"
                subtotal = item.get("qty", 0) * item.get("harga_beli", 0)
                subtotal_format = f"Rp {int(subtotal):,}"
            except Exception as e:
                print(_("pembelian.lbl_error_format"), e)
                harga_format = "Rp -"
                subtotal_format = "Rp -"
            tree_konfirmasi.insert("", "end", values=(item.get("kode_produk"), item.get("nama"), item.get("qty"), harga_format, subtotal_format))
        
        total_harga = sum(item.get("qty", 0) * item.get("harga_beli", 0) for item in produk_terpilih)
        total_format = f"Rp {int(total_harga):,}"
        tk.Label(frame_total, text=f"Total Price: {total_format}", font=("Segoe UI", 10, "bold")).pack(pady=5)

        def simpan_ke_db():
            supplier_id = supplier_map[supplier_nama]
            tambah_pembelian(supplier_id, produk_terpilih)
            messagebox.showinfo(_("pembelian.sukses"), _("pembelian.success_simpan"))
            window.destroy()
            muat_histori()
        tk.Button(window, text="OK", command=simpan_ke_db).pack(side="left", padx=20, pady=10)
        tk.Button(window, text=_("pembelian.batal"), command=window.destroy).pack(side="right", padx=20, pady=10)

    return buka_konfirmasi_pembelian

def build_histori_pembelian(frame):
    tree_histori = setup_treeview_histori(frame)
    muat_histori(tree_histori)
    return tree_histori

def setup_treeview_histori(frame):
    font_normal = ("Segoe UI", 10)
    frame_histori = tk.Frame(frame)
    frame_histori.pack(fill="both", expand=True, padx=10, pady=5)

    tk.Label(frame_histori, text=_("pembelian.lbl_frame_histori"), font=font_normal).pack(anchor="w")
    frame_histori_scroll = tk.Frame(frame_histori)
    frame_histori_scroll.pack(fill="both", expand=True)

    scroll_histori = tk.Scrollbar(frame_histori_scroll, orient="vertical")
    tree_histori = ttk.Treeview(frame_histori_scroll, columns=(_("pembelian.id"), _("pembelian.tanggal"), _("pembelian.supplier"), _("pembelian.total")), show="headings", yscrollcommand=scroll_histori.set)
    
    for col in (_("pembelian.id"), _("pembelian.tanggal"), _("pembelian.supplier"), _("pembelian.total")):
        tree_histori.heading(col, text=col)
        tree_histori.column(col, anchor="center", width=100)

    scroll_histori.config(command=tree_histori.yview)
    tree_histori.pack(side="left", fill="both", expand=True)
    scroll_histori.pack(side="right", fill="y")

    return tree_histori

def muat_histori(tree_histori):
    tree_histori.delete(*tree_histori.get_children())
    histori = get_histori_pembelian()
    for id_pembelian, tanggal, supplier_nama, total in histori:
        try:
            total_format = f"Rp {int(float(total)):,}"
        except Exception as e:
            print(_("pembelian.lbl_error_format"), e)
            total_format = "RP -"
        tree_histori.insert("", "end", values=(id_pembelian, tanggal, supplier_nama, total_format))

def simpan_pembelian(combo_supplier, tree_input, supplier_map, tree_histori):
    supplier_nama = combo_supplier.get()
    supplier_id = supplier_map.get(supplier_nama)
    if not supplier_id:
        messagebox.showerror("Error", _("pembelian.msg_supplier_belum"))
        return

    daftar_barang = []
    for row_id in tree_input.get_children():
        values = tree_input.item(row_id)["values"]
        if len (values) < 4:
            continue

        try:
            kode_produk = str(values[0]).strip()
            nama = str(values[1]).strip()
            qty_raw = values[2]
            harga_raw = values[3]

            qty = int(qty_raw)
            harga_beli = int(float(harga_raw))

            if qty > 0:
                daftar_barang.append({"kode_produk": kode_produk, "nama": nama, "qty": qty, "harga_beli": harga_beli})
        except Exception as e:
            print(_("pembelian.err_konversi"), e)
            continue

    if not daftar_barang:
        messagebox.showwarning(_("pembelian.kosong"), _("pembelian.msg_warning_tidak_ada"))
        return

    hasil = tambah_pembelian(supplier_id, daftar_barang)
    if hasil:
        messagebox.showinfo(_("pembelian.sukses"), _("pembelian.sukses_transaksi"))
        combo_supplier.set("")
        for row_id in tree_input.get_children():
            values = tree_input.item(row_id)["values"]
            if len(values) > 2:
                values[2] = 0 # Reset Jumlah
            tree_input.item(row_id, values=values)
    else:
        messagebox.showerror(_("pembelian.gagal"), _("pembelian.gagal_transaksi"))
    muat_histori(tree_histori)

def bersihkan_rupiah(rp_string):
    try :
        angka = rp_string.replace("Rp", "").replace(",","").strip()
        return float(angka)
    except Exception as e:
        print(_("pembelian.lbl_error_parsing"), rp_string, e)
        return 0.0

def tambah_produk(event, tree_input):
    item_id = tree_input.focus()
    if not item_id:
        return
    values = tree_input.item(item_id)["values"]
    kode_produk = values[1]
    nama_produk = values[2]
    jumlah_sekarang = int(values[3]) if str(values[3]).isdigit() else 0

    jumlah_baru = simpledialog.askinteger(_("pembelian.tambah_produk"), _("pembelian.jumlah_baru").format(nama=nama_produk), initialvalue=jumlah_sekarang, minvalue=1)
    if jumlah_baru:
        values[3] = jumlah_baru
        tree_input.item(item_id, values=values)
    if values[0] != "✔":
        messagebox.showinfo(_("pembelian.info"), _("pembelian.lbl_centang"))
        return

def build_histori_interaksi(frame, tree_histori, tree_input, combo_supplier, supplier_map):
    setup_detail_popup(tree_histori, frame)
    setup_btn_lihat_detail(tree_histori, frame)
    setup_btn_simpan_pembelian(combo_supplier, tree_input, supplier_map, frame)

def setup_detail_popup(tree_histori, frame):
    tampilkan_detail_manual(tree_histori, frame)

def setup_btn_simpan_pembelian(combo_supplier, tree_input, supplier_map, frame, tree_histori):
    def ambil_produk_terpilih():
        hasil = []
        for item_id in tree_input.get_children():
            values = tree_input.item(item_id)["values"]
            if values[0] == "✔" and int(values[3]) > 0:
                hasil.append({"kode_produk":values[1], "nama":values[2], "qty":int(values[3]), "harga_beli":int(bersihkan_rupiah(values[4]))})
        return hasil
    
    def buka_konfirmasi_pembelian():
        produk_terpilih = ambil_produk_terpilih()
        if not produk_terpilih:
            messagebox.showinfo(_("pembelian.info"), _("pembelian.lbl_tidak_dipilih"))
            return
        
        supplier_nama = combo_supplier.get()
        if not supplier_nama:
            messagebox.showinfo(_("pembelian.info"), _("pembelian.lbl_pilih_supplier"))
            return

        supplier_id = supplier_map[supplier_nama]
        hasil = tambah_pembelian(supplier_id, produk_terpilih)
        if hasil:
            messagebox.showinfo(_("pembelian.sukses"), _("pembelian.sukses_transaksi"))
            combo_supplier.set("")
            for row_id in tree_input.get_children():
                values = tree_input.item(row_id)["values"]
                values[3] = 0
                tree_input.item(row_id, values=values)
        else:
            messagebox.showerror(_("pembelian.gagal"), _("pembelian.gagal_transaksi"))
        muat_histori(tree_histori)

    return buka_konfirmasi_pembelian
   
def setup_btn_lihat_detail(tree_histori, frame):
    btn_lihat_detail = tk.Button(frame, text=_("pembelian.btn_lihat_detail"), command=lambda: tampilkan_detail_manual(tree_histori, frame))
    btn_lihat_detail.pack(pady=5)

def tampilkan_detail_manual(tree_histori, frame):
    selected = tree_histori.focus()
    if not selected:
        messagebox.showerror(_("pembelian.info"), _("pembelian.msg_pilih_histori"))
        return
    values = tree_histori.item(selected)["values"]
    pembelian_id = values[0] # Asumsi kolom pertama adalah ID
    detail = ambil_detail_terformat(pembelian_id)
    if not detail:
        messagebox.showinfo(_("pembelian.info"), _("pembelian.msg_detail_not_found"))
        return
    
    window = tk.Toplevel(frame)
    window.title(f"Transaction Detail #{pembelian_id}")
    window.geometry("500x400")

    tree_popup = setup_treeview_popup(window)
    for item in detail:
        harga_format = f"Rp {int(float(item.get('harga_beli', 0))):,}"
        tree_popup.insert("", "end", values=(item.get("kode_produk", "-"), item.get("nama_produk", "-"), item.get("qty", 0), harga_format))
    tree_popup.bind("<Double-1>", lambda e: edit_qty_popup(e, tree_popup))
    total_harga = sum(int(item("qty", 0)) * item(float(item.get("harga_beli", 0))) for item in detail)
    label_total = tk.Label(window, text=f"Total Price: Rp {total_harga:,}", font=("Segoe UI", 10, "bold"))
    label_total.pack(pady=5)
 
    def simpan_koreksi():
        hasil_koreksi = []
        for iid in tree_popup.get_children():
            v = tree_popup.item(iid)["values"]
            hasil_koreksi.append({"kode_produk": v[0], "nama_produk":v[1], "qty":int(v[2]), "harga_beli": int(bersihkan_angka(v[3]))})
        # Validasi: pastikan ada qty>0
        if not any(item["qty"] > 0 for item in hasil_koreksi):
            messagebox.showwarning(_("pembelian.gagal"), _("pembelian.msg_warning"))
            return
        if not messagebox.askyesno(_("pembelian.konfirmasi"), _("pembelian.msg_konfirmasi")):
            return
        update_pembelian(pembelian_id, hasil_koreksi)
        messagebox.showinfo(_("pembelian.sukses"), _("pembelian.msg_info"))
        muat_histori(tree_histori)
        window.destroy()

    def edit_qty_popup(event, tree):
        item_id = tree.identify_row(event.y)
        col = tree.identify_column(event.x)

        if not item_id or col != "#3": # Kolom ke 3 --> Qty
            return
        values = tree.item(item_id)["values"]
        nama_produk = values[1]
        qty_sekarang = int(values[2]) if str(values[2]).isdigit() else 0

        qty_baru = simpledialog.askinteger(_("pembelian.simpledialog"), _("pembelian.qty_baru").format(nama=nama_produk), initialvalue=qty_sekarang, minvalue=0)
        if qty_baru is not None:
            values[2] = qty_baru
            tree.item(item_id, values=values)

    def batal_koreksi():
        window.destroy()

    frame_btn = tk.Frame(window)
    frame_btn.pack(pady=10)
    tk.Button(frame_btn, text=_("pembelian.btn_simpan_koreksi"), command=simpan_koreksi).pack(side="left", padx=10)
    tk.Button(frame_btn, text=_("pembelian.btn_frame_batal"), command=batal_koreksi).pack(side="right", padx=10)

def setup_treeview_popup(window):
    frame_popup_scroll = tk.Frame(window)
    frame_popup_scroll.pack(fill="both", expand=True)

    scroll_popup = tk.Scrollbar(frame_popup_scroll, orient="vertical")
    tree_popup = ttk.Treeview(frame_popup_scroll, columns=(_("pembelian.kode"), _("pembelian.nama"), _("pembelian.qty"), _("pembelian.harga")), show="headings", yscrollcommand=scroll_popup.set)
    scroll_popup.config(command=tree_popup.yview)

    for col in (_("pembelian.kode"), _("pembelian.nama"), _("pembelian.qty"), _("pembelian.harga")):
        tree_popup.heading(col, text=col)
        tree_popup.column(col, anchor="center", width=100)
    tree_popup.pack(side="left", fill="both", expand=True)
    scroll_popup.pack(side="right", fill="y")
    return tree_popup

def bind_edit_jumlah_popup(tree_popup, label_total):
    def edit_jumlah_popup(event):
        item_id = tree_popup.focus()
        if not item_id:
            return
        values = tree_popup.item(item_id)["values"]
        nama_produk = values[1]
        try:
            jumlah_sekarang = int(values[2])
        except:
            jumlah_sekarang = 0
        jumlah_baru = simpledialog.askinteger(_("pembelian.simpledialog"), _("pembelian.jumlah_baru").format(nama=nama_produk)
                                              , initialvalue=jumlah_sekarang, minvalue=0)
        if jumlah_baru is not None:
            if jumlah_baru == 0:
                messagebox.showwarning("Invalid", _("pembelian.msg_show_min"))
                return
            values[2] = jumlah_baru
            tree_popup.item(item_id, values=values)

            total = sum(int(tree_popup.item(iid)["values"][2]) * int(float(tree_popup.item(iid)["values"][3])) for iid in tree_popup.get_children())
            label_total.config(text=_("pembelian.total_harga").format(to=total),)
    tree_popup.bind("<Double-1>", edit_jumlah_popup)

def ambil_detail_terformat(pembelian_id):
    detail = get_detail_pembelian(pembelian_id)
    hasil = []
    for kode, qty, harga in detail:
        kode_bersih = str(kode).strip()
        nama = get_produk_nama(kode_bersih)
        hasil.append({
            "kode_produk": kode_bersih,
            "nama_produk": nama,
            "qty": qty,
            "harga_beli": harga
        })
    return hasil

if __name__ == "__main__":
    root = tk.Tk()
    root.title_(("pembelian.root_title"))
    buat_frame_pembelian()
    root.mainloop()