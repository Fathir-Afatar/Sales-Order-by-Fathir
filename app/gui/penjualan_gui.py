# Standard Library
import sys, os

# Third-party
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
from tkinter import ttk, messagebox

# Local application
from app.core.penjualan_core import (proses_penjualan, get_daftar_member
                                     , load_transaksi_rincian, handler_cek_nama_member
                                     , get_selected_transaksi_id, get_detail_transaksi)
from app.core.product_core import semua_produk
from app.constants.config import get_connection
from app.core.pengaturan_core import format_nota_thermal, cetak_nota_thermal
from app.translator import _, i18n

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

transaksi_terakhir = None

def buat_frame_penjualan(parent, set_judul_modul):
    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True)
    set_judul_modul(_("penjualan.set_judul_modul"))

    # Tabs & Produk
    tab_transaksi, tab_rincian = buat_notebook_penjualan(frame)
    produk_list, produk_display_list = ambil_produk_dan_display()
    form_refs = buat_form_input_penjualan(tab_transaksi, produk_display_list)
    tree, keranjang = buat_keranjang_penjualan(tab_transaksi)

    # Bind search dan pilih produk
    form_refs["produk_entry"].bind("<KeyRelease>", lambda e: filter_produk(form_refs, produk_display_list))
    form_refs["produk_listbox"].bind("<<ListboxSelect>>", lambda e: pilih_produk(form_refs))
    form_refs["ongkir_entry"].bind("<KeyRelease>", lambda e: update_total(form_refs, keranjang))

    # ------- State Transaksi -----
    state_transaksi = {
        "terakhir_id": None,
        "pembeli": "-",
        "ongkir": 0,
        "total":0
    }
    #------Handler Tombol -----------
    def tambah_ke_keranjang():
        tambah_item_ke_keranjang(form_refs, produk_display_list, keranjang, tree)
    
    def simpan_transaksi():
        proses_transaksi(form_refs, keranjang, tree, rincian_tree, state_transaksi, lambda: update_total(form_refs, keranjang))
    
    def hapus_produk():
        hapus_produk_terpilih(tree, keranjang, lambda: update_total(form_refs, keranjang))
    
    def reset_transaksi_gui():
        reset_transaksi(form_refs, keranjang, tree, lambda: update_total(form_refs, keranjang))
    
    def preview_nota_gui():
        preview_nota(
            state_transaksi["terakhir_id"],
            state_transaksi["pembeli"],
            keranjang,
            state_transaksi["total"],
            ongkir=state_transaksi["ongkir"]
        )
    tombol_handlers = {
        "tambah": tambah_ke_keranjang,
        "simpan": simpan_transaksi,
        "hapus": hapus_produk,
        "reset": reset_transaksi_gui,
        "preview": preview_nota_gui
    }

    buat_tombol_penjualan(form_refs["tombol_frame"], tombol_handlers, state_transaksi)
    # ------- Tab Rincian ------

    rincian_tree, detail_frame = buat_tab_rincian(tab_rincian)
    load_transaksi_rincian(rincian_tree)

    tk.Button(detail_frame, text=_("penjualan.btn_detail_frame"), command=lambda: 
              lihat_detail_transaksi_cetak(rincian_tree)).grid(row=0, column=0, padx=5)

    tk.Button(form_refs["form_frame"], text=_("penjualan.cek"), command=lambda:
              handler_cek_nama_member(form_refs["member_var"], form_refs["nama_member_label"]
                                      , form_refs["daftar_member"])).grid(row=3, column=2, padx=5)

    return frame

def buat_notebook_penjualan(frame):
    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    tab_transaksi = tk.Frame(notebook)
    tab_rincian = tk.Frame(notebook)

    notebook.add(tab_transaksi, text=_("penjualan.tab_transaksi"))
    notebook.add(tab_rincian, text=_("penjualan.tab_rincian"))
    return tab_transaksi, tab_rincian

def ambil_produk_dan_display():
    produk_list = semua_produk()
    produk_display_list = {
        f"{p['nama_produk']} (ID {p['id_produk']})": p for p in produk_list
    }
    return produk_list, produk_display_list

def buat_form_input_penjualan(tab_transaksi, produk_display_list):
    produk_var = tk.StringVar()
    total_var = tk.StringVar(value="Total: Rp0")
    member_var = tk.StringVar()

    form_frame = tk.Frame(tab_transaksi)
    form_frame.grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=10)

    tombol_frame = tk.Frame(tab_transaksi)
    tombol_frame.grid(row=1, column=0, columnspan=4, pady=10)

    produk_entry = tk.Entry(form_frame, textvariable=produk_var, width=40)
    produk_entry.grid(row=0, column=1, padx=5)

    produk_listbox = tk.Listbox(form_frame, width=40, height=5)
    produk_listbox.grid(row=1, column=1, padx=5, pady=5)
    produk_listbox.grid_remove()

    jumlah_entry = tk.Entry(form_frame, width=10)
    jumlah_entry.grid(row=2, column=1, sticky="w", padx=5)

    member_entry = tk.Entry(form_frame, textvariable=member_var, width=40)
    member_entry.grid(row=3, column=1, padx=5, pady=5)

    member_listbox = tk.Listbox(form_frame, width=40, height=5)
    member_listbox.grid(row=4, column=1, padx=5, pady=5)
    member_listbox.grid_remove()

    harga_manual_entry = tk.Entry(form_frame, width=15)
    harga_manual_entry.grid(row=4, column=1, sticky="w", padx=5)

    ongkir_entry = tk.Entry(form_frame, width=15)
    ongkir_entry.grid(row=6, column=1, sticky="w", padx=5)
    
    nama_member_label = tk.Label(form_frame, text=_("penjualan.nama_member_label"), font=("Arial", 10), fg="blue")
    nama_member_label.grid(row=3, column=3, padx=5, pady=2, sticky="w")

    total_label = tk.Label(form_frame, textvariable=total_var, font=("Segoe UI", 12, "bold"), anchor="e")
    total_label.grid(row=8, column=1, sticky="e", padx=10, pady=(10, 0))

    daftar_member = get_daftar_member()

    def update_member_listbox(event=None):
        typed = member_var.get().lower()
        member_listbox.delete(0, tk.END)
        filtered = [m for m in daftar_member if typed in m["nama"].lower()]
        for m in filtered:
            member_listbox.insert(tk.END, m["nama"])
        member_listbox.grid() if filtered else member_listbox.grid_remove()
    
    def pilih_member(event=None):
        selected = member_listbox.get(tk.ACTIVE)
        member_var.set(selected)
        member_listbox.grid_remove()

    member_entry.bind("<KeyRelease>", update_member_listbox)
    member_listbox.bind("<<ListboxSelect>>", pilih_member)

    tk.Label(form_frame, text=_("penjualan.pilih_produk")).grid(row=0, column=0, sticky="w")
    tk.Label(form_frame, text=_("penjualan.jumlah")).grid(row=2, column=0, sticky="w")
    tk.Label(form_frame, text=_("penjualan.nama_member")).grid(row=3, column=0, sticky="w")
    tk.Label(form_frame, text=_("penjualan.harga_manual")).grid(row=4, column=0, sticky="w")
    tk.Label(form_frame, text=_("penjualan.ongkir")).grid(row=6, column=0, sticky="w")
    tk.Label(form_frame, text=_("penjualan.label_harga_default"), fg="gray").grid(row=5, column=1, sticky="w")
    tk.Label(form_frame, text=_("penjualan.label_ongkir"), fg="gray").grid(row=7, column=1, sticky="w")

    return {
        "form_frame": form_frame,
        "produk_var": produk_var,
        "total_var": total_var,
        "produk_entry": produk_entry,
        "produk_listbox": produk_listbox,
        "jumlah_entry": jumlah_entry,
        "nama_member_label": nama_member_label,
        "member_var": member_var,
        "member_entry": member_entry,
        "member_listbox": member_listbox,
        "daftar_member": daftar_member,
        "harga_manual_entry": harga_manual_entry,
        "ongkir_entry": ongkir_entry,
        "tombol_frame": tombol_frame,
        "total_var": total_var,
        "total_label": total_label
    }

def buat_keranjang_penjualan(tab_transaksi):
    keranjang_frame = tk.Frame(tab_transaksi)
    keranjang_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

    keranjang_scroll = tk.Scrollbar(keranjang_frame, orient="vertical")
    keranjang_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(keranjang_frame
                        , columns=(_("penjualan.produk"), _("penjualan.jumlah")
                                   , _("penjualan.harga"), _("penjualan.subtotal"))
                                   , show="headings", yscrollcommand=keranjang_scroll.set)
    for col in (_("penjualan.produk"), _("penjualan.jumlah"), _("penjualan.harga"), _("penjualan.subtotal")):
        tree.heading(col, text=col)
        tree.column(col, anchor="center")
    tree.pack(fill="both", expand=True)

    keranjang_scroll.config(command=tree.yview)
    keranjang = []

    return tree, keranjang

def filter_produk(refs, produk_display_list):
    typed = refs["produk_var"].get().lower()
    listbox = refs["produk_listbox"]
    listbox.delete(0, tk.END)
    matches = [item for item in produk_display_list if typed in item.lower()]
    if matches:
        for item in matches:
            listbox.insert(tk.END, item)
        listbox.grid()
    else:
        listbox.grid_remove()

def pilih_produk(refs):
    listbox = refs["produk_listbox"]
    selection = listbox.curselection()
    if selection:
        selected = listbox.get(selection[0])
        refs["produk_var"].set(selected)
        listbox.delete(0, tk.END)
        listbox.grid_remove()

def tambah_item_ke_keranjang(refs, produk_display_list, keranjang, tree):
    nama_produk_gui = refs["produk_var"].get()
    produk_data = produk_display_list.get(nama_produk_gui)
    if not produk_data:
        messagebox.showerror(_("penjualan.error"), _("penjualan.err_pilih_produk"))
        return
    
    harga_input = refs["harga_manual_entry"].get().strip()
    try:
        harga_satuan = float(harga_input) if harga_input else produk_data["harga_jual"]
    except ValueError:
        messagebox.showerror(_("penjualan.error"), _("penjualan.err_harga_manual"))
        return

    try:
        jumlah = int(refs["jumlah_entry"].get())
        if jumlah <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror(_("penjualan.error"), _("penjualan.err_jumlah_positif"))
        return
    
    produk_id = produk_data["id_produk"]
    subtotal = harga_satuan * jumlah

    keranjang.append({
        "produk_id": produk_id,
        "produk_nama": nama_produk_gui,
        "jumlah": jumlah,
        "harga_satuan": harga_satuan,
        "subtotal": subtotal
    })

    tree.insert("", tk.END, values=(nama_produk_gui, jumlah, f"Rp {harga_satuan:,.0f}", f"Rp {subtotal:,.0f}"))
    refs["jumlah_entry"].delete(0, tk.END)
    refs["harga_manual_entry"].delete(0, tk.END)
    update_total(refs, keranjang)

def update_total(refs, keranjang):
    total = sum(item["subtotal"] for item in keranjang)
    try:
        ongkir_input = refs["ongkir_entry"].get().strip()
        ongkir = float(ongkir_input) if ongkir_input else 0
        total += ongkir
    except:
        pass

    refs["total_var"].set(f"Total: Rp{total:,.0f}")

def hapus_produk_terpilih(tree, keranjang, update_total_fn):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning(_("penjualan.war_hapus"), _("penjualan.pilih_baris_produk"))
        return
    item_values = tree.item(selected_item)["values"]
    nama_produk = item_values[0]
    jumlah = item_values[1]

    for i, item in enumerate(keranjang):
        if item["produk_nama"] == nama_produk and item["jumlah"] == jumlah:
            keranjang.pop(i)
            break
    tree.delete(selected_item)
    update_total_fn()

def reset_transaksi(refs, keranjang, tree, update_total_fn):
    keranjang.clear()
    tree.delete(*tree.get_children())
    refs["jumlah_entry"].delete(0, tk.END)
    refs["produk_var"].set("")
    refs["member_entry"].delete(0, tk.END)
    refs["ongkir_entry"].delete(0, tk.END)
    update_total_fn()

def preview_nota(transaksi_id, pembeli, keranjang, total, status="DRAFT", ongkir=0):
    nota_text = format_nota_thermal(transaksi_id, pembeli, keranjang, total, status=status, ongkir=ongkir)

    preview_window = tk.Toplevel()
    preview_window.title(f"Preview Nota - Transaksi #{transaksi_id}")
    preview_window.geometry("400x500")

    text_area = tk.Text(preview_window, wrap="word", font=("Courier New", 10))
    text_area.insert(tk.END, nota_text)
    text_area.config(state="disabled")
    text_area.pack(fill="both", expand=True, padx=10, pady=10)

    cetak_button = tk.Button(preview_window, text=_("penjualan.btn_cetak")
                             , font=("Arial", 10), bg="green", fg="white", command=lambda: cetak_nota_thermal(transaksi_id))
    cetak_button.pack(pady=10)


def proses_transaksi(refs, keranjang, tree, rincian_tree, state_transaksi, update_total_fn):
    ongkir_input = refs["ongkir_entry"].get().strip()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        nama_dipilih = refs["member_var"].get().strip()
        daftar_member = refs["daftar_member"]
        member_id = next((m["id"] for m in refs["daftar_member"] if m["nama"] == nama_dipilih), None)
        pembeli = nama_dipilih if member_id else "[Tidak ditemukan]"
        ongkir = float(ongkir_input) if ongkir_input else 0
        total_barang = sum(i["subtotal"] for i in keranjang)
        total = total_barang + ongkir

        transaksi_id = proses_penjualan({
            "member_id": member_id,
            "nama_member": pembeli,
            "daftar_barang": keranjang,
            "ongkos_kirim": ongkir
        })
        state_transaksi.update({
            "terakhir_id": transaksi_id,
            "pembeli": pembeli,
            "ongkir": ongkir,
            "total": total
        })

        simpan_nota_csv(transaksi_id, pembeli, keranjang, total, ongkir)
        preview_nota(transaksi_id, pembeli, keranjang, total, ongkir=ongkir)
        tree.after(100, lambda: load_transaksi_rincian(rincian_tree))
        reset_transaksi(refs, keranjang, tree, update_total_fn)
        messagebox.showinfo(_("penjualan.sukses"), _("penjualan.bsg_transaksi_sukses").format(id=transaksi_id),)
    
    except Exception as e:
        messagebox.showerror(_("penjualan.error"), str(e))
    finally:
        conn.close()

def simpan_nota_csv(transaksi_id, pembeli, keranjang, total, ongkir=0):
    nota = format_nota_thermal(transaksi_id, pembeli, keranjang, total, ongkir=ongkir)
    filename = f"nota_{transaksi_id}.txt"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        f.write(nota)
    messagebox.showinfo(_("penjualan.nota"), _("penjualan.msg_nota_transaksi").format(file=filename),)

def buat_tombol_penjualan(frame, handlers, state_refs):
    tk.Button(frame, text=_("penjualan.tambah_keranjang"), command=handlers["tambah"]).grid(row=0, column=0, padx=5)
    tk.Button(frame, text=_("penjualan.simpan"), command=handlers["simpan"]).grid(row=0, column=1, padx=5)
    tk.Button(frame, text=_("penjualan.hapus_produk"), command=handlers["hapus"]).grid(row=0, column=2, padx=5)
    tk.Button(frame, text="Reset", command=handlers["reset"]).grid(row=0, column=3, padx=5)

def buat_treeview_keranjang(frame, scroll):
    """
    Deprecated
    """
    tree = ttk.Treeview(frame, columns=("Produk", "Jumlah", "Harga", "Subtotal"), show="headings", height=10, yscrollcommand=scroll.set)
    for col in ("Produk", "Jumlah", "Harga", "Subtotal"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)
    tree.pack(side="left", fill="both", expand=True)
    scroll.config(command=tree.yview)
    return tree

def buat_label_total(frame, total_var):
    """
    Deprecated
    """
    label = ttk.Label(frame, textvariable=total_var, font=("Arial", 12, "bold"))
    label.grid(row=3, column=0, columnspan=4, pady=10)
    return label

def buat_tab_rincian(tab_rincian):
    tk.Label(tab_rincian, text=_("penjualan.label_rincian"), font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)

    tree_frame = tk.Frame(tab_rincian)
    tree_frame.grid(row=1, column=0, padx=10, pady=10)
    
    scroll = tk.Scrollbar(tree_frame, orient="vertical")
    scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(tree_frame, columns=(
        _("penjualan.id"), _("penjualan.tanggal"), _("penjualan.total"), _("penjualan.status")
        ), show="headings", height=15, yscrollcommand=scroll.set)
    for col in (_("penjualan.id"), _("penjualan.tanggal"), _("penjualan.total"), _("penjualan.status")):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)
    tree.pack(side="left", fill="both", expand=True)
    scroll.config(command=tree.yview)

    detail_frame = tk.Frame(tab_rincian)
    detail_frame.grid(row=2, column=0, pady=10)

    return tree, detail_frame
    
def lihat_detail_transaksi_cetak(tree):
    transaksi_id = get_selected_transaksi_id(tree)
    if not transaksi_id:
        return
    
    transaksi_info, item_dicts = get_detail_transaksi(transaksi_id)
    if not transaksi_info:
        return
    
    nota_text = format_nota_thermal(
        transaksi_id, 
        transaksi_info["pembeli"], 
        item_dicts, 
        transaksi_info["total"], 
        status=transaksi_info["status"], 
        ongkir=transaksi_info["ongkir"], 
        tanggal=transaksi_info["tanggal"]
    )

    popup = tk.Toplevel()
    popup.title(_("penjualan.detail_cetak_nota").format(id=transaksi_id),)
    popup.geometry("400x500")

    text_area = tk.Text(popup, wrap="word", font=("Courier New", 10))
    text_area.insert(tk.END, nota_text)
    text_area.config(state="disabled")
    text_area.pack(fill="both", expand=True, padx=10, pady=10)

    btn_download = tk.Button(popup, text=_("penjualan.btn_download"), bg="blue", 
        fg="white", command=lambda: simpan_nota_sebagai_gambar(nota_text, transaksi_id)
    )
    btn_download.pack(pady=5)

    cetak_button = tk.Button(popup, text=_("penjualan.btn_cetak"), font=("Arial", 10), 
        bg="green", fg="white", padx=10, pady=5, command=lambda: cetak_nota_thermal(transaksi_id)
    )
    cetak_button.pack(pady=10)

def simpan_nota_sebagai_gambar(nota_text, transaksi_id):
    font_path = "C:/Windows/Fonts/consola.ttf"
    font = ImageFont.truetype(font_path, 14)

    lines = nota_text.split("\n")
    max_width = max([font.getlength(line) for line in lines]) + 20
    line_height = font.getbbox("A")[3] + 6
    img_height = line_height * len(lines) + 20

    img = Image.new("RGB", (int(max_width), img_height), color="white")
    draw = ImageDraw.Draw(img)

    # Gambar teks
    y = 10
    for line in lines:
        draw.text((10, y), line, font=font, fill="black")
        y += line_height
    
    # Simpan
    filename = f"nota_{transaksi_id}.png"
    img.save(filename)
    messagebox.showinfo(_("penjualan.sukses"), _("penjualan.simpan_nota").format(file=filename))

if __name__ == "__main__":
    buat_frame_penjualan()