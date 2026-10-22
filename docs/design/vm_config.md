# Konfigurasi VM (VirtualBox)

| | Target | Attacker | Monitoring |
|---|---|---|---|
| Nama | `PBL-K4-01-Target-Ubuntu` | `PBL-K4-02-Attacker-Kali` | `PBL-K4-03-Monitoring-Onion` |
| OS | Ubuntu Server 26.04.1 LTS | Kali Linux 2026.2 | Security Onion 2.x (Ubuntu 16.04) |
| vCPU / RAM | 2 / 2048 MB | 2 / 2048 MB | 2 / 6144 MB |
| Disk | 25 GB (fixed) | 40 GB (dinamis) | 60 GB (dinamis) |
| NIC 1 | intnet `pbl-kel4` | intnet `pbl-kel4` | intnet `pbl-kel4`, promisc **allow-all** |
| NIC 2 | NAT | NAT | Host-only `192.168.56.1` |

Snapshot Target: `00-clean-base` → `10-ubuntu-2604-terpasang` → `20-lab-ready`
(rollback sebelum tiap skenario serangan).

## Akses administrasi

```bash
ssh -p 2222 iotadmin@127.0.0.1      # password: 123 (lab lokal)
```

`iotadmin` punya `sudo` NOPASSWD **untuk kemudahan otomasi lab** — dicabut sebelum penilaian
akhir (lihat `docs/blueteam/hardening_checklist.md`, kontrol A-2/A-4).

## Software di Target Node

| Paket | Versi | Fungsi |
|---|---|---|
| nodejs | 22.22.1 | runtime Nuxt/Nitro |
| postgresql | 18.6 | basis data `kabita` |
| ufw | 0.36.2 | firewall |
| fail2ban | 1.x | proteksi brute force SSH |
| rsyslog, chrony, unattended-upgrades | — | logging & waktu |

Unit systemd `kabita.service` menjalankan `node /opt/kabita/.output/server/index.mjs`
sebagai user `iotadmin`, port 80 (CAP_NET_BIND_SERVICE).
