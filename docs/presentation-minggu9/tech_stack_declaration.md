# Deklarasi Tech Stack & Replikasi — KABITA (Kelompok 4)

**Produk IoT:** KABITA — pencatatan berat badan dan pakan kambing
**Pertemuan:** 9 (Checkpoint Fase 1 → 2) · **Revisi:** 22 Oktober 2026 (klarifikasi produk asli)
**Subnet lab:** `192.168.4.0/24` · **Target Node:** `192.168.4.5` — Ubuntu Server LTS 26.04

---

## 1. Konteks produk (KABITA)

KABITA adalah sistem pencatatan peternakan kambing. Perangkat lapangan menimbang kambing dan
pakan, lalu mengirim data ke backend untuk dicatat per ekor, per kandang, dan per hari.

| Komponen asli KABITA | Fungsi |
|---|---|
| Timbangan badan (load cell + HX711) | mengukur berat kambing (kg) |
| Timbangan pakan / wadah pakan | mengukur pakan yang diberikan (kg) |
| Penanda identitas (ear tag / RFID) | mengidentifikasi kambing |
| Gateway (ESP32 / Raspberry Pi) | mengirim telemetri ke backend |
| **Backend: ThingsBoard CE di Ubuntu Server** | menyimpan telemetri, dashboard, aturan, API |
| PostgreSQL | penyimpanan entity & telemetri ThingsBoard |

**Yang dinilai sebagai infrastruktur backend** dan menjadi objek SOC: ThingsBoard beserta
PostgreSQL dan portnya — bukan timbangan fisik.

---

## 2. Tabel Deklarasi Tech Stack (asli → replika)

Replika memakai **ThingsBoard Community Edition yang sama** seperti produk asli, sehingga
pemetaan bersifat 1:1. Yang tidak direplikasi hanya perangkat fisik (timbangan, RFID), yang
digantikan skrip pengirim telemetri.

| # | Komponen Backend | Teknologi pada KABITA asli | Replika di Target Node | Port | Catatan |
|---|---|---|---|---|---|
| 1 | Sistem operasi server | Ubuntu Server LTS | Ubuntu Server **26.04.1 LTS** | — | sama |
| 2 | Platform IoT / dashboard | **ThingsBoard CE** (Java 17, Spring Boot) | ThingsBoard CE, service `thingsboard` | **8080** | UI + REST API |
| 3 | Database | PostgreSQL 16 | PostgreSQL 16, database `thingsboard` | 5432 | hanya `127.0.0.1` |
| 4 | Transport MQTT perangkat | ThingsBoard MQTT transport | MQTT transport ThingsBoard | **1883** | autentikasi memakai **device access token** |
| 5 | Transport HTTP perangkat | REST `POST /api/v1/{token}/telemetry` | sama | 8080 | token di URL (kebiasaan nyata di lapangan) |
| 6 | Model data | Device per timbangan; telemetri `berat_kg`, `pakan_kg`, `rfid` | sama (device `KABITA-Timbangan-01`) | — | 1 device = 1 timbangan |
| 7 | Akun | Tenant admin + sysadmin | default `tenant@thingsboard.org`, `sysadmin@thingsboard.org` | — | **kredensial default** (kelemahan disengaja) |
| 8 | Manajemen server | SSH | OpenSSH port 22 | 22 | password auth aktif (kelemahan disengaja) |
| 9 | TLS | produksi: HTTPS | tidak dipakai di replika | — | dinyatakan terbuka; jadi temuan |
| 10 | Perangkat fisik | timbangan, RFID, gateway | **tidak ada** — digantikan `mosquitto_pub`/`curl` | — | batas replika |

### 2.1 Alur data yang direplikasi

```text
[timbangan] --MQTT 1883 (device token)--> [ThingsBoard] --JDBC--> [PostgreSQL 5432]
     |                                            |
     +--HTTP 8080 /api/v1/{token}/telemetry-------> dashboard KABITA (8080)
```

Telemetri contoh yang dikirim replika:

```json
{"berat_kg": 32.4, "pakan_kg": 1.8, "rfid": "KMB-014"}
```

---

## 3. Kelemahan yang sengaja dipasang (sasaran Fase 2)

Semua kelemahan di bawah adalah kondisi yang **lazim ditemukan** pada deployment ThingsBoard di
lapangan, sehingga skenario Red Team relevan dengan produk asli.

| # | Kelemahan | Lokasi | Skenario | Ditutup pada Fase 2 oleh |
|---|---|---|---|---|
| 1 | Kredensial default `tenant@thingsboard.org`/`tenant`, `sysadmin`/`sysadmin` | 8080 | RT-02 | A-1, A-2, A-4, B-3 |
| 2 | Password SSH lemah `iotadmin`/`123`, password auth aktif | 22 | RT-02 | A-1, A-2, A-4 |
| 3 | Device access token dipakai apa adanya (dapat dicuri/ditebak) | 1883/8080 | RT-03, RT-04 | C-2 |
| 4 | Telemetri dapat dipalsukan (berat/pakan) tanpa validasi | 8080/1883 | RT-03, RT-04 | C-2 |
| 5 | MQTT tanpa TLS, token terkirim plaintext | 1883 | RT-04 | (temuan; TLS dicatat) |
| 6 | PostgreSQL terbuka ke segmen lab pada konfigurasi awal | 5432 | RT-01 | B-2 |
| 7 | Tanpa rate limit pada API/dashboard | 8080 | RT-05 | ufw limit |

**Aturan:** setiap kelemahan wajib punya kontrol penutup di `hardening_checklist.md`. Serangan
yang tetap berhasil setelah mitigasi ditandai `TERBUKA` di `purple-team-log.md`.

---

## 4. Batasan replika (dinyatakan terbuka di presentasi)

1. Tidak ada timbangan, load cell, RFID, atau gateway fisik — telemetri dibangkitkan perangkat
   lunak. Konsekuensinya: tidak ada skenario serangan ke perangkat lapangan, hanya ke backend.
2. Tidak memakai TLS/HTTPS. Disengaja agar kredensial dan token terlihat di Wireshark (bahan
   analisis Blue Team), bukan kelalaian yang tidak tercatat.
3. Dataset kecil (satu device, beberapa ekor kambing) agar ringan pada 4 GB RAM.
4. Semua uji hanya di `192.168.4.0/24`; tidak ada koneksi ke backend KABITA yang sesungguhnya.

---

## 5. Kesepakatan tim

| Peran | Nama | Menyetujui pemetaan di atas |
|---|---|---|
| Lead | Olan | ☐ |
| Blue Team | Anggi Permana Putra (J0404241154) | ☐ |
| Red Team | Raka Syauqi Ferdian (J0404241112) | ☐ |
| Red Team | Zidan | ☐ |

_Diverifikasi ulang pada: ______ (tanggal commit final)_
