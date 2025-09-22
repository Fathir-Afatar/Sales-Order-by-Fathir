import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from local_escpos.printer import Usb

p = Usb(0x28e9, 0x0289)
p.text("Langkah Pertama: Python x POS80 Thermal Printer\n")
p.text("Halo dari POS Pintar!\n")
p.text("Dicetak langsung dari Python menggunakan ESC/POS dan USB Backed. Terhubung, terformat, dan berhasil\n")
p.cut()