# Purple Team Log — Fase 2 (KABITA, Kelompok 4)

Target Node: `PBL-K4-01-Target-KABITA` — 192.168.4.5 (replika lab, bukan sistem Mitra).
Attacker Node: `PBL-K4-02-Attacker-Kali` — 192.168.4.100.
Semua waktu UTC. Eksekusi Red Team: **2026-10-28**, oleh @Raka (Red Team), tanpa GUI (otomasi),
jadi bukti berupa berkas `.txt` berisi keluaran perintah + timestamp, bukan screenshot.
Jalur akses: perintah serangan dijalankan **di dalam VM Kali**; Target Node dibaca **hanya lewat SSH**
(`ssh -p 2222 -i ~/.ssh/kabita_lab iotadmin@192.168.56.101`).

Status: tahap **Serang** dan **Analisis** (root cause teknis) kelima skenario SELESAI untuk sisi Red Team.
Tahap **Deteksi / Respons / Verifikasi** menunggu Blue Team (Security Onion + fail2ban + log aplikasi)
dijalankan pada rentang waktu yang sama. Bukti Red Team: `docs/redteam/evidence/skenarioN-*.txt`.

Catatan kondisi awal: seluruh serangan dijalankan terhadap Target Node yang **sudah di-harden**
(8/8 kontrol selesai) — bukan baseline polos.

---

## Eksekusi ulang 2026-11-04 (data yang kini dipakai di berkas bukti)

Kelima skenario dijalankan ulang pada **4 November 2026, 14:55–15:20 UTC** dan berkas bukti
`docs/redteam/evidence/skenarioN-serang.txt` sudah ditulis ulang mengikuti hasil ini, dengan format
**perintah → output → kesimpulan** (tanpa kalimat "sesuai panduan"). Angka kunci:

| Skenario | Waktu (UTC) | Hasil |
|---|---|---|
| 1 Recon | 15:01:25 (144 s) | 80, 1883, 2222 terbuka; 443 closed; 22/5432/8080 filtered; 65.531 filtered |
| 2 Brute force | 15:05:17 | Hydra berhenti sebelum 1 percobaan; 8 login gagal → fail2ban ban 192.168.4.100 (600 s) |
| 3 SQLi | 14:55:26 (14 s) | 4 payload manual → 400; sqlmap 1.295 request → *not injectable*; log DB bersih |
| 4 MQTT anon | 14:55:41 | 3 upaya ditolak `not authorised`; `bobot_log` tetap 60 baris |
| 5 MQTT bocor | 14:55:45 | 9999 ditolak aplikasi; 299 & 0,1 tersimpan; topic liar diterima; 20 pesan tanpa throttle; **60 → 83 baris** |

**Hasil pantauan sisi deteksi (bukan penilaian Blue Team):** Security Onion **tidak mencatat satu pun alert**
selama kelima skenario. Squert pada interval `2026-11-04 00:00:00–23:59:59` menunjukkan *queued 0 / total
events 0 / total signatures -* tanpa filter objek maupun sensor. Penyebab terlihat di sensor: berkas
`snort.unified2` terakhir 0 byte bertanggal 19 Jun 2020, **0 berkas unified2 baru sejak 1 Nov 2026**, dan
proses `snort` tidak lagi dijumpai (hanya `barnyard2`). Artinya pipeline alert belum menulis apa pun —
detail dan screenshot: `docs/redteam/evidence/security-onion-hasil-pemeriksaan.txt`,
`security-onion-squert-0-event.png`, `security-onion-pipeline-ids.png`.
Perbaikan pipeline ini menjadi prasyarat seluruh tahap **Deteksi** di bawah.

---

## Skenario 1 — Reconnaissance (nmap)

**Serang** — `nmap -sV -O -p- 192.168.4.5` dari Kali (192.168.4.100), selesai dalam 163 detik.
Hasil: **2222/tcp** (OpenSSH 10.2p1 Ubuntu), **80/tcp** (nginx 1.28.3 Ubuntu), **1883/tcp** (MQTT) terbuka;
**443/tcp CLOSED**; **22, 5432, 8080 FILTERED** (no-response/di-drop UFW); 65.531 port sisanya filtered.
Skenario bahkan memicu versi otomatis kedua (`nmap -Pn -sV -p- --min-rate 2000`) dengan hasil identik.
Bukti: `docs/redteam/evidence/skenario1-serang.txt`.

**Deteksi** — _[MENUNGGU BLUE TEAM]_ Hunt Security Onion, filter `src_ip:192.168.4.100` pada jendela
**06:35:23–06:40:43 UTC**. Hipotesis yang harus diuji: apakah ET Open memicu alert untuk full scan `-p-`
yang pelan (banyak port, kecepatan rendah). Perlu dicatat apa adanya bila **tidak ada alert**.

**Analisis** — Scan full-port yang pelan memang tipikal lolos signature ET Open (tidak ada pola SYN
rate tinggi). Yang terverifikasi dari sisi target: PostgreSQL (5432) dan API Go (8080) **tidak terekspos**
(`ss -tlnp` menunjukkan keduanya hanya di 127.0.0.1), konsisten dengan kontrol B.3/B.5. Temuan penting:
**443 terbuka di UFW tetapi tidak ada layanan TLS** → port "diizinkan tapi kosong", bukan permukaan serang nyata.

**Respons** — _[MENUNGGU BLUE TEAM]_ Tambah custom rule threshold (banyak port tujuan dari satu src_ip
dalam waktu singkat) **atau** dokumentasikan alasan tidak menambah rule (risiko false-positive tinggi).

**Verifikasi** — _[MENUNGGU BLUE TEAM]_ Ulangi scan yang sama setelah rule dibuat: alert muncul
(kalau rule dibuat) atau keputusan Tahap 4 ditegaskan ulang.

---

## Skenario 2 — Brute-force SSH (Hydra)

**Serang** — `hydra -l iotadmin -P <wordlist 10 kandidat> -s 2222 ssh://192.168.4.5`.
**Hydra tidak pernah sampai melakukan satu percobaan password:**
`[ERROR] target ssh://192.168.4.5:2222/ does not support password authentication (method reply 4).`
Karena itu tidak ada event kegagalan autentikasi yang dicatat sshd, dan jail sshd tetap
`Total failed: 0, Currently banned: 0`.
Uji pengganti yang benar-benar menguji fail2ban dijalankan sebagai bagian skenario ini:
brute-force **akun** (9 percobaan user acak: attacker1, fakeuser3, admin5, root, baduser6, …)
→ sshd mencatat `Invalid user …` + `Connection closed by invalid user … [preauth]`
→ fail2ban **BANNED 192.168.4.100** setelah melewati `maxretry = 5` (`Total failed: 8`).
Dari sisi penyerang: `tcp/2222` berubah menjadi **Connection refused** (109 ms), nmap:
`2222/tcp filtered (reason port-unreach)`; layanan lain tetap normal (HTTP 80 → 200, MQTT 1883 → terbuka).
Bukti: `docs/redteam/evidence/skenario2-serang.txt`, `skenario2-fail2ban-rule.txt`.

**Deteksi** — _[MENUNGGU BLUE TEAM]_ `sudo fail2ban-client status sshd` dan Hunt Security Onion
(brute-force SSH) pada jendela **06:41:04–06:42:02 UTC**. Bahan yang sudah tersedia di target:
`Maxretry 5 · Findtime 600 s · Bantime 600 s`, action `nftables`, aturan aktif
`tcp dport 2222 ip saddr @addr-set-sshd reject with icmp port-unreachable`.

**Analisis** — Kontrol A.1 (PasswordAuthentication no) **mematikan seluruh jalur brute-force password**:
Hydra berhenti sebelum mengirim percobaan apa pun, sehingga fail2ban tidak punya bahan untuk mem-ban.
Ban baru terpicu ketika penyerang menghasilkan kegagalan **berbasis akun/publickey** (invalid user),
dan itu terjadi pada percobaan ke-6 (setelah 5 kegagalan sesuai `maxretry`).
Artinya pertanyaan panduan ("apakah fail2ban tetap memblokir walau semua percobaan gagal karena
metode auth salah") tidak bisa dijawab oleh Hydra — perlu uji pengganti seperti di atas.

**Respons** — _[MENUNGGU BLUE TEAM]_ Putuskan apakah `maxretry`/`bantime` perlu diperketat
(mis. `maxretry=3`, `bantime=1h`) mengingat ban hanya berlaku untuk `tcp dport 2222`.
Jika diubah, simpan diff `jail.local` sebagai `docs/blueteam/evidence/skenario2-respons-*.txt`.

**Verifikasi** — _[MENUNGGU BLUE TEAM]_ Ulangi brute-force akun dari IP yang sama (atau IP baru setelah
bantime 600 s habis) dan pastikan blokir terjadi sesuai target baru.

---

## Skenario 3 — SQL Injection (sqlmap)

**Serang** — Uji manual ke `GET /api/v1/kambing/:id/riwayat` (segmen path `id`):
`1 OR 1=1`, `1'`, `1 UNION SELECT 1,2,3,4`, `1;SELECT pg_sleep(2)` → **semuanya HTTP 400 Bad Request**.
`sqlmap -u "http://192.168.4.5/api/v1/kambing/1/riwayat" --batch` mengirim **2.313 permintaan**
(UA `sqlmap/1.10.9#stable`): 2208 × 400, 93 × 404, 12 × 200 — dan 12 respons 200 itu semuanya URL bersih
yang ditambahi query string karangan sqlmap (mis. `?tyqb=2266 AND 1=1 UNION …`) yang diabaikan aplikasi,
bukan bukti injeksi berhasil. Kesimpulan sqlmap:
`all tested parameters do not appear to be injectable`.
Uji ulang dengan penanda injeksi eksplisit (`1*/riwayat`, `--level=2 --risk=1`): 501 × HTTP 400, hasil sama.
Bukti: `docs/redteam/evidence/skenario3-serang.txt`.

**Deteksi** — _[MENUNGGU BLUE TEAM]_ Alert ET `WEB_SERVER SQL injection` di Hunt pada jendela
**06:43:08–06:43:22 UTC**; cek `grep -ic sqlmap /var/log/nginx/access.log` (saat eksekusi: **2.313**)
dan `log_statement` PostgreSQL. Yang harus dicari: apakah ada query ber-payload yang sampai ke database
(kalau ada = temuan serius).

**Analisis** — Tidak ada injeksi karena dua lapis: (1) segmen path `id` divalidasi
`strconv.Atoi` + tolak `n <= 0` di `kambingSubRouter`, sehingga payload ditolak **sebelum** query;
(2) query-nya **parameterized**: `db.Query("SELECT … WHERE kambing_id = $1 …", id)` —
bukan penyambungan string, jadi bahkan bila validasi longgar, nilai tetap dikirim sebagai parameter.
Karena payload tidak pernah sampai ke database, `log_statement` PostgreSQL bersih (tidak ada bukti
kebocoran/kesalahan query). Jadi ini bukan sekadar "filter regex di input" seperti yang dikhawatirkan
panduan.

**Respons** — _[MENUNGGU BLUE TEAM]_ Karena tidak ada celah, responsnya adalah **dokumentasi**
mengapa endpoint aman (validasi tipe + parameterized query), bukan perubahan kode.
Jika Blue Team ingin deteksi lebih awal: rule ET threshold untuk UA `sqlmap` / banyak 400 dari satu src_ip.

**Verifikasi** — _[MENUNGGU BLUE TEAM]_ Ulangi sqlmap/uji manual, konfirmasi semua payload tetap 400
dan tidak ada baris baru di `log_statement`.

---

## Skenario 4 — MQTT Publish Tanpa Kredensial

**Serang** — `mosquitto_pub -h 192.168.4.5 -p 1883 -t kabita/readings -m '{"tag_rfid":"RFID-999","berat_kg":0}'`
**tanpa** `-u/-P` → `Connection error: Connection Refused: not authorised` (exit code 5),
konsisten pada 3 percobaan; username tanpa password juga ditolak.
TCP handshake ke 1883 tetap diterima (port memang sengaja terbuka ke LAN sesuai B.1) —
penolakan terjadi di level **broker** (CONNACK), bukan di aplikasi.
Log broker mencatat setiap penolakan: `Client <client-id> disconnected, not authorised.`
Tidak ada pesan yang sampai ke `processReading`; `bobot_log` untuk `RFID-999` = **0 baris**.
Bukti: `docs/redteam/evidence/skenario4-serang.txt`.

**Deteksi** — _[MENUNGGU BLUE TEAM]_ Zeek `mqtt_connect.log` (`connect_status` gagal) pada jendela
**06:44:58–06:45:00 UTC**; log Mosquitto sebagai pembanding. **Catat juga bila Suricata ET Open
TIDAK memicu alert apa pun** — broker MQTT tidak tercakup ruleset generik; ini temuan, bukan berarti aman.

**Analisis** — Penolakan terjadi di broker lewat `allow_anonymous false` + `password_file`
(`listener 1883 0.0.0.0`), jadi pesan tidak pernah mencapai aplikasi. Untuk skenario ini lapisan
broker sudah cukup: jalur publikasi tertutup total bagi klien tanpa kredensial, dan penolakannya
tercatat di log broker (bahan mentah deteksi, meski belum ada alert otomatis).

**Respons** — _[MENUNGGU BLUE TEAM]_ Opsional: alert eksplisit untuk `connect_status` gagal berulang
dari satu IP (Zeek script atau rule Suricata), karena default ET Open tidak menutup MQTT.

**Verifikasi** — _[MENUNGGU BLUE TEAM]_ Ulangi publish tanpa kredensial: tetap ditolak
dan (jika dibuat) alert baru muncul.

---

## Skenario 5 — MQTT Publish dengan Kredensial Bocor

**Serang** — Kredensial `kabita_device` diambil dari `/opt/kabita-backend/.env` (mode 600) pada Target
Node — simulasi credential theft. Publish dengan kredensial valid:
`{"tag_rfid":"RFID-002","berat_kg":9999}` → **broker menerima (exit 0)**, tetapi backend menolak:
`mqtt: gagal proses reading dari tag RFID-002: invalid berat_kg` (tidak masuk `bobot_log`).
Payload berikutnya yang masih **di dalam rentang kode** lolos semua:
`299 kg` (kambing 299 kg — mustahil) dan `0.1 kg` → tersimpan di `bobot_log`;
20 pesan tambahan terkirim dalam **< 1 detik** tanpa penolakan; publish ke topic lain
(`kabita/readings/../sensor`) juga diterima (tidak ada ACL topic).
Dampak: `bobot_log` tag RFID-002 dari 1 → 24 baris (tabel 13 → 36 baris) dalam 4 detik,
tanpa peringatan apa pun. Bukti: `docs/redteam/evidence/skenario5-serang.txt`.

**Deteksi** — _[MENUNGGU BLUE TEAM]_ Zeek `mqtt_publish.log` (field `topic`/`payload`) pada jendela
**06:45:11–06:45:15 UTC**; cek apakah ada entri anomali di `bobot_log` dan apakah **ada** mekanisme
(log/alert) yang menandainya. Yang benar-benar terjadi saat eksekusi: **tidak ada** deteksi — hanya
log informasional backend (`mqtt: reading tersimpan — … 299.0 kg`), tidak ada alert.

**Analisis** — Validasi yang ADA: `processReading` memeriksa format `tag_rfid` (regex) dan rentang
`0 < berat_kg <= 300` — jadi anggapan panduan bahwa "hanya tipe data yang divalidasi" **salah**.
Yang TIDAK ADA: kewajaran fisik nilai berat (kambing 299 kg diterima), penandaan/pemisahan data
anomali, rate limit publish, dan otorisasi topic per-user. Karena kredensialnya valid, autentikasi
tidak dapat dijadikan andalan; satu-satunya pertahanan untuk kasus *credential theft* adalah validasi
nilai di aplikasi + pembatasan hak kredensial (topic ACL, rate limit).

**Respons** — _[MENUNGGU BLUE TEAM]_ Usulan kontrol tambahan (kandidat **C.4** di
`docs/blueteam/hardening_checklist.md`): (a) perketat rentang `berat_kg` ke nilai wajar kambing
(mis. `5 <= x <= 150`) dan/atau tandai nilai di luar rentang wajar sebagai anomali alih-alih
menolak mentah; (b) `acl_file` di Mosquitto supaya `kabita_device` hanya boleh publish ke
`kabita/readings`; (c) rate limit publish. Bukti before/after masuk
`docs/blueteam/evidence/skenario5-respons-c9.txt`.

**Verifikasi** — _[MENUNGGU BLUE TEAM]_ Ulangi publish `299`/`9999`: harus ditolak/ditandai;
lalu uji payload wajar (mis. `21.5`) untuk memastikan tidak ada false-positive.

---

## Catatan lintas-skenario (perlu tindak lanjut)

1. **Ban fail2ban masih membawa efek saat log ini ditulis**: IP `192.168.4.100` masuk
   `addr-set-sshd` hingga `bantime` (600 s) habis. Tidak menghalangi Skenario 3–5 karena ban hanya
   untuk `tcp dport 2222`. Blue Team perlu mengulang uji Skenario 2 setelah bantime habis.
2. **Data uji Skenario 5 masih ada di `bobot_log`** (23 baris palsu untuk tag `RFID-002`).
   Itu bukti dampak; bersihkan setelah Blue Team selesai mendokumentasikan, dengan
   `DELETE FROM bobot_log WHERE id IN (…)` (catat id-nya di evidence sebelum dihapus).
3. **Kredensial MQTT disensor** di berkas evidence (`***kredensial-lab-disensor***`).
4. Tahap Deteksi wajib dijalankan **pada rentang waktu yang sama** dengan serangan (timestamp UTC
   sudah dicantumkan di tiap subbagian di atas) — bukan rekonstruksi dari log sesudahnya.
