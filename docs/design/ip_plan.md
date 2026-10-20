# IP Plan - Kelompok 4

**Subnet Jaringan:** `192.168.4.0/24`
**Skenario:** Multi-service exploitation (Web & Database) menggunakan Metasploitable2

## Tabel Alokasi IP

| Hostname                | IP Address       | OS Direncanakan         | Peran         |
|--------------------------|------------------|--------------------------|---------------|
| Target Server (Korban)   | 192.168.4.5      | Metasploitable2          | Blue Team (setup) |
| Attacker Node             | 192.168.4.100    | Kali Linux               | Red Team      |
| Monitoring Node           | 192.168.4.200    | Security Onion           | Blue Team     |

## Catatan Tambahan

- Subnet `192.168.4.0/24` dipilih agar unik dan tidak bentrok dengan kelompok lain, sesuai Kontrak Kuliah Poin 3a.
- Monitoring Node (Security Onion) ditempatkan pada segmen yang sama agar dapat memantau seluruh trafik antara Attacker Node dan Target Node.
- Metasploitable2 dipilih sebagai Target Server karena menyediakan banyak service dengan celah keamanan default sekaligus dalam satu VM, antara lain:
  - **Web** - port 80 (DVWA bawaan, phpMyAdmin, Mutillidae)
  - **Database** - port 3306 (MySQL), 5432 (PostgreSQL)
  - **Service lain** - port 21 (FTP/vsftpd versi vulnerable), 23 (Telnet), 445 (Samba)
- Fokus service mana yang akan dieksploitasi (Web/DB/lainnya) akan ditentukan lebih lanjut oleh Red Team berdasarkan riset celah keamanan pada pertemuan ini.

---

## Revisi Minggu 9 — Target Node menjadi Ubuntu Server

Keputusan awal (di atas) memakai Metasploitable2. Setelah instalasi berjalan, kelompok
memutuskan **mengganti Target Node ke Ubuntu Server** agar replika benar-benar menyerupai
*backend* sistem IoT (dashboard, API, database, broker MQTT) dan agar tetap bisa menjalankan
`apt`/`ufw`/`fail2ban` untuk keperluan hardening.

Tabel di atas dipertahankan sebagai riwayat keputusan Minggu 4. Alokasi IP **tidak berubah**.

| Hostname | IP Address | OS (revisi) | Peran |
|---|---|---|---|
| Target Server (Korban) | 192.168.4.5 | Ubuntu Server LTS 26.04 | Blue Team (setup) |
| Attacker Node | 192.168.4.100 | Kali Linux 2026.2 | Red Team |
| Monitoring Node | 192.168.4.200 | Security Onion 3.2 | Blue Team |

### Konfigurasi jaringan (sisi VirtualBox, sudah diterapkan)

| Node | NIC 1 (segmen lab) | NIC 2 (luar segmen) |
|---|---|---|
| Target Node | Internal Network `pbl-kel4` | NAT |
| Attacker Node | Internal Network `pbl-kel4` | NAT |
| Monitoring Node | Internal Network `pbl-kel4`, **promiscuous `allow-all`** | Host-only `192.168.56.1` |

Catatan penting:

1. Di VirtualBox, trafik unicast antar-VM pada Internal Network hanya terlihat sensor bila
   adapter monitoring di-set promiscuous `allow-all`. Ini sudah diverifikasi lewat
   `VBoxManage showvminfo` dan harus diuji ulang di dalam guest dengan `tcpdump`.
2. **Ubuntu 25.04 (isi VM saat ini) sudah EOL** — harus diganti dengan 26.04 LTS sebelum
   kontrol B-3 (patch OS) dapat dibuktikan. Detail instalasi: `docs/design/replica_setup.md`.
3. Kelemahan replika dipasang **sengaja** dan didaftar di `replica_setup.md` Bagian 3.
4. Diagram terbaru: `docs/design/topology-v2.png` (diagram Minggu 4 tetap disimpan sebagai
   `topology.png`).

