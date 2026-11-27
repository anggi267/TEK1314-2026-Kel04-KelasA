# Hardening Checklist — Target Node (KABITA Replica)

Kelompok 4 — baseline **2026-10-23**, diperbarui **Fase 3 (Minggu 14–15)** setelah eksekusi kelima skenario
pada 4 November 2026.

## Status akhir

**8 dari 8 kontrol baseline (A.1–C.3) selesai** dan seluruhnya sudah diuji dengan serangan nyata.
**4 di antaranya terbukti menahan serangan** dari sisi penyerang; sisanya terbukti tidak relevan dengan
skenario yang dijalankan. Dari kelima skenario, satu berhasil dieksploitasi sehingga muncul **kandidat
kontrol baru C.4** dan **dua kebutuhan D.1–D.2** yang belum dieksekusi (lihat bagian bawah).

## Kontrol baseline (A–C) — selesai dan teruji

| # | Kategori | Kontrol | Status | Teruji oleh | Bukti |
|---|---|---|---|---|---|
| A.1 | Access & Authentication | SSH key-based auth, `PermitRootLogin no`, `PasswordAuthentication no` | Selesai | **Skenario 2** — Hydra berhenti sebelum 1 percobaan (`method reply 4`) | `evidence/a1-sshd_config-after.txt`, `a1-sshd_config-effective.txt`, `a1-login-password-rejected.txt` |
| A.2 | Access & Authentication | Port SSH custom (2222) + fail2ban rate-limit (maxretry 5 / findtime 600 s / bantime 600 s, action nftables) | Selesai | **Skenario 2** — 8 kegagalan → ban selektif pada `tcp/2222` sementara 80 & 1883 tetap normal | `evidence/a2-fail2ban-status.txt`, `a2-fail2ban-ban-attacker.txt`, `redteam/evidence/skenario2-fail2ban-rule.txt` |
| B.1 | Service & Attack Surface | UFW whitelist port 2222/80/443/1883, default deny — 1883 untuk MQTT broker, sengaja dibuka ke LAN tapi wajib auth (bukan anonymous) | Selesai | **Skenario 1** — hanya 3 port terbuka dari 65.535 | `evidence/b1-ufw-status.txt` |
| B.2 | Service & Attack Surface | Nonaktifkan service tak terpakai (ModemManager) + unattended-upgrades aktif | Selesai | Tidak diuji langsung oleh skenario (tidak ada vektor yang menyentuhnya) | `evidence/b2-services-after.txt`, `b2-unattended-upgrades.txt` |
| B.3 | Service & Attack Surface | PostgreSQL `listen_addresses=localhost`, akun default bersih | Selesai | **Skenario 1** — 5432 dan 8080 berstatus *filtered*, tidak terjangkau dari segmen lab | `evidence/b3-ss-tlnp.txt`, `b3-pg-roles.txt` |
| C.1 | Data & Application | Kredensial DB via `.env` (mode 600), tidak hardcode | Selesai | Tidak diuji langsung — tetapi **menjadi jalur masuk Skenario 5** (kredensial MQTT dibaca dari berkas ini) | `evidence/c1-env-permissions.txt` |
| C.2 | Data & Application | Validasi input (`tag_rfid`, `berat_kg`, `:id`) + parameterized query | Selesai | **Skenario 3** — 4 payload manual → 400; 1.295 request sqlmap → *not injectable*; `log_statement` bersih | `evidence/c2-sqli-probe-400.txt`, `redteam/evidence/skenario3-serang.txt` |
| C.3 | Data & Application | Least-privilege DB user + logging query mencurigakan | Selesai | **Skenario 4** — 3 upaya anonim ditolak `not authorised`; `bobot_log` tidak bertambah | `evidence/b3-pg-roles.txt`, `c3-log_statement.txt`, `c3-log-sample.txt` |

## Kandidat kontrol baru (C.4) — C.4a sudah dieksekusi 26 Nov 2026

Muncul dari Skenario 5, satu-satunya jalur yang berhasil dieksploitasi. Ketiga butir di bawah menutup
**asumsi tersembunyi** bahwa kredensial selalu tetap rahasia — asumsi yang gugur saat kredensial `kabita_device`
diambil dari `/opt/kabita-backend/.env`.

| # | Kontrol | Menutup | Status |
|---|---|---|---|
| C.4a | **ACL topik Mosquitto** — `acl_file /etc/mosquitto/acl` (225 byte) berisi blok `user kabita_device` + `topic readwrite kabita/readings`, dan blok `user kabita_backend` + `topic read kabita/readings` (user ini **belum ada** di `/etc/mosquitto/passwd`, jadi bloknya masih no-op) | Publish ke topik yang tidak dipakai aplikasi | **Selesai — 26 Nov 2026 03:22 UTC, diperbaiki 27 Nov 2026.** `acl_file` dirujuk di `mosquitto.conf:14`; kepemilikan `mosquitto:mosquitto` mode 640. Verifikasi: publish ke `kabita/sensor-liar` dengan kredensial **sah** → `Warning: Publish 1 failed: Not authorized` (MQTT5, QoS 1) — `evidence/c4a-acl-isi.png`, `c4a-verifikasi-akhir.png` |
| C.4b | **Validasi kewajaran nilai** — perketat `berat_kg` ke rentang biologis wajar (mis. 5–150 kg) dan/atau tandai nilai di luar kewajaran sebagai anomali alih-alih menerimanya sebagai data sah | Tersimpannya 299 kg dan 0,1 kg sebagai bobot kambing yang "sah" | Belum. Dasar: kode `processReading` masih `0 < berat_kg ≤ 300` (`c2-validasi-kode.png`) dan jalur `kabita/readings` terbukti masih menerima publish pasca-ACL (`c4a-verifikasi-akhir.png`, publish 9999 sampai ke backend). Baris `id 85`/`86` dari 26 Nov **02:51 UTC** masuk **sebelum** ACL dipasang 03:22 — jadi itu bukan bukti pasca-mitigasi |
| C.4c | **Pembatasan laju publish** per klien/topik | 20 pesan terkirim dalam < 1 detik tanpa penolakan | Belum |

Ditambah satu tindakan **containment** yang bersifat situasional (bukan kontrol permanen): rotasi kredensial
`kabita_device` ke nilai acak kuat 24 byte base64, sinkronisasi `MQTT_PASSWORD` di `.env`, lalu restart
`mosquitto` dan `kabita-backend`. **Sudah dijalankan 26 November 2026 03:22 UTC** — `/etc/mosquitto/passwd`
bertanggal 03:22:01, backend restart 03:23:37, dan kredensial lama kini ditolak `not authorised`.

**Bug C.4a yang ditemukan dan diperbaiki 27 November 2026.** Aturan awal hanya memberi
`topic write kabita/readings` kepada `kabita_device`, padahal backend memakai **kredensial yang sama**
(`MQTT_USER=kabita_device` di `.env`) untuk *subscribe*. Akibatnya ACL memutus subscriber-nya sendiri:
publish berhasil (`exit 0`) tetapi tidak ada `reading` yang diproses — `journalctl -u kabita-backend`
kosong, tidak ada galat apa pun. Diperbaiki menjadi `topic readwrite kabita/readings`; ingest pulih
(publish `berat_kg: 9999` → backend mencatat `mqtt: gagal proses reading … invalid berat_kg`).
Pemisahan hak device vs backend belum dilakukan — perlu user `kabita_backend` di `/etc/mosquitto/passwd`
dan `MQTT_USER` di `.env` diganti; selama belum, blok `user kabita_backend` di ACL tidak berefek.

**Batas keberhasilan C.4a:** ACL hanya menutup jalur topik liar. Jalur `kabita/readings` tetap menerima nilai
mustahil sampai C.4b dieksekusi — jadi skenario 5 belum tertutup seluruhnya.

> **Catatan metodologi verifikasi ACL.** `mosquitto_pub` tetap keluar `exit 0` walaupun broker menolak.
> Dengan MQTT 3.1.1 pesan dibuang tanpa pesan galat; dengan `-V mqttv5 -q 1` barulah muncul
> `Warning: Publish 1 failed: Not authorized.` Karena itu bukti penolakan ACL tidak boleh berhenti pada
> exit code — lihat `evidence/c4a-verifikasi-akhir.png`.

## Bukti screenshot per kontrol (Bagian VIII panduan)

Bukti diambil langsung dari console VM Target Node (tty1) pada 27 November 2026, perintah terlihat
berbarengan dengan keluarannya. Berkas `.txt` di folder yang sama tetap dipertahankan sebagai bukti
teks asli dari eksekusi Oktober 2026.

| Kontrol | Screenshot | Isi |
|---|---|---|
| A.1 | `evidence/before A. Access & Authentication.jpeg` | kondisi `sshd_config` sebelum hardening |
| A.1 | `evidence/a1-sshd_config-after.png` | `Port 2222`, `PermitRootLogin no`, `PasswordAuthentication no`, `PubkeyAuthentication yes` |
| A.1 | `evidence/a1-login-password-rejected.png` | percobaan login dengan password → `Permission denied`, `exit=255` |
| A.2 | `evidence/a2-fail2ban-jail.png` | `fail2ban-client status sshd` + isi `jail.local` (port 2222, maxretry 5, bantime 600) |
| B.1 | `evidence/b1-ufw-status.png` | `ufw status verbose`: default deny incoming, 2222/80/443/1883 allow, 22 deny |
| B.2 | `evidence/b2-services-after.png` | jumlah service berjalan + `ModemManager`/`unattended-upgrades` |
| B.2 | `evidence/b2-unattended-upgrades.png` | `20auto-upgrades`: Update-Package-Lists & Unattended-Upgrade `"1"` |
| B.3 | `evidence/b3-ss-tlnp.png` | `ss -tlnp`: 5432 hanya `127.0.0.1`, 8080 hanya loopback |
| C.1 | `evidence/c1-env-permissions.png` | `.env` mode `600 kabita:kabita` + potongan `os.Getenv(...)` di `main.go` |
| C.2 | `evidence/c2-validasi-kode.png` | regex `tag_rfid` + rentang `0 < berat_kg ≤ 300` di `processReading` |
| C.3 | `evidence/c3-log-statement.png` | `SHOW log_statement` → `mod` |
| C.3 | `evidence/c3-pg-roles.png` | `pg_roles`: `kabita_app` & `kabita_device` bukan superuser |
| C.4a | `evidence/c4a-acl-isi.png` | isi `/etc/mosquitto/acl` + `acl_file` di `mosquitto.conf:14` |
| C.4a | `evidence/c4a-verifikasi-akhir.png` | publish ke `kabita/readings` diterima backend; publish ke `kabita/sensor-liar` → `Not authorized` |

## Kebutuhan visibilitas (D.1–D.2) — prasyarat, belum dieksekusi

Bukan "kontrol pengerasan" dalam arti A/B/C, tetapi **kondisi agar seluruh penilaian deteksi punya arti**.
Selama keduanya belum terpenuhi, setiap skenario serangan akan tetap bernilai 0 alert.

| # | Kebutuhan | Kondisi saat eksekusi 4 Nov 2026 | Status |
|---|---|---|---|
| D.1 | **Pipeline IDS** — proses `snort` hidup dengan `-i eth0`, `output unified2` memakai path absolut `/nsm/sensor_data/seconion-eth0/snort-1/`, dan `barnyard2` membaca direktori sensor yang sama | Proses `snort` tidak berjalan; `snort.unified2` 0 byte bertanggal 19 Jun 2020; 0 berkas baru sejak 1 Nov 2026; `barnyard2` membaca `seconion-import/snort-1` | Belum |
| D.2 | **Log forwarding** — `/etc/rsyslog.d/60-pbl-kabita.conf` berisi `*.* @@192.168.4.200:514` di Target Node | Tidak ada forwarding; log aplikasi, Nginx, Mosquitto, dan PostgreSQL hanya tersimpan lokal di Target Node | Belum |

## Catatan

> **MQTT (1883/tcp) terekspos ke jaringan lab secara sengaja** — alat/simulator perlu publish dari luar. Beda
> dari PostgreSQL (5432, loopback) dan API (8080, loopback) yang tertutup total. Mitigasi yang berlaku saat ini:
> `allow_anonymous false` + `password_file`, **bukan** isolasi jaringan. Konsekuensi yang terbukti di Skenario 5:
> autentikasi adalah **satu-satunya** lapisan pertahanan jalur ini, sehingga kebocoran kredensial berarti
> hilangnya seluruh kendali atas integritas data sensor. Inilah alasan C.4a–C.4c menjadi prioritas.

> **Port 443 diizinkan UFW tetapi tidak ada layanan TLS di belakangnya** (Skenario 1: `443/closed`). Ini
> "port diizinkan tapi kosong" — bukan permukaan serang nyata, tetapi kandidat pembersihan aturan.

> **Kontrol yang sengaja tidak diubah:** A.1, C.2, dan C.3 terbukti efektif dan tidak disentuh. Menambah kontrol
> pada lapisan yang sudah bekerja hanya menambah biaya operasional tanpa mengurangi risiko — prinsipnya adalah
> memperbaiki lapisan yang gagal, bukan menumpuk kontrol pada lapisan yang lulus.
