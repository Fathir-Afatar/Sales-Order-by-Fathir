import usb.core

devices = usb.core.find(find_all=True)
for dev in devices:
    print(f"[DEBUG] Device: VID={hex(dev.idVendor)}, PID={hex(dev.idProduct)}")