# Hardening Checklist — Target Node Replika `192.168.4.5` (Metasploitable2)

**Kelompok 4 · TEK1314 Kelas A · Checkpoint Minggu 9**
**Acuan:** Panduan PBL Pertemuan 9, Bagian VIII (minimal 8 kontrol, ≥2 per kategori A/B/C, bukti before/after).

> **Cara mengisi status:** `Belum` → `Sebagian` → `Selesai`. Kolom status **hanya** boleh
> diubah menjadi `Selesai` bila file bukti before *dan* after sudah ada di
> `docs/blueteam/evidence/` dengan nama sesuai kolom "File bukti".
> Semua perintah di bawah dijalankan dari dalam VM target sebagai `msfadmin` (sudo),
> bukan sebagai `root` langsung.

## Ringkasan status

| Kategori | Jumlah kontrol | Selesai | Sebagian | Belum |
|---|---|---|---|---|
| A. Access & Authentication | 4 | 0 | 0 | 4 |
| B. Service & Attack Surface | 3 | 0 | 0 | 3 |
| C. Data & Application | 3 | 0 | 0 | 3 |
| **Total** | **10** | **0** | **0** | **10** |

_Status per commit terakhir Minggu 9: seluruh eksekusi dijadwalkan pada Fase 2 (Minggu 10)._
_Pada Minggu 9 yang dinilai adalah kejelasan rencana + kesiapan bukti, bukan angka "selesai"._

---

## A. Access & Authentication

### A-1 · Nonaktifkan login `root` langsung via SSH
**Perintah / config:**
```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo /etc/init.d/ssh restart
grep -i permitrootlogin /etc/ssh/sshd_config
```
**Verifikasi:** `ssh root@192.168.4.5` → `Permission denied (publickey,password)`.
**Bukti before:** `A1_before_sshd_config.png` (isi `sshd_config` asli)
**Bukti after:** `A1_after_sshd_config.png` + `A1_after_root_login_denied.png`
**Status:** `Belum` · **PIC:** Blue Team

### A-2 · SSH key-based auth, matikan password auth
**Perintah / config:**
```bash
ssh-keygen -t ed25519 -f ~/.ssh/pbl_kel4 -N ""
ssh-copy-id -i ~/.ssh/pbl_kel4.pub msfadmin@192.168.4.5
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sudo /etc/init.d/ssh restart
```
**Verifikasi:** login dengan `-o PreferredAuthentications=password` → ditolak; dengan `-i ~/.ssh/pbl_kel4` → berhasil.
**Bukti:** `A2_before_password_login_ok.png`, `A2_after_password_login_denied.png`, `A2_after_key_login_ok.png`
**Status:** `Belum` · **PIC:** Blue Team

### A-3 · Ganti port default SSH 22 → 2222
**Perintah / config:**
```bash
sudo sed -i 's/^#\?Port .*/Port 2222/' /etc/ssh/sshd_config
sudo /etc/init.d/ssh restart
```
**Verifikasi:** `nmap -p22,2222 192.168.4.5` → 22 `closed`, 2222 `open`.
**Bukti:** `A3_before_ssh_port22_nmap.png`, `A3_after_ssh_port2222_nmap.png`
**Status:** `Belum` · **PIC:** Blue Team
_Catatan: ganti port bukan kontrol keamanan sejati (security by obscurity) — nilainya
untuk mengurangi noise bot otomatis. Tetap dipasangkan dengan A-2 dan A-4._

### A-4 · Fail2ban / rate-limit percobaan login
**Perintah / config:**
```bash
sudo apt-get install -y fail2ban
sudo tee /etc/fail2ban/jail.local >/dev/null <<'EOF'
[sshd]
enabled = true
port = 2222
maxretry = 3
bantime = 600
findtime = 600
EOF
sudo service fail2ban restart
sudo fail2ban-client status sshd
```
**Verifikasi:** 4 percobaan login gagal dari Kali → IP `192.168.4.100` masuk daftar `Banned IP list`.
**Bukti:** `A4_after_fail2ban_status_banned.png`
**Status:** `Belum` · **PIC:** Blue Team

---

## B. Service & Attack Surface

### B-1 · Nonaktifkan service/port yang tidak dipakai
Target yang dimatikan: `telnet(23)`, `rlogin/rsh(512-514)`, `tftp(69)`, `smtp(25)`, `ircd(6667)`,
`distccd(3632)`, `tomcat(8180)` — tidak satu pun dipakai replika backend IoT.
```bash
sudo update-rc.d -f telnetd remove 2>/dev/null; sudo killall telnetd 2>/dev/null
sudo /etc/init.d/postfix stop;   sudo update-rc.d -f postfix remove
sudo /etc/init.d/samba stop;     sudo update-rc.d -f samba remove
sudo pkill -f distccd; sudo pkill -f ircd; sudo pkill -f tomcat
```
**Verifikasi:** `nmap -p- 192.168.4.5` sebelum vs sesudah → jumlah port terbuka turun.
**Bukti:** `B1_before_nmap_full.png`, `B1_after_nmap_full.png`, `B1_port_delta.md` (tabel port hilang)
**Status:** `Belum` · **PIC:** Blue Team

### B-2 · Firewall whitelist port (ufw), default deny
Hanya izinkan yang dibutuhkan replika: 80/tcp (dashboard/API), 3306/tcp **hanya dari** `192.168.4.5`
lokal + `192.168.4.200` (monitoring), 2222/tcp (SSH), 1883/tcp (MQTT, setelah Fase 2).
```bash
sudo apt-get install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2222/tcp
sudo ufw allow 80/tcp
sudo ufw allow from 192.168.4.200 to any port 2222 proto tcp
sudo ufw allow from 192.168.4.200 to any port 3306 proto tcp
sudo ufw --force enable
sudo ufw status verbose
```
**Verifikasi:** dari Kali `nmap -sS -p1-1024 192.168.4.5` → hanya port whitelist `open`,
sisanya `filtered`. MySQL dari Kali (`mysql -h 192.168.4.5 -u root`) → timeout, bukan
`Access denied` (paket tidak sampai).
**Bukti:** `B2_after_ufw_status.png`, `B2_before_nmap_vs_after_nmap.png`
**Status:** `Belum` · **PIC:** Blue Team

### B-3 · Patch OS/paket & hapus kredensial default DB/aplikasi
```bash
sudo apt-get update && sudo apt-get -y upgrade
# kredensial default MySQL kosong -> set password root yang kuat
mysqladmin -u root password 'K3l4-PBL-Str0ng!'
# akun default aplikasi
sudo passwd msfadmin          # ganti password default msfadmin
# DVWA: ganti admin/password via halaman setup.php
mysql -u root -p -e "UPDATE dvwa.users SET password=MD5('N3wAdm1n!') WHERE user='admin';"
```
**Verifikasi:** `mysql -h 192.168.4.5 -u root` tanpa password → `Access denied`;
`hydra -l root -P rockyou.txt mysql://192.168.4.5` → 0 valid pair pada uji cepat 100 kandidat.
**Bukti:** `B3_before_mysql_root_nopass.png`, `B3_after_mysql_access_denied.png`, `B3_after_apt_upgrade.png`
**Status:** `Belum` · **PIC:** Blue Team

---

## C. Data & Application

### C-1 · Kredensial tidak hardcoded — pindah ke environment variable
Kode dashboard replika memakai kredensial DB langsung di source (`db.php` gaya DVWA).
```bash
# pada direktori aplikasi replika
sudo tee /var/www/pbl/.env >/dev/null <<'EOF'
DB_HOST=127.0.0.1
DB_USER=pbl_app
DB_PASS=<diisi-via-secrets-manager-lokal>
MQTT_USER=pbl_gw
EOF
sudo chmod 600 /var/www/pbl/.env
sudo chown www-data:www-data /var/www/pbl/.env
# pastikan .env tidak masuk repo/git
echo ".env" | sudo tee -a /var/www/pbl/.gitignore
```
**Verifikasi:** `grep -rn "password" /var/www/pbl --include=*.php` → tidak ada password literal;
`git log -S "DB_PASS"` pada repo replika → kosong.
**Bukti:** `C1_before_dbphp_hardcoded.png`, `C1_after_env_file_chmod600.png`, `C1_after_grep_no_secret.png`
**Status:** `Belum` · **PIC:** Red Team (review kode) + Blue Team (terapkan)

### C-2 · Validasi input pada endpoint API & topic MQTT
Replika API diubah dari query string mentah menjadi prepared statement + allow-list topik MQTT.
```php
// sebelum: $id = $_GET['id']; $q = "SELECT * FROM sensor_readings WHERE id=$id";
$stmt = $pdo->prepare('SELECT * FROM sensor_readings WHERE id = :id');
$stmt->bindValue(':id', filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT), PDO::PARAM_INT);
$stmt->execute();
```
Untuk MQTT (Fase 2), broker dikonfigurasi ACL: gateway hanya boleh `publish` ke
`sensor/+/data`, dashboard hanya `subscribe`; publish ke `aktuator/#` hanya oleh service otomasi.
**Verifikasi:** `sqlmap -u "http://192.168.4.5/pbl/api.php?id=1" --batch` → tidak ada injeksi
(`parameter appears to be protected`); `mosquitto_pub -t aktuator/pompa -m "1"` dengan user
gateway → `Not authorized`.
**Bukti:** `C2_before_sqlmap_vulnerable.png`, `C2_after_sqlmap_protected.png`, `C2_after_mqtt_acl_denied.png`
**Status:** `Belum` · **PIC:** Red Team + Blue Team

### C-3 · Least-privilege user DB + logging aktivitas mencurigakan
```bash
mysql -u root -p <<'EOF'
CREATE USER 'pbl_app'@'localhost' IDENTIFIED BY '<password-dari-.env>';
GRANT SELECT, INSERT, UPDATE ON pbl_db.sensor_readings TO 'pbl_app'@'localhost';
GRANT SELECT ON pbl_db.users TO 'pbl_app'@'localhost';
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'pbl_app'@'localhost';
FLUSH PRIVILEGES;
EOF
# logging: audit login & akses file di syslog
sudo sed -i 's/^#\?auth\.\*/auth.*   \/var\/log\/auth.log/' /etc/syslog.conf
sudo /etc/init.d/syslog restart
```
**Verifikasi:** `SHOW GRANTS FOR 'pbl_app'@'localhost';` → hanya 2 grant, **tanpa** `DROP`/`GRANT`;
`grep "Failed password" /var/log/auth.log` menampilkan percobaan login Red Team.
**Bukti:** `C3_after_show_grants.png`, `C3_after_authlog_failed_logins.png`
**Status:** `Belum` · **PIC:** Blue Team

---

## D. Baseline Traffic Normal (Fase 1)

Tujuan: punya pembanding "normal" agar alert Fase 2 punya arti. Diambil **sebelum** serangan.

| Skenario normal | Perintah | Metrik baseline |
|---|---|---|
| Ping periodik sensor→server | `ping -i 5 192.168.4.5` (15 menit) | RTT rata-rata, jitter, jumlah paket |
| Buka dashboard & login | 10× akses `http://192.168.4.5/` dari Kali | Request/menit, ukuran respons |
| Query data sensor | 1 panggilan API tiap 10 detik selama 10 menit | Request/menit, payload |
| Sinkronisasi waktu | `ntpdate` harian | 1 sesi/hari, port 123/udp |

**Artefak:** `pcap` 15 menit di Security Onion (`baseline_minggu9.pcap`), tangkapan layar
Zeek `conn.log`/`http.log`, dan tabel ringkasan `baseline_summary.md`.
**Status:** `Belum` · **PIC:** Blue Team

## E. Matriks bukti → kriteria penilaian

| Kriteria (Bagian VII) | Bukti di repo |
|---|---|
| Pemetaan tech stack (20%) | `docs/presentation-minggu9/tech_stack_declaration.md` |
| Arsitektur & kesesuaian Minggu 4 (20%) | `docs/design/topology.png`, `docs/design/ip_plan.md`, slide 3 |
| Progres hardening nyata (30%) | dokumen ini + `docs/blueteam/evidence/` |
| Rencana attack plan (20%) | `docs/redteam/attack_plan.md` |
| Kerja sama & peran (10%) | pembagian PIC di tabel + `docs/logbook.md` |

## F. Catatan jujur untuk presentasi

1. Seluruh kontrol di atas **belum dieksekusi** pada commit Minggu 9 — VM target belum
   dijalankan ulang setelah UTS. Yang disiapkan adalah perintah pasti + skema bukti, agar
   eksekusi Fase 2 (Minggu 10) tinggal jalan dan screenshot.
2. Bila waktu sempit, prioritas eksekusi: **A-2, B-1, B-2, B-3, C-1** (lima kontrol ini sudah
   memenuhi 3 kategori dengan dampak terbesar), lalu sisanya.
3. Jangan mengubah status menjadi `Selesai` tanpa file bukti — dosen membuka repo langsung
   saat presentasi.

