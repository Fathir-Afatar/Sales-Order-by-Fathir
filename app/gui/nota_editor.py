# Standard Library
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

CONFIG_PATH = r"C:\Users\Fathir\Documents\pos-pintar-by-fathir\config\nota_config.json"

def simpan_config(data):
    """Persist system configuration settings to a local JSON file.

    Args:
        data (Dict[str, str]): Dictionary containing configuration keys and
            values.
    """
    os.makedirs("config", exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)
    messagebox.showinfo("Disimpan", "Pengaturan nota berhasil disimpan!")

def pilih_logo():
    """Open a file dialog to select an image file for the store logo."""
    path = filedialog.askopenfilename(title="Pilih Logo", filetypes=[("Image Files", "*.png*.jpg")])
    entry_logo.delete(0, tk.END)
    entry_logo.insert(0, path)

def main():
    """Initialize and render the main receipt configuration editor window."""
    global entry_kop, entry_footer, entry_logo

    window = tk.Tk()
    window.title("Editor Nota - POS Pintar")
    window.geometry("500x400")

    tk.Label(window, text="Nama Ranting / Cabang").pack()
    entry_ranting = tk.Entry(window, width=60)
    entry_ranting.pack(pady=5)

    tk.Label(window, text="Kop Nota(Nama Toko / Alamat)").pack()
    entry_kop = tk.Entry(window, width=60)
    entry_kop.pack(pady=5)

    tk.Label(window, text="Logo Toko (PNG/JPG)").pack()
    entry_logo = tk.Entry(window, width=60)
    entry_logo.pack(pady=5)
    tk.Button(window, text="Pilih Logo", command=pilih_logo).pack()

    tk.Label(window, text="Footer / Ucapan").pack()
    entry_footer = tk.Entry(window, width=60)
    entry_footer.pack(pady=5)

    def simpan():
        """Extract form values and invoke configuration storage."""
        data = {
            "kop": entry_kop.get(),
            "logo": entry_logo.get(),
            "footer": entry_footer.get(),
            "ranting": entry_ranting.get()
        }
        simpan_config(data)
    
    tk.Button(window, text="Simpan Pengaturan", command=simpan).pack(pady=10)

    tk.Button(window, text="Preview Nota", command=preview_nota).pack(pady=5)

    window.mainloop()

def preview_nota():
    """Launch a preview modal dialog rendering receipt details with dummy data."""
    if not os.path.exists(CONFIG_PATH):
        messagebox.showerror("Error", "Config belum tersedia!")
        return
    
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    
    transaksi_dummy = {
        "tanggal": "2025-07-18",
        "id": "TRX0021",
        "member": "Budi",
        "Ranting" : "Timur",
        "barang" : [
            {"nama": "Kopi Sachet", "qty": 2, "harga":5000},
            {"nama": "Gula pasir", "qty" : 1, "harga": 10000}
        ]
    }
    win = tk.Toplevel()
    win.title("Preview Nota")
    frame = tk.Frame(win, padx=10, pady=10)
    frame.pack()

    ranting = config.get("ranting", "Timur")
    tk.Label(frame, text=f"Ranting: {ranting}").pack(anchor="w")

    logo_path = config.get("logo", "")
    top_frame = tk.Frame(frame)
    top_frame.pack()

    if logo_path and os.path.exists(logo_path):
        try:
            img = tk.PhotoImage(file=logo_path)
            logo_label = tk.Label(top_frame, image=img)
            logo_label.image = img
            logo_label.pack(side="left")
        except:
            tk.Label(top_frame, text="[Logo gagal dimuat]").pack(side="left")
                     
    kop_label = tk.Label(top_frame, text=config.get("kop", "POS Pintar "), font=("Helvetica", 12, "bold"), justify="left")
    kop_label.pack(side="left", padx=10)
    
    tk.Label(frame, text="-" * 45).pack()

    info = transaksi_dummy
    tk.Label(frame, text=f"Tanggal: {info['tanggal']} ID:{info['id']}").pack(anchor="w")
    tk.Label(frame, text=f"Member: {info['member']} Ranting: {ranting}").pack(anchor="w")

    tk.Label(frame, text="-" * 45).pack()

    total = 0
    for item in info["barang"]:
        subtotal = item["qty"] * item["harga"]
        total += subtotal
        baris = f"{item['nama']} x{item['qty']} @Rp{item['harga']:,} Rp{subtotal:,}"
        tk.Label(frame, text=baris).pack(anchor="w")
    
    tk.Label(frame, text= "-" * 45).pack()
    tk.Label(frame, text=f"Total: {'':.25} Rp{total:,},", font=("Helvetica", 10, "bold")).pack(anchor="e", pady=5)

    tk.Label(frame, text=config.get("foooter", ""), font=("Helvetica", 9, "italic")).pack()
    

if __name__ == "__main__":
    main()
