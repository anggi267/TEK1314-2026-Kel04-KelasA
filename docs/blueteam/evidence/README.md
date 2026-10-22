# Evidence — Blue Team (hardening before/after)

Folder ini menampung bukti **before** dan **after** untuk setiap kontrol pada
`docs/blueteam/hardening_checklist.md`.

## Isi folder saat ini (21 Oktober 2026)

| Path | Isi | Status |
|---|---|---|
| `hardening-fase1/before.txt` | potret kondisi sebelum hardening (port, service, ufw, jumlah paket upgradable) | ✅ |
| `hardening-fase1/after.txt` | potret setelah hardening (port, service, `ufw status verbose`, `fail2ban-client status sshd`, uji web 200) | ✅ |
| `baseline/baseline_minggu9.pcap` | capture traffic normal 440 paket / 41,3 detik | ✅ |
| `baseline/baseline_metrics.txt` | ringkasan metrik baseline | ✅ |

Bukti ini mendukung laporan Fase 1 (`docs/reports/fase1/`). Bukti per-kontrol dengan pola
`<ID>_<before|after>_<topik>` menyusul pada saat kontrol tersebut dieksekusi di Fase 2.

## Aturan penamaan

```
<ID-KONTROL>_<before|after>_<ringkasan>.png|txt
```

Contoh:
- `A2_before_password_login_ok.png`
- `A2_after_password_login_denied.png`
- `B1_before_nmap_full.txt` / `B1_after_nmap_full.txt`
- `B2_after_ufw_status.png`

## Aturan isi bukti

1. **Satu kontrol = minimal satu bukti before + satu bukti after.** Bukti berbentuk teks
   (output `nmap`, `ss -tulpn`, `ufw status`) lebih kuat daripada screenshot saja — simpan
   keduanya bila memungkinkan.
2. Screenshot wajib menampilkan **prompt hostname + tanggal** (atau jalankan
   `date; <perintah> | tee <file>`), agar tidak dipertanyakan keasliannya.
3. Jangan menyensor berlebihan sampai bukti tidak terbaca; sensor hanya password/hash.
4. Dump `nmap` disimpan sebagai `.txt` (format `-oN`), bukan hanya gambar.

## Skrip bantu

- `scripts/blueteam/01_rekam_baseline.sh` — merekam kondisi awal (port terbuka, config SSH,
  status service) ke `before/`.
- `scripts/blueteam/02_rekam_after.sh` — merekam kondisi setelah hardening ke `after/`.

Jalankan dari VM target: `sudo bash 01_rekam_baseline.sh` lalu bandingkan antar folder.

## Checklist cepat sebelum commit

- [ ] Setiap kontrol `Selesai` punya file `_before_` dan `_after_`
- [ ] Nama file sesuai ID kontrol (A1–A4, B1–B3, C1–C3)
- [x] `baseline_minggu9.pcap` + `baseline_metrics.txt` tersedia
- [ ] Setiap kontrol yang diklaim `Selesai` punya link bukti di hardening_checklist
- [ ] Tidak ada kredensial asli yang ikut ter-commit
