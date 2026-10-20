# Catatan Konfigurasi VM — Lab PBL Kelompok 4

**Dikonfigurasi:** 20 Oktober 2026 · **VirtualBox:** 7.2.16r174877 · **Host:** Windows 11, 16 vCPU, RAM 19,7 GB (≈9 GB bebas), disk D: 398 GB bebas
**Dokumen terkait:** `docs/design/ip_plan.md`, `docs/design/replica_setup.md`, `docs/design/topology-v2.png`

Semua konfigurasi di bawah dilakukan dari host memakai `VBoxManage` (VM dalam keadaan mati).
Perubahan yang **belum** bisa dilakukan dari host (butuh login ke guest) dicatat di Bagian 5.

---

## 1. Inventaris VM (kondisi setelah konfigurasi)

| # | Nama VM (baru) | Nama lama | Peran | OS | RAM | vCPU | NIC 1 | NIC 2 | Snapshot |
|---|---|---|---|---|---|---|---|---|---|
| 01 | `PBL-K4-01-Target-Ubuntu` | `Target node` | Target Node / replika backend IoT | **Ubuntu Server 26.04.1 LTS** (kernel 7.0.0-38) | 2048 MB | 2 | Internal Network `pbl-kel4` | NAT (+PF 2222→22) | `10-ubuntu-2604-terpasang` |
| 02 | `PBL-K4-02-Attacker-Kali` | `kali-linux-2026.2-virtualbox-amd64` | Attacker Node | Kali Linux 2026.2 | 2048 MB | 2 | Internal Network `pbl-kel4` | NAT | `00-clean-base` |
| 03 | `PBL-K4-03-Monitoring-Onion` | `CyberOps Security Onion` | Monitoring Node | Security Onion **2.x** (basis Ubuntu 16.04) | 6144 MB | 2 | Internal Network `pbl-kel4`, promisc **allow-all** | Host-only `192.168.56.1` | `00-clean-base` |

Verifikasi dari `VBoxManage showvminfo`:

```
PBL-K4-01-Target-Ubuntu    mac 080027579CFD  intnet1=pbl-kel4  nic2=nat
PBL-K4-02-Attacker-Kali    mac 0800275A87BC  intnet1=pbl-kel4  nic2=nat
PBL-K4-03-Monitoring-Onion mac 0800270433F8  intnet1=pbl-kel4  promisc=allow-all  nic2=hostonly(192.168.56.1)
```

**VM lain yang ada di folder `D:\VirtualBox` tapi TIDAK dipakai:**

| Folder | Status | Keterangan |
|---|---|---|
| `Cybersecurity LabVM Worksation 20230210` | terdaftar, mati, NIC1 NAT, RAM 2 GB | CyberOps Workstation — alat praktikum Minggu 2–3, bukan node topologi |
| `Cybersecurity LabVM Worksation 20250409` | **tidak terdaftar** di VirtualBox | salinan lama; boleh dihapus bila tidak diperlukan (hemat ~8 GB) |

### 2.1 Hasil instalasi (verifikasi via SSH 127.0.0.1:2222)

```
hostname : target-iot
OS       : Ubuntu 26.04.1 LTS
kernel   : 7.0.0-38-generic
user     : iotadmin (adm, cdrom, sudo, dip, plugdev, users, lxd)
disk     : /dev/sda2  25G, terpakai 7,3G (32%)
sshd     : OpenSSH 10.2p1, listen 0.0.0.0:22
timezone : Asia/Jakarta (WIB)
```

Kendala yang ditemukan saat instalasi (penting bila mengulang):

| Gejala | Penyebab sebenarnya | Solusi |
|---|---|---|
| Berhenti di `Loading essential drivers` | floppy controller aktif tanpa media | `modifyvm --floppy disabled` |
| Lama tanpa menulis disk | subiquity menunggu jawaban `Continue with autoinstall? (yes\|no)` | jawab `yes` di konsol (scancode `15 95 12 92 1f 9f` + `1c 9c`) |
| DVD tidak bootable | ISO dipindah ke SATA saat port diubah | ISO installer di **IDE 0-1**, seed di **IDE 1-0**, disk di **IDE 0-0** |
| Menggantung di `wait_for_apply` | NIC lab (intnet) tanpa DHCP | sementara `--nic1 none` saat install |
| Ekstraksi macet di disk dinamis | disk dinamis + RAM 3 GB | disk **fixed** + RAM 4 GB + 4 vCPU saat install |

---

## 3. Perubahan yang diterapkan (before → after)

| Item | Sebelum | Sesudah | Alasan |
|---|---|---|---|
| Nama VM | acak / menyesatkan (`Target node`, `CyberOps Security Onion`) | berpola `PBL-K4-0X-Peran-OS` | menghindari salah tafsir; deskripsi VM kini memuat peran & IP |
| NIC 1 Target | NAT | Internal Network `pbl-kel4` | agar satu segmen dengan attacker & sensor |
| NIC 1 Attacker | NAT | Internal Network `pbl-kel4` | idem |
| NIC 1 Monitoring | Internal Network `dmz` | Internal Network `pbl-kel4` + **promisc `allow-all`** | syarat sensor bisa melihat unicast Attacker→Target |
| NIC 2 Monitoring | Internal Network `dmz` (duplikat) | Host-only `192.168.56.1` | akses web UI tanpa mengotori segmen lab |
| NIC 2 Target & Attacker | — | NAT | update paket (`apt update`) |
| vCPU | 1 (target, monitoring) | 2 | apt/nginx & sensor tidak tersendat |
| RAM Monitoring | 4096 MB | 6144 MB | Security Onion butuh memori lebih besar agar stack Elastic/Suricata hidup |
| Audio | aktif (`dsound`) | `none` | tidak dipakai, mengurangi noise & overhead |
| Clipboard Target/Attacker | default | bidirectional | memindahkan perintah/hasil antar VM–host |
| Snapshot | tidak ada | `00-clean-base` di ketiga VM | rollback cepat sebelum hardening / sesudah uji rusak |

---

## 3. Perintah yang dijalankan (reproducible)

```bash
VBM="/c/Program Files/Oracle/VirtualBox/VBoxManage.exe"

# 1. Target Node
"$VBM" modifyvm "Target node" --name "PBL-K4-01-Target-Ubuntu" \
  --nic1 intnet --intnet1 pbl-kel4 --nic2 nat \
  --cpus 2 --memory 2048 --audio none --clipboard bidirectional \
  --description "Target Node, IP 192.168.4.5, NIC1 pbl-kel4, NIC2 NAT"

# 2. Attacker Node
"$VBM" modifyvm "kali-linux-2026.2-virtualbox-amd64" --name "PBL-K4-02-Attacker-Kali" \
  --nic1 intnet --intnet1 pbl-kel4 --nic2 nat \
  --cpus 2 --memory 2048 --audio none --clipboard bidirectional \
  --description "Attacker Node, IP 192.168.4.100, login kali/kali"

# 3. Monitoring Node
"$VBM" modifyvm "CyberOps Security Onion" --name "PBL-K4-03-Monitoring-Onion" \
  --nic1 intnet --intnet1 pbl-kel4 --nicpromisc1 allow-all \
  --nic2 hostonly --hostonlyadapter2 "VirtualBox Host-Only Ethernet Adapter" \
  --cpus 2 --memory 6144 --audio none \
  --description "Monitoring Node (Security Onion 2.x), IP 192.168.4.200"

# 4. Snapshot baseline
"$VBM" snapshot "PBL-K4-01-Target-Ubuntu"   take "00-clean-base"
"$VBM" snapshot "PBL-K4-02-Attacker-Kali"   take "00-clean-base"
"$VBM" snapshot "PBL-K4-03-Monitoring-Onion" take "00-clean-base"
```

**Rollback bila VM rusak:** `VBoxManage snapshot "<nama-vm>" restore "00-clean-base"`.

---

## 4. Bukti bahwa VM Monitoring memang Security Onion

Nama lama VM ini membingungkan (`CyberOps Security Onion`). Untuk memastikan tanpa harus login,
isi disk VDI dipindai (sampling ~50%, 8,6 GB). Ditemukan jejak khas Security Onion:

| String ditemukan | Arti |
|---|---|
| `/etc/nsm/rules/`, `default-rule-path: /etc/nsm/rules/` | struktur direktori NSM khas Security Onion 1.x/2.x |
| `/usr/sbin/so-elasticsearch-*`, `so-elastic-status` | skrip manajemen `so-*` bawaan Security Onion |
| `salt-minion`, `/etc/rc0.d/K01salt-minion` | stack Salt dipakai Security Onion 2.x |
| `Security Onion 20120224`, VLAN/filter `tcpdump` | teks konfigurasi Squert/NSM era SO klasik |

**Kesimpulan:** ini **Security Onion generasi 2.x (basis Ubuntu 16.04, init sysvinit)** — bukan
CyberOps Workstation, dan **bukan** Security Onion 3.2. Konsekuensinya dicatat di Bagian 6.

---

## 5. Yang masih harus dilakukan DI DALAM guest (belum bisa dari host)

Tidak ada kredensial guest yang tersimpan, jadi langkah ini harus dijalankan manual saat VM
dinyalakan. Urutannya penting: **NIC dulu, baru uji sensor.**

### 5.1 Target Node — `PBL-K4-01-Target-Ubuntu` (OS sudah terpasang, tinggal IP)

Login console sebagai `iotadmin`, lalu tempel satu blok ini:

```bash
sudo tee /etc/netplan/60-pbl-lab.yaml >/dev/null <<'YAML'
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: false
      addresses: [192.168.4.5/24]
      optional: true
YAML
sudo chmod 600 /etc/netplan/60-pbl-lab.yaml
sudo netplan apply
ip -4 -br a                  # harapan: enp0s3 = 192.168.4.5/24, enp0s8 tetap 10.0.3.15
ping -c 3 192.168.4.100      # setelah Kali diberi IP 192.168.4.100
```

> Kenapa tidak diotomasi: Hermes diblokir kebijakan saat mencoba mengirim password ke `sudo -S`.
> Alternatif agar bisa otomatis: isi `SUDO_PASSWORD` di `~/.hermes/.env`.
> Setelah IP aktif, lanjutkan stack replika (`docs/design/replica_setup.md`); `apt` sudah berfungsi.

### 5.2 Attacker Node — `PBL-K4-02-Attacker-Kali`

```bash
sudo ip addr add 192.168.4.100/24 dev eth0 && sudo ip link set eth0 up
ping -c 3 192.168.4.5
```
(atau permanen lewat NetworkManager: `nmcli con mod "Wired connection 1" ipv4.addresses 192.168.4.100/24 ipv4.method manual`)

### 5.3 Monitoring Node — `PBL-K4-03-Monitoring-Onion`

```bash
# 1. pastikan ini benar Security Onion
so-status || ls /etc/nsm                    # SO 2.x: gunakan so-status / nsm
ip -brief a                                 # NIC1 = segmen lab, NIC2 = 192.168.56.x

# 2. set IP sensor
sudo nano /etc/network/interfaces           # SO 2.x memakai ifupdown, bukan netplan
# auto <nic1>
# iface <nic1> inet static
#     address 192.168.4.200
#     netmask 255.255.255.0
sudo ifup <nic1>

# 3. UJI apakah sensor benar-benar melihat trafik lab (paling penting)
sudo tcpdump -i <nic1> -nn host 192.168.4.100
#    sambil di Kali: ping -c 20 192.168.4.5
#    HARUS muncul paket. Kalau kosong: promisc/NIC belum benar.
```

### 5.4 Bila `so-status` tidak ada / sensor tidak jalan

Pilih satu:
1. **Perbaiki SO 2.x** — `sudo so-setup` (butuh akses internet lewat NIC NAT/host-only).
2. **Import OVA yang sudah ada:** `VBoxManage import "D:\materi kuliah\Keamanan Siber\Security_Onion.ova"`
   lalu set NIC-nya seperti VM 03.
3. **Pasang SO 3.2 dari ISO** (14 GB, butuh ≥30 GB disk & RAM besar) — pilihan terberat.

---

## 6. Isu terbuka & keputusan yang perlu diambil kelompok

| # | Isu | Dampak | Rekomendasi |
|---|---|---|---|
| 1 | Target dulu Ubuntu 25.04 (EOL) | kontrol B-3 tidak bisa dibuktikan | **SELESAI** — kini Ubuntu 26.04.1 LTS terpasang, `apt upgrade` berfungsi |
| 1b | IP statis `192.168.4.5` belum aktif di guest | node lab belum bisa saling ping | jalankan blok Bagian 5.1 |
| 2 | Monitoring memakai **Security Onion 2.x** (EOL) | tidak ada update signature; sebagian panduan 3.x tidak berlaku | tetap dipakai bila sensor terbukti menangkap trafik; sebutkan versinya di laporan |
| 3 | Tiga VM hidup bersamaan butuh ≈10 GB RAM (9 GB bebas) | salah satu VM bisa lambat/OOM | tutup aplikasi berat; atau jalankan Monitoring + satu node lain bergantian |
| 4 | VM `Cybersecurity LabVM Worksation 20250409` tidak terdaftar | makan ~8 GB disk | hapus folder bila tidak dipakai |
| 5 | Kredensial guest tidak tercatat | sesi S1 terhambat | isi tabel kredensial di bawah (jangan di-commit bila berisi password nyata) |

### Tabel kredensial (isi manual, JANGAN di-commit)

| VM | Username | Password | Catatan |
|---|---|---|---|
| PBL-K4-01-Target-Ubuntu |  |  | dibuat saat instalasi Ubuntu |
| PBL-K4-02-Attacker-Kali | `kali` | `kali` | default image Kali (publik) |
| PBL-K4-03-Monitoring-Onion |  |  | user yang dibuat saat `so-setup` |

> Simpan tabel ini di tempat lain (bukan repo). Repo hanya boleh memuat kredensial **dummy**
> yang memang sengaja dipasang untuk skenario (mis. `iotadmin`).
