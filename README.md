# Logbook PBL Keamanan Siber — Kelompok 4

**TEK1314 Keamanan Siber** · Kelas A · Skenario SOC Engagement — backend sistem IoT KABITA
Target Node replika `192.168.4.5` · Monitoring `192.168.4.200` (Security Onion) · Attacker `192.168.4.100`

> **Lingkup:** seluruh pengujian dilakukan terhadap **replika** sistem IoT KABITA di lab terisolasi
> `192.168.4.0/24`, bukan sistem produksi milik Mitra. Data yang digunakan adalah data dummy/sintetis.

---

## Anggota & Peran

| Nama                            | NIM         | Peran     |
| :------------------------------ | :---------- | :-------- |
| Olan Elrai Ramotan Sibagariang  | J0404241158 | Lead      |
| Anggi Permana Putra             | J0404241154 | Blue Team |
| Raka Syauqi Ferdian             | J0404241112 | Red Team  |
| Muhammad Zidan                  | J0404241173 | Red Team  |

---

## Artefak Final (Fase 3 — Minggu 14–15)

Semua artefak diunggah **sebelum praktikum Minggu 14 dimulai**, terlepas dari sesi undian yang didapat.

| Artefak | Path | Isi |
| :--- | :--- | :--- |
| **Incident Report final** | [`docs/final/incident_report.pdf`](docs/final/incident_report.pdf) | 8 bagian NIST SP 800-61r2, 21 halaman |
| **Video demo Purple Team Loop** | [`docs/final/video_demo.mp4`](docs/final/video_demo.mp4) · [skrip & naskah](<docs/final/Skrip & Naskah Video Demo Purple Team Loop — Skenario 5 (KABITA).md>) | 1 siklus penuh: serangan → deteksi → mitigasi → verifikasi |
| **Slide presentasi final** | [`docs/presentation-final/slides.pdf`](docs/presentation-final/slides.pdf) | 12 slide landscape sesuai kisi-kisi Bagian VII |

---

## Ringkasan Akhir Proyek

Tiga node pada Internal Network `pbl-kel4` membentuk rantai SOC lengkap: **Target Node** Ubuntu 26.04
(Nginx, backend Golang, Mosquitto, PostgreSQL, fail2ban, UFW), **Attacker Node** Kali Linux, dan
**Monitoring Node** Security Onion. Yang direplikasi dari KABITA adalah **bentuk arsitektur** — pilihan
komponen, protokol, dan titik pertemuan jalur data — bukan skala maupun data Mitra.

Lima skenario serangan dieksekusi **4 November 2026, 14:55–15:20 UTC** terhadap Target Node yang sudah
ter-harden (8/8 kontrol A.1–C.3):

| # | Skenario | Hasil | Status |
| :- | :--- | :--- | :--- |
| 1 | Reconnaissance (`nmap -p-`) | 3 port terbuka: 80/nginx, 1883/mqtt, 2222/ssh. 443 *closed*, 22/5432/8080 *filtered*, 65.531 port filtered | Tertahan |
| 2 | Brute-force SSH (Hydra) | Hydra berhenti **sebelum satu percobaan** (`method reply 4`); 8 login akun gagal → fail2ban ban 600 s | Tertahan |
| 3 | SQL injection (sqlmap) | 4 payload manual → 400; 1.295 request → *not injectable*; `log_statement` PostgreSQL bersih | Tertahan |
| 4 | MQTT tanpa kredensial | 3 upaya ditolak `not authorised`; `bobot_log` tidak bertambah | Tertahan |
| 5 | MQTT kredensial bocor | 299 kg & 0,1 kg tersimpan; topik liar diterima; 20 pesan < 1 s tanpa throttle; **60 → 83 baris** | **Berhasil dieksploitasi** |
| — | Deteksi (Security Onion) | **0 alert** untuk seluruh rangkaian serangan | **Gagal** |

**Dua kegagalan sistemik yang menjadi inti Incident Report:**

1. **Visibilitas nol.** Squert mencatat 0 event untuk seluruh rentang 4 November 2026 tanpa filter objek
   maupun sensor. Penyebab di sisi sensor: proses `snort` mati, berkas `snort.unified2` berukuran 0 byte
   bertanggal 19 Juni 2020, `output unified2` memakai path relatif, dan `barnyard2` membaca direktori
   `seconion-import/` alih-alih `seconion-eth0/`.
2. **Asumsi kredensial.** Jalur data MQTT hanya memiliki **satu** lapis pertahanan — autentikasi broker.
   Begitu kredensial bocor, integritas data sensor tidak punya pertahanan kedua: validasi
   `0 < berat_kg <= 300` adalah batas teknis, bukan batas kewajaran biologis.

**Kesimpulan:** postur lapisan A/B/C terbukti kuat terhadap serangan *tanpa* kredensial — 4 dari 5
skenario gagal total dibuktikan dari sisi penyerang. Pekerjaan rumah terbesar bukan menambah kontrol akses,
tetapi memulihkan pipeline deteksi (D.1), mengalirkan log ke sensor (D.2), dan menempatkan pertahanan kedua
di aplikasi yang tidak bergantung pada kerahasiaan kredensial (C.4a/b/c).

---

## Struktur Repositori

```
docs/
├── design/                    Topologi, IP plan, konfigurasi VM (Minggu 4)
├── presentation-minggu9/      Tech stack declaration + slide checkpoint (Minggu 9)
├── blueteam/                  Hardening checklist A.1–C.3 + bukti before/after
├── redteam/                   Attack plan + bukti kelima skenario + diagnostik IDS
├── purple-team-log.md         Lima tahap × lima skenario, timestamp UTC
├── final/                     Fase 3: incident report + video demo
└── presentation-final/        Fase 3: slide presentasi final
```

| Direktori | Isi |
| :--- | :--- |
| [`docs/design/`](docs/design/) | Topologi tiga node, IP plan `192.168.4.0/24`, konfigurasi & langkah replikasi VM |
| [`docs/presentation-minggu9/`](docs/presentation-minggu9/) | Pemetaan tech stack asli KABITA → replika, slide checkpoint Minggu 9 |
| [`docs/blueteam/`](docs/blueteam/) | `hardening_checklist.md` (A.1–C.3) dan `evidence/` berisi bukti before/after |
| [`docs/redteam/`](docs/redteam/) | `attack_plan.md`, `evidence/skenario1-5-serang.txt`, diagnostik pipeline IDS |
| [`docs/purple-team-log.md`](docs/purple-team-log.md) | Log lima tahap per skenario: Serang → Deteksi → Analisis → Respons → Verifikasi |
| [`docs/final/`](docs/final/) | Incident Report final (PDF) dan video demo Purple Team Loop |
| [`docs/presentation-final/`](docs/presentation-final/) | Slide presentasi final (PDF) |

---

## Log Mingguan

**Minggu 1–3, setup.** Instalasi CyberOps Workstation dan Security Onion pada laptop Utama.

**Minggu 4, topologi dan IP.** Topologi tiga node (Attacker–Target–Monitoring) dirancang di Internal
Network `pbl-kel4`, subnet `192.168.4.0/24`, tanpa DHCP. Bukti di [`docs/design/`](docs/design/).

**Minggu 5–6, praktikum.** Belum ada tambahan.

**Minggu 7–8, UTS.** UTS praktikum dan UTS teori; PBL dijeda.

**Minggu 9, checkpoint.** Deklarasi tech stack replika (Golang/PostgreSQL/MQTT) dikonfirmasi;
8 kontrol hardening A.1–C.3 dieksekusi dengan bukti before/after; backend Golang dengan jalur HTTP REST
dan subscriber MQTT (`processReading` bersama) diimplementasikan dan diuji end-to-end; attack plan lima
skenario disusun; kerangka purple team log disiapkan.

**Minggu 10–11, eksekusi serangan.** Kelima skenario Red Team dijalankan 28 Oktober 2026, lalu **diulang
bersih pada 4 November 2026** (seluruh angka di repositori kini berasal dari eksekusi ulang). Ditemukan
6 kekeliruan premis pada panduan eksekusi — port 443 ternyata *closed* bukan terbuka, Hydra tidak dapat
mencoba password auth sama sekali, sqlmap memerlukan penanda path eksplisit, dan aplikasi ternyata
memiliki validasi rentang `0 < berat_kg <= 300` yang sebelumnya tidak diketahui.

**Minggu 12, forensik & incident response.** Diagnostik pipeline IDS menemukan akar kegagalan deteksi
(Snort mati, `unified2` 0 byte sejak 2020, Barnyard2 salah direktori). Pemetaan kontrol efektif vs area
yang memerlukan tindakan Blue Team mengacu NIST SP 800-61r2.

**Minggu 13, remediasi & panduan Blue Team.** Panduan eksekusi Blue Team disusun lengkap ke
`PBL-pendukung/docs/Panduan Eksekusi Fase 2 — SOC KABITA (Kelompok 4).docx`: 9 subbagian, setiap perintah
dilabeli node eksekusi, metode akses, tujuan, dan berkas bukti yang wajib disimpan.

**Minggu 14–15, Fase 3.** Sintesis seluruh temuan menjadi Incident Report NIST SP 800-61r2 (21 halaman),
slide presentasi 12 halaman, video demo siklus Purple Team Loop, dan pembaruan README ini.

---

## Status Deliverable

| Deliverable | Status | Path |
| :--- | :--- | :--- |
| Topologi dan IP plan | selesai | `docs/design/` |
| Deklarasi tech stack | selesai | `docs/presentation-minggu9/tech_stack_declaration.md` |
| Backend Golang (HTTP + MQTT) | selesai, teruji end-to-end | `PBL-pendukung/app/kabita-golang/` |
| Hardening checklist + bukti | selesai, 8 kontrol A.1–C.3 | `docs/blueteam/` |
| Attack plan Fase 2 | selesai, 5 skenario | `docs/redteam/attack_plan.md` |
| Bukti eksekusi serangan | selesai, eksekusi ulang 4 Nov 2026 | `docs/redteam/evidence/` |
| Purple team log | selesai, 5 tahap × 5 skenario | `docs/purple-team-log.md` |
| Diagnostik pipeline IDS | selesai, akar masalah teridentifikasi | `docs/redteam/evidence/security-onion-*` |
| **Incident Report final** | **selesai** | `docs/final/incident_report.pdf` |
| **Video demo Purple Team Loop** | **selesai** | `docs/final/video_demo.mp4` |
| **Slide presentasi final** | **selesai** | `docs/presentation-final/slides.pdf` |
| **README final** | **selesai** | dokumen ini |

---

## Catatan Metodologis

- **Bukti Red Team berbentuk `.txt`, bukan screenshot.** Eksekusi serangan dijalankan secara otomasi tanpa
  GUI, sehingga bukti utama berupa keluaran perintah yang benar-benar dieksekusi beserta timestamp UTC.
  Untuk sisi deteksi, bukti visual berupa screenshot **ada** karena pemeriksaan dilakukan pada konsol VM
  berbasis GUI.
- **Nilai sandi disensor** pada seluruh berkas bukti dan dokumen.
- **Temuan negatif ditulis apa adanya.** Pernyataan "tidak terdeteksi" dan "belum diverifikasi" dipertahankan
  karena setara nilainya dengan temuan alert.
- **Data uji Skenario 5 masih berada di `bobot_log`** (23 baris, `id 61–83`) sebagai bukti dampak. Sanitasi
  dilakukan setelah Blue Team mendokumentasikannya, dengan ID dicatat terlebih dahulu.

---

## Referensi Panduan

- `PBL-pendukung/docs/Panduan PBL Minggu14-15 Final_Presentation.pdf` — Fase 3 (Incident Report, video,
  slide, artefak)
- `PBL-pendukung/docs/Panduan PBL Minggu 9 — SOC KABITA (Kelompok 4).docx` — hardening & attack plan
- `PBL-pendukung/docs/Panduan Eksekusi Fase 2 — SOC KABITA (Kelompok 4).docx` — panduan eksekusi Red Team
  dan Blue Team
- NIST SP 800-61r2 — *Computer Security Incident Handling Guide*
