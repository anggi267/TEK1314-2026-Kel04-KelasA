# Deklarasi Tech Stack & Replikasi — Kelompok 4 (TEK1314 Kelas A)

**Pertemuan:** 9 (Checkpoint Fase 1 → Fase 2)
**Subnet lab:** `192.168.4.0/24` (lihat `docs/design/ip_plan.md`)
**Target Node replika:** `192.168.4.5` — Metasploitable2

---

## 0. Konteks produk IoT (WAJIB DISESUAIKAN)

> **Status: PERLU KONFIRMASI KELOMPOK.**
> Bagian yang ditandai `[[ISI: ...]]` di bawah masih berupa asumsi kerja agar dokumen bisa
> dipresentasikan. Ganti dengan produk IoT asli kelompok sebelum commit final.
> Asumsi kerja saat ini: **sistem otomasi & monitoring budidaya (smart farming)** —
> sensor kelembapan tanah + aktuator pompa, dengan backend server data, API gateway,
> dan dashboard monitoring. Yang diamankan SOC adalah **backend-nya**, bukan sensor fisik.

## 1. Tabel Deklarasi Tech Stack (asli → replika)

| # | Komponen Backend | Teknologi pada proyek IoT asli | Replikasi di Target Node (`192.168.4.5`) | Port | Catatan adaptasi |
|---|---|---|---|---|---|
| 1 | Sistem operasi server | Linux (Ubuntu Server 22.04 LTS) `[[ISI]]` | Metasploitable2 (Ubuntu 8.04, kernel 2.6) | — | Versi OS sengaja dibuat lama & rentan agar celah dapat didemonstrasikan; hardening tetap dilakukan di atasnya |
| 2 | Web dashboard monitoring | Aplikasi web (PHP/Laravel atau Node.js) + Nginx `[[ISI]]` | Apache 2.2 + PHP 5.2, DVWA / Mutillidae | 80/tcp | DVWA berperan sebagai "dashboard" dengan form login, session, dan query DB — cukup untuk mereplika permukaan serangan web |
| 3 | API gateway | REST API (endpoint `/api/sensor`, `/api/aktuator`) `[[ISI]]` | Endpoint PHP di DVWA + phpMyAdmin | 80/tcp, 8080/tcp | Request API dimodelkan sebagai parameter GET/POST yang dapat diuji injeksi |
| 4 | Database / penyimpanan data | MySQL 8 / PostgreSQL 14 `[[ISI]]` | MySQL 5.0.51a | 3306/tcp | Menyimpan tabel `users` & `sensor_readings`; kredensial default `root` tanpa password = celah nyata untuk diuji |
| 5 | Protokol komunikasi sensor | MQTT 3.1.1 (Mosquitto) + HTTP REST `[[ISI]]` | **Ditambah di Fase 2:** Mosquitto broker di port 1883 (instalasi paket pada VM target) | 1883/tcp | Metasploitable2 belum membawa broker MQTT; penambahan ini yang membuat replika relevan dengan protokol IoT. Bila tidak memungkinkan, topik MQTT diganti uji HTTP REST saja |
| 6 | Autentikasi pengguna | JWT / session + MFA dashboard `[[ISI]]` | Session PHP DVWA + akun default `admin`/`password`, `msfadmin`/`msfadmin` | 80, 22 | Dipakai untuk menguji default credential & brute-force |
| 7 | Manajemen jarak jauh | SSH (key-based, non-root) `[[ISI]]` | OpenSSH 4.7p1, login password aktif | 22/tcp | Menjadi objek hardening kategori A |
| 8 | Transfer berkas firmware/backup | SFTP / FTP internal `[[ISI]]` | vsftpd 2.3.4 (backdoor CVE-2011-2523) | 21/tcp | Contoh teknis "service usang yang wajib dipatch/dinonaktifkan" |
| 9 | Telemetri & log | Syslog + agent monitoring `[[ISI]]` | Syslog Metasploitable2 → diteruskan ke Security Onion | 514/udp | Menjadi sumber log Blue Team selain sensor jaringan |
| 10 | Segmentasi & kontrol jaringan | VLAN terpisah untuk perangkat lapangan vs server `[[ISI]]` | Satu switch, satu subnet `192.168.4.0/24` | — | Keterbatasan lab: segmentasi disimulasikan lewat firewall host (ufw) + aturan deny, bukan VLAN fisik |

## 2. Alasan replika memakai Metasploitable2

1. **Konsistensi dengan Minggu 4** — OS target sudah dikunci di `docs/design/ip_plan.md` dan
   digambar di `docs/design/topology.png`. Mengganti target sekarang berarti membatalkan
   deliverable Minggu 4 (nilai arsitektur 20%).
2. **Celah nyata, bukan simulasi main-main** — setiap temuan Red Team dapat dikaitkan dengan
   CVE/konfigurasi default yang benar-benar ada (vsftpd 2.3.4, MySQL root kosong, DVWA SQLi
   tingkat low), sehingga rencana serangan Fase 2 dapat dinilai kelayakannya oleh dosen.
3. **Ringan** — 1 VM melayani peran web, DB, dan manajemen sekaligus; cocok dengan RAM laptop
   anggota (kendala yang sudah dicatat sejak Minggu 4).

## 3. Batasan replika (dinyatakan terbuka di presentasi)

- Tidak ada perangkat sensor fisik, LoRaWAN, atau koneksi ke Mitra — seluruh uji dilakukan di
  jaringan tertutup `192.168.4.0/24` (sesuai Prinsip Simulasi vs Sistem Nyata, Bagian III panduan).
- TLS/HTTPS tidak direplikasi pada Fase 2 (dashboard berjalan di HTTP) — justru menjadi bahan
  analisis Blue Team: traffic kredensial terlihat di Wireshark.
- Broker MQTT baru ditambahkan pada Fase 2, sehingga skenario RT-04 (MQTT spoofing) berstatus
  *kondisional* sampai broker terpasang.

## 4. Kesepakatan tim

| Peran | Nama | Menyetujui pemetaan di atas |
|---|---|---|
| Lead | Olan | ☐ |
| Blue Team | Anggi Permana Putra (J0404241154) | ☐ |
| Red Team | Raka Syauqi Ferdian (J0404241112) | ☐ |
| Red Team | Zidan | ☐ |

_Diverifikasi ulang pada: ______ (tanggal commit final)_
