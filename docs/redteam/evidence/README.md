# Evidence — Red Team (hasil eksekusi serangan)

Diisi bertahap mulai Minggu 10, satu subfolder per skenario:

```
rt01/  Reconnaissance (nmap)
rt02/  Exploitation vsftpd 2.3.4 (Metasploit)
rt03/  SQL injection dashboard (sqlmap/Burp)
rt04/  MQTT spoof publish (mosquitto)
rt05/  SYN flood terkontrol (hping3)
```

## Isi minimum per subfolder

| File | Isi |
|---|---|
| `<id>_command.txt` | Perintah persis + timestamp (`date`) |
| `<id>_output.txt` | Output teks (`nmap -oN`, `sqlmap` log, `msfconsole -x ... > file`) |
| `<id>_screen.png` | Screenshot terminal saat eksekusi |
| `<id>_alert.png` | Screenshot alert Security Onion dari Blue Team (atau catatan bila **tidak** ada alert) |
| `<id>_notes.md` | Berhasil/gagal, penyebab, kaitan ke kontrol checklist |

## Aturan

1. Rekam kondisi **sebelum** mitigasi dan **sesudah** mitigasi (Tahap 1 dan Tahap 5) — keduanya
   wajib, karena inti penilaian adalah siklus tertutup.
2. Bila serangan **tidak terdeteksi**, itu tetap temuan: tulis `<id>_no_alert.md` berisi apa yang
   dicek (query Zeek/Suricata) dan usulan rule baru.
3. Jangan pernah menjalankan skenario ke IP di luar `192.168.4.0/24`.
4. Sensor data pribadi/hash sebelum commit.

## Indeks cepat (diisi saat eksekusi)

| Skenario | Tanggal | Berhasil? | Terdeteksi? | Catatan |
|---|---|---|---|---|
| RT-01 | — | — | — | — |
| RT-02 | — | — | — | — |
| RT-03 | — | — | — | — |
| RT-04 | — | — | — | — |
| RT-05 | — | — | — | — |
