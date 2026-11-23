# Purple Team Log — Fase 2 (KABITA, Kelompok 4)

Target Node: `PBL-K4-01-Target-KABITA` — 192.168.4.5 (replika lab, bukan sistem Mitra).
Attacker Node: `PBL-K4-02-Attacker-Kali` — 192.168.4.100.
Semua waktu UTC. Eksekusi Red Team: **2026-10-28**, oleh @Raka (Red Team), tanpa GUI (otomasi),
jadi bukti berupa berkas `.txt` berisi keluaran perintah + timestamp, bukan screenshot.
Jalur akses: perintah serangan dijalankan **di dalam VM Kali**; Target Node dibaca **hanya lewat SSH**
(`ssh -p 2222 -i ~/.ssh/kabita_lab iotadmin@192.168.56.101`).

Status (diperbarui Fase 3, Minggu 14–15): **kelima tahap terisi untuk kelima skenario.**
Serang dan Analisis selesai oleh Red Team. **Deteksi sudah dinilai** — hasilnya nol alert untuk seluruh skenario,
dengan akar masalah teridentifikasi di sensor (lihat bagian "Catatan lintas-skenario"). **Respons** berisi kontrol
yang diusulkan beserta status pelaksanaannya. **Verifikasi** tuntas untuk empat skenario karena kegagalan
serangan itu sendiri sudah membuktikan kontrol bekerja; Skenario 5 masih menunggu eksekusi mitigasi.
Bukti Red Team: `docs/redteam/evidence/skenarioN-*.txt`. Sintesis lengkap: `docs/final/incident_report.pdf`.

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
| 4 MQTT anon | 14:55:41 | 3 upaya ditolak `not authorised`; `bobot_log` tidak bertambah |
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

**Deteksi** — _[SELESAI — hasil: TIDAK TERDETEKSI]_ Squert diperiksa pada interval seluruh
`2026-11-04 00:00:00–23:59:59` dengan `FILTERED BY OBJECT: NO` dan `FILTERED BY SENSOR: NO`:
**queued 0 / total events 0 / total signatures -**. Jadi nol alert, bukan akibat penyaringan tampilan.
Diagnostik sensor menunjukkan proses `snort` tidak berjalan, berkas `snort.unified2` terakhir berukuran
0 byte bertanggal 19 Jun 2020, dan 0 berkas unified2 baru sejak 1 Nov 2026. Deteksi otomatis: **gagal**.
Catatan lapis kedua: bahkan bila pipeline hidup, ET Open tidak memiliki signature untuk pemindaian penuh yang
pelan dan berstatus *filtered* — pola ini hanya dapat ditangkap lewat agregasi jumlah port tujuan per source IP.
Bukti: `docs/redteam/evidence/security-onion-squert-0-event.png`, `security-onion-hasil-pemeriksaan.txt`.

**Analisis** — Scan full-port yang pelan memang tipikal lolos signature ET Open (tidak ada pola SYN
rate tinggi). Yang terverifikasi dari sisi target: PostgreSQL (5432) dan API Go (8080) **tidak terekspos**
(`ss -tlnp` menunjukkan keduanya hanya di 127.0.0.1), konsisten dengan kontrol B.3/B.5. Temuan penting:
**443 terbuka di UFW tetapi tidak ada layanan TLS** → port "diizinkan tapi kosong", bukan permukaan serang nyata.

**Respons** — _[RANCANGAN — belum dieksekusi]_
(a) Custom rule threshold di `/etc/nsm/rules/local.rules`:
`alert tcp $EXTERNAL_NET any -> $HOME_NET any (msg:"PBL-K4 Port Scan Threshold"; flags:S;
threshold: type both, track by_src, count 50, seconds 60; sid:1000001; rev:1;)` — menutup lapis kedua
kegagalan deteksi yang tidak terselesaikan hanya dengan memperbaiki pipeline.
(b) Hapus aturan UFW `443/tcp` yang diizinkan tanpa layanan di belakangnya.
Catatan: bagian (a) harus dijalankan di Monitoring Node, bagian (b) di Target Node — bukan di mesin yang sama.

**Verifikasi** — _[SEBAGIAN — menunggu eksekusi]_
Kontrol B.1 dan B.3 sudah **terverifikasi oleh kegagalan serangan**: hanya 3 port terbuka dari 65.535, dan
PostgreSQL 5432 serta API 8080 berstatus *filtered* sehingga tidak terjangkau dari segmen lab.
Yang belum: setelah rule `sid:1000001` dipasang, ulangi `nmap -Pn -sS -p 1-100 192.168.4.5` dan pastikan
alert *PBL-K4 Port Scan Threshold* muncul di Squert / Elasticsearch. Bila alert tidak muncul, keputusan untuk
tidak menambah rule harus ditegaskan ulang secara eksplisit — bukan dibiarkan ambigu.

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

**Deteksi** — _[SELESAI — hasil: TERDETEKSI DI HOST, TIDAK DI IDS]_ Dari sisi host, fail2ban bekerja:
`Total failed: 8`, `Currently banned: 1`, `Banned IP list: 192.168.4.100`, dengan action `nftables` dan aturan
`tcp dport 2222 ip saddr @addr-set-sshd reject with icmp port-unreachable`. Efek ban terukur dan selektif:
`tcp/2222` menjadi *Connection refused* sementara `tcp/80` dan `tcp/1883` tetap normal.
Dari sisi IDS: **0 alert** di Security Onion meski terjadi 8 kegagalan autentikasi — pola yang justru paling
standar untuk dideteksi. Bahan mentahnya ada di `journalctl -u ssh` (`Invalid user …`) tetapi tidak pernah
sampai ke sensor karena tidak ada rsyslog forwarding. Bukti: `skenario2-serang.txt`,
`skenario2-fail2ban-rule.txt`, `a2-fail2ban-*.txt`.

**Analisis** — Kontrol A.1 (PasswordAuthentication no) **mematikan seluruh jalur brute-force password**:
Hydra berhenti sebelum mengirim percobaan apa pun, sehingga fail2ban tidak punya bahan untuk mem-ban.
Ban baru terpicu ketika penyerang menghasilkan kegagalan **berbasis akun/publickey** (invalid user),
dan itu terjadi pada percobaan ke-6 (setelah 5 kegagalan sesuai `maxretry`).
Artinya pertanyaan panduan ("apakah fail2ban tetap memblokir walau semua percobaan gagal karena
metode auth salah") tidak bisa dijawab oleh Hydra — perlu uji pengganti seperti di atas.

**Respons** — _[RANCANGAN — belum dieksekusi]_ Perketat jail lewat `/etc/fail2ban/jail.d/pbl-kabita.local`:
`maxretry = 4`, `findtime = 300`, `bantime = 3600`, `bantime.increment = true`, lalu
`fail2ban-client reload`. Rasionalnya: jendela 600 detik terlalu singkat untuk penyerang yang gigih, dan
percobaan ke-6 terlambat untuk pola brute force akun. Untuk verifikasi ulang, IP penyerang perlu dilepas dulu
dengan `fail2ban-client set sshd unbanip 192.168.4.100` (ban hanya berlaku untuk `tcp dport 2222`, jadi
skenario lain tidak terhalang).

**Verifikasi** — _[TUNTAS untuk perilaku ban; MENUNGGU untuk target baru]_
Terverifikasi: ban bekerja dan bersifat selektif — `tcp/2222` menjadi *Connection refused* sementara 80 dan
1883 tetap normal. Yang belum: setelah `maxretry` diperketat menjadi 4, ulangi 5 login gagal dan pastikan ban
terjadi pada percobaan ke-4 (bukan ke-6). Bila `bantime.increment` aktif, catat juga durasi blokir bertingkat
pada ban kedua.

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

**Deteksi** — _[SELESAI — hasil: TIDAK TERDETEKSI, tetapi jejak forensik LENGKAP]_ Squert: 0 alert.
Namun `/var/log/nginx/access.log` pada Target Node memuat **1.295 request** dengan User-Agent
`sqlmap/1.10.9#stable`, **1.101** di antaranya berstatus 400, seluruhnya dari 192.168.4.100 dalam 14 detik.
Ini sinyal yang sangat jelas dan datanya benar-benar ada — yang tidak ada adalah mesin yang membacanya:
tidak ada log forwarding ke sensor (D.2) dan tidak ada aturan agregasi "banyak 400 dari satu source IP".
Jadi deteksi bersifat **manual/forensik**, bukan otomatis. Bukti: `skenario3-serang.txt`.

**Analisis** — Tidak ada injeksi karena dua lapis: (1) segmen path `id` divalidasi
`strconv.Atoi` + tolak `n <= 0` di `kambingSubRouter`, sehingga payload ditolak **sebelum** query;
(2) query-nya **parameterized**: `db.Query("SELECT … WHERE kambing_id = $1 …", id)` —
bukan penyambungan string, jadi bahkan bila validasi longgar, nilai tetap dikirim sebagai parameter.
Karena payload tidak pernah sampai ke database, `log_statement` PostgreSQL bersih (tidak ada bukti
kebocoran/kesalahan query). Jadi ini bukan sekadar "filter regex di input" seperti yang dikhawatirkan
panduan.

**Respons** — _[RANCANGAN — belum dieksekusi]_ Karena **tidak ada celah**, responsnya bukan perubahan
kode melainkan dua hal: (a) **dokumentasi** mengapa endpoint aman (validasi `strconv.Atoi` + parameterized
query `$1` — dua lapis independen), dan (b) rsyslog forwarding
`/etc/rsyslog.d/60-pbl-kabita.conf` berisi `*.* @@192.168.4.200:514` di Target Node, agar pola sqlmap
(1.295 request, 1.101 respons 400) tersedia di sensor dan bukan hanya di `access.log` lokal.

**Verifikasi** — _[TUNTAS]_ Verifikasi sudah tuntas karena **kegagalan serangan itu sendiri** adalah
buktinya: 4 payload manual dijawab 400 dan sqlmap menyimpulkan *not injectable* pada 1.295 request, baik
dengan penanda otomatis maupun penanda manual (`1*/riwayat`). Diperkuat oleh ketiadaan bukti di sisi database:
`log_statement` PostgreSQL bersih dan `journalctl -u kabita-backend | grep -Ei 'sql|query error|pq:'` tidak
menghasilkan keluaran — payload tidak pernah sampai ke mesin basis data.
Yang belum: verifikasi bahwa rsyslog forwarding benar-benar mengalirkan log ke sensor
(`tcpdump -ni eth0 'port 514 and host 192.168.4.5' -c 5` di Monitoring Node).

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

**Deteksi** — _[SELESAI — hasil: TERCATAT DI BROKER, TIDAK DI IDS]_ Log Mosquitto mencatat setiap
penolakan sebagai log informasional:
`Client auto-8893AC65-… disconnected, not authorised.` (3 entri dari ketiga upaya) plus
`Client nmap disconnected, not authorised.` — yang terakhir adalah sisa pemindaian Skenario 1 yang menyentuh
port 1883. Artinya **bahan korelasi antar-skenario tersedia dalam satu berkas log**, tetapi tidak ada sistem
yang melakukannya otomatis. Squert: **0 alert**; ET Open tidak mencakup protokol MQTT.
Bukti: `skenario4-serang.txt`.

**Analisis** — Penolakan terjadi di broker lewat `allow_anonymous false` + `password_file`
(`listener 1883 0.0.0.0`), jadi pesan tidak pernah mencapai aplikasi. Untuk skenario ini lapisan
broker sudah cukup: jalur publikasi tertutup total bagi klien tanpa kredensial, dan penolakannya
tercatat di log broker (bahan mentah deteksi, meski belum ada alert otomatis).

**Respons** — _[RANCANGAN — belum dieksekusi]_ Alert eksplisit untuk `connect_status` gagal berulang
dari satu source IP (Zeek script atau rule Suricata), karena default ET Open tidak menutup MQTT. Diperkuat
oleh respons Skenario 5: begitu `acl_file` diterapkan (C.4a), publish ke topik liar ditolak broker sehingga
tidak lagi bergantung pada pembacaan log saja.

**Verifikasi** — _[TUNTAS]_ Verifikasi tuntas: ketiga upaya tanpa kredensial ditolak broker
`Connection Refused: not authorised` (exit 5), dan `select count(*) from bobot_log` tetap **60** — tidak ada
data yang masuk maupun terbaca. Penolakan hanya terlihat di log broker, bukan sebagai alert IDS, dan itu
dicatat sebagai temuan (bukan sebagai keberhasilan deteksi).

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

**Deteksi** — _[SELESAI — hasil: TIDAK TERDETEKSI]_ Squert: 0 alert. Satu-satunya jejak adalah log
informasional backend (`mqtt: reading tersimpan — … 299.0 kg`) yang tidak menandai apa pun sebagai anomali.
Tidak ada mekanisme (log, alert, atau karantina) yang membedakan nilai wajar dari nilai mustahil.
Bukti: `skenario5-serang.txt`, `skenario5-hasil.png`.

**Analisis** — Validasi yang ADA: `processReading` memeriksa format `tag_rfid` (regex) dan rentang
`0 < berat_kg <= 300` — jadi anggapan panduan bahwa "hanya tipe data yang divalidasi" **salah**.
Yang TIDAK ADA: kewajaran fisik nilai berat (kambing 299 kg diterima), penandaan/pemisahan data
anomali, rate limit publish, dan otorisasi topic per-user. Karena kredensialnya valid, autentikasi
tidak dapat dijadikan andalan; satu-satunya pertahanan untuk kasus *credential theft* adalah validasi
nilai di aplikasi + pembatasan hak kredensial (topic ACL, rate limit).

**Respons** — _[RANCANGAN — belum dieksekusi, kandidat kontrol C.4]_
(a) **C.4a — ACL topik:** `/etc/mosquitto/acl` berisi `user kabita_device` / `topic write kabita/readings` /
`topic read kabita/readings`, diaktifkan dengan `acl_file /etc/mosquitto/acl` di `mosquitto.conf`.
(b) **C.4b — validasi kewajaran nilai:** perketat `berat_kg` ke rentang biologis (mis. 5–150 kg) dan/atau
tandai nilai di luar rentang wajar sebagai anomali alih-alih menolak mentah.
(c) **C.4c — rate limit publish** per klien/topik.
Ditambah **containment**: rotasi kredensial `kabita_device` (24 byte base64 via `mosquitto_passwd`),
sinkronisasi `MQTT_PASSWORD` di `/opt/kabita-backend/.env`, restart `mosquitto` + `kabita-backend`.
Bukti before/after yang harus disimpan: `docs/blueteam/evidence/skenario5-respons-*.txt`.

**Verifikasi** — _[BELUM — menunggu eksekusi mitigasi]_ Kriteria lulus yang harus dibuktikan:
(1) publish `299` dan `9999` ditolak atau ditandai; (2) publish `21,5` tetap diterima — tidak boleh ada
false positive yang memutus operasi normal; (3) publish dengan **kredensial lama** ditolak broker setelah
rotasi; (4) publish ke `kabita/sensor-liar` ditolak ACL; (5) `select count(*) from bobot_log` kembali **60**
setelah sanitasi 23 baris palsu (id 61–83) yang ID-nya dicatat lebih dulu ke berkas bukti.

---

## Catatan lintas-skenario (perlu tindak lanjut)

1. **Ban fail2ban sudah tidak membawa efek.** Saat eksekusi ulang 4 November 2026, ban 600 detik memang
   aktif untuk IP `192.168.4.100` (`addr-set-sshd`), tetapi hanya pada `tcp dport 2222` sehingga tidak
   menghalangi Skenario 3–5. Ban sudah habis dengan sendirinya; untuk uji ulang Skenario 2 penyerang
   hanya perlu memastikan IP-nya tidak sedang terblokir.
2. **Data uji Skenario 5 masih ada di `bobot_log`** (23 baris palsu untuk tag `RFID-002`).
   Itu bukti dampak; bersihkan setelah Blue Team selesai mendokumentasikan, dengan
   `DELETE FROM bobot_log WHERE id IN (…)` (catat id-nya di evidence sebelum dihapus).
3. **Kredensial MQTT disensor** di berkas evidence (`***kredensial-lab-disensor***`).
4. Tahap Deteksi wajib dijalankan **pada rentang waktu yang sama** dengan serangan (timestamp UTC
   sudah dicantumkan di tiap subbagian di atas) — bukan rekonstruksi dari log sesudahnya.

5. **Akar kegagalan deteksi sudah diidentifikasi dan wajib diperbaiki lebih dulu.** Squert mencatat 0 event
   untuk seluruh rentang hari eksekusi, dan penyebabnya ada di sensor: proses `snort` tidak berjalan,
   `output unified2` memakai nama relatif (`filename snort.unified2`) sehingga berkas tidak ditulis ke
   `/nsm/sensor_data/seconion-eth0/snort-1/`, dan `barnyard2` membaca direktori `seconion-import/snort-1`
   alih-alih `seconion-eth0/snort-1`. Selama tiga hal ini belum diperbaiki, setiap penilaian Deteksi untuk
   skenario berikutnya akan tetap bernilai nol — bukan karena serangannya halus, tetapi karena tidak ada
   mesin yang mengevaluasinya. Perbaikan berada di ranah Blue Team dan menjadi **prasyarat** seluruh tahap
   Deteksi di atas. Detail: `docs/redteam/evidence/security-onion-hasil-pemeriksaan.txt`.

6. **Konsistensi dengan Incident Report.** Log ini adalah bahan mentah; sintesisnya (klasifikasi insiden,
   dampak fungsional/informasi per skenario, pemetaan kontrol efektif vs yang masih perlu diperkuat, dan
   rekomendasi lanjutan) berada di `docs/final/incident_report.pdf`. Angka di kedua dokumen berasal dari
   eksekusi yang sama (4 November 2026, 14:55–15:20 UTC); bila ada perbedaan, Incident Report yang berlaku.
