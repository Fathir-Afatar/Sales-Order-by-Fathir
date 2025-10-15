CREATE TABLE produk (
  id_produk INTEGER PRIMARY KEY,
  nama_produk TEXT,
  kode_produk TEXT,
  kategori_id INTEGER,
  merk TEXT,
  harga_beli REAL,
  harga_jual REAL,
  stok INTEGER,
  berat REAL, kategori_produk TEXT,
  FOREIGN KEY (kategori_id) REFERENCES kategori(id_kategori)
)

CREATE TABLE kategori (
  id_kategori INTEGER PRIMARY KEY,
  nama_kategori TEXT
)

CREATE TABLE member (
  id_member INTEGER PRIMARY KEY,
  nama TEXT NOT NULL,
  alamat TEXT,        -- opsional
  no_hp TEXT,          -- opsional
  koordinat TEXT,     -- opsional
  ranting TEXT        -- opsional
, tipe TEXT, kode_member TEXT)

CREATE TABLE supplier (
  id_supplier INTEGER PRIMARY KEY,
  nama_supplier TEXT,
  alamat text,
  no_hp TEXT, 
  kode_supplier TEXT)

CREATE TABLE transaksi_pembelian (
  id_pembelian INTEGER PRIMARY KEY,
  tanggal TEXT,
  supplier_id INTEGER,
  total_harga REAL,
  FOREIGN KEY (supplier_id) REFERENCES supplier (id_supplier)
)

CREATE TABLE detail_penjualan (
    id_detail INTEGER PRIMARY KEY AUTOINCREMENT,
    transaksi_id INTEGER NOT NULL,
    produk_id INTEGER NOT NULL,
    nama_produk TEXT NOT NULL,
    jumlah INTEGER NOT NULL CHECK(jumlah >= 0),
    harga_satuan REAL NOT NULL,
    diskon REAL DEFAULT 0,
    subtotal REAL NOT NULL,
    satuan TEXT,
    catatan TEXT,
    FOREIGN KEY (produk_id) REFERENCES produk(id_produk),
    FOREIGN KEY (transaksi_id) REFERENCES transaksi_penjualan(id_transaksi)
)

CREATE TABLE transaksi_penjualan (
    id_transaksi INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal DATETIME NOT NULL,
    kode_member INTEGER,
    nama_member TEXT,
    total_harga REAL NOT NULL,
    ongkos_kirim REAL DEFAULT 0,
    voucher REAL DEFAULT 0,
    metode_bayar TEXT,
    catatan TEXT, status TEXT DEFAULT 'FINAL',
    FOREIGN KEY (kode_member) REFERENCES member(id_member) ON DELETE SET NULL
)

CREATE TABLE transaksi_pembelian (
  id_pembelian INTEGER PRIMARY KEY,
  tanggal TEXT,
  supplier_id INTEGER,
  total_harga REAL,
  FOREIGN KEY (supplier_id) REFERENCES supplier (id_supplier)
)

CREATE TABLE detail_pembelian (
  id_detail INTEGER PRIMARY KEY,
  pembelian_id INTEGER,
  produk_id INTEGER,
  qty INTEGER,
  harga_beli REAL,
  FOREIGN KEY (pembelian_id) REFERENCES transaksi_pembelian(id_pembelian),
  FOREIGN KEY (produk_id) REFERENCES produk(id_produk)
);

CREATE TABLE Pengeluaran (
  id_pengeluaran INTEGER PRIMARY KEY,
  tanggal TEXT,
  nama_pengeluaran TEXT,
  nominal REAL,
  keterangan text, 
  kategori TEXT)

CREATE TABLE user (
  id_user INTEGER PRIMARY KEY,
  username TEXT,
  password_hash TEXT,
  role TEXT,
  nama TEXT
);

CREATE TABLE log_stock (
  id_log INTEGER PRIMARY KEY,
  produk_id INTEGER,
  tanggal TEXT,
  stok_awal INTEGER,
  stok_akhir INTEGER,
  jenis_perubahan TEXT,
  FOREIGN KEY (produk_id) REFERENCES produk(id_produk)
);

CREATE TABLE log_harga_beli_harga_jual (
id INTEGER PRIMARY KEY AUTOINCREMENT,
kode_produk TEXT,
harga_beli INTEGER,
harga_jual INTEGER,
tanggal TEXT
)