import usb.core
import usb.util

"""
This file only for checking, or debug, the usb printer.
"""

dev = usb.core.find(idVendor=0x28e9, idProduct=0x0289)

if dev is None:
    print("Printer tidak ditemukan oleh pyusb")
else:
    print("Printer ditemukan oleh pyusb")
    try:
        manufacturer = usb.util.get_string(dev, dev.IManufacturer)
        product = usb.util.get_string(dev, dev.iProduct)
        print("Manufacturer:", manufacturer)
        print("Product:", product)
    except Exception as e:
        print("Gagal membaca info printer")