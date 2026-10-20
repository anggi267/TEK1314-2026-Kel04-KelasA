# Setup Target Node Replika — Ubuntu Server (Sengaja Rentan)

**Target Node:** `192.168.4.5` · **OS:** Ubuntu Server LTS 26.04 (lihat catatan versi)
**Tujuan:** membangun replika *backend* sistem IoT — dashboard, API, database, broker MQTT —
yang **menyerupai produksi tetapi sengaja diberi kelemahan terkontrol** agar skenario Red Team
Bagian IX dapat dijalankan dan dimitigasi Blue Team.

> ⚠ Kelemahan di dokumen ini **hanya boleh** dipasang di VM lab `192.168.4.5` dalam
> Internal Network `pbl-kel4`. Jangan pernah meniru konfigurasi ini di server nyata.

## 0. Catatan versi OS (wajib dibaca)

VM `Target node` yang ada sekarang terdeteksi **Ubuntu 25.04 (Plucky Puffin)** — rilis
interim yang dukungannya sudah berakhir Januari 2026. Repositori keamanannya tertutup,
sehingga kontrol **B-3 (patch OS)** tidak bisa dibuktikan.

**Tindakan:** pasang ulang dengan **Ubuntu Server 26.04 LTS** (menyusul 24.04 LTS bila ingin
lebih matang). Setelah itu `apt update && apt upgrade` harus berjalan tanpa error — itulah
bukti awal untuk B-3.

## 1. Prasyarat jaringan (sudah dikonfigurasi di sisi VirtualBox)

| Adapter | Fungsi | Setting |
|---|---|---|
| NIC 1 | Segmen lab (sama dengan Kali & sensor) | Internal Network `pbl-kel4` |
| NIC 2 | Internet untuk update paket | NAT |

IP statis di dalam guest (netplan, `/etc/netplan/50-pbl.yaml`):

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: false
      addresses: [192.168.4.5/24]
    enp0s8:
      dhcp4: true
```

```bash
sudo netplan apply && ip -brief a
```

## 2. Stack yang dipasang (peta ke arsitektur IoT)

| Komponen IoT | Perangkat lunak di replika | Port |
|---|---|---|
| Dashboard monitoring | nginx + PHP-FPM + DVWA (aplikasi sengaja rentan) | 80 |
| API gateway | `api.php` kustom (menerima `?id=` untuk data sensor) | 80 |
| Database | MariaDB/MySQL (`iot_db`: `users`, `sensor_readings`) | 3306 |
| Broker MQTT | Mosquitto, **anonymous diaktifkan** (kelemahan disengaja) | 1883 |
| Manajemen | OpenSSH, user `iotadmin` dengan password lemah | 22 |

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx php-fpm php-mysql mariadb-server mosquitto mosquitto-clients unzip

# dashboard: DVWA (vulnerable by design -> bahan RT-03)
cd /var/www && sudo git clone https://github.com/digininja/DVWA.git iot-dashboard
sudo chown -R www-data:www-data /var/www/iot-dashboard
sudo cp /var/www/iot-dashboard/config/config.inc.php.dist /var/www/iot-dashboard/config/config.inc.php

# database
sudo mysql -e "CREATE DATABASE iot_db; CREATE DATABASE dvwa;
  CREATE USER 'iotadmin'@'localhost' IDENTIFIED BY 'iotadmin123';
  GRANT ALL ON iot_db.* TO 'iotadmin'@'localhost';
  GRANT ALL ON dvwa.* TO 'iotadmin'@'localhost'; FLUSH PRIVILEGES;"

# MQTT: anonymous + tanpa ACL  (INI KELEMAHAN YANG DISENGAJA)
sudo tee /etc/mosquitto/conf.d/pbl.conf >/dev/null <<'EOF'
listener 1883
allow_anonymous true
EOF
sudo systemctl restart mosquitto

# user manajemen dengan password lemah (bahan RT-02)
sudo adduser --disabled-password --gecos "" iotadmin 2>/dev/null || true
echo 'iotadmin:iotadmin123' | sudo chpasswd
sudo usermod -aG sudo iotadmin
```

## 3. Kelemahan yang sengaja dipasang (dan siapa yang mengujinya)

| # | Kelemahan | Lokasi | Skenario | Kontrol penutup |
|---|---|---|---|---|
| 1 | Password lemah `iotadmin:iotadmin123` + SSH password auth aktif | :22 | RT-02 | A-2, A-4 |
| 2 | SQL injection pada `api.php` & DVWA level low | :80 | RT-03 | C-2, C-3 |
| 3 | MQTT anonymous, tanpa ACL topik | :1883 | RT-04 | C-2 |
| 4 | MySQL mendengarkan di semua interface | :3306 | RT-03 | B-2 |
| 5 | Service bawaan tidak dipakai tetap hidup | berbagai | RT-01 | B-1 |
| 6 | Tidak ada rate limit di dashboard | :80 | RT-05 | ufw limit |

**Aturan penting:** setiap kelemahan di tabel ini **wajib** punya kontrol penutup di
`docs/blueteam/hardening_checklist.md`. Kalau sebuah kelemahan tidak bisa ditutup, hapus dari
daftar — kalian tidak boleh menyisakan serangan yang tetap berhasil di Tahap 5.

## 4. Verifikasi replika siap diuji

```bash
# dari Target
sudo ss -tulpn | grep -E ':(22|80|3306|1883)'
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1/iot-dashboard/login.php

# dari Kali
nmap -sV -p22,80,3306,1883 192.168.4.5
mosquitto_sub -h 192.168.4.5 -t '#' -v      # harus bisa connect tanpa kredensial
curl "http://192.168.4.5/iot-dashboard/vulnerabilities/sqli/?id=1&Submit=Submit"
```

Bila keempat port terlihat dari Kali dan `mosquitto_sub` tersambung tanpa kredensial, replika
sudah dalam kondisi "rentan sesuai rencana" dan siap masuk sesi S1 (baseline + hardening).

## 5. Urutan aman: rentan dulu, hardening kemudian

1. Pasang stack **apa adanya** (dokumen ini) → rekam bukti `before`.
2. Jalankan RT-01…RT-05 pada kondisi ini (Tahap 1 Purple Team Loop).
3. Baru terapkan hardening A/B/C; setiap penutupan diuji ulang (Tahap 5).

Kalau hardening dilakukan sebelum serangan pertama, tidak akan ada bukti "sebelum" dan nilai
kriteria hardening (30%) sulit dipertahankan.
