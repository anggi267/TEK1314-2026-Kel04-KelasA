# Logbook PBL Keamanan Siber - Kelompok 4

**TEK1314 Keamanan Siber** | Kelas A | Skenario SOC Engagement - backend sistem IoT
Target Node replika `192.168.4.5` | Monitoring `192.168.4.200` (Security Onion)

## Anggota & Peran

| Nama                            | NIM         | Peran     |
| :------------------------------ | :---------- | :-------- |
| Olan Elrai Ramotan Sibagariang  | J0404241158 | Lead      |
| Anggi Permana Putra             | J0404241154 | Blue Team |
| Raka Syauqi Ferdian             | J0404241112 | Red Team  |
| Muhammad Zidan                  | J0404241173 | Red Team  |

## Log Mingguan

**Minggu 1-3, setup.** Instalasi CyberOps Workstation dan Security Onion pada laptop Utama.

**Minggu 4, topologi dan IP.** Topologi tiga node (Attacker–Target–Monitoring) dirancang di Internal Network `pbl-kel4`, subnet `192.168.4.0/24`. Bukti di [`docs/design/`](docs/design/).

**Minggu 5-6, praktikum.** Belum ada tambahan

**Minggu 7-8, UTS.** UTS praktikum dan UTS Teori, belum melanjutkan PBL.

**Minggu 9, checkpoint.** Deklarasi tech stack replika backend KABITA (Golang/PostgreSQL/MQTT) dikonfirmasi; 8 kontrol hardening dieksekusi dengan bukti before/after; backend Golang dengan jalur HTTP REST dan subscriber MQTT (`processReading` bersama) diimplementasikan dan diuji end-to-end; attack plan Fase 2 disusun 5 skenario dari 3 kategori; kerangka purple team log disiapkan (2026-10-23 s.d. 2026-10-24).

## Status Deliverable

| Deliverable                     | Status                        |
| :------------------------------ | :----------------------------- |
| Topologi dan IP plan            | selesai                       |
| Deklarasi tech stack            | selesai                       |
| Backend Golang (HTTP + MQTT)    | selesai, teruji end-to-end    |
| Slide presentasi (`slides.pdf`) | dibuat, belum di-export & commit |
| Hardening checklist dan bukti   | selesai, 8 kontrol            |
| Attack plan Fase 2              | selesai, 5 skenario           |
| Purple team log                 | kerangka, diisi Minggu 10-11  |
| Vulnerability Assessment Report | belum, Minggu 11              |

## Isi Repositori

`docs/design/` topologi dan IP plan | `docs/presentation-minggu9/` tech stack dan slide | `docs/blueteam/` checklist hardening dan bukti | `docs/redteam/` attack plan dan bukti serangan | `docs/purple-team-log.md` log 5 tahap