import sys, os
sys.path.append(os.path.abspath("."))

from local_escpos.printer import Usb
print("[INFO] Import berhasil:", Usb)