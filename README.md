# PBL TEK1314 — Simulated SOC Engagement · Kelompok 4 (Kelas A)

Replika backend IoT **KABITA** (pencatatan berat badan & pakan kambing) di lab tertutup tiga node,
plus siklus Blue Team -> Red Team -> Purple Team selama 11 minggu.

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
| Attacker | `PBL-K4-02-Attacker-Kali` | Kali Linux 2026.2 | 192.168.4.100 | menyerang |
| Target | `PBL-K4-01-Target-Ubuntu` | Ubuntu Server 26.04.1 | 192.168.4.5 | KABITA |
| Monitoring | `PBL-K4-03-Monitoring-Onion` | Security Onion 2.x | 192.168.4.200 | sensor |

Segmen lab = Internal Network VirtualBox **`pbl-kel4`**, tanpa DHCP dan tanpa rute internet.
Gambar: `docs/design/topology.png`.

## Isi repositori (sesuai Panduan Minggu 9, Bagian XI)

```
docs/
  design/
    topology.png                    diagram topologi lab
    ip_plan.md                      skema IP & penamaan VM
  presentation-minggu9/
    slides.pdf                      slide presentasi (8 halaman, 16:9)
    tech_stack_declaration.md       deklarasi tech stack & replikasi
  blueteam/
    hardening_checklist.md          10 kontrol A/B/C + status + bukti
    evidence/
      baseline/                     pcap + metrik traffic normal
      hardening/                    before/after hardening
      BUKTI_dashboard.png           dashboard KABITA terbuka
      BUKTI_login.png               halaman login operator
  redteam/
    attack_plan.md                  5 skenario + rules of engagement
    evidence/                       diisi Minggu 10-11
  purple-team-log.md                log 5 tahap per skenario
  logbook.md                        progres Minggu 1-9
  evidence/instalasi-minggu2/       screenshot instalasi VM (bukti Minggu 2)
```

Selain sembilan berkas wajib di atas, ada satu folder bukti tambahan
(`docs/evidence/instalasi-minggu2/`) berisi tangkapan layar instalasi VirtualBox dan
Security Onion pada Minggu 2.

## Status (22 Oktober 2026)

| Bagian | Status | Bukti |
|---|---|---|
| Lab 3 node, IP statis, saling ping | selesai | `docs/design/ip_plan.md` |
| Replika KABITA (Nuxt 4 + PostgreSQL 18) | jalan di port 80 | `docs/presentation-minggu9/tech_stack_declaration.md` |
| Baseline traffic normal | 482 paket | `docs/blueteam/evidence/baseline/` |
| Hardening awal | 2 selesai, 1 sebagian | `docs/blueteam/evidence/hardening/` |
| 10 kontrol hardening | 7 untuk Fase 2 | `docs/blueteam/hardening_checklist.md` |
| 5 skenario serangan | eksekusi Minggu 10 | `docs/redteam/attack_plan.md` |
| Purple Team Loop | diisi Minggu 10-11 | `docs/purple-team-log.md` |

## Aturan main

- Semua data sintetis; tidak ada serangan ke sistem Mitra atau internet.
- DoS maksimal **satu** skenario, maksimal 60 detik, satu service, satu IP.
- Kredensial di repo adalah kredensial lab (VM lokal, tanpa data nyata).

## Materi pendukung (di luar repositori)

Kode aplikasi, skrip build, laporan Fase 1, dan panduan perintah per VM tidak termasuk struktur
yang diminta panduan, jadi disimpan di folder sebelah. **Mulai dari sini kalau kamu anggota tim
yang baru bergabung:** `PBL-pendukung/docs/DOKUMENTASI-KONFIGURASI-VM.md` (docx + pdf juga ada).
Isinya hanya perintah yang dijalankan **di dalam VM** (target, Kali, Onion) — tanpa perintah host.

```
D:\materi kuliah\Keamanan Siber\PBL-pendukung\
  app\kabita\                    kode replika KABITA (Nuxt 4 + PostgreSQL)
  scripts\                       deploy_kabita.py, screenshot_dashboard.py, build dokumen
  docs\DOKUMENTASI-KONFIGURASI-VM.md   semua konfigurasi VM + command (docx + pdf)
  docs\checkpoint-pertemuan9.md   panduan perintah per VM (docx + pdf juga)
  docs\reports\fase1\            laporan Fase 1 (.md/.docx/.pdf)
  docs\design\                   replica_setup.md, vm_config.md, diagram alternatif
  docs\presentation-minggu9\     slides.pptx, slides.html, slides-akurat.pdf
```
