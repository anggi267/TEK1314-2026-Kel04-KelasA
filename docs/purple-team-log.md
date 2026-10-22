# Purple Team Log

Siklus lima tahap per skenario: **serang → deteksi → analisis → mitigasi → uji ulang**.
Diisi saat eksekusi Minggu 10–11. Status awal: semua `RENCANA`.

| Skenario | Serang | Deteksi | Analisis | Mitigasi | Uji ulang | Status |
|---|---|---|---|---|---|---|
| RT-01 Discovery | — | — | — | — | — | RENCANA |
| RT-02 Kredensial SSH | — | — | — | — | — | RENCANA |
| RT-03 SQL injection | — | — | — | — | — | RENCANA |
| RT-04 Pemalsuan sesi | — | — | — | — | — | RENCANA |
| RT-05 DoS terkontrol | — | — | — | — | — | RENCANA |

## Format pengisian per sel

```
<tanggal & jam> | <ringkasan tindakan/hasil> | <bukti: file di evidence/ atau query log>
```

Contoh (ilustrasi format, bukan hasil nyata):
`22 Okt 14:05 | sqlmap dapat 60 baris telemetri | evidence/RT-03/sqlmap_dump.txt`

## Kolom deteksi: sumber yang dipakai

| Sumber | Perintah / lokasi |
|---|---|
| Akses aplikasi | `sudo journalctl -u kabita --since '-10min'` |
| Firewall | `sudo tail -f /var/log/ufw.log` |
| Auth SSH | `sudo journalctl -u ssh --since '-10min'`, `sudo fail2ban-client status sshd` |
| PostgreSQL | `sudo tail -f /var/log/postgresql/postgresql-18-main.log` |
| Sensor (Onion) | `sudo tcpdump -i eth0 -nn host 192.168.4.100` |

## Aturan penilaian siklus

Satu skenario dianggap **tuntas** hanya bila kelima kolom terisi dan uji ulang menunjukkan
perilaku berubah (serangan gagal / terdeteksi), dengan bukti file yang bisa dibuka.
