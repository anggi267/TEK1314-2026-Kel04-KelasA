# Panduan Checkpoint Pertemuan 9 — Perintah per VM

Semua perintah di bawah disusun berurutan. Label di awal setiap blok menunjukkan **di mana**
perintah dijalankan:

| Label | Arti |
|---|---|
| `[HOST]` | Windows (PowerShell/git-bash), tempat VirtualBox |
| `[TARGET]` | VM `PBL-K4-01-Target-Ubuntu` (192.168.4.5) |
| `[KALI]` | VM `PBL-K4-02-Attacker-Kali` (192.168.4.100) |
| `[ONION]` | VM `PBL-K4-03-Monitoring-Onion` (192.168.4.200) |

Kredensial lab: `iotadmin` / `123` (Target), `kali` / `kali` (Kali), `analyst` / `cyberops` (Onion).

---

## Checkpoint yang harus tercapai

| # | Checkpoint | Bukti yang disimpan |
|---|---|---|
| 1 | Tiga VM menyala, semua di `pbl-kel4` | screenshot tiga VM / `VBoxManage showvminfo` |
| 2 | Ketiga node saling ping | keluaran `ping` (0% loss) |
| 3 | Dashboard KABITA terbuka di browser | screenshot `http://192.168.4.5/` |
| 4 | API mengembalikan data PostgreSQL | `curl /api/ringkasan` |
| 5 | Sensor Onion melihat trafik lab | `tcpdump` di Onion |
| 6 | Baseline traffic terekam | `baseline_kabita.pcap` + metrik |
| 7 | Hardening awal aktif | `ufw status`, `fail2ban-client status sshd` |
| 8 | Slide + laporan terunggah | `git push` sukses, file ada di GitHub |

---

## 0. [HOST] Nyalakan lab

```bash
VBM="/c/Program Files/Oracle/VirtualBox/VBoxManage.exe"
"$VBM" startvm "PBL-K4-01-Target-Ubuntu" --type headless
"$VBM" startvm "PBL-K4-02-Attacker-Kali"  --type gui
"$VBM" startvm "PBL-K4-03-Monitoring-Onion" --type gui
```

Cek adaptor lab sudah benar (harus `intnet pbl-kel4`):

```bash
"$VBM" showvminfo "PBL-K4-01-Target-Ubuntu" | grep -i "NIC 1"
"$VBM" showvminfo "PBL-K4-03-Monitoring-Onion" | grep -iE "NIC 1|Promisc"
```

Snapshot bersih sebelum eksperimen:

```bash
"$VBM" snapshot "PBL-K4-01-Target-Ubuntu" take "pra-skenario" --description "sebelum uji"
```

---

## 1. [TARGET] Pastikan layanan KABITA hidup

```bash
systemctl is-active kabita postgresql fail2ban ufw
curl -s -o /dev/null -w 'dashboard: %{http_code}\n' http://127.0.0.1/
curl -s http://127.0.0.1/api/ringkasan
```

Harapan: `active` ×4, `dashboard: 200`, dan JSON `{"jumlah_kambing":"6", ...}`.

Kalau `kabita` mati:

```bash
sudo journalctl -u kabita -n 30 --no-pager
sudo systemctl restart kabita && sleep 3 && systemctl is-active kabita
```

Kalau data kosong / ingin reset data (data lama hilang):

```bash
# [HOST] dari folder repo
python scripts/docs/deploy_kabita.py --db-only
```

---

## 2. [TARGET] Cek jaringan & port

```bash
ip -4 -o addr show enp0s3            # harus 192.168.4.5/24
ss -tulpn | grep LISTEN              # 22, 80 (0.0.0.0), 5432 (127.0.0.1)
sudo ufw status verbose              # active, deny incoming, allow 22 & 80
```

---

## 3. [KALI] Siapkan IP lab & uji koneksi

Login TTY: `Ctrl+Alt+F3`, lalu user `kali`, password `kali`.

```bash
sudo nmcli con add type ethernet ifname eth0 con-name pbl-lab ip4 192.168.4.100/24
sudo nmcli con up pbl-lab
ip -4 -o addr show eth0              # harus 192.168.4.100/24
ping -c3 192.168.4.5
curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://192.168.4.5/
curl -s http://192.168.4.5/api/kambing | head -c 200
```

---

## 4. [ONION] Pastikan sensor melihat trafik lab

Login: user `analyst`, password `cyberops`.

```bash
sudo ip link set eth0 promisc on arp on
sudo ip addr add 192.168.4.200/24 dev eth0
ping -c3 192.168.4.100
sudo tcpdump -i eth0 -nn host 192.168.4.100 -c 10
```

Sambil `tcpdump` berjalan, jalankan di **[KALI]**: `ping -c5 192.168.4.5`.
Harapan: 10 baris paket muncul di Onion.

---

## 5. [TARGET] Rekam baseline traffic normal

Terminal 1 — **[TARGET]**:

```bash
sudo tcpdump -i enp0s3 -nn -w ~/baseline.pcap -c 900
```

Terminal 2 — **[KALI]**:

```bash
for i in $(seq 1 15); do
  curl -s -o /dev/null http://192.168.4.5/
  curl -s -o /dev/null http://192.168.4.5/api/kambing
  ping -c1 -W1 192.168.4.5 >/dev/null
  sleep 2
done
```

Setelah loop selesai, **[TARGET]**:

```bash
sudo tcpdump -r ~/baseline.pcap -nn | wc -l
sudo cp ~/baseline.pcap /tmp/baseline_kabita.pcap
```

Simpan ke repo dari **[HOST]** (lihat bagian 7).

---

## 6. [TARGET] Terapkan / verifikasi hardening awal

```bash
# patch
sudo apt update && sudo apt -y full-upgrade

# minimalisasi service
for s in ModemManager snapd fwupd multipathd upower udisks2; do
  sudo systemctl disable --now "$s" 2>/dev/null
done

# firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'admin ssh'
sudo ufw allow from 192.168.4.0/24 to any port 80 proto tcp comment 'dashboard KABITA'
sudo ufw --force enable
sudo ufw status verbose

# brute force
sudo systemctl enable --now fail2ban
sudo fail2ban-client status sshd
```

Simpan bukti (jalankan di **[TARGET]**, hasilnya disalin ke repo pada bagian 7):

```bash
{
  echo "### Sistem";        lsb_release -ds; uname -r
  echo "### Port";          ss -tulpn | grep LISTEN
  echo "### Service";       systemctl list-units --type=service --state=running --no-pager --no-legend | awk '{print $1}' | sort
  echo "### ufw";           sudo ufw status verbose
  echo "### fail2ban";      sudo fail2ban-client status sshd
  echo "### KABITA";        systemctl is-active kabita; curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1/
  echo "### upgradable";    apt list --upgradable 2>/dev/null | tail -n +2 | wc -l
} | sudo tee /tmp/after.txt
```

---

## 7. [HOST] Ambil bukti ke repo

```bash
cd "D:/materi kuliah/Keamanan Siber/PBL"

# pcap baseline
scp -P 2222 iotadmin@127.0.0.1:/tmp/baseline_kabita.pcap \
  docs/blueteam/evidence/baseline/baseline_kabita.pcap

# keluaran hardening
scp -P 2222 iotadmin@127.0.0.1:/tmp/after.txt \
  docs/blueteam/evidence/hardening/after.txt

# metrik (hitung manual dari pcap)
sudo tcpdump -r docs/blueteam/evidence/baseline/baseline_kabita.pcap -nn 2>/dev/null | wc -l
```

Cek cepat isi repo:

```bash
git status
ls docs/blueteam/evidence/baseline docs/blueteam/evidence/hardening
```

---

## 8. [HOST] Slide, laporan, dan push

```bash
# slide (HTML -> PDF, 1280x720)
# buka docs/presentation-minggu9/slides.html lalu Print to PDF (lihat README di folder itu)

# laporan
python scripts/docs/md_report_to_docx.py \
  docs/reports/fase1/laporan-fase1.md \
  docs/reports/fase1/Laporan-Fase1-TEK1314-Kelompok4.docx

# commit & push
git add -A
git commit -m "checkpoint minggu 9: lab KABITA (Nuxt + PostgreSQL), baseline, hardening awal"
git push origin main
```

---

## Yang harus kamu kerjakan sendiri (tidak bisa diotomasi)

| # | Tugas | Cara |
|---|---|---|
| 1 | **Screenshot dashboard** untuk bukti | Buka Firefox/Chrome di VM Target: `http://127.0.0.1/`, login `admin` / `admin123`, tangkap layar, simpan `docs/blueteam/evidence/BUKTI_dashboard.png` |
| 2 | **Screenshot sensor Onion** | Jalankan `tcpdump` di Onion sambil ping dari Kali, tangkap terminalnya → `docs/blueteam/evidence/BUKTI_sensor.png` |
| 3 | **Push ke GitHub** | Butuh Personal Access Token: GitHub → Settings → Developer settings → Tokens (classic) → Generate, scope `repo`. Lalu `git push` saat diminta user = `rakasyau`, password = token |
| 4 | **Unggah slide sebelum sesi** | `docs/presentation-minggu9/slides.pdf` harus sudah ada di GitHub sebelum kelas mulai |
| 5 | **Isi nama & NIM di slide/laporan** | Sudah terisi; cek ulang di `slides.pdf` halaman 2 dan laporan halaman 1 |
| 6 | **Cabut sudo NOPASSWD sebelum penilaian** | Di Target: `sudo rm /etc/sudoers.d/90-pbl-nopasswd` (setelah semua otomasi selesai) |

## Kalau ada yang gagal

| Gejala | Perbaikan |
|---|---|
| `dashboard: 000` dari Kali | cek `ufw status` di Target; pastikan rule `80 from 192.168.4.0/24` ada |
| `502`/`500` di dashboard | `sudo journalctl -u kabita -n 50`; biasanya koneksi PostgreSQL |
| `ping` gagal antar VM | cek NIC 1 ketiga VM = `intnet pbl-kel4` |
| IP hilang setelah reboot Kali | `sudo nmcli con up pbl-lab` |
| Onion tidak melihat paket | `sudo ip link set eth0 promisc on arp on` |
