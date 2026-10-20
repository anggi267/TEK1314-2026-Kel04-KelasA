# Logbook Progres Kelompok 4 — Minggu 1 s.d. 9

**Mata kuliah:** TEK1314 Keamanan Siber (Kelas A) · **Kelompok:** 4
**Repo:** `TEK1314-2026-Kel04-KelasA` · **Subnet:** `192.168.4.0/24`
**Peran:** Olan (Lead) · Anggi Permana Putra (Blue) · Raka Syauqi Ferdian (Red) · Zidan (Red)

Catatan: logbook disusun dari artefak yang benar-benar ada di repo (commit, dokumen, laporan
praktikum) dan catatan sesi kelompok. Baris bertanda `[[cek]]` perlu dikonfirmasi anggota yang
memegang sesi tersebut sebelum commit final.

| Minggu | Fokus | Aktivitas | Bukti / artefak | Status |
|---|---|---|---|---|
| 1 | Pengantar keamanan siber & pembentukan tim | Kesepakatan peran (Lead/Red/Blue), pembuatan repo GitHub, aturan kerja kelompok | Repo `TEK1314-2026-Kel04-KelasA` (commit `c53492d`) | Selesai |
| 2 | Instalasi tools | Instalasi CyberOps Workstation VM dan Security Onion (OVA/ISO 3.2.0); verifikasi VM boot & antarmuka | `docs/Pertemuan 2/Laptop Utama/Cybersecurity_labVM.png`, `Security_Onion.png`; commit `80c1fcb` "instalasi VM" | Selesai |
| 3 | Hardening & audit dasar Linux | Praktikum dasar Linux: manajemen user, permission, service, audit awal | Materi `Pertemuan 3/Hardening & Audit Dasar Sistem Linux.pdf`; catatan praktikum `[[cek]]` | Selesai |
| 4 | Perancangan arsitektur & skema IP | Topologi Attacker–Target–Monitoring, penetapan `192.168.4.0/24`, pemilihan Metasploitable2 sebagai target, riset port berpotensi dieksploitasi | `docs/design/topology.png`, `docs/design/ip_plan.md` (commit `41238c3`, `02c6401`) | Selesai |
| 5 | Integritas transfer data & analisis jaringan | Tugas kelas integritas data, praktikum Packet Tracer + Wireshark (routing, TCP/IP, enkripsi) | `Pertemuan 5/*` (laporan, diagram TTL, alur data) | Selesai |
| 6 | Packet Tracer & ACL | Praktikum identifikasi alur paket dan demonstrasi ACL (filter trafik antar segmen) | `Pertemuan 6/P6_J0404241112_Raka Syauqi Ferdian.docx/.pdf` | Selesai |
| 7 | UTS Praktikum | Ujian praktikum (Packet Tracer + lembar jawaban), evaluasi pemahaman konfigurasi & analisis | `Uprak UTS/Ujian Praktikum TEK3A 2026.pka`, `Lembar jawaban Uprak siber Raka.docx` | Selesai |
| 8 | UTS teori | Ujian tulis; tidak ada deliverable PBL | — | Selesai |
| 9 | Checkpoint Fase 1 → 2 | Penyusunan deck 8 slide, Deklarasi Tech Stack, hardening checklist 10 kontrol + skema bukti, attack plan 5 skenario, template purple team log | `docs/presentation-minggu9/`, `docs/blueteam/`, `docs/redteam/`, `docs/purple-team-log.md` | Selesai (dokumen) |
| 10 | Monitoring ops & simulasi infiltrasi | Eksekusi hardening prioritas, baseline pcap, RT-01 & RT-02 | (menyusul) | Belum |
| 11 | SIEM / Security Onion investigation | RT-03–RT-05, penutupan 5 tahap Purple Team Loop, Vulnerability Assessment Report | (menyusul) | Belum |

## Kendala yang tercatat

| Minggu | Kendala | Penanganan |
|---|---|---|
| 2 | Kebutuhan RAM/disk untuk 3 VM pada laptop anggota | Security Onion dijalankan bergantian dengan target; alokasi RAM diatur per sesi |
| 4 | Target harus "backend IoT", sementara Metasploitable2 bersifat generik | Memetakan komponen IoT (dashboard, API, DB, MQTT) ke layanan yang tersedia di Metasploitable2; broker MQTT ditambahkan di Fase 2 (lihat `tech_stack_declaration.md`) |
| 7–8 | Beban UTS membuat lab tidak dijalankan ulang | Seluruh perintah hardening disiapkan lebih dulu, eksekusi dijadwalkan Minggu 10 |
| 9 | Metasploitable2 belum punya MQTT → skenario RT-04 berisiko tidak bisa dijalankan | RT-04 ditandai **kondisional**; bila broker gagal dipasang, diganti uji HTTP REST pada endpoint API |
