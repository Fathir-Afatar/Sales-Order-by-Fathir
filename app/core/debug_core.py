# Standard library
import logging
import os
import usb.backend.libusb1

# Local application
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
    """Log an informational message to the application log file.

    Args:
        msg (str): Message text or information to record.
    """
    logging.info(msg)

def log_error(msg, exc=None):
    """Log an error message to the application log file.

    If an exception object is provided, the full stack trace will be recorded to
    facilitate debugging.

    Args:
        msg (str): Error description or context message.
        exc (Optional[Exception], optional): Exception instance caught during
            runtime. Defaults to None.
    """
    if exc:
        logging.error(msg, exc_info=True)
    else:
        logging.error(msg)

def ambil_log_terakhir(jumlah_baris=50):
    """Retrieve the last specified number of lines from the application log file.

    Handles missing or empty log files gracefully to prevent UI runtime errors.

    Args:
        jumlah_baris (int, optional): Number of bottom log lines to read. Defaults
            to 50.

    Returns:
        List[str]: List of log line strings, or a status message if empty or missing.
    """
    if not os.path.exists(LOG_PATH):
        return["[INFO] Belum ada log."]
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        return ["[INFO] Log masih kosong."]
    return lines[-jumlah_baris:]

def cek_status_database():
    """Check database connection status and count registered tables.

    Attempts to establish a connection, fetch table metadata, and calculate the
    database file size on disk.

    Returns:
        Dict[str, Any]: Dictionary containing database status metadata:
            - status (str): "OK" on success, "ERROR" on failure.
            - jumlah_tabel (int, optional): Total count of tables found.
            - path (str, optional): Absolute database file path.
            - ukuran (int, optional): File size in bytes.
            - error (str, optional): Error message if connection fails.
    """
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
    """
    Deprecated: This function no longer use.
    """
    log_info(f"Transasksi #{transaksi_id} berhasil disimpan")

def log_transaksi_gagal(transaksi_id, error):
    """
    Deprecated: This function no longer use.
    """
    log_error(f"Transaksi #{transaksi_id} gagal: {error}")

def log_cetak_berhasil(transaksi_id):
    """
    Deprecated: This function no longer use.
    """
    log_info(f"Nota transaksi #{transaksi_id} berhasil dicetak ke printer")

def log_cetak_gagal(transaksi_id, error):
    """
    Deprecated: This function no longer use.
    """
    log_error(f"Cetak nota transaksi #{transaksi_id} gagal: {error}")

def log_fungsi(nama_fungsi):
    """
    Deprecated: This function no longer use.
    """
    from functools import wraps
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_info(f"Fungsi {nama_fungsi} dipanggil")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def cek_status_printer():
    """Check the connectivity and operational status of the default USB printer.

    Reads default printer configurations, converts vendor and product IDs to
    hexadecimal values, and verifies device presence via PyUSB (`libusb1`).

    Returns:
        Dict[str, Any]: Dictionary detailing printer status:
            - status (str): "TERDETEKSI" or "TIDAK TERDETEKSI".
            - vendor_id (str, optional): Vendor ID string if detected.
            - product_id (str, optional): Product ID string if detected.
            - error (str, optional): Reason for detection failure.
    """
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

