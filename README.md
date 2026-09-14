# Sales Order Management by Fathir

Aplikasi Sales Order Management. Digunakan untuk membuat nota lebih cepat dan meminimalisir kesalahan menghitung manual.
Dilengkapi Manajemen member, produk, supplier. Dan juga Transaksi penjualan, Pembelian, Pengeluaran. Pencatatan Stok. Dan Laporan.


## Fitur Utama

- Transaksi penjualan dengan validasi member
- Preview dan cetak nota thermal via USB
- Rincian transaksi dan cetak ulang nota
- Modular GUI dengan Tkinter
- Dokumentasi milestone dan refleksi pengembangan
- Catatan pengeluaran kantor di luar transaksi
- Catatan pembelian barang masuk

## Teknologi

- Python 3.13
- Tkinter
- SQlite3
- escpos (USB thermal printer)
- Modular architecture

## Cara Menjalankan

```bash
python app_gui.py
```
# Setup Printer Thermal untuk Sales Order by Fathir

Panduan ini membantu pengguna untuk menghubungkan printer thermal ke aplikasi Sales Order by Fathir (versi 2). Ikuti langkah-langkah berikut agar printer bisa terdeteksi dan digunakan dengan lancar.

---

## 1. Persiapan Awal

### Yang dibutuhkan:

- Printer thermal (misalnya: XPrinter, Epson, Eppos, dll)
- Kabel USB Printer
- Sistem operasi Windows 10 atau 11
- Aplikasi Sales Order by Fathir (versi 2)
- Pastikan printer thermal mendukung ESC/POS Command

## 2. Instalasi Driver USB

1. Colokkan printer ke port USB
2. jalankan 'Zadig.exe' atau bisa download di internet
3. Di Zadig:
    - Pilih printer thermal dari daftar perangkat USB
    - Pilih driver: `WinUSB (v6.1.7600.16385)`
    - Klik **Install Driver**
4. Tunggu hingga proses selesai dan pastikan printer muncul di Device Manager sebagai 'USB Input Device' atau sejenisnya. Atau kadang bernama `micro-printer` 

---

3. Uji Deteksi Printer

1. Jalankan aplikasi Sales Order
2. Buka Tab **Pengaturan > Tes & Pengaturan printer**
3. Pada menu Pilih Printer USB, jika printer terdeteksi akan muncul daftar seperti
28e9:289
4. Klik tombol **Tes Cetak**
5. Jika berhasil, printer akan mencetak teks "Tes Cetak berhasil"

---

## 4. Simpan Printer Default

1. Setelah memilih printer dari daftar, klik **Simpan Printer Default**
2. Printer ini akan digunakan otomatis saat mencetak nota penjualan

--- 

5. Cetak Nota Penjualan

Setelah printer disimpan sebagai default:
- Setiap transaksi penjualan akan otomatis mencetak nota ke printer thermal 
- Jika printer tidak terhubung, sistem akan menyimpan fallback nota ke file `.txt`

---


## 6. Troubleshooting

| Masalah | Solusi |
|--------|--------|
| Printer tidak muncul di daftar | Pastikan kabel USB terpasang dan driver sudah diinstal dengan Zadig |
| Tes cetak gagal (Access Denied) | Jalankan aplikasi sebagai Administrator |
| Cetak nota gagal | Pastikan printer default sudah disimpan dan backend `libusb1` aktif |
| Muncul log `Detach kernel driver gagal` | Abaikan jika cetak tetap berhasil—itu hanya peringatan di Windows |

## Tips Tambahan

- Gunakan port USB yang sama setiap kali menyalakan printer
- Jangan buka aplikasi lain yang bisa mengakses printer thermal secara langsung
