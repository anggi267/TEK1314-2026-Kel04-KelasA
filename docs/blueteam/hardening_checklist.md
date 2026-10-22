# Hardening Checklist — Target Node Replika `192.168.4.5`

**Kelompok 4 · TEK1314 Kelas A · Checkpoint Minggu 9**
**Target:** Ubuntu Server LTS 26.04 (revisi Minggu 9 — lihat `docs/design/replica_setup.md`)
**Acuan:** Panduan PBL Pertemuan 9, Bagian VIII (min. 8 kontrol, ≥2 per kategori A/B/C, bukti before/after).

> **Cara mengisi status:** `Belum` → `Sebagian` → `Selesai`. Status **hanya** boleh menjadi
> `Selesai` bila file bukti before *dan* after sudah ada di `docs/blueteam/evidence/` sesuai
> kolom "Bukti". Semua perintah dijalankan sebagai user `iotadmin` (sudo), bukan `root` langsung.

## Ringkasan status

| Kategori | Jumlah kontrol | Selesai | Sebagian | Belum |
|---|---|---|---|---|
| A. Access & Authentication | 4 | 0 | 0 | 4 |
| B. Service & Attack Surface | 3 | 0 | 3 | 0 |
| C. Data & Application | 3 | 0 | 0 | 3 |
| **Total** | **10** | **0** | **3** | **7** |

### Status eksekusi Fase 1 (21 Oktober 2026)

| Kontrol | Status | Bukti |
|---|---|---|
| B-2 firewall `ufw` | **Sebagian** — ufw aktif: default deny incoming, allow 22/80/1883 dari `192.168.4.0/24`; bukti `nmap` before/after belum diambil | `docs/blueteam/evidence/hardening-fase1/{before,after}.txt` |
| B-3 patch OS | **Sebagian** — `apt update/upgrade/full-upgrade`; 15 paket tertahan *phased update*; akun default **sengaja belum** dihapus (sasaran RT-02) | idem |
| B-1 minimalisasi service | **Sebagian** — `ModemManager` dinonaktifkan; service lain tidak terpasang; pemindaian port before/after menyusul | idem |
| A-1…A-4, C-1…C-3 | Belum — ditunda ke Fase 2 agar sasaran RT-02/RT-03 tetap ada | `attack_plan.md` |

> **Catatan perubahan stack (22 Okt 2026):** bukti di atas direkam saat replika masih memakai
> **nginx + PHP-FPM + MariaDB + Mosquitto** (stack sementara sebelum produk KABITA diklarifikasi).
> Replika final memakai **ThingsBoard CE + PostgreSQL** (`docs/design/replica_setup.md`), sehingga
> port acuan berubah menjadi **8080** (UI/REST), **1883** (MQTT), **5432** (PostgreSQL lokal), dan
> **22** (SSH). Konsekuensi yang harus dieksekusi ulang di awal Fase 2:
> (a) baseline traffic baru pada ThingsBoard, (b) `nmap` before/after untuk B-1/B-2, dan
> (c) verifikasi bahwa layanan `thingsboard` tetap 200 setelah `ufw` aktif.

_Prasyarat terpenuhi: VM target **Ubuntu Server 26.04.1 LTS**, IP `192.168.4.5/24` aktif, `sshd`
berjalan, sudo NOPASSWD untuk otomasi. Replika ThingsBoard menyusul sesuai
`docs/design/replica_setup.md`; baseline sementara sudah direkam di `docs/reports/fase1/`._

---

## A. Access & Authentication

### A-1 · Nonaktifkan login `root` langsung via SSH
```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sshd -t && sudo systemctl restart ssh
sudo sshd -T | grep -i permitrootlogin          # harapan: permitrootlogin no
```
**Verifikasi:** `ssh root@192.168.4.5` → `Permission denied`.
**Bukti:** `A1_before_sshd_config.txt`, `A1_after_sshd_config.txt`, `A1_after_root_login_denied.png`
**Status:** `Belum` · **PIC:** Blue Team

### A-2 · SSH key-based auth, matikan password auth
```bash
ssh-keygen -t ed25519 -f ~/.ssh/pbl_kel4 -N ""
ssh-copy-id -i ~/.ssh/pbl_kel4.pub iotadmin@192.168.4.5
ssh -i ~/.ssh/pbl_kel4 iotadmin@192.168.4.5 "echo key-ok"     # UJI DULU sebelum mematikan password
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sudo sshd -t && sudo systemctl restart ssh
```
**Verifikasi:** `ssh -o PreferredAuthentications=password iotadmin@192.168.4.5` → ditolak; login dengan `-i` → berhasil.
**Bukti:** `A2_before_password_login_ok.png`, `A2_after_key_login_ok.png`, `A2_after_password_login_denied.png`
**Status:** `Belum` · **PIC:** Blue Team

### A-3 · Ganti port default SSH 22 → 2222
```bash
sudo sed -i 's/^#\?Port .*/Port 2222/' /etc/ssh/sshd_config
sudo ufw allow 2222/tcp            # buka SEBELUM restart, agar tidak terkunci
sudo sshd -t && sudo systemctl restart ssh
```
**Verifikasi:** `nmap -p22,2222 192.168.4.5` → 22 `closed`, 2222 `open`.
**Bukti:** `A3_before_ssh_port22_nmap.txt`, `A3_after_ssh_port2222_nmap.txt`
**Status:** `Belum` · **PIC:** Blue Team
_Catatan: ganti port bukan kontrol keamanan sejati; nilainya mengurangi noise bot. Wajib dipasangkan dengan A-2 + A-4._

### A-4 · Rate-limit percobaan login (fail2ban)
```bash
sudo apt install -y fail2ban
sudo tee /etc/fail2ban/jail.local >/dev/null <<'EOF'
[sshd]
enabled = true
port = 2222
maxretry = 3
bantime = 600
findtime = 600
ignoreip = 127.0.0.1/8 192.168.4.200
EOF
sudo systemctl enable --now fail2ban && sudo fail2ban-client status sshd
```
**Verifikasi:** 4 login gagal dari Kali → `192.168.4.100` masuk `Banned IP list`.
**Bukti:** `A4_after_fail2ban_banned.png`
**Status:** `Belum` · **PIC:** Blue Team

---

## B. Service & Attack Surface

### B-1 · Nonaktifkan service/port yang tidak dipakai
Replika **KABITA** (ThingsBoard) hanya butuh 8080 (UI/REST), 1883 (MQTT transport), 5432
(PostgreSQL, **lokal saja**), dan 22 (SSH). Service bawaan Ubuntu Server yang tidak dipakai
dimatikan:
```bash
sudo systemctl disable --now avahi-daemon cups cups-browsed rpcbind ModemManager 2>/dev/null
sudo systemctl list-unit-files --state=enabled | grep -Ev "ssh|thingsboard|postgresql|systemd|networking|apparmor|cron|rsyslog|unattended"
nmap -sS -p- 192.168.4.5 -oN /tmp/after_port.txt     # dari Kali
```
**Verifikasi:** jumlah port terbuka berkurang dibanding baseline; setiap port yang tersisa punya alasan.
**Bukti:** `B1_before_nmap_full.txt`, `B1_after_nmap_full.txt`, `B1_port_delta.md`
**Status:** `Belum` · **PIC:** Blue Team

### B-2 · Firewall whitelist + tutup PostgreSQL dari luar
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2222/tcp
sudo ufw allow from 192.168.4.0/24 to any port 8080 proto tcp     # dashboard/REST KABITA
sudo ufw allow from 192.168.4.100 to any port 1883 proto tcp      # MQTT hanya gateway/attacker lab
sudo ufw allow from 192.168.4.200 to any port 514 proto udp       # log ke sensor
sudo ufw --force enable && sudo ufw status verbose

# PostgreSQL hanya lokal (ThingsBoard memanggil lewat localhost)
sudo sed -i "s/^#\?listen_addresses.*/listen_addresses = '127.0.0.1'/" /etc/postgresql/*/main/postgresql.conf
sudo systemctl restart postgresql
```
**Verifikasi:** dari Kali `nmap -sS -p1-1024 192.168.4.5` → hanya 8080/1883/22 `open`, 5432
`filtered`; `psql -h 192.168.4.5 -U thingsboard` → timeout (bukan `password authentication failed`).
**Bukti:** `B2_after_ufw_status.png`, `B2_before_nmap_vs_after_nmap.png`, `B2_after_postgres_localhost_only.txt`
**Status:** `Belum` · **PIC:** Blue Team

### B-3 · Patch OS/paket + hapus kredensial default
```bash
sudo apt update && sudo apt -y full-upgrade
sudo apt install -y unattended-upgrades && sudo dpkg-reconfigure -plow unattended-upgrades
sudo passwd iotadmin                # ganti password lemah (SSH)
# hapus akun demo ThingsBoard: login UI sebagai sysadmin -> ganti password, atau:
curl -s -X POST http://127.0.0.1:8080/api/auth/login -H 'Content-Type: application/json' \
  -d '{"username":"sysadmin@thingsboard.org","password":"sysadmin"}' | head -c 200
apt list --upgradable                                  # harapan: kosong
```
**Verifikasi:** `apt list --upgradable` kosong; login `tenant@thingsboard.org`/`tenant` → 401;
`hydra -l iotadmin -P rockyou.txt ssh://192.168.4.5 -s 2222 -t 4` → 0 valid pair (setelah A-2/A-4).
**Bukti:** `B3_before_apt_upgradable.txt`, `B3_after_apt_upgraded.txt`, `B3_after_default_admin_rejected.txt`
**Status:** `Belum` · **PIC:** Blue Team

---

## C. Data & Application

### C-1 · Kredensial tidak hardcoded (env var / file konfigurasi ketat)
```bash
sudo chmod 600 /etc/thingsboard/conf/thingsboard.conf
sudo chown thingsboard:thingsboard /etc/thingsboard/conf/thingsboard.conf
sudo grep -E 'SPRING_DATASOURCE_(USERNAME|PASSWORD)' /etc/thingsboard/conf/thingsboard.conf | sed 's/=.*/=<REDACTED>/'
grep -rnE '[A-Za-z0-9]{20,}' --include=*.md --include=*.sh . | grep -v '<TOKEN>' | head
```
**Verifikasi:** tidak ada password/token asli di repo (hasil grep bersih); file konfigurasi
`600 thingsboard:thingsboard`; token device hanya ada di UI ThingsBoard dan `.env` lokal yang
masuk `.gitignore`.
**Bukti:** `C1_before_secret_in_repo.txt`, `C1_after_conf_chmod600.txt`, `C1_after_no_hardcoded.txt`
**Status:** `Belum` · **PIC:** Red (review kode) + Blue (terapkan)

### C-2 · Rotasi device token + validasi telemetri + TLS MQTT
```bash
# 1. rotasi token tiap device (UI: Devices -> pilih device -> Manage credentials -> rotate)
#    token lama otomatis ditolak; catat waktu rotasi di logbook
# 2. rule chain "KABITA-Validate" (script node) menolak nilai di luar rentang wajar:
#    berat_kg 5-120 kg, pakan_kg 0-10 kg, rfid harus terdaftar
# 3. wajibkan TLS pada transport MQTT
sudo sed -i 's/^#\?\s*export MQTT_SSL_ENABLED.*/export MQTT_SSL_ENABLED=true/' /etc/thingsboard/conf/thingsboard.conf
sudo sed -i 's/^#\?\s*export MQTT_BIND_PORT.*/export MQTT_BIND_PORT=8883/' /etc/thingsboard/conf/thingsboard.conf
sudo systemctl restart thingsboard
```
**Verifikasi:** `mosquitto_pub` dengan token lama → `Connection Refused: not authorized`;
publish `{"berat_kg":99.9}` → ditolak rule chain (tidak muncul di telemetri);
`curl /api/v1/<token-lama>/telemetry` → 401.
**Bukti:** `C2_before_telemetry_injection.txt`, `C2_after_token_rotated_401.txt`,
`C2_after_range_rejected.txt`, `C2_after_mqtt_tls_required.txt`
**Status:** `Belum` · **PIC:** Red + Blue

### C-3 · Least-privilege user DB + logging
```bash
sudo -u postgres psql <<'EOF'
-- role ThingsBoard hanya berhak pada database miliknya, bukan superuser
ALTER ROLE thingsboard NOSUPERUSER NOCREATEDB NOCREATEROLE;
GRANT ALL PRIVILEGES ON DATABASE thingsboard TO thingsboard;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
EOF
sudo -u postgres psql -c "\du thingsboard"    # harapan: Attributes kosong (bukan superuser)
# logging: teruskan auth.log + log ThingsBoard ke sensor
sudo apt install -y rsyslog
echo '*.* @@192.168.4.200:514' | sudo tee /etc/rsyslog.d/50-remote.conf
sudo systemctl restart rsyslog
sudo grep -c "Failed password" /var/log/auth.log
```
**Verifikasi:** `thingsboard` bukan superuser dan tidak punya akses ke database lain; `auth.log`
menampilkan percobaan login Red Team dan log yang sama muncul di Security Onion.
**Bukti:** `C3_after_pg_roles.txt`, `C3_after_authlog_failed_logins.txt`, `C3_after_logs_in_onion.png`
**Status:** `Belum` · **PIC:** Blue Team

---

## D. Baseline Traffic Normal (Fase 1)

| Skenario normal | Perintah | Metrik baseline |
|---|---|---|
| Ping periodik gateway→server | `ping -i 5 192.168.4.5` (15 menit) | RTT rata-rata, jitter, jumlah paket |
| Buka dashboard KABITA & login tenant | 10× `curl -s -o /dev/null -w "%{http_code} %{time_total}\n" http://192.168.4.5:8080/login` | request/menit, ukuran respons |
| Ambil telemetri via REST | `curl /api/v1/<token>/telemetry` tiap 10 detik selama 10 menit | request/menit, payload |
| Publish telemetri normal (MQTT) | `mosquitto_pub -t v1/devices/me/telemetry -m '{"berat_kg":32.4,"pakan_kg":1.8}'` tiap 30 s | pesan/menit per device |
| Sinkronisasi waktu | `timedatectl` / NTP | 1 sesi/hari, port 123/udp |

**Artefak:** `baseline_minggu9.pcap` di sensor, ekspor Zeek `conn.log`/`http.log`, dan ringkasan
`baseline_summary.md`.
**Status:** `Belum` · **PIC:** Blue Team

## E. Matriks bukti → kriteria penilaian

| Kriteria (Bagian VII) | Bukti di repo |
|---|---|
| Pemetaan tech stack (20%) | `docs/presentation-minggu9/tech_stack_declaration.md` |
| Arsitektur & kesesuaian Minggu 4 (20%) | `docs/design/topology-v2.png`, `topology.png`, `ip_plan.md`, slide 3 |
| Progres hardening nyata (30%) | dokumen ini + `docs/blueteam/evidence/` |
| Rencana attack plan (20%) | `docs/redteam/attack_plan.md` |
| Kerja sama & peran (10%) | pembagian PIC di tabel + `docs/logbook.md` |

## F. Catatan jujur untuk presentasi

1. Seluruh kontrol di atas **belum dieksekusi**. OS target sudah memenuhi prasyarat
   (Ubuntu 26.04.1 LTS) dan IP statis lab aktif; **ThingsBoard belum terpasang** — instalasi
   mengikuti `docs/design/replica_setup.md` dan menjadi langkah pertama Fase 2.
2. Bila waktu sempit, prioritas: **B-3, A-2, B-1, B-2, C-2** (mencakup 3 kategori, dampak
   terbesar, dan langsung menutup kelemahan yang dipakai RT-02/RT-03/RT-04).
3. Untuk target Ubuntu, `ufw`/`fail2ban`/`sysctl` tersedia normal — tidak perlu jalur cadangan
   `iptables` seperti pada rencana awal berbasis Metasploitable2.
4. Jangan menaikkan status ke `Selesai` tanpa file bukti: dosen membuka repo langsung saat sesi.
