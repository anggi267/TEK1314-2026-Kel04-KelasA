# Status Lab & Catatan Progres — Kelompok 4

**Terakhir diperbarui:** 20 Oktober 2026, 23:30 WIB
**Repo:** `TEK1314-2026-Kel04-KelasA` · **commit terakhir:** `2b93af7`
**Host:** Windows 11, 16 vCPU, RAM 19,7 GB, `D:\VirtualBox` (folder VM ±82 GB)

Dokumen ini adalah ringkasan tunggal: apa yang sudah dikerjakan, konfigurasi apa yang terpasang,
bukti apa yang ada, dan apa yang tersisa. Rincian teknis per topik ada di dokumen yang ditautkan.

---

## 1. Ringkasan status

| Area | Status | Bukti / tautan |
|---|---|---|
| Dokumentasi Minggu 9 (slide, tech stack, checklist, attack plan, purple log, logbook) | ✅ Selesai | `docs/presentation-minggu9/`, `docs/blueteam/`, `docs/redteam/`, `docs/purple-team-log.md` |
| Runbook per role Fase 1–3 (docx + PDF) | ✅ Selesai | `docs/roles/Runbook-...-Fase1-3.docx` / `.pdf` |
| Arsitektur & skema IP | ✅ Selesai (revisi Minggu 9: target Ubuntu Server) | `docs/design/topology-v2.png`, `ip_plan.md` |
| VM VirtualBox: nama, NIC, resource | ✅ Selesai | §2, `docs/design/vm_config.md` |
| Instalasi OS target | ✅ Ubuntu Server 26.04.1 LTS (autoinstall) | `vm_config.md` §2.1 |
| IP lab + ping 3 node | ✅ Semua arah 0% loss, sensor merekam trafik | §3 |
| Akses sudo untuk otomasi | ✅ `iotadmin` NOPASSWD | §4.1 |
| Stack replika IoT (nginx, DVWA, MariaDB, Mosquitto) | ❌ Belum | rencana: `docs/design/replica_setup.md` |
| Hardening 10 kontrol (bagian VIII) | ❌ Belum dieksekusi (baru rencana + skema bukti) | `docs/blueteam/hardening_checklist.md` |
| Eksekusi 5 skenario serangan + Purple Loop | ❌ Belum (Fase 2, Minggu 10–11) | `docs/redteam/attack_plan.md` |
| Push ke GitHub | ⚠️ Belum — kredensial git tidak tersimpan di mesin ini | 8 commit lokal |
| Detail produk IoT asli | ⚠️ Masih placeholder `[[ISI]]` | `tech_stack_declaration.md` |

---

## 2. Inventaris VM (kondisi aktual, ketiga VM menyala)

| VM | Peran | OS | RAM | vCPU | Disk | NIC 1 | NIC 2 | Akses | Snapshot |
|---|---|---|---|---|---|---|---|---|---|
| `PBL-K4-01-Target-Ubuntu` | Target Node | Ubuntu Server **26.04.1 LTS** (kernel 7.0.0-38) | 4096 MB | 4 | 25 GB fixed (`target-2604-fixed.vdi`) | Internal `pbl-kel4` → `192.168.4.5/24` | NAT → `10.0.3.15` + PF `2222→22` | `iotadmin` / `123`, sudo NOPASSWD | `10-ubuntu-2604-terpasang`, `20-lab-ready` |
| `PBL-K4-02-Attacker-Kali` | Attacker Node | Kali Linux 2026.2 | 2048 MB | 2 | 16 GB | Internal `pbl-kel4` → `192.168.4.100/24` | NAT | `kali` / `kali` | `00-clean-base`, `30-ip-lab-aktif` |
| `PBL-K4-03-Monitoring-Onion` | Monitoring Node | Security Onion **2.x** (Ubuntu 16.04) | 6144 MB | 2 | 8,6 GB | Internal `pbl-kel4`, promisc **allow-all** → `192.168.4.200/24` | Host-only `192.168.56.1` (+ NAT adapter 3) | `analyst` / `cyberops` (hostname `SecOnion`) | `00-clean-base`, `30-ip-lab-aktif` |

Tidak dipakai: `Cybersecurity LabVM Worksation 20230210` (CyberOps Workstation, alat praktikum) dan
folder `Cybersecurity LabVM Worksation 20250409` (±8 GB, tidak terdaftar).
Cadangan OS lama: `Target node.vdi` (Ubuntu 25.04) dan `target-2604.vdi` (percobaan disk dinamis).

---

## 3. Jaringan & uji konektivitas

**Segmen:** Internal Network `pbl-kel4`, `192.168.4.0/24`, tanpa DHCP, tanpa gateway ke internet.
**Adapter kedua** (NAT/host-only) hanya untuk update paket & akses admin.

Matriks ping (diverifikasi 23:15 WIB):

| Dari ↓ ke → | Target `.5` | Kali `.100` | Onion `.200` |
|---|---|---|---|
| Target `.5` | — | ✅ 0% (3,3 ms) | ✅ 0% (3,9 ms) |
| Kali `.100` | ✅ 0% (7,5 ms) | — | ✅ 0% (2,2 ms) |
| Onion `.200` | ✅ 0% (4/4 paket terekam di target) | ✅ 0% (2,0 ms) | — |

Bukti sensor melihat trafik lab (`tcpdump -i eth0` di Onion):

```text
16:04:03.136797 IP 192.168.4.100 > 192.168.4.5: ICMP echo request, id 58782, seq 1
16:04:03.137413 IP 192.168.4.5 > 192.168.4.100: ICMP echo reply, id 58782, seq 1
```

---

## 4. Konfigurasi guest (yang terpasang)

### 4.1 Target Node — Ubuntu 26.04.1 LTS

| Item | Isi |
|---|---|
| Hostname | `target-iot` |
| IP lab | `192.168.4.5/24` di `enp0s3` via `/etc/netplan/60-pbl-lab.yaml` (mode 600), `optional: true` |
| IP NAT | `10.0.3.15/24` di `enp0s8` (DHCP) |
| Sudo | `/etc/sudoers.d/90-pbl-nopasswd` → `iotadmin ALL=NOPASSWD: ALL` (diverifikasi `sudo -n whoami` = root) |
| sshd | aktif, password auth aktif, `OpenSSH 10.2p1` |
| Paket dasar | hanya bawaan installer (nginx/DVWA/MariaDB/Mosquitto **belum** dipasang) |
| Cara pasang | autoinstall (seed cloud-init `CIDATA`) + disk fixed 25 GB |

### 4.2 Attacker Node — Kali

| Item | Isi |
|---|---|
| IP lab | `192.168.4.100/24` di `eth0` lewat profil NetworkManager `pbl-lab` |
| Catatan | `ip addr add` **tidak** dipakai — alamat pada interface NM tidak dijawab ARP |
| sshd | tidak aktif (default image) — relevan untuk skenario RT-02 |

### 4.3 Monitoring Node — Security Onion 2.x

| Item | Isi |
|---|---|
| Hostname | `SecOnion` |
| IP lab | `192.168.4.200/24` di `eth0` |
| Interface sensor | `iface eth0 inet manual` + `up ip link set $IFACE promisc on arp on up` |
| Persistensi IP | `post-up ip addr add 192.168.4.200/24 dev eth0` di `/etc/network/interfaces` |
| Manajemen | `eth1` = `192.168.0.1/24` (dibuat oleh setup Security Onion) |
| Tools | Sguil, Squert, Kibana, CyberChef terlihat di desktop |

### 4.4 Perubahan host (VirtualBox) yang diterapkan

1. Rename VM ke pola `PBL-K4-0X-Peran-OS` + deskripsi peran/IP.
2. NIC 1 ketiga VM → Internal Network `pbl-kel4`; sensor ditambah `promisc allow-all`.
3. NIC 2 → NAT (Target, Kali) dan Host-only (Onion); adapter NAT ketiga tetap ada di Onion.
4. vCPU 2, audio dimatikan, clipboard bidirectional (Target/Kali), snapshot dasar dibuat.
5. Install target: disk **fixed 25 GB**, ISO installer di `IDE 0-1`, seed di `IDE 1-0`, disk di `IDE 0-0`, `--floppy disabled`.
6. Port-forward NAT `127.0.0.1:2222 → target:22` (verifikasi & admin).

---

## 5. Snapshot & rollback

```bash
VBM="/c/Program Files/Oracle/VirtualBox/VBoxManage.exe"
"$VBM" snapshot "PBL-K4-01-Target-Ubuntu"   list
"$VBM" snapshot "PBL-K4-01-Target-Ubuntu"   restore "20-lab-ready"
"$VBM" snapshot "PBL-K4-02-Attacker-Kali"   restore "30-ip-lab-aktif"
"$VBM" snapshot "PBL-K4-03-Monitoring-Onion" restore "30-ip-lab-aktif"
```

| VM | Snapshot | Isi |
|---|---|---|
| Target | `10-ubuntu-2604-terpasang` | setelah instalasi, sebelum IP/sudo |
| Target | `20-lab-ready` | 26.04 + password `123` + sudo NOPASSWD + IP `.5` |
| Kali | `00-clean-base`, `30-ip-lab-aktif` | sebelum perubahan; setelah profil `pbl-lab` |
| Onion | `00-clean-base`, `30-ip-lab-aktif` | sebelum perubahan; setelah IP `.200` + arp on |

---

## 6. Kendala yang ditemui & solusinya

| # | Kendala | Penyebab sebenarnya | Solusi yang dipakai |
|---|---|---|---|
| 1 | VM tidak bisa saling ping | Kali & Target di NAT, Onion di internal `dmz` (duplikat) | semua NIC1 → Internal `pbl-kel4` |
| 2 | Installer berhenti di `Loading essential drivers` | floppy controller aktif tanpa media | `modifyvm --floppy disabled` |
| 3 | Installer lama tanpa menulis disk | subiquity menunggu jawaban `Continue with autoinstall? (yes|no)` | jawab `yes` via konsol (scancode) |
| 4 | DVD tidak bootable setelah pindah controller | ISO di SATA saat port diubah | ISO installer di **IDE 0-1**, seed di **IDE 1-0** |
| 5 | Subiquity menggantung di `wait_for_apply` | NIC lab tanpa DHCP | `--nic1 none` selama install, dikembalikan setelahnya |
| 6 | Ekstraksi squashfs macet | disk dinamis + RAM 3 GB | disk **fixed** + RAM 4 GB + 4 vCPU |
| 7 | Seed cloud-init v2 tidak jalan | `cloud-init` **disabled** pada sistem hasil autoinstall | root shell GRUB (`init=/bin/bash`) untuk set password & sudoers |
| 8 | Ping Target→Kali gagal walau IP benar | IP via `ip addr add` pada interface NM tidak dijawab ARP | profil `nmcli` (`pbl-lab`) |
| 9 | Ping ke Onion gagal walau IP terpasang | interface sensor SO memakai `arp off` | `ip link set eth0 arp on` + ubah permanen di `/etc/network/interfaces` |
| 10 | SSH ke Onion via NAT PF `2223` tidak stabil | port-forward pada adapter NAT ketiga | dikerjakan lewat konsol VM |

---

## 7. Yang belum selesai (urutan prioritas)

1. **Stack replika** di Target: nginx + PHP-FPM + DVWA + MariaDB (`iot_db`) + Mosquitto
   (`allow_anonymous true`), user OS `iotadmin` sudah ada. Panduan: `docs/design/replica_setup.md`.
2. **Baseline traffic normal** (`baseline_minggu9.pcap`, `baseline_summary.md`) sebelum serangan.
3. **Hardening 10 kontrol** A/B/C + bukti before/after (`docs/blueteam/hardening_checklist.md`).
4. **Eksekusi RT-01…RT-05** + tutup 5 tahap Purple Team Loop (`docs/purple-team-log.md`).
5. **Verifikasi fungsional Security Onion**: `so-status`, apakah Elastic/Suricata benar-benar
   menerima log (SO 2.x EOL — sebutkan versinya di laporan).
6. **Push ke GitHub** (8 commit lokal) + undang dosen sebagai collaborator bila repo privat.
7. **Konfirmasi produk IoT asli** untuk mengganti penanda `[[ISI]]` di slide & tech stack.

---

## 8. Riwayat commit dokumentasi & lab

| Commit | Isi |
|---|---|
| `783351e` | slide Minggu 9 (8 slide), hardening checklist, attack plan |
| `e2d870c` | runbook per role Fase 1–3 (docx + PDF) |
| `1e778a0` | catatan CyberOps bukan node topologi |
| `b3d1888` | konfigurasi VM (nama, NIC, resource, snapshot) |
| `9cc95a1` | instalasi Ubuntu 26.04.1 LTS (autoinstall) |
| `f6caada` | password `123`, sudo NOPASSWD, IP `.5` |
| `ff0711c` | IP Kali via nmcli, ping dua arah |
| `2b93af7` | IP Onion `.200`, arp on, matriks ping 3 node, bukti sensor |

---

## 9. Verifikasi cepat (bila VM dihidupkan ulang)

```bash
VBM="/c/Program Files/Oracle/VirtualBox/VBoxManage.exe"

# nyalakan ketiga node
"$VBM" startvm "PBL-K4-01-Target-Ubuntu" --type headless
"$VBM" startvm "PBL-K4-02-Attacker-Kali" --type headless
"$VBM" startvm "PBL-K4-03-Monitoring-Onion" --type headless

# uji dari host -> target
ssh -p 2222 iotadmin@127.0.0.1        # password: 123

# di target
ping -c 2 192.168.4.100 && ping -c 2 192.168.4.200
```

Di Onion (konsol): `ping -c 2 192.168.4.5`, lalu
`sudo tcpdump -i eth0 -nn host 192.168.4.100` sambil Kali melakukan ping — paket harus muncul.
