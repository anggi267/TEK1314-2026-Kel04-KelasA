# Checklist Hardening — 10 Kontrol

Target Node: Ubuntu Server 26.04.1 + KABITA (Nuxt 4 + PostgreSQL 18).
Status per 22 Oktober 2026: **2 selesai, 1 sebagian, 7 belum** (sisanya sasaran Fase 2).

| Kategori | Kontrol | Selesai | Sebagian | Belum |
|---|---|---|---|---|
| A. Akses & Autentikasi | 4 | 0 | 0 | 4 |
| B. Service & Attack Surface | 3 | 2 | 1 | 0 |
| C. Data & Aplikasi | 3 | 0 | 0 | 3 |
| **Total** | **10** | **2** | **1** | **7** |

Bukti before/after: `docs/blueteam/evidence/hardening/`.

---

## A. Akses & Autentikasi

### A-1 Kredensial default diganti & password di-hash
- **Kondisi sekarang:** `admin/admin123` dan `operator/operator123`, password **plaintext** di tabel `users`.
- **Uji:** `psql -d kabita -c "select username, password from users"` → terbaca apa adanya.
- **Perbaikan (Fase 2):** hash bcrypt/argon2, paksa ganti saat login pertama.
- **Status:** Belum (sengaja, sasaran RT-02/RT-03).

### A-2 SSH memakai key, password auth dimatikan
- **Kondisi sekarang:** `PasswordAuthentication yes`, `PermitRootLogin no`.
- **Uji:** `sudo sshd -T | grep -i passwordauth` → `yes`.
- **Perbaikan:** pasang public key, lalu `PasswordAuthentication no` + `sudo systemctl reload ssh`.
- **Status:** Belum.

### A-3 Akses administrasi dibatasi
- **Kondisi sekarang:** ufw hanya membuka 22 dan 80; belum ada `AllowUsers`/`Match Address`.
- **Uji:** `sudo ufw status` (✅), `sudo sshd -T | grep allowusers` (kosong).
- **Status:** Belum (separuh terpenuhi lewat firewall, lihat B-2).

### A-4 Sudo tanpa password dicabut
- **Kondisi sekarang:** `iotadmin ALL=(ALL) NOPASSWD: ALL` (kemudahan otomasi lab).
- **Uji:** `sudo -n -l` → baris NOPASSWD.
- **Perbaikan:** hapus `/etc/sudoers.d/90-pbl-nopasswd`, login pakai password.
- **Status:** Belum — **wajib dicabut sebelum penilaian akhir**.

---

## B. Service & Attack Surface

### B-1 Minimalisasi service
- **Tindakan:** `systemctl disable --now ModemManager snapd fwupd multipathd upower udisks2`.
- **Hasil:** service aktif turun dari 24 → 18 (hanya yang dibutuhkan: ssh, kabita, postgresql,
  fail2ban, chrony, journald, networkd, rsyslog, cron).
- **Bukti:** `hardening/before.txt` vs `hardening/after.txt` bagian *Service aktif*.
- **Status:** ✅ **Selesai**.

### B-2 Firewall default-deny
- **Tindakan:** `ufw default deny incoming`, allow `22/tcp` (admin), allow `80/tcp` dari
  `192.168.4.0/24` saja; PostgreSQL tidak dibuka (hanya `127.0.0.1`).
- **Uji:** `sudo ufw status verbose` → `Status: active`, 2 rule.
- **Bukti:** `hardening/after.txt` bagian *Firewall ufw*.
- **Status:** ✅ **Selesai**.

### B-3 Patch sistem & pembaruan otomatis
- **Tindakan:** `apt update && apt full-upgrade`, `unattended-upgrades` aktif.
- **Hasil:** `full-upgrade` selesai; **10 paket** keluarga `systemd`/`udev` masih ditahan
  *phased update* Ubuntu (bukan kegagalan, tidak butuh reboot). Sisa ini dicatat, bukan diklaim selesai.
- **Status:** ⏳ **Sebagian**.

---

## C. Data & Aplikasi

### C-1 TLS pada dashboard
- **Kondisi sekarang:** HTTP polos di port 80 (cookie sesi ikut terekspos).
- **Perbaikan (Fase 2):** sertifikat self-signed, redirect 80 → 443, cookie `Secure`.
- **Status:** Belum.

### C-2 Query parameterized & validasi input
- **Kondisi sekarang:** dua endpoint merangkai SQL dari input (`/api/telemetri`, `/api/login`) —
  sudah dibuktikan bisa ditembus (detail: `PBL-pendukung/docs/design/replica_setup.md`).
- **Perbaikan (Fase 2):** prepared statement + validasi tipe/rentang.
- **Status:** Belum (sengaja, sasaran RT-03).

### C-3 Token device & least privilege database
- **Kondisi sekarang:** token statis di query string, tanpa rotasi; role `kabita` punya
  `ALL` pada schema `public`.
- **Perbaikan (Fase 2):** rotasi token, rate limit, grant hanya SELECT/INSERT pada tabel yang perlu.
- **Status:** Belum.
