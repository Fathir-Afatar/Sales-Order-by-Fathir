import logging
import os
import usb.backend.libusb1
from app.constants.config import get_connection, get_database_path
from app.core.printer_core import ambil_printer_default
from local_escpos.printer import Usb

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOG_PATH = os.path.join(BASE_DIR, "debug", "debug.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def log_info(msg):
    logging.info(msg)

def log_error(msg, exc=None):
    if exc:
        logging.error(msg, exc_info=True)
    else:
        logging.error(msg)

def ambil_log_terakhir(jumlah_baris=50):
    if not os.path.exists(LOG_PATH):
        return["[INFO] Belum ada log."]
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        return ["[INFO] Log masih kosong."]
    return lines[-jumlah_baris:]

def cek_status_database():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabel = cursor.fetchall()
        conn.close()

        db_path = get_database_path() # Ambil path dari koneksi SQLite
        ukuran = os.path.getsize(db_path)

        log_info(f"Database OK: {len(tabel)} tabel ditemukan")
        return {
            "status": "OK",
            "jumlah_tabel": len(tabel),
            "path": db_path,
            "ukuran": ukuran
        }
    except Exception as e:
        log_error("Gagal koneksi ke database", e)
        return {
            "status": "ERROR",
            "error": str(e)
        }

def log_transaksi_berhasil(transaksi_id):
    log_info(f"Transasksi #{transaksi_id} berhasil disimpan")

def log_transaksi_gagal(transaksi_id, error):
    log_error(f"Transaksi #{transaksi_id} gagal: {error}")

def log_cetak_berhasil(transaksi_id):
    log_info(f"Nota transaksi #{transaksi_id} berhasil dicetak ke printer")

def log_cetak_gagal(transaksi_id, error):
    log_error(f"Cetak nota transaksi #{transaksi_id} gagal: {error}")

# catatan, tambah log di fungsi penting di semua Modul

def log_fungsi(nama_fungsi):
    from functools import wraps
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_info(f"Fungsi {nama_fungsi} dipanggil")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def cek_status_printer():
    try:
        printer = ambil_printer_default()
        log_info(f"[DEBUG] Printer default: {printer}")
        if not printer or "vendor_id" not in printer or "product_id" not in printer:
            return {"status": "TIDAK TERDETEKSI", "error": "Konfigurasi printer tidak lengkap"}
        
        vendor_id = int(printer["vendor_id"], 16)
        product_id = int(printer["product_id"], 16)

        # Gunakan backed liusb1 secara eksplisit
        backend = usb.backend.libusb1.get_backend()
        if backend is None:
            return {"status":"TIDAK TERDETEKSI", "error": "Backend libusb1 tidak tersedia"}
        # Coba deteksi printer tanpa membuka koneksi penuh
        dev = usb.core.find(idVendor=vendor_id, idProduct=product_id, backend=backend)
        log_info("Backend aktif: usb.backend.libusb1")
        if dev is None:
            return {"status": "TIDAK TERDETEKSI", "error": "Printer tidak ditemukan "}
        return {
            "status": "TERDETEKSI",
            "vendor_id": printer["vendor_id"],
            "product_id": printer["product_id"]
        }
    except Exception as e:
        return {
            "status": "TIDAK TERDETEKSI",
            "error": str(e)
        }


# cara panggil log_fungsi(nama_fungsi)
# from app.core.debug_core import log_fungsi
#@log_fungsi("simpan_member")
#def simpan_member():
#   . . .. . . 

