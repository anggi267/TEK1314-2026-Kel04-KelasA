# TEK1314-2026-Kel04-KelasA

**Simulated SOC Engagement — Mengamankan Infrastruktur Backend Sistem IoT**
Mata kuliah Keamanan Siber (TEK1314) · D4 Teknologi Rekayasa Komputer · Kelas A · Kelompok 4

## Skenario

Kelompok 4 berperan sebagai **SOC (Security Operations Center)** yang mengamankan *backend*
produk **KABITA** — sistem pencatatan **berat badan & pakan kambing**: Ubuntu Server +
**ThingsBoard** + PostgreSQL, bukan timbangan fisiknya. Red Team mensimulasikan aktor ancaman eksternal (pencurian data operasional,
gangguan ketersediaan, pemalsuan perintah aktuator) di dalam **jaringan lab tertutup**;
Blue Team mendeteksi, menganalisis, dan merespons mengikuti NIST SP 800-61r2.

> Seluruh pengujian dilakukan pada **Target Node replika** di `192.168.4.0/24`.
> Tidak ada scanning/eksploitasi ke sistem Mitra maupun sistem IoT produksi.

## Topologi & pengalamatan

| Host | IP | OS | Peran |
|---|---|---|---|
| Target Server (replika backend IoT) | `192.168.4.5` | Ubuntu Server LTS 26.04 | Blue Team |
| Attacker Node | `192.168.4.100` | Kali Linux | Red Team |
| Monitoring Node | `192.168.4.200` | Security Onion 3.2 | Blue Team |

- [`docs/design/topology.png`](docs/design/topology.png) — diagram topologi (Minggu 4)
- [`docs/design/ip_plan.md`](docs/design/ip_plan.md) — skema IP (Minggu 4) + revisi Minggu 9
- [`docs/design/topology-v2.png`](docs/design/topology-v2.png) — diagram revisi (target Ubuntu Server, segmen `pbl-kel4`)
- [`docs/design/replica_setup.md`](docs/design/replica_setup.md) — cara membangun replika backend IoT yang sengaja rentan
- [`docs/design/vm_config.md`](docs/design/vm_config.md) — catatan konfigurasi VM VirtualBox (nama, NIC, RAM, snapshot, langkah guest yang tersisa)

> Catatan: VM **CyberOps Workstation / Cybersecurity LabVM** hanya alat praktikum Minggu 2–3 —
> **bukan** bagian topologi PBL. Topologi yang dinilai tetap tiga node: Attacker, Target, Monitoring.

## Tim

| Peran | Nama |
|---|---|
| Lead | Olan |
| Blue Team | Anggi Permana Putra (J0404241154) |
| Red Team | Raka Syauqi Ferdian (J0404241112), Zidan |

## Deliverable Minggu 9 (Checkpoint Fase 1 → 2)

| Artefak | Lokasi | Isi |
|---|---|---|
| Slide presentasi (PDF) | [`docs/presentation-minggu9/slides.pdf`](docs/presentation-minggu9/slides.pdf) | 8 slide: konteks IoT, tech stack, arsitektur, hardening, demo, attack plan, kendala |
| Deklarasi Tech Stack | [`docs/presentation-minggu9/tech_stack_declaration.md`](docs/presentation-minggu9/tech_stack_declaration.md) | Pemetaan teknologi IoT asli → replika Target Node + batasannya |
| Hardening checklist | [`docs/blueteam/hardening_checklist.md`](docs/blueteam/hardening_checklist.md) | 10 kontrol (A/B/C), perintah, skema bukti before/after, status |
| Bukti Blue Team | [`docs/blueteam/evidence/`](docs/blueteam/evidence/) | Konvensi nama file + checklist kelengkapan bukti |
| Attack plan Fase 2 | [`docs/redteam/attack_plan.md`](docs/redteam/attack_plan.md) | 5 skenario, 4 kategori, tools eksplisit, batas etika |
| Bukti Red Team | [`docs/redteam/evidence/`](docs/redteam/evidence/) | Struktur bukti per skenario (diisi Minggu 10–11) |
| Purple Team Log | [`docs/purple-team-log.md`](docs/purple-team-log.md) | 5 tahap siklus tertutup per skenario |
| Logbook Minggu 1–9 | [`docs/logbook.md`](docs/logbook.md) | Progres, artefak, kendala, dan penanganannya |

> **Laporan Fase 1:** [`docs/reports/fase1/Laporan-Fase1-TEK1314-Kelompok4.docx`](docs/reports/fase1/Laporan-Fase1-TEK1314-Kelompok4.docx)
> (versi PDF ada di folder yang sama) — hardening awal, baseline traffic, dan kesiapan Fase 2.

> **Status lab & konfigurasi VM terkini:** [`docs/lab-status.md`](docs/lab-status.md) —
> inventaris VM, IP, matriks ping 3 node, snapshot, kendala & sisa pekerjaan.

## Status jujur per Minggu 9

- **Dokumen & rencana:** lengkap (tech stack, 10 kontrol hardening, 5 skenario serangan,
  template purple team log, logbook).
- **Perubahan Minggu 9–10:** target diganti dari Metasploitable2 ke **Ubuntu Server 26.04.1 LTS**
  (terpasang via autoinstall, hostname `target-iot`, IP `192.168.4.5`, user `iotadmin`).
- **Klarifikasi produk (22 Okt):** produk asli = **KABITA** (berat badan & pakan kambing) dengan
  backend **ThingsBoard + PostgreSQL**. Replika final mengikuti stack itu; detail peta komponen di
  `docs/presentation-minggu9/tech_stack_declaration.md` dan langkah instalasi di
  `docs/design/replica_setup.md`.
- **Eksekusi Fase 1 (21 Okt):** baseline terekam (440 paket/41,3 s) dan hardening awal
  (`ufw`, `fail2ban`, patch) terbukti tidak memutus layanan — pada stack **sementara**
  (nginx/PHP/MariaDB/Mosquitto). Setelah ThingsBoard terpasang, baseline dan bukti `nmap`
  harus direkam ulang pada stack final. Status `Selesai` pada checklist hanya boleh diisi bila file
  bukti sudah ada di `docs/blueteam/evidence/`.

## Kesesuaian dengan struktur wajib (Panduan Minggu 9, Bagian XI)

| Wajib menurut panduan | Path di repo ini | Status |
|---|---|---|
| `docs/design/topology.png`, `ip_plan.md` (Minggu 4, dipertahankan) | sama | ✅ ada, tidak dihapus/ditimpa |
| `docs/presentation-minggu9/slides.pdf` | sama | ✅ PDF 8 halaman |
| `docs/presentation-minggu9/tech_stack_declaration.md` | sama | ✅ tabel pemetaan + kelemahan sengaja |
| `docs/blueteam/hardening_checklist.md` | sama | ✅ 10 kontrol (A/B/C) + status & skema bukti |
| `docs/blueteam/evidence/` | `baseline/`, `hardening-fase1/` | ✅ pcap + metrik + before/after |
| `docs/redteam/attack_plan.md` | sama | ✅ 5 skenario, 4 kategori, tools eksplisit |
| `docs/redteam/evidence/` | README + subfolder per skenario | ⏳ diisi Minggu 10–11 |
| `docs/purple-team-log.md` | sama | ✅ 5 tahap × 5 skenario (status RENCANA) |
| Logbook Minggu 1–9 | `docs/logbook.md` | ✅ termutakhirkan |

**Dokumen pendukung (di luar struktur wajib, tidak menggantikan yang di atas):**
`docs/design/replica_setup.md`, `docs/design/vm_config.md`, `docs/design/topology-v2.png`,
`docs/lab-status.md`, `docs/reports/fase1/`, `docs/roles/`, `docs/evidence/instalasi-minggu2/`,
`scripts/`.

## Runbook pengerjaan per role

Urutan kerja operasional dari Fase 1 sampai Fase 3 (siapa mengerjakan apa, dalam urutan apa,
dengan bukti apa):

- [`docs/roles/Runbook-PBL-TEK1314-Kelompok4-Fase1-3.docx`](docs/roles/Runbook-PBL-TEK1314-Kelompok4-Fase1-3.docx) — versi Word (8 halaman)
- [`docs/roles/Runbook-PBL-TEK1314-Kelompok4-Fase1-3.pdf`](docs/roles/Runbook-PBL-TEK1314-Kelompok4-Fase1-3.pdf) — versi PDF untuk dibaca cepat
- [`docs/roles/runbook.md`](docs/roles/runbook.md) — ringkasan Fase 2 dalam markdown (untuk commit & diff)
- [`scripts/docs/build_runbook.py`](scripts/docs/build_runbook.py) — skrip pembangun ulang dokumen Word

## Roadmap Fase 2

| Minggu | Fokus | Artefak |
|---|---|---|
| 10 | Baseline pcap, hardening prioritas (A-2, B-1, B-2, B-3, C-1), RT-01 & RT-02 | `docs/blueteam/evidence/`, `docs/redteam/evidence/rt01,rt02/` |
| 11 | RT-03–RT-05, penutupan 5 tahap Purple Team Loop | `docs/purple-team-log.md`, Vulnerability Assessment Report |
| 12 | Digital forensics & draf Incident Report (NIST SP 800-61r2) | `docs/reports/` |
| 13 | Remediasi lanjutan pada replika | catatan remediasi |
| 15 | Presentasi final + demo live + video | laporan akhir |

## Struktur repositori

```
docs/
  design/                  topology.png (Minggu 4), topology-v2.png, ip_plan.md,
                           replica_setup.md, vm_config.md
  presentation-minggu9/    slides.pdf, slides.html, tech_stack_declaration.md
  blueteam/                hardening_checklist.md, evidence/{baseline,hardening-fase1}/
  redteam/                 attack_plan.md, evidence/
  purple-team-log.md       log 5 tahap Purple Team Loop
  logbook.md               logbook Minggu 1-10
  lab-status.md            ringkasan status lab & konfigurasi VM
  reports/fase1/           laporan Fase 1 (.md/.docx/.pdf)
  roles/                   runbook per role + Runbook Fase1-3 (.docx/.pdf)
  evidence/instalasi-minggu2/  screenshot instalasi VM (Minggu 2)
scripts/
  blueteam/                perekam bukti before/after hardening
  docs/                    pembangun dokumen (runbook, laporan, seed ISO, topologi, vm_keys)
```

## Aturan kerja

1. Commit message deskriptif (contoh: `docs: add minggu-9 hardening checklist and attack plan`).
2. Jangan commit kredensial asli, hash password, atau data pribadi.
3. Semua uji serangan hanya ke `192.168.4.0/24`, dengan snapshot VM sebelum sesi.
4. Setiap klaim di laporan wajib punya bukti file di `docs/**/evidence/`.
