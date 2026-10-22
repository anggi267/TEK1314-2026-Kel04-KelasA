# Replika Backend KABITA di Target Node (Ubuntu Server + ThingsBoard)

Panduan membangun replika backend **KABITA** — pencatatan berat badan & pakan kambing — di
Target Node `192.168.4.5`, sesuai `docs/presentation-minggu9/tech_stack_declaration.md`.

Replika memakai **ThingsBoard Community Edition** yang sama dengan produk asli, ditambah
PostgreSQL. Perangkat fisik (timbangan, RFID) digantikan skrip pengirim telemetri.

---

## 1. Prasyarat

| Item | Nilai | Keterangan |
|---|---|---|
| VM | 2 vCPU / **4096 MB** RAM / disk ≥ 25 GB | ThingsBoard + PostgreSQL butuh ≥ 4 GB; 2 GB akan OOM |
| OS | Ubuntu Server 26.04.1 LTS | sudah terpasang, IP `192.168.4.5/24` |
| Java | OpenJDK 17 (JRE) | wajib untuk ThingsBoard 4.x |
| PostgreSQL | 16/17 | Ubuntu 26.04 mungkin membawa versi lebih baru — cek kompatibilitas rilis TB |
| Snapshot | `20-lab-ready` | titik balik bila instalasi gagal |

> **Catatan penting:** naikkan RAM VM ke 4096 MB sebelum instalasi
> (`VBoxManage modifyvm PBL-K4-01-Target-Ubuntu --memory 4096`, VM harus mati).

---

## 2. Instalasi ThingsBoard CE (langkah perintah)

### 2.1 Dependensi

```bash
sudo apt update
sudo apt install -y openjdk-17-jre-headless postgresql curl gnupg
java -version            # harus 17.x
psql --version           # catat versinya
```

Bila `openjdk-17-jre-headless` tidak tersedia di repo Ubuntu 26.04, gunakan JDK 17 dari
Adoptium:

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://packages.adoptium.net/artifactory/api/gpg/key/public \
  | sudo gpg --dearmor -o /etc/apt/keyrings/adoptium.gpg
echo "deb [signed-by=/etc/apt/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb $(. /etc/os-release; echo $VERSION_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/adoptium.list
sudo apt update && sudo apt install -y temurin-17-jre
```

### 2.2 Database

```bash
sudo -u postgres psql <<'SQL'
CREATE DATABASE thingsboard;
CREATE USER thingsboard WITH PASSWORD 'thingsboard';
GRANT ALL PRIVILEGES ON DATABASE thingsboard TO thingsboard;
ALTER DATABASE thingsboard OWNER TO thingsboard;
SQL
```

### 2.3 Paket ThingsBoard

```bash
cd /tmp
TB_VER=4.2.1                      # sesuaikan dengan rilis stabil terbaru
curl -L -o thingsboard.deb \
  "https://github.com/thingsboard/thingsboard/releases/download/v${TB_VER}/thingsboard-${TB_VER}.deb"
sudo dpkg -i thingsboard.deb
```

### 2.4 Konfigurasi koneksi database

Edit `/etc/thingsboard/conf/thingsboard.conf`, tambahkan:

```properties
export DATABASE_ENTITIES_TYPE=sql
export DATABASE_TS_TYPE=sql
export SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/thingsboard
export SPRING_DATASOURCE_USERNAME=thingsboard
export SPRING_DATASOURCE_PASSWORD=thingsboard
export JAVA_OPTS="$JAVA_OPTS -Xms1G -Xmx1536M -XX:+UseG1GC"
```

### 2.5 Inisialisasi skema + akun demo

```bash
sudo /usr/share/thingsboard/bin/install/install.sh --loadDemo
sudo systemctl enable --now thingsboard
sudo journalctl -u thingsboard -f     # tunggu "Started Thingsboard"
```

Start pertama memakan 2–5 menit. Bila gagal, periksa `/var/log/thingsboard/thingsboard.log`.

### 2.6 Verifikasi

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/login   # harap 200
ss -tulpn | grep -E ':(8080|1883|5432) '
```

Login UI: `http://192.168.4.5:8080`
Akun default (sengaja dibiarkan): `tenant@thingsboard.org` / `tenant`,
`sysadmin@thingsboard.org` / `sysadmin`.

---

## 3. Menyiapkan perangkat KABITA (device + telemetri)

### 3.1 Buat device

1. Login sebagai tenant → **Devices** → **+** → nama `KABITA-Timbangan-01`, tipe `timbangan`.
2. Buka device → **Manage credentials** → salin **Access token**.

### 3.2 Kirim telemetri (menggantikan timbangan fisik)

```bash
# jalur HTTP
curl -s -X POST "http://192.168.4.5:8080/api/v1/<TOKEN>/telemetry" \
  -H 'Content-Type: application/json' \
  -d '{"berat_kg":32.4,"pakan_kg":1.8,"rfid":"KMB-014"}'

# jalur MQTT (pakai client mosquitto)
mosquitto_pub -h 192.168.4.5 -p 1883 -u '<TOKEN>' -P '' \
  -t v1/devices/me/telemetry -m '{"berat_kg":33.1,"pakan_kg":1.6,"rfid":"KMB-014"}'
```

### 3.3 Dashboard

Buat dashboard **KABITA — Berat & Pakan** dengan widget time-series `berat_kg` dan `pakan_kg`,
lalu bagikan sebagai **public** (kebiasaan lapangan yang menjadi temuan: dashboard publik tanpa
autentikasi).

---

## 4. Kelemahan yang sengaja dibiarkan (sesuai deklarasi)

| # | Kondisi | Cara menyesuaikan | Skenario |
|---|---|---|---|
| 1 | Kredensial default tidak diganti | jangan ubah akun tenant/sysadmin | RT-02 |
| 2 | SSH password auth + password `123` | `sshd_config` tetap `PasswordAuthentication yes` | RT-02 |
| 3 | Token device dipakai apa adanya | token disalin ke skrip serangan, tanpa rotasi | RT-03/RT-04 |
| 4 | Dashboard dibagikan publik | aktifkan public dashboard | RT-03 |
| 5 | MQTT tanpa TLS | jangan aktifkan TLS pada transport MQTT | RT-04 |
| 6 | PostgreSQL terbuka | `listen_addresses='*'` + satu entri `pg_hba` untuk `192.168.4.0/24` | RT-01 |
| 7 | Tanpa rate limit | jangan pasang reverse proxy/limit di depan 8080 | RT-05 |

Setiap butir **wajib** punya baris penutup di `docs/blueteam/hardening_checklist.md`.

---

## 5. Rollback dan pemulihan

```bash
sudo systemctl stop thingsboard        # hentikan sebelum snapshot/rollback
VBoxManage snapshot "PBL-K4-01-Target-Ubuntu" restore "20-lab-ready"
```

Untuk mengulang instalasi tanpa rollback:

```bash
sudo apt purge -y thingsboard
sudo -u postgres psql -c 'DROP DATABASE thingsboard;' -c 'DROP USER thingsboard;'
```

---

## 6. Catatan sumber daya (jujur)

- ThingsBoard CE butuh Java heap ~1–1,5 GB + PostgreSQL ~150 MB + OS ~400 MB. Pada 2 GB RAM,
  service akan OOM-kill saat start; **4096 MB** adalah batas aman minimum untuk lab ini.
- Tiga VM hidup bersamaan (Target 4 GB, Kali 2 GB, Onion 6 GB) = 12 GB; host punya 19,7 GB,
  jadi jalankan Onion hanya saat pengujian deteksi.
- Unduhan paket (JDK ±180 MB, PostgreSQL ±50 MB, ThingsBoard ±250 MB) memakan waktu pada
  jaringan lambat; hentikan layanan yang tidak perlu lebih dulu agar tidak memicu timeout.

---

## 7. Alternatif bila RAM tidak cukup: Docker Compose

```yaml
services:
  postgres:
    image: postgres:16
    environment: [POSTGRES_DB=thingsboard, POSTGRES_PASSWORD=thingsboard, POSTGRES_USER=thingsboard]
    volumes: [tb-pg:/var/lib/postgresql/data]
  thingsboard:
    image: thingsboard/tb-postgres:4.2.1
    ports: ["8080:9090", "1883:1883", "5683:5683/udp"]
    environment: [TB_QUEUE_TYPE=in-memory]
    volumes: [tb-data:/data, tb-logs:/var/log/thingsboard]
volumes: {tb-pg: {}, tb-data: {}, tb-logs: {}}
```

Docker memakai ±2,5 GB RAM total — pilihan pertama bila kapasitas host menipis, tetapi
menambah satu lapisan yang harus di-hardening sendiri (grup `docker` = root).
