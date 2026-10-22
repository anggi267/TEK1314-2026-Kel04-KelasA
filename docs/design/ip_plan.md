# Skema IP & Penamaan VM

Subnet lab: **192.168.4.0/24** (Internal Network `pbl-kel4`, tanpa DHCP).

| Node | Nama VM | IP lab | Gateway | Adapter 2 |
|---|---|---|---|---|
| Attacker | `PBL-K4-02-Attacker-Kali` | 192.168.4.100/24 | — | NAT (dhcp) |
| Target | `PBL-K4-01-Target-Ubuntu` | 192.168.4.5/24 | — | NAT 10.0.3.15 + forward 2222→22 |
| Monitoring | `PBL-K4-03-Monitoring-Onion` | 192.168.4.200/24 | — | Host-only 192.168.56.1 |

## Port yang dipakai Target Node

| Port | Layanan | Akses |
|---|---|---|
| 22/tcp | SSH (admin) | semua (lab + NAT) |
| 80/tcp | dashboard & API KABITA (Nuxt/Nitro) | 192.168.4.0/24 |
| 5432/tcp | PostgreSQL | hanya `127.0.0.1` |

## Konfigurasi per node

**Kali** — IP lab ditambahkan lewat NetworkManager, bukan `ip addr add` (kalau lewat `ip addr`,
ARP tidak dijawab dan host lain gagal ping):

```bash
sudo nmcli con add type ethernet ifname eth0 con-name pbl-lab ip4 192.168.4.100/24
sudo nmcli con up pbl-lab
```

**Target** — netplan statis, permanen:

```yaml
# /etc/netplan/60-pbl-lab.yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: false
      addresses: [192.168.4.5/24]
      optional: true
```

**Onion** — sensor pasif (`promisc on arp off`); agar bisa di-ping, ARP diaktifkan:

```bash
sudo ip link set eth0 promisc on arp on
sudo ip addr add 192.168.4.200/24 dev eth0
```

## Catatan revisi Minggu 9

Target Node semula direncanakan Metasploitable2, diganti **Ubuntu Server 26.04.1 LTS** agar
replika menyerupai backend IoT nyata (Nuxt + PostgreSQL) dan kontrol hardening bisa dibuktikan.
Subnet dan IP **tidak berubah** dari Minggu 4.
