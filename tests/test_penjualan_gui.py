# untuk test penjualan
import sys
import os

from app.core.product_core import tambah_produk
from app.core.member_core import tambah_member
from app.core.supplier_core import tambah_supplier

"""
Deprecated. Only for testing.
"""

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))

tambah_produk("Roti Tawar", "RT123", kategori_id=1, merk="SariRoti", harga_beli=5000, harga_jual=7000, stok=100, berat=0.5)

tambah_member("Fathir test", no_hp="93874983749287")

tambah_supplier("Sosro Distribution", no_hp="89698789", alamat="Jakarta")
