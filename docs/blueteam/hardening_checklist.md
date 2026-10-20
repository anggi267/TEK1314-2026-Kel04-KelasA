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
| B. Service & Attack Surface | 3 | 0 | 0 | 3 |
| C. Data & Application | 3 | 0 | 0 | 3 |
| **Total** | **10** | **0** | **0** | **10** |

_Prasyarat terpenuhi: VM target **Ubuntu Server 26.04.1 LTS**, IP statis `192.168.4.5/24` sudah
aktif, `sshd` berjalan, dan `iotadmin` punya sudo NOPASSWD (kemudahan lab — lihat
`docs/design/vm_config.md`). Yang belum: stack replika (nginx/DVWA/MariaDB/Mosquitto)._

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
Replika backend IoT hanya butuh 80 (dashboard/API), 3306 (lokal), 1883 (MQTT), 2222 (SSH).
Service bawaan Ubuntu Server yang tidak dipakai dimatikan:
```bash
sudo systemctl disable --now avahi-daemon cups cups-browsed rpcbind ModemManager 2>/dev/null
sudo systemctl list-unit-files --state=enabled | grep -Ev "ssh|nginx|mariadb|mosquitto|systemd|networking|apparmor|cron|rsyslog|unattended"
nmap -sS -p- 192.168.4.5 -oN /tmp/after_port.txt     # dari Kali
```
**Verifikasi:** jumlah port terbuka berkurang dibanding baseline; setiap port yang tersisa punya alasan.
**Bukti:** `B1_before_nmap_full.txt`, `B1_after_nmap_full.txt`, `B1_port_delta.md`
**Status:** `Belum` · **PIC:** Blue Team

### B-2 · Firewall whitelist + tutup MySQL dari luar
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2222/tcp
sudo ufw allow 80/tcp
sudo ufw allow from 192.168.4.100 to any port 1883 proto tcp
sudo ufw allow from 192.168.4.200 to any port 514 proto udp
sudo ufw --force enable && sudo ufw status verbose

# MySQL hanya lokal
sudo sed -i 's/^bind-address.*/bind-address = 127.0.0.1/' /etc/mysql/mariadb.conf.d/50-server.cnf
sudo systemctl restart mariadb
```
**Verifikasi:** dari Kali `nmap -sS -p1-1024 192.168.4.5` → hanya port whitelist `open`, sisanya
`filtered`; `mysql -h 192.168.4.5 -u iotadmin -p` → timeout (bukan `Access denied`).
**Bukti:** `B2_after_ufw_status.png`, `B2_before_nmap_vs_after_nmap.png`, `B2_after_mysql_localhost_only.txt`
**Status:** `Belum` · **PIC:** Blue Team

### B-3 · Patch OS/paket + hapus kredensial default
```bash
sudo apt update && sudo apt -y upgrade
sudo apt install -y unattended-upgrades && sudo dpkg-reconfigure -plow unattended-upgrades
sudo mysql_secure_installation      # hapus anonymous user, matikan remote root, hapus test DB
sudo passwd iotadmin                # ganti password lemah iotadmin123
mysql -u root -e "SELECT user,host FROM mysql.user;"   # harapan: tidak ada user tanpa password
apt list --upgradable                                  # harapan: kosong
```
**Verifikasi:** `apt list --upgradable` kosong; `mysql -u root` tanpa sudo → ditolak;
`hydra -l iotadmin -P rockyou.txt ssh://192.168.4.5 -s 2222 -t 4` → 0 valid pair (setelah A-2/A-4).
**Bukti:** `B3_before_apt_upgradable.txt`, `B3_after_apt_upgraded.txt`, `B3_after_mysql_secure.png`
**Status:** `Belum` · **PIC:** Blue Team

---

## C. Data & Application

### C-1 · Kredensial tidak hardcoded (env var)
```bash
sudo tee /var/www/iot-dashboard/.env >/dev/null <<'EOF'
DB_HOST=127.0.0.1
DB_NAME=iot_db
DB_USER=pbl_app
DB_PASS=<diisi-saat-eksekusi>
MQTT_USER=iot_gateway
MQTT_PASS=<diisi-saat-eksekusi>
EOF
sudo chmod 600 /var/www/iot-dashboard/.env
sudo chown www-data:www-data /var/www/iot-dashboard/.env
grep -rn "password\s*=" /var/www/iot-dashboard --include=*.php | grep -v ".env"   # harapan: kosong
```
**Bukti:** `C1_before_hardcoded_creds.png`, `C1_after_env_chmod600.txt`, `C1_after_no_hardcoded.txt`
**Status:** `Belum` · **PIC:** Red (review kode) + Blue (terapkan)

### C-2 · Validasi input API + autentikasi/ACL MQTT
```php
// /var/www/iot-dashboard/api.php — sebelum: "SELECT * FROM sensor_readings WHERE id=$id"
$stmt = $pdo->prepare('SELECT id, moisture, ts FROM sensor_readings WHERE id = :id');
$stmt->bindValue(':id', filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT), PDO::PARAM_INT);
$stmt->execute();
```
```bash
# Mosquitto: matikan anonymous, wajib user + ACL topik
sudo mosquitto_passwd -c /etc/mosquitto/passwd iot_gateway
sudo tee /etc/mosquitto/conf.d/pbl.conf >/dev/null <<'EOF'
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd
acl_file /etc/mosquitto/acl
EOF
sudo tee /etc/mosquitto/acl >/dev/null <<'EOF'
user iot_gateway
topic write sensor/+/data
topic read aktuator/#
EOF
sudo systemctl restart mosquitto
```
**Verifikasi:** `sqlmap -u "http://192.168.4.5/iot-dashboard/api.php?id=1" --batch` → tidak injectable;
`mosquitto_pub -h 192.168.4.5 -t aktuator/pompa -m x` tanpa kredensial → `Connection Refused: not authorized`.
**Bukti:** `C2_before_sqlmap_vulnerable.txt`, `C2_after_sqlmap_protected.txt`, `C2_after_mqtt_acl_denied.txt`
**Status:** `Belum` · **PIC:** Red + Blue

### C-3 · Least-privilege user DB + logging
```bash
mysql -u root <<'EOF'
CREATE USER IF NOT EXISTS 'pbl_app'@'localhost' IDENTIFIED BY '<password-dari-.env>';
GRANT SELECT, INSERT, UPDATE ON iot_db.sensor_readings TO 'pbl_app'@'localhost';
GRANT SELECT ON iot_db.users TO 'pbl_app'@'localhost';
FLUSH PRIVILEGES;
EOF
mysql -u root -e "SHOW GRANTS FOR 'pbl_app'@'localhost';"
# logging: aktifkan audit login & teruskan ke sensor
sudo apt install -y rsyslog
echo '*.* @@192.168.4.200:514' | sudo tee /etc/rsyslog.d/50-remote.conf
sudo systemctl restart rsyslog
sudo grep -c "Failed password" /var/log/auth.log
```
**Verifikasi:** grant hanya SELECT/INSERT/UPDATE pada 2 tabel (tanpa DROP/GRANT); `auth.log`
menampilkan percobaan login Red Team dan log yang sama muncul di Security Onion.
**Bukti:** `C3_after_show_grants.txt`, `C3_after_authlog_failed_logins.txt`, `C3_after_logs_in_onion.png`
**Status:** `Belum` · **PIC:** Blue Team

---

## D. Baseline Traffic Normal (Fase 1)

| Skenario normal | Perintah | Metrik baseline |
|---|---|---|
| Ping periodik sensor→server | `ping -i 5 192.168.4.5` (15 menit) | RTT rata-rata, jitter, jumlah paket |
| Buka dashboard & login | 10× `curl -s -o /dev/null -w "%{http_code} %{time_total}\n" http://192.168.4.5/iot-dashboard/login.php` | request/menit, ukuran respons |
| Query data sensor | 1× `curl ".../api.php?id=1"` tiap 10 detik selama 10 menit | request/menit, payload |
| Publish MQTT normal | `mosquitto_pub -t sensor/soil/data -m '{"moisture":42}'` tiap 30 s | pesan/menit per topik |
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
   (Ubuntu 26.04.1 LTS), tetapi IP statis lab dan stack replika belum dipasang.
2. Bila waktu sempit, prioritas: **B-3, A-2, B-1, B-2, C-2** (mencakup 3 kategori, dampak
   terbesar, dan langsung menutup kelemahan yang dipakai RT-02/RT-03/RT-04).
3. Untuk target Ubuntu, `ufw`/`fail2ban`/`sysctl` tersedia normal — tidak perlu jalur cadangan
   `iptables` seperti pada rencana awal berbasis Metasploitable2.
4. Jangan menaikkan status ke `Selesai` tanpa file bukti: dosen membuka repo langsung saat sesi.
