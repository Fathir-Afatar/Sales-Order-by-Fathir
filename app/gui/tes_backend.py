import usb.backend.libusb1

"""
Deprecated. Only for testing.
"""

backend = usb.backend.libusb1.get_backend()
if backend is None:
    print("❌ Backend libusb1 tidak tersedia")
else:
    print("✅ Backend libusb1 aktif")