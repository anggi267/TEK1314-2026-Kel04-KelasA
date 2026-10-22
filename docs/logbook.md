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
| 2 | Instalasi tools | Instalasi CyberOps Workstation VM dan Security Onion (OVA/ISO 3.2.0); verifikasi VM boot & antarmuka. **Catatan: CyberOps Workstation = alat praktikum, tidak dipakai di topologi PBL** | `docs/evidence/instalasi-minggu2/Laptop Utama/Cybersecurity_labVM.png`, `Security_Onion.png`; commit `80c1fcb` "instalasi VM" | Selesai |
| 3 | Hardening & audit dasar Linux | Praktikum dasar Linux: manajemen user, permission, service, audit awal | Materi `Pertemuan 3/Hardening & Audit Dasar Sistem Linux.pdf`; catatan praktikum `[[cek]]` | Selesai |
| 4 | Perancangan arsitektur & skema IP | Topologi Attacker–Target–Monitoring, penetapan `192.168.4.0/24`, pemilihan Metasploitable2 sebagai target, riset port berpotensi dieksploitasi | `docs/design/topology.png`, `docs/design/ip_plan.md` (commit `41238c3`, `02c6401`) | Selesai |
| 5 | Integritas transfer data & analisis jaringan | Tugas kelas integritas data, praktikum Packet Tracer + Wireshark (routing, TCP/IP, enkripsi) | `Pertemuan 5/*` (laporan, diagram TTL, alur data) | Selesai |
| 6 | Packet Tracer & ACL | Praktikum identifikasi alur paket dan demonstrasi ACL (filter trafik antar segmen) | `Pertemuan 6/P6_J0404241112_Raka Syauqi Ferdian.docx/.pdf` | Selesai |
| 7 | UTS Praktikum | Ujian praktikum (Packet Tracer + lembar jawaban), evaluasi pemahaman konfigurasi & analisis | `Uprak UTS/Ujian Praktikum TEK3A 2026.pka`, `Lembar jawaban Uprak siber Raka.docx` | Selesai |
| 8 | UTS teori | Ujian tulis; tidak ada deliverable PBL | — | Selesai |
| 9 | Checkpoint Fase 1 → 2 | Penyusunan deck 8 slide, Deklarasi Tech Stack, hardening checklist 10 kontrol + skema bukti, attack plan 5 skenario, template purple team log | `docs/presentation-minggu9/`, `docs/blueteam/`, `docs/redteam/`, `docs/purple-team-log.md` | Selesai (dokumen) |
| 7 (Fase 1) | Penyelesaian Fase 1 | Replika backend IoT terpasang (nginx 1.28.3, PHP-FPM 8.5.4, MariaDB 11.8.6, Mosquitto); baseline 440 paket/41,3 s; hardening awal (ufw, fail2ban, patch, minimalisasi service) | `docs/reports/fase1/`, `docs/blueteam/evidence/{baseline,hardening-fase1}/` | Selesai |
| 10 (klarifikasi produk) | Penyesuaian ke produk asli **KABITA** | Produk = pencatatan **berat badan & pakan kambing**; backend **Ubuntu Server + ThingsBoard CE + PostgreSQL** (8080/1883/5432). Dokumen disesuaikan: deklarasi tech stack, panduan replika, attack plan (RT-02/03/04), checklist B/C, purple-team log | `docs/presentation-minggu9/tech_stack_declaration.md`, `docs/design/replica_setup.md`, `docs/redteam/attack_plan.md` | Selesai (dokumen); instalasi TB = langkah Fase 2 |
| 10 (dokumentasi) | Rekap status & konfigurasi | `docs/lab-status.md`: inventaris VM, IP, matriks ping, snapshot, kendala, sisa pekerjaan, riwayat commit | `docs/lab-status.md` | Selesai |
| 10 (konektivitas) | IP lab & uji ping 3 node | Target `.5`, Kali `.100`, Onion `.200` aktif; **keenam arah ping 0% loss**; sensor Onion merekam ICMP `.100 ↔ .5` (promisc bekerja). Dua jebakan: `ip addr add` di Kali tidak dijawab ARP (pakai nmcli), dan Onion punya `arp off` di interface sensor | `docs/design/vm_config.md` §4.1; snapshot `30-ip-lab-aktif` | Selesai |
| 10 (akses) | Akses operasional target | Password `iotadmin` = `123` (diset via root shell GRUB karena cloud-init disabled), sudo NOPASSWD, IP lab `192.168.4.5/24` aktif, sshd aktif | `docs/design/vm_config.md`; snapshot `20-lab-ready` | Selesai |
| 10 (instalasi) | Instalasi OS target | Ubuntu Server 26.04.1 LTS dipasang **unattended** (autoinstall + seed `CIDATA`); hostname `target-iot`, user `iotadmin`, disk fixed 25 GB, sshd aktif | `docs/design/vm_config.md` §2.1; snapshot `10-ubuntu-2604-terpasang` | Selesai (IP statis & stack menyusul) |
| 10 (persiapan) | Perbaikan lab & revisi arsitektur | Target diganti ke Ubuntu Server; ketiga VM dipindah ke Internal Network `pbl-kel4` (+ promiscuous pada sensor); dokumen Minggu 9 direvisi agar konsisten | `docs/design/topology-v2.png`, `replica_setup.md`, `ip_plan.md` (revisi) | Selesai |
| 10 | Monitoring ops & simulasi infiltrasi | Eksekusi hardening prioritas, baseline pcap, RT-01 & RT-02 | (menyusul) | Belum |
| 11 | SIEM / Security Onion investigation | RT-03–RT-05, penutupan 5 tahap Purple Team Loop, Vulnerability Assessment Report | (menyusul) | Belum |

## Kendala yang tercatat

| Minggu | Kendala | Penanganan |
|---|---|---|
| 2 | Kebutuhan RAM/disk untuk 3 VM pada laptop anggota | Security Onion dijalankan bergantian dengan target; alokasi RAM diatur per sesi |
| 4 | Target harus "backend IoT", sementara target awal bersifat generik | **Diselesaikan Minggu 9:** target diganti ke Ubuntu Server sehingga dashboard/API/DB/MQTT dapat dipasang apa adanya (lihat `replica_setup.md`) |
| 7–8 | Beban UTS membuat lab tidak dijalankan ulang | Seluruh perintah hardening disiapkan lebih dulu, eksekusi dijadwalkan Minggu 10 |
| 9 | Broker MQTT belum ada di replika → RT-04 berisiko tidak bisa dijalankan | **Diselesaikan Minggu 9:** Mosquitto dipasang sengaja tanpa auth (kelemahan #3) sehingga RT-04 punya sasaran nyata |
