# PBL TEK1314 — Simulated SOC Engagement · Kelompok 4 (Kelas A)

Replika backend IoT **KABITA** (pencatatan berat badan & pakan kambing) di lab tertutup
tiga node, plus siklus Blue Team → Red Team → Purple Team selama 11 minggu.

## Tim

| Peran | Nama | NIM |
|---|---|---|
| Lead | Olan Elrai Ramotan Sibagariang | J0404241158 |
| Blue Team | Anggi Permana Putra | J0404241154 |
| Red Team | Raka Syauqi Ferdian | J0404241112 |
| Red Team | Muhammad Zidan | J0404241173 |

## Topologi lab

| Node | VM | OS | IP lab | Peran |
|---|---|---|---|---|
| Attacker | `PBL-K4-02-Attacker-Kali` | Kali Linux 2026.2 | `192.168.4.100` | menyerang |
| Target | `PBL-K4-01-Target-Ubuntu` | Ubuntu Server 26.04.1 | `192.168.4.5` | KABITA |
| Monitoring | `PBL-K4-03-Monitoring-Onion` | Security Onion 2.x | `192.168.4.200` | sensor/deteksi |

Segmen lab = Internal Network VirtualBox **`pbl-kel4`**. Tidak ada DHCP, tidak ada rute ke
internet. Adapter kedua tiap VM (NAT/host-only) hanya untuk administrasi & pembaruan.
Gambar: `docs/design/topology.png` (Minggu 4) dan `docs/design/topology-v2.png` (kondisi aktual).

## Status (22 Oktober 2026)

| Bagian | Status | Bukti |
|---|---|---|
| Lab 3 node + IP statis + saling ping | ✅ | `docs/design/ip_plan.md` |
| Replika KABITA (Nuxt 4 + PostgreSQL 18) | ✅ jalan di `:80` | `docs/design/replica_setup.md` |
| Baseline traffic normal | ✅ 482 paket | `docs/blueteam/evidence/baseline/` |
| Hardening awal (patch, ufw, fail2ban, service) | ✅ 3 kontrol "sebagian" | `docs/blueteam/evidence/hardening/` |
| Checklist hardening 10 kontrol | ⏳ 7 kontrol untuk Fase 2 | `docs/blueteam/hardening_checklist.md` |
| 5 skenario serangan | ⏳ rencana siap, eksekusi Minggu 10 | `docs/redteam/attack_plan.md` |
| Purple Team Loop | ⏳ log kosong, diisi Minggu 10–11 | `docs/purple-team-log.md` |

## Struktur repo

```
app/kabita/              kode replika KABITA (Nuxt 4 + PostgreSQL)
docs/
  checkpoint-pertemuan9.md   panduan perintah per VM sampai checkpoint 9
  design/                  ip_plan, replica_setup, vm_config, topology*.png
  presentation-minggu9/    slides.pdf (Canva), slides.pptx, slides-akurat.pdf,
                           slides.html, tech_stack_declaration.md, README.md
  blueteam/                hardening_checklist.md + evidence/
  redteam/                 attack_plan.md + evidence/
  purple-team-log.md       log 5 tahap per skenario
  logbook.md               progres Minggu 1–9
  reports/fase1/           laporan Fase 1 (.md/.docx/.pdf)
scripts/                   deploy_kabita.py, md_report_to_docx.py, vm_keys.py, ...
```

## Mulai dari mana

1. **`docs/checkpoint-pertemuan9.md`** — semua perintah yang harus dijalankan, per VM.
2. `docs/presentation-minggu9/` — slide: `slides.pdf` (ekspor Canva), `slides-akurat.pdf` (teks terverifikasi), `slides.pptx`.
3. `docs/blueteam/hardening_checklist.md` — kontrol yang dinilai (30%).
4. `docs/redteam/attack_plan.md` — skenario Fase 2.

## Aturan main

- Semua data sintetis; tidak ada data peternakan nyata dan tidak ada serangan ke sistem Mitra.
- DoS maksimal **satu** skenario, ≤60 detik, satu service, satu IP.
- Kredensial di repo adalah kredensial lab (VM lokal, tanpa data nyata).
