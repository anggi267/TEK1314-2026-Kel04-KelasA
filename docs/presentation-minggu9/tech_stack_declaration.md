# Deklarasi Tech Stack & Replikasi — Kelompok 4 (TEK1314 Kelas A)

**Pertemuan:** 9 (Checkpoint Fase 1 → Fase 2) · **Revisi:** Minggu 9 (target diganti ke Ubuntu Server)
**Subnet lab:** `192.168.4.0/24` · **Target Node:** `192.168.4.5` — Ubuntu Server LTS 26.04

---

## 1. Tabel Deklarasi Tech Stack (asli → replika)

Karena replika memakai **Ubuntu Server**, komponen backend dapat dipetakan nyaris satu-satu.
Yang perlu disesuaikan hanya `[[ISI: ...]]` (detail produk IoT asli kelompok).

| # | Komponen Backend | Teknologi pada proyek IoT asli | Replika di Target Node (Ubuntu Server) | Port | Catatan |
|---|---|---|---|---|---|
| 1 | Sistem operasi server | Ubuntu Server LTS 26.04 `[[ISI]]` | Ubuntu Server LTS 26.04 | — | Sama jenis; dukungan keamanan aktif → `apt upgrade` bisa dibuktikan (B-3) |
| 2 | Web dashboard monitoring | Aplikasi web (Nginx + PHP/Node) `[[ISI]]` | Nginx + PHP-FPM + DVWA sebagai dashboard | 80/tcp | DVWA dipakai karena *vulnerable by design* → bahan RT-03 |
| 3 | API gateway | REST: `/api/sensor`, `/api/aktuator` `[[ISI]]` | `api.php` (parameter `?id=`) di direktori dashboard | 80/tcp | Endpoint sengaja dibuat tanpa prepared statement |
| 4 | Database / penyimpanan | MySQL 8 / MariaDB `[[ISI]]` | MariaDB — database `iot_db` (`users`, `sensor_readings`) | 3306/tcp | Mendengarkan di semua interface (kelemahan disengaja #4) |
| 5 | Protokol komunikasi sensor | MQTT 3.1.1 (Mosquitto) `[[ISI]]` | Mosquitto, `allow_anonymous true`, tanpa ACL topik | 1883/tcp | Kelemahan disengaja #3 → RT-04; ditutup lewat C-2 |
| 6 | Autentikasi pengguna | JWT / session + role `[[ISI]]` | Session login dashboard + user OS `iotadmin` | 80, 22 | Password lemah `iotadmin123` (kelemahan disengaja #1) |
| 7 | Manajemen jarak jauh | SSH key-based, non-root `[[ISI]]` | OpenSSH, password auth aktif, port 22 | 22/tcp | Objek kontrol A-1…A-4 |
| 8 | Telemetri & log | Syslog + agent monitoring `[[ISI]]` | syslog + `auth.log` → diteruskan ke Security Onion | 514/udp | Sumber log Blue Team |
| 9 | Segmentasi & kontrol jaringan | VLAN perangkat lapangan vs server `[[ISI]]` | Satu segmen Internal Network `pbl-kel4` + firewall host | — | Keterbatasan lab: dipisahkan di host (ufw), bukan VLAN fisik |
| 10 | Pembaruan firmware/perangkat | OTA update bertanda tangan `[[ISI]]` | Tidak direplikasi | — | Dinyatakan terbuka di presentasi |

## 2. Kelemahan yang sengaja dipasang (bukan kelalaian)

Replika **harus** punya celah agar skenario Red Team Bagian IX punya sasaran nyata. Daftar
lengkap ada di `docs/design/replica_setup.md` Bagian 3:

| # | Kelemahan | Skenario | Ditutup oleh |
|---|---|---|---|
| 1 | Password lemah `iotadmin` + SSH password auth | RT-02 | A-2, A-4 |
| 2 | SQL injection `api.php` / DVWA level low | RT-03 | C-2, C-3 |
| 3 | MQTT anonymous tanpa ACL | RT-04 | C-2 |
| 4 | MySQL terbuka di semua interface | RT-03 | B-2 |
| 5 | Service tidak terpakai tetap hidup | RT-01 | B-1 |
| 6 | Tanpa rate limit di dashboard | RT-05 | ufw limit |

## 3. Mengapa Ubuntu Server (bukan Metasploitable2)

1. **Konsisten dengan narasi IoT** — backend yang diamankan memang Ubuntu/Nginx/MySQL/MQTT,
   bukan kumpulan service acak.
2. **Hardening dapat dibuktikan dengan tool standar** — `ufw`, `fail2ban`, `systemctl`,
   `apt upgrade` semuanya tersedia dan berfungsi (Metasploitable2 berbasis Ubuntu 8.04 yang
   repositorinya sudah EOL, sehingga beberapa kontrol mustahil dieksekusi).
3. **Tiga kategori hardening (A/B/C) dapat diuji ujung ke ujung** — termasuk patching dan
   pembatasan permukaan serangan di level aplikasi.
4. **Risiko yang dikelola:** karena OS tidak rentan bawaan, kelemahan dipasang eksplisit
   (Bagian 2). Ini justru lebih jujur: setiap celah punya kontrol penutup yang diuji.

## 4. Batasan replika (dinyatakan terbuka di presentasi)

- Tidak ada perangkat sensor fisik, LoRaWAN, atau koneksi ke Mitra — semua uji di jaringan
  tertutup `192.168.4.0/24`.
- TLS tidak digunakan pada Fase 2 (dashboard HTTP) → kredensial terlihat di Wireshark;
  ini menjadi temuan Blue Team, bukan kelalaian tak tercatat.
- Tidak ada OTA update bertanda tangan; replika berhenti pada "patch OS + patch aplikasi".

## 5. Kesepakatan tim

| Peran | Nama | Menyetujui pemetaan di atas |
|---|---|---|
| Lead | Olan | ☐ |
| Blue Team | Anggi Permana Putra (J0404241154) | ☐ |
| Red Team | Raka Syauqi Ferdian (J0404241112) | ☐ |
| Red Team | Zidan | ☐ |

_Diverifikasi ulang pada: ______ (tanggal commit final)_
