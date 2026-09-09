import usb.core
"""
Deprecated. Only for testing.
"""
devices = usb.core.find(find_all= True)
for dev in devices:
    print(f"Vendor: {hex(dev.idVendor)}, Product: {hex(dev.idProduct)}")