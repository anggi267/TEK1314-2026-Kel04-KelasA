# Artefak Fase 3 — `docs/final/`

Folder ini berisi artefak akhir PBL TEK1314 Keamanan Siber Kelompok 4 yang diminta Bagian IX
panduan Minggu 14–15.

| Artefak | Berkas | Keterangan |
| :--- | :--- | :--- |
| **Incident Report final** | [`incident_report.pdf`](incident_report.pdf) | 8 bagian NIST SP 800-61r2, 23 halaman |
| **Video demo Purple Team Loop** | **<https://youtu.be/Qn6f1lt6bEY>** | 7 menit 12 detik, 1858×1080 — satu siklus penuh |

## Tautan video demo

**<https://youtu.be/Qn6f1lt6bEY>**

Tautan ini dicantumkan sesuai **Bagian X butir 4** panduan: video demo yang berukuran besar
(78 MB) tidak disertakan sebagai berkas biner di dalam repository, melainkan diunggah ke YouTube
sebagai **unlisted** dan tautannya dicantumkan jelas di README. Tautan yang sama juga tercantum di
[`README.md`](../../README.md) halaman utama repositori.

Isi video — satu siklus Purple Team Loop penuh pada Skenario 5 (kredensial MQTT bocor), sesuai
Bagian VI butir 2:

1. **Serang** — publish `9999` (ditolak backend), `299` kg dan `0,1` kg (tersimpan), topik liar
   `kabita/sensor-liar` (diterima), lalu 20 pesan beruntun tanpa jeda.
2. **Deteksi** — Squert mencatat **0 alert**; penyebabnya ditelusuri ke sensor (proses `snort` mati,
   `snort.unified2` 0 byte sejak 2020).
3. **Analisis** — validasi yang ada hanya batas teknis `0 < berat_kg ≤ 300`, bukan kewajaran biologis.
4. **Mitigasi** — rotasi kredensial `kabita_device` dan pemasangan ACL topik (C.4a), 26 November 2026
   03:22 UTC.
5. **Verifikasi** — kredensial lama ditolak `not authorised`; publish ke topik liar dengan kredensial
   **sah** juga ditolak, membuktikan penolakan terjadi di lapisan ACL.

Nama host dan IP terlihat di layar sepanjang rekaman (`PBL-K4-01-Target-KABITA 192.168.4.5`,
`PBL-K4-02-Attacker-Kali 192.168.4.100`, `PBL-K4-03-Monitoring-Onion 192.168.4.200`), sesuai
Bagian VI butir 4 — bukti bahwa ini infrastruktur kelompok sendiri, bukan cuplikan dari sumber lain.

## Berkas pendukung di luar repository

- Versi Word Incident Report (`incident_report.docx`) dan berkas video asli disimpan di
  `PBL-pendukung/docs/`, tidak disertakan di repository agar hanya artefak penilaian yang masuk.
- Naskah dan shot list video: `PBL-pendukung/docs/Video demo/Skrip & Naskah Video Demo Purple Team
  Loop — Skenario 5 (KABITA).md`.

## Batas lingkup

Seluruh isi video dan laporan hanya berdasarkan simulasi pada **replika** sistem KABITA di segmen
`192.168.4.0/24` dengan data dummy. Tidak ada satu pun uji coba yang diarahkan ke infrastruktur
produksi Mitra.
