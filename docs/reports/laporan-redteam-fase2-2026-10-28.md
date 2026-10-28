# Laporan Eksekusi Red Team — Fase 2 SOC KABITA (Kelompok 4)

Tanggal eksekusi: **28 Oktober 2026** (semua waktu UTC) · Pelaksana: @Raka (Red Team) · Otomasi tanpa GUI
Rujukan: `docs/Panduan Eksekusi Fase 2 — SOC KABITA (Kelompok 4).docx`
Lingkup: **hanya bagian Red Team** dari kelima skenario (tahap Deteksi/Respons/Verifikasi diserahkan ke Blue Team)

Target: `PBL-K4-01-Target-KABITA` (192.168.4.5, replika lab yang sudah di-harden 8/8 kontrol).
Attacker: `PBL-K4-02-Attacker-Kali` (192.168.4.100). Tidak ada serangan ke sistem KABITA milik Mitra.

---

## 1. Cara akses yang dipakai

| Node | Jalur akses | Catatan |
|---|---|---|
| Attacker (Kali) | `VBoxManage guestcontrol run` (Guest Additions, user `kali`) — skrip bash dikirim base64 | Kali tidak punya NIC host-only/NAT-forward, jadi tidak bisa di-SSH dari laptop; hanya perintah serangan yang dijalankan di sini |
| Target Node | **SSH saja** — `ssh -p 2222 -i ~/.ssh/kabita_lab iotadmin@192.168.56.101`, sudo lewat PTY | Hanya untuk membaca keadaan target (log, config, kode, isi DB) sebagai bahan analisis; tidak ada perubahan konfigurasi |

Semua bukti = keluaran perintah nyata, dengan timestamp UTC (tanpa screenshot karena eksekusi headless).

## 2. Ringkasan hasil kelima skenario

| # | Skenario | Hasil nyata | Status |
|---|---|---|---|
| 1 | Reconnaissance (nmap) | Terbuka hanya **2222** (OpenSSH 10.2p1), **80** (nginx 1.28.3), **1883** (MQTT). **443 CLOSED**, **22/5432/8080 FILTERED**, 65.531 port sisanya filtered. Selesai 163 detik | Selesai (Serang + Analisis) |
| 2 | Brute-force SSH (Hydra) | **Hydra berhenti sebelum 1 percobaan**: `does not support password authentication (method reply 4)` → 0 percobaan, fail2ban **tidak terpicu** (`Total failed: 0`). Uji pengganti (brute-force akun) → **IP 192.168.4.100 DIBAN** setelah 8 kegagalan (maxretry 5); tcp/2222 jadi *Connection refused*; port 80 & 1883 tetap normal | Selesai, dengan koreksi cara uji |
| 3 | SQL injection (sqlmap) | 4 payload manual (`1 OR 1=1`, `1'`, `1 UNION SELECT …`, `1;SELECT pg_sleep(2)`) → **semua 400**. sqlmap mengirim **2.313 request** (2208×400, 93×404, 12×200) → `all tested parameters do not appear to be injectable`. Varifikasi kode: `strconv.Atoi` + query **parameterized** (`$1`); tidak ada query ber-payload di `log_statement` PostgreSQL | Selesai (Serang + Analisis) |
| 4 | MQTT publish tanpa kredensial | Ditolak broker: **`Connection Refused: not authorised`** (exit 5), konsisten 3×; log broker mencatat `Client <id> disconnected, not authorised.`; `bobot_log` tag RFID-999 = **0 baris** | Selesai (Serang + Analisis) |
| 5 | MQTT publish kredensial bocor | Payload panduan (**9999 kg**) **ditolak aplikasi** (`invalid berat_kg`, di luar rentang ≤300) — jadi TIDAK masuk DB. Yang lolos: **299 kg** dan **0,1 kg** → tersimpan di `bobot_log`; 20 pesan terkirim **< 1 detik** tanpa penolakan; publish ke topic lain juga diterima (tidak ada ACL). Dampak: `bobot_log` tag RFID-002 dari 1 → 24 baris (tabel 13 → 36) dalam 4 detik, **tanpa satu pun peringatan** | Selesai (Serang + Analisis) |

Kesimpulan singkat: 3 dari 5 skenario tertahan rapi oleh hardening (1, 3, 4 — plus 2 untuk jalur password),
dan **1 skenario terbukti sebagai celah nyata: Skenario 5** (kredensial valid → data palsu diterima tanpa
deteksi apa pun).

## 3. Kesalahan pada dokumen panduan yang ditemukan, dan perbaikannya

Semua perbaikan sudah **diterapkan langsung ke dalam .docx** dengan menambahkan blok
`KOREKSI HASIL EKSEKUSI 2026-10-28` pada paragraf/sel terkait (teks asli tidak dihapus), plus bagian
penutup **"Catatan Revisi — 28 Oktober 2026"**. Salinan sebelum perubahan disimpan sebagai
`Panduan Eksekusi Fase 2 — SOC KABITA (Kelompok 4) [sebelum koreksi 2026-10-28].docx`.

| # | Isi dokumen (salah) | Fakta hasil eksekusi | Perbaikan di dokumen |
|---|---|---|---|
| 1 | Skenario 1: "hanya port 2222, **80/443**, 1883 terbuka" | 443 **CLOSED** — UFW mengizinkan tapi tidak ada layanan TLS; 22/5432/8080 filtered | Paragraf "Hasil yang diharapkan" dikoreksi + catatan `-O` jalan tanpa sudo |
| 2 | Skenario 2: "yang diuji … apakah **fail2ban tetap memblokir** IP penyerang meski semua percobaan gagal karena metode auth salah" | Hydra **tidak melakukan percobaan apa pun** pada host ber-`PasswordAuthentication no`, sehingga fail2ban tidak punya event → premis tidak bisa diuji dengan Hydra | Sel tabel diberi hasil nyata + perintah uji pengganti (brute-force akun); paragraf penjelas dikoreksi |
| 3 | Skenario 3: kekhawatiran "validasi mungkin hanya filter regex, bukan parameterized query" | Terbukti **parameterized** (`WHERE kambing_id = $1`) + validasi `strconv.Atoi`; 2.313 request tidak ada yang injectable | Ditambahkan hasil + varian `1*/riwayat` agar titik injeksi eksplisit (perintah asli tetap valid) |
| 4 | Skenario 5: "processReading … **hanya memvalidasi tipe data**; payload 9999 akan lolos ke bobot_log" | Kode sudah membatasi **0 < berat_kg ≤ 300** → 9999 **ditolak**; yang lolos justru nilai dalam rentang tapi tidak wajar (299 / 0,1) | Sel tabel, paragraf premise, "Analisis", dan "Respons" dikoreksi; kandidat **C.4** diubah menjadi: perketat rentang ke nilai wajar + penandaan anomali + `acl_file` topic MQTT + rate limit |
| 5 | Konvensi bukti mengasumsikan screenshot (`.png`) | Eksekusi tanpa GUI | Ditambahkan catatan: screenshot diganti `.txt` berisi keluaran perintah + timestamp UTC dengan pola nama yang sama |
| 6 | Rujukan kontrol **"C.7"** (validasi input), **"C.8"** (log_statement), dan usulan **"C.9"** | `docs/blueteam/hardening_checklist.md` hanya punya kontrol **C.1–C.3** (8 kontrol: A.1–A.2, B.1–B.3, C.1–C.3) | Rujukan diperbaiki: C.7 → **C.2**, C.8 → **C.3**, usulan kontrol baru → **C.4** |

Temuan tambahan yang tidak ada di dokumen (layak masuk laporan VA): **tidak ada `acl_file`** di Mosquitto
(user mana pun yang punya kredensial bisa publish ke topic apa pun) dan **tidak ada rate limit publish**.

## 4. Berkas yang dihasilkan

Bukti (semua berisi keluaran mentah + ringkasan di bagian atas):

```
docs/redteam/evidence/skenario1-serang.txt          nmap: port terbuka/closed/filtered + cross-check ss -tlnp
docs/redteam/evidence/skenario2-serang.txt          Hydra (abort) + brute-force akun + efek ban
docs/redteam/evidence/skenario2-fail2ban-rule.txt   aturan nftables f2b-table yang terpasang
docs/redteam/evidence/skenario3-serang.txt          sqlmap + payload manual + log nginx 400/sqlmap
docs/redteam/evidence/skenario4-serang.txt          mosquitto_pub tanpa kredensial + log broker
docs/redteam/evidence/skenario5-serang.txt          kredensial bocor: 9999 ditolak, 299/0,1 lolos, tanpa deteksi
```

Dokumen:

```
docs/purple-team-log.md                             kerangka 5 skenario; tahap Serang + Analisis terisi,
                                                    Deteksi/Respons/Verifikasi ditandai [MENUNGGU BLUE TEAM]
docs/reports/laporan-redteam-fase2-2026-10-28.md    laporan ini
```

Perkakas eksekusi (di luar repo, sesuai konvensi bahwa PBL hanya berisi berkas wajib):
`PBL-pendukung/scripts/redteam/` — `pbl.py` (harness Kali/Target), `skenario1.py` … `skenario5.py`,
`skenario2b.py` (uji pengganti fail2ban), `fix_docx.py` (perbaikan panduan).

## 5. Sisa pekerjaan (Blue Team, jangan terlewat)

1. **Deteksi** untuk kelima skenario pada jendela waktu berikut (UTC):
   S1 `06:35:23–06:40:43`, S2 `06:41:04–06:42:02`, S3 `06:43:08–06:43:22`, S4 `06:44:58–06:45:00`, S5 `06:45:11–06:45:15`.
   Fokus: apakah Suricata ET Open memicu alert, dan khusus S4/S5 apakah Zeek `mqtt_connect.log`/`mqtt_publish.log` aktif.
   **Catat apa adanya bila tidak ada alert** — untuk S1 (full scan pelan) dan S4 ini justru temuan utama.
2. **Respons**: keputusan rule threshold scan (S1), perketat `maxretry`/`bantime` bila perlu (S2),
   kontrol C.4 (S5) + tambahkan barisnya ke `docs/blueteam/hardening_checklist.md` dengan bukti before/after.
3. **Verifikasi**: ulangi tiap serangan setelah mitigasi; untuk S2 ulangi setelah `bantime` (600 s) habis.

Keadaan lab yang perlu diperhatikan:

- IP `192.168.4.100` masih ada di set `f2b-sshd` hingga `bantime` habis (600 s sejak 06:42 UTC). Ban hanya
  untuk `tcp dport 2222`, tidak mengganggu port 80/1883.
- **23 baris data palsu masih tersimpan** di `bobot_log` untuk tag `RFID-002` (bukti dampak S5).
  Catat id-nya dulu di evidence, baru bersihkan (mis. `DELETE FROM bobot_log WHERE id > 13 …`).
- Kredensial MQTT disensor di semua berkas bukti (`***kredensial-lab-disensor***`).

## 6. Cara mengulang eksekusi

```bash
# dari laptop (bash), harness ada di PBL-pendukung/scripts/redteam/
cd "D:/materi kuliah/Keamanan Siber/PBL-pendukung/scripts/redteam"
/d/Anaconda/python.exe skenario1.py    # reconnaissance (≈3 menit)
/d/Anaconda/python.exe skenario2.py    # hydra + uji koneksi
/d/Anaconda/python.exe skenario2b.py   # uji pengganti fail2ban (brute-force akun)
/d/Anaconda/python.exe skenario3.py    # sqlmap + payload manual
/d/Anaconda/python.exe skenario4.py    # MQTT tanpa kredensial
/d/Anaconda/python.exe skenario5.py    # MQTT kredensial bocor (membaca .env Target Node)
```

Prasyarat: tiga VM PBL-K4-01/02/03 hidup, key `~/.ssh/kabita_lab` ada, Python dengan `paramiko`.

## 7. Batasan yang jujur

- Bukti berupa teks, bukan screenshot (tidak ada sesi GUI di Kali); timestamp UTC disertakan agar Blue Team
  bisa mencocokkan dengan Hunt/log.
- sqlmap dijalankan dengan `--level=2 --risk=1` untuk versi penanda `*` (agar tidak berjam-jam); versi
  perintah panduan memakai default sqlmap apa adanya (`--batch`).
- Kata sandi MQTT dan kata sandi sudo lab dipakai hanya di dalam skrip otomasi dan tidak ditulis ke berkas
  bukti.
