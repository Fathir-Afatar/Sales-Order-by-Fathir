import sys
import os
from app.core.debug_core import log_error
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
#from local_escpos.printer import Usb
from escpos.printer import Usb

def test_cetak_usb(vendor_id, product_id):
    try:
        p = Usb(vendor_id, product_id)
        p.text("Tes cetak berhasil\n")
        p.text("Printer ini siap digunakan.\n")
        p.cut()
        return True
    except Exception as e:
        log_error("Tes cetak gagal", e)
        return False