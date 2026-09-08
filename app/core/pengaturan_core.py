# Standard library
import json
import os
import usb.core
import usb.backend.libusb1
import time
import sqlite3
#from escpos.printer import Usb

# Third-party
from datetime import datetime

# Local application
from app.constants.config import get_connection
from app.core.debug_core import log_cetak_gagal, log_info, log_error
from app.core.printer_core import ambil_printer_default
from local_escpos.printer import Usb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "..", "..", "config")
NOTA_CONFIG_PATH = os.path.join(CONFIG_DIR, "nota_config.json")
PRINTER_CONFIG_PATH = os.path.join(CONFIG_DIR,"printer_config.json")

def simpan_format_nota(data):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(NOTA_CONFIG_PATH, "w")  as f:
        json.dump(data, f, indent=4)

def ambil_format_nota():
    if not os.path.exists(NOTA_CONFIG_PATH):
        return{
            "header": "Toko POS Pintar",
            "footer": "Terimakasih",
            "font_size": 12,
            "margin_kiri": 5,
            "margin_kanan": 5,
            "lebar_kertas": "58mm"
        }
    with open(NOTA_CONFIG_PATH, "r") as f:
        return json.load(f)

def get_usb_printer_list():
    try:
        backend = usb.backend.libusb1.get_backend()
        devices = usb.core.find(find_all=True, backend=backend)
        printer_list = []
        for dev in devices:
            print(f"[DEBUG] Detected USB device: {hex(dev.idVendor)}:{hex(dev.idProduct)}")
            if dev.idVendor and dev.idProduct:
                vendor = hex(dev.idVendor)[2:] # hilangkan '0x'
                product = hex(dev.idProduct)[2:]
                printer_list.append(f"{vendor}:{product}")
        return printer_list
    except Exception as e:
        print("[ERROR] Gagal medeteksi printer USB:", e)
        return []

def simpan_printer_default(vendor_id, product_id):
    config_dir = os.path.join(os.getcwd(), "config")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "printer_config.json")
    data = {"vendor_id": vendor_id, "product_id": product_id}
    try:
        with open(config_path, "w") as f:
            json.dump(data, f)
        print("[INFO] Printer default berhasil disimpan:", data)
    except Exception as e:
        print("[ERROR] Gagal menyimpan printer default:", e)

def test_cetak_usb(vendor_id, product_id, text="Tes cetak berhasil."):
    try:
        printer = Usb(vendor_id, product_id, close_port_after_job=True)
        printer.open()
        printer.text(text + "\n")
        printer.text("Printer ini siap digunakan.\n")
        printer.cut()
        printer.close()
        log_info(f"Tes berhasil ke printer ({vendor_id}, {product_id})")
        return True
    except Exception as e:
        print("[ERROR] Tes cetak gagal:", e)
        return False
    
LEBAR_BARIS = 42

def format_tanggal_indonesia(dt):
    bulan_map = {
        "01": "Januari", "02": "Februari", "03": "Maret", "04": "April",
        "05": "Mei", "06": "Juni", "07": "Juli", "08": "Agustus",
        "09": "September", "10": "Oktober", "11": "November", "12": "Desember"
    }
    tanggal_obj = dt if isinstance(dt, datetime) else datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    hari = tanggal_obj.strftime("%d")
    bulan = bulan_map[tanggal_obj.strftime("%m")]
    tahun = tanggal_obj.strftime("%Y")
    return f"{hari} {bulan} {tahun}"

def format_item_thermal(nama, harga, qty, subtotal, max_width=LEBAR_BARIS):
    lines = []
    nama = nama[:30] if len(nama) > 30 else nama
    lines.append(f"{nama:<30}{subtotal:>12,.0f}")
    lines.append(f"{qty} x {harga:,.0f}")
    return "\n".join(lines)                                   

def format_nota_thermal(transaksi_id, pembeli, items, total, status="DRAFT", ongkir=0, tanggal = None):
    from app.core.pengaturan_core import ambil_format_nota
    config = ambil_format_nota()
    tanggal_str = format_tanggal_indonesia(tanggal or datetime.now())
    lines = []

    lines.append("=" * LEBAR_BARIS)
    for baris in config["header"].split("\n"):
        lines.append(baris.strip().center(LEBAR_BARIS))
    lines.append("=" * LEBAR_BARIS)
    lines.append(f"Transaksi : #{transaksi_id}")
    lines.append(f"Tanggal   : {tanggal_str}")
    lines.append(f"Pembeli   : {pembeli}")
    lines.append(f"-" * LEBAR_BARIS)
    lines.append(f"{'Produk':<30} {'Subtotal':>12}")
    lines.append("-" * LEBAR_BARIS)

    for item in items:
        lines.append(format_item_thermal(
            item["produk_nama"],
            item["harga_satuan"],
            item["jumlah"],
            item["subtotal"]
            ))
        
        if item.get("diskon"):
            lines.append(f"{'Diskon':<30}{item['diskon']:>12,.0f}")
        if item.get("catatan"):
            lines.append(f"{'Catatan':<9} {item['catatan'][:LEBAR_BARIS-9]}")
    
    lines.append("-" * LEBAR_BARIS)
    lines.append(f"{'Subtotal':<24}{f'Rp {total - ongkir:,.0f}':>18}")
    lines.append(f"{'Ongkir':<24}{f'Rp {ongkir:,.0f}':>18}")
    lines.append(f"{'Total':<24}{f'Rp {total:,.0f}':>18}")
    lines.append("=" * LEBAR_BARIS)
    for baris in config["footer"].split("\n"):
        lines.append(baris.strip().center(LEBAR_BARIS))
    lines.append("=" * LEBAR_BARIS)
    return "\n".join(lines)

def cetak_nota_thermal(transaksi_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()    
    try:
        # Ambil transaksi utama
        cursor.execute("""
            SELECT tanggal, nama_member, total_harga, ongkos_kirim
            FROM transaksi_penjualan
            WHERE id_transaksi = ?
        """, (transaksi_id,))
        transaksi = cursor.fetchone()
        if not transaksi:
            print("[ERROR] Transaksi tidak ditemukan.")
            return
        
        tanggal = transaksi["tanggal"]
        pembeli = transaksi["nama_member"] or "-"
        total = transaksi["total_harga"]
        ongkir = transaksi["ongkos_kirim"]

        # Ambil Detail barang
        cursor.execute("""
            SELECT nama_produk AS produk_nama, jumlah, harga_satuan, subtotal 
            FROM detail_penjualan
            WHERE transaksi_id = ?
        """, (transaksi_id,))
        items = [dict(row) for row in cursor.fetchall()]
        # Format nota pakai yang sudah ada
        nota_str = format_nota_thermal(transaksi_id, pembeli, items, total, ongkir=ongkir, tanggal=tanggal)
        # Kirim ke printer thermal
        try:
            printer_info = ambil_printer_default()
            vendor_id = int(printer_info["vendor_id"], 16)
            product_id = int(printer_info["product_id"], 16)
            backend = usb.backend.libusb1.get_backend()

            p = Usb(vendor_id, product_id, backend=backend, close_port_after_job=True)
            p.open()
            p.text(nota_str)
            p.cut()
            p.close()
            time.sleep(0.5)
            print("[INFO] Nota berhasil dicetak ke printer thermal.")
        except Exception as e:
            log_cetak_gagal(transaksi_id, str(e))
            # Fallback ke file
            fallback_path = os.path.join("debug", f"nota_fallback_{transaksi_id}.txt")
            os.makedirs("debug", exist_ok=True)
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write(nota_str)
            log_info(f"Fallback cetak nota transaksi #{transaksi_id} disimpan ke {fallback_path}")
            print("[ERROR] Gagal mencetak nota:", e)
    finally:
         conn.close()

def simulasi_cetak_nota(transaksi_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try: 
        # Ambil transaksi utama
        cursor.execute("""
            SELECT tanggal, nama_member, total_harga, ongkos_kirim
            FROM transaksi_penjualan
            WHERE id_transaksi = ?
        """, (transaksi_id,))
        transaksi = cursor.fetchone()
        if not transaksi:
            print("[ERROR] Transaksi tidak ditemukan.")
            return
        
        tanggal = transaksi["tanggal"]
        pembeli = transaksi["nama_member"] or "-"
        total = transaksi["total_harga"]
        ongkir = transaksi["ongkos_kirim"]

        # Ambil Detail barang
        cursor.execute("""
            SELECT nama_produk AS produk_nama, jumlah, harga_satuan, subtotal 
            FROM detail_penjualan
            WHERE transaksi_id = ?
        """, (transaksi_id,))
        items = [dict(row) for row in cursor.fetchall()]
        # Format nota pakai yang sudah ada
        nota_str = format_nota_thermal(
            transaksi_id, 
            transaksi["nama_member"] or "-", 
            items, 
            transaksi["total_harga"], 
            ongkir=transaksi["ongkos_kirim"], 
            tanggal=transaksi["tanggal"]
            )
        # Simpan ke file .txt

        os.makedirs("debug", exist_ok=True)
        path = os.path.join("debug", f"nota_simulasi{transaksi_id}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(nota_str)
        log_info(f"Simulasi cekta nota transaksi #{transaksi_id} disimpan ke {path}")
        return {"status": "Berhasil", "lokasi": path}

    except Exception as e:
        log_error(f"Simulasi cetak gagal untuk transaksi #{transaksi_id}", e)
        return {"status": "Gagal", "error": str(e)}
    finally:
        conn.close()

