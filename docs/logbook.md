# Logbook Progres (Minggu 1–9)

| Minggu | Agenda | Hasil | Bukti |
|---|---|---|---|
| 1 | Kontrak PBL, pembagian peran | Olan (Lead), Anggi (Blue), Raka & Zidan (Red) | `README.md` |
| 2 | Instalasi tools | VirtualBox + VM dasar; Security Onion OVA | — |
| 3 | Praktikum jaringan & recon | nmap, tcpdump, Wireshark dasar | — |
| 4 | Desain topologi & skema IP | 3 node, subnet `192.168.4.0/24`, IP tetap | `docs/design/topology.png`, `ip_plan.md` |
| 5 | Rencana Blue Team | 10 kontrol (A/B/C) + skema bukti | `docs/blueteam/hardening_checklist.md` |
| 6 | Rencana Red Team | 5 skenario + rules of engagement | `docs/redteam/attack_plan.md` |
| 7 | Purple Team Loop (rancangan) | format 5 tahap per skenario | `docs/purple-team-log.md` |
| 8 | Perbaikan lab | VM dipindah ke intnet `pbl-kel4`, promisc sensor, IP statis, saling ping | `docs/design/ip_plan.md` |
| 9 | **Target Node + stack KABITA** | Ubuntu Server 26.04.1, Nuxt 4 di :80, PostgreSQL 18 (`kabita`), 6 kambing/60 telemetri | `docs/presentation-minggu9/tech_stack_declaration.md` |
| 9 | Hardening awal | ufw default-deny, fail2ban, patch, service diminimalkan, baseline 482 paket | `docs/blueteam/evidence/` |
| 9 | Slide & laporan | `slides.pdf` 1280x720, laporan Fase 1 (docx+pdf, di `PBL-pendukung/`) | `docs/presentation-minggu9/slides.pdf` |

## Kendala yang tercatat

| Kendala | Penyelesaian |
|---|---|
| VM tidak saling terhubung (segmen beda) | semua NIC lab → intnet `pbl-kel4` |
| Instalasi unattended berhenti di konfirmasi | jawab `yes` pada konsol |
| IP statis di Kali tidak dijawab ARP | pakai `nmcli` (NetworkManager), bukan `ip addr add` |
| Sensor tidak menjawab ARP | `promisc on arp off` bawaan SO → set `arp on` |
| nginx & MariaDB hilang saat migrasi stack | replika final tanpa nginx (Nitro langsung :80), DB PostgreSQL |
| Paket upgrade tertahan | *phased update* Ubuntu; dicatat sebagai sisa B-3 |
