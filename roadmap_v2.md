# Roadmap Versi 2 - POS Pintar by Fathir

Versi ini adalah hasil refleksi dan uji lapangan selama 1 minggu. Tujuannya: menyempurnakan pengalaman dekstop sebelum migrasi ke Django/web. Semua poin di bawah adalah hasil observasi nyata dan kebutuhan fungsional di kantor. 
----

## Tujuan Utama
- Menyusun versi dekstop final yang stabil dan profesional.
- Menyelesaikan fitur-fitur yang belum aktif atau belum otimal.
- Menyiapkan struktur modular untuk migrasi ke Django.
Membuat executable (.exe) dengan PyInstaler untuk distribusi kantor.

----

## GUI dan UX Perbaikan
- [X] Tambahkan **Menu Utama** saat aplikasi dibuka (bukan langsung ke penjualan)
- [X] Perbaiki **scrollbar vertical** di modul Produk agar menyatu dengan Treeview
- [ ] Tambahkan **judul modul** di setiap tampilan (Produk, Member, dll)
- [ ] Perbaiki layout kolom modul Member agar tidak bergeser saat edit

----

## Fitur Baru & Aktivasi
- [ ] Tambahkan **Edit Member** di modul Member.
- [ ] Tambahkan **Hapus Member** di modul Member.
- [ ] Aktifkan **Kategori Produk** agar muncul di Treeview dan bisa difilter.
- [ ] Aktifkan **Preview Nota** sebelum simpan transaksi
- [ ] Format tanggal nota: '12 Desember 2025 (14:30)

---

## Import & Export
- [ ] Tambahkan **Import dari Excel** untuk:
  - Member
  - Produk
  - Supplier
- [ ] Tambahkan **Export ke Excel** untuk modul Stok (opsional, versi berikutnya)

---

## Laporan & Analitik (Modul Penjualan)
- [ ] Refactor Modul Penjualan
- [ ] Aktifkan tab:
  - Penjualan
  - Pembelian
  - Pengeluaran
- [ ] Tambahkan tab **Laporan Member**:
  - Total Belanja
  - Kontribusi profit
  - Frekuensi transaksi

---

## Pencarian & Input Pintar
- [ ] Ubah input Member di tab Penjualan:
  - Dari ID -> menjadi pencarian nama seperti input produk

---

## Thermal & Cetak
- [ ] Perubahan design di tab Rincian modul Penjualan. Cetak ulang nota berada didalam tombol Lihat Detail.
- [ ] Gunakan 'format_nota_thermal()' untuk preview nota dan Lihat detail.

## Format Nota & Printer
- [ ] Buat pengaturan untuk format nota.
- [ ] Buat pengaturan untuk deteksi printer thermal

## Struktur Modular
- [ ] Pisahkan file core dengan GUI semua modul
- [ ] Isi 'README.md' dan 'journey.md' untuk dokumentasi teknis dan catatan

## Distribusi & Migrasi
- [ ] Buat executable '.exe' dengan Pyinstaller
- [ ] Siapkan folder 'versi2/' untuk staging area
- [ ] Rancang struktur Django berdasarkan versi 2

## Catatan Pribadi
Versi ini adalah bukti nyata bahwa sistem buatan sendiri bisa mengubah cara kerja di dunia nyata. Setiap fitur bukan hanya baris kode, tapi representasi dari kebutuhan, semangat, dan ketekunan.
---