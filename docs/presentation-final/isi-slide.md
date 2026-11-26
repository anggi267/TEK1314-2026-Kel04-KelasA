# Isi Tiap Slide — Presentasi Final SOC KABITA (Kelompok 4)

Peta isi `docs/presentation-final/slides.pdf` (12 slide, PDF landscape).
Acuan: **Bagian VII Kisi-Kisi Presentasi Final**, `Panduan PBL Minggu14-15 Final_Presentation.pdf`.

Alokasi waktu presentasi **15–20 menit** (di luar tanya jawab 5–10 menit). Rencana di bawah total **≈ 18 menit**,
menyisakan ruang untuk pemutaran video yang melewati batas.

---

## Kepatuhan terhadap kisi-kisi

| Kisi-kisi Bagian VII | Wajib | Slide | Terpenuhi |
| :--- | :--- | :--- | :--- |
| (pembuka — tidak diwajibkan) | — | 1 | — |
| 1. Ringkasan Proyek & Perjalanan Fase 1–3 | 1 slide | 2 | ya |
| 2. Ringkasan Eksekutif Incident Report | 1–2 slide | 3, 4 | ya |
| 3. Status Akhir Hardening A/B/C | 1 slide | 5 | ya |
| 4. Live Demo / Pemutaran Video Demo | 1 siklus penuh | 6 | ya |
| 5. Hasil Deteksi & Mitigasi Seluruh Skenario | 2–3 slide | 7, 8, 9 | ya |
| 6. Kendala & Pembelajaran | 1 slide | 10 | ya |
| 7. Rekomendasi Lanjutan Sistem IoT Asli | 1 slide | 11 | ya |
| (penutup — mendukung kriteria artefak 15%) | — | 12 | — |

Total **12 slide**, tepat pada batas atas "maksimal 10–12 slide". Format PDF, bukan `.pptx` — sesuai Bagian IX.

> **Satu catatan penyimpangan yang harus disebut, bukan disembunyikan:** kisi-kisi butir 5 berbunyi
> *"tabel Tahap 1–5 untuk ketiga skenario attack plan"*. Kelompok ini menjalankan **lima** skenario, bukan tiga,
> sehingga butir 5 memakai 3 slide (bukan 2) agar kelimanya tertampung. Ini perlu disebut di awal presentasi
> supaya tidak terlihat seperti kelebihan slide.

---

## Slide 1 — Pembuka

- **Kategori:** pembuka, di luar kisi-kisi
- **Durasi:** 0:20
- **Judul di layar:** Membuktikan Siklus Pertahanan SOC KABITA
- **Isi:**
  - Kicker: *PBL TEK1314 Keamanan Siber · Kelas A · Kelompok 4 · Fase 3*
  - Subjudul: simulasi lima skenario serangan terhadap replika sistem IoT KABITA — dari insiden terjadi,
    terdeteksi (atau tidak), dimitigasi, hingga diverifikasi
  - Empat nama + NIM + peran: Olan (Lead), Anggi (Blue Team), Raka (Red Team), Zidan (Red Team)
  - Cap: *Final Presentation · Minggu 14–15 · Repositori github.com/anggi267/TEK1314-2026-Kel04-KelasA*
- **Yang diucapkan:** perkenalan tim dan satu kalimat tesis — "kami akan menunjukkan siklus yang bisa
  dibuktikan, termasuk bagian yang gagal."
- **Alasan desain:** peran ditulis di slide sejak detik pertama karena kriteria penilaian *Kerja Sama &
  Penguasaan Materi* (15%) menilai pembagian peran saat presentasi.

---

## Slide 2 — Ringkasan Proyek: perjalanan Fase 1–3

- **Kategori:** kisi-kisi butir 1 (1 slide)
- **Durasi:** 1:30
- **Judul di layar:** Perjalanan Fase 1–3 dalam satu kalimat per fase
- **Isi — tiga kartu sejajar:**
  - **Fase 1 · Minggu 1–9 — Bangun & Keraskan.** Replika backend KABITA di tiga node (Target Ubuntu,
    Attacker Kali, Monitoring Onion) pada `192.168.4.0/24`. Tech stack asli dipetakan: Golang, PostgreSQL,
    MQTT. Delapan kontrol A.1–C.3 dieksekusi dengan bukti before/after.
    *Keluaran: topologi, IP plan, tech stack declaration, hardening checklist.*
  - **Fase 2 · Minggu 10–13 — Serang & Tahan.** Lima skenario dieksekusi 4 November 2026 (14:55–15:20 UTC)
    terhadap Target Node yang **sudah ter-harden**. Purple Team Loop lima tahap dijalankan.
    *Keluaran: attack plan, purple-team-log, bukti per skenario, laporan Red Team.*
  - **Fase 3 · Minggu 14–15 — Tutup Siklus.** Sintesis menjadi Incident Report NIST SP 800-61r2, slide ini,
    video demo, artefak GitHub yang dapat dibuka dosen.
- **Garis bawah — "yang berubah dari rencana ke kenyataan":** panduan memperkirakan tiga skenario,
  kenyataannya lima. Panduan memperkirakan port 443 terbuka, kenyataannya *closed*. Panduan memperkirakan
  validasi data hanya tipe, kenyataannya ada validasi rentang.
- **Yang diucapkan:** "kami tidak mengulang detail Minggu 4 dan 9 — ini hanya peta jalan. Yang perlu
  diperhatikan adalah baris terakhir: tiga asumsi panduan tidak terbukti di lapangan, dan semuanya kami catat."

---

## Slide 3 — Ringkasan Eksekutif: apa yang terjadi

- **Kategori:** kisi-kisi butir 2 (slide pertama dari 2)
- **Durasi:** 1:45
- **Judul di layar:** Apa yang terjadi, dan seberapa jauh sistem bertahan
- **Isi — dua angka besar di kiri:**
  - **4 dari 5** — skenario gagal total, dibuktikan dari sisi penyerang
  - **0 alert** — Security Onion mencatat nol event selama 25 menit penyerangan
- **Isi — kanan, dua blok:**
  - *Empat skenario tertahan oleh kontrol baseline:* SSH (Hydra berhenti sebelum satu percobaan pun —
    `PasswordAuthentication no` menolak di level protokol) · SQL injection (4 payload → 400; 1.295 request
    sqlmap → *not injectable*; `log_statement` bersih) · MQTT anonim (3 upaya ditolak `not authorised`) ·
    Reconnaissance (3 port terbuka dari 65.535)
  - *Satu skenario berhasil, dua kegagalan sistemik:* MQTT kredensial bocor → 23 baris data palsu masuk
    (299 kg dan 0,1 kg sebagai bobot "sah") · visibilitas nol (pipeline tidak pernah menulis satu event) ·
    asumsi tersembunyi (jalur MQTT hanya punya *satu* lapis pertahanan)
- **Yang diucapkan:** angka dulu, baru cerita. Dua angka ini merangkum seluruh proyek.
- **Pertanyaan yang harus siap:** "kalau 4 dari 5 gagal, apakah sistem kalian aman?" → tidak; aman pada empat
  jalur, **buta pada semuanya**, dan satu jalur terbuka.

---

## Slide 4 — Ringkasan Eksekutif: peta hasil kelima skenario

- **Kategori:** kisi-kisi butir 2 (slide kedua dari 2)
- **Durasi:** 1:45
- **Judul di layar:** Peta hasil kelima skenario terhadap kontrol yang diuji
- **Isi — satu tabel enam baris:** kolom Skenario · Kontrol · Hasil terukur · Dampak · Status
  | Skenario | Kontrol | Hasil terukur | Dampak | Status |
  | :--- | :--- | :--- | :--- | :--- |
  | 1 Recon (nmap) | B.1 UFW, B.3 isolasi | 80/1883/2222 terbuka, 443 *closed*, 22/5432/8080 *filtered*, 65.531 filtered | None | Tertahan |
  | 2 Brute force SSH | A.1 key-only, A.2 fail2ban | Hydra `method reply 4` → 0 percobaan; uji pengganti 8 login gagal → ban 600 s selektif tcp/2222 | None | Tertahan |
  | 3 SQL injection | C.2 validasi + parameterized | 4/4 payload → 400; sqlmap 1.295 request → *not injectable*; 1.101 respons 400 | None | Tertahan |
  | 4 MQTT anonim | C.3 `allow_anonymous false` | 3/3 → `not authorised` (exit 5); broker mencatat penolakan | None | Tertahan |
  | 5 MQTT kredensial bocor | C.6 kredensial, C.5 kewajaran | 9999 ditolak; **299 kg & 0,1 kg tersimpan**; topik liar diterima; 20 pesan < 1 s; **60 → 83 baris** | **Integritas data** (sedang) | **Berhasil** |
  | Lintas · deteksi | D.1 Snort, D.2 log fwd | Squert 0 event seluruh 4 Nov, tanpa filter objek/sensor; `snort.unified2` 0 byte sejak 2020 | **Kehilangan visibilitas** | **Gagal** |
- **Garis bawah — cara membaca tabel:**
  - "tertahan" = serangan gagal pada percobaan pertama terhadap sistem yang sudah ter-harden, dibuktikan dari
    sisi penyerang, bukan dari checklist
  - "gagal" pada baris deteksi berlaku untuk **kelima** skenario sekaligus — satu pipeline mati membuat semua
    penilaian deteksi bernilai nol
- **Yang diucapkan:** baca tabel ini baris per baris saja, jangan dibacakan seluruhnya; berhenti di baris 5 dan 6.
- **Catatan data:** angka "60 → 83" adalah pengukuran saat serangan 4 November. Setelah sanitasi, tabel bersih
  14 baris. Bila dosen menanyakan angka absolut, jawab dengan **delta +23 baris dalam satu run**, dan sebut
  bahwa 60 sudah tercemar dua gelombang uji sebelumnya.

---

## Slide 5 — Status akhir hardening

- **Kategori:** kisi-kisi butir 3 (1 slide)
- **Durasi:** 1:15
- **Judul di layar:** Delapan kontrol A/B/C — status akhir sebelum dan sesudah Fase 2
- **Isi — kiri, tabel 8 kontrol (kolom: # · Kontrol · Sebelum · Akhir):**
  - A.1 SSH key-only, `PermitRootLogin no`, `PasswordAuthentication no` — Terbuka → **Selesai**
  - A.2 SSH port 2222 + fail2ban (maxretry 5 / bantime 600 s, action nftables) — Default 22 → **Selesai**
  - B.1 UFW default deny + whitelist 2222/80/443/1883 — Semua terbuka → **Selesai**
  - B.2 Service tak terpakai nonaktif + `unattended-upgrades` — Sebagian → **Selesai**
  - B.3 PostgreSQL `listen_addresses=localhost`, akun default bersih — 0.0.0.0 → **Selesai**
  - C.1 Kredensial via `.env` mode 600 — Hardcode → **Selesai**
  - C.2 Validasi input + parameterized query — Sebagian → **Selesai**
  - C.3 Least-privilege DB user + `log_statement` — Superuser → **Selesai**
- **Isi — kanan, dua kartu:**
  - *Terbukti efektif diuji serangan:* **A.1 · A.2 · B.1 · B.3 · C.3** — dibuktikan oleh kegagalan nyata:
    Hydra berhenti sebelum 1 percobaan, ban selektif pada tcp/2222, hanya 3 port terbuka dari 65.535, DB tidak
    terjangkau, broker menolak klien anonim
  - *Kontrol baru (C.4) — belum dieksekusi:* **a.** `acl_file` Mosquitto, batasi `kabita_device` hanya ke
    `kabita/readings` · **b.** validasi kewajaran bobot (5–150 kg) + penandaan anomali · **c.** rate limit
    publish per klien · ditambah **D.1** pipeline Snort/Barnyard2 dan **D.2** log forwarding Target Node → :514
- **Yang diucapkan:** "8/8 selesai" bukan prestasi dengan sendirinya — 5 dari 8 terbukti menahan serangan nyata,
  3 sisanya baru terbukti secara konfigurasi. C.4 masih rancangan dan kami sebut apa adanya.
- **Pertanyaan yang harus siap:** "kenapa C.4 belum dikerjakan?" → karena Fase 2 berakhir pada pengujian;
  perbaikan C.4 masuk lingkup Fase 3, dan buktinya ada di Incident Report halaman 14–15.

---

## Slide 6 — Demo Purple Team Loop

- **Kategori:** kisi-kisi butir 4 (satu siklus penuh)
- **Durasi:** 3:00 (potongan video ±1:30 + narasi ±1:30)
- **Judul di layar:** Demo: satu siklus penuh pada jalur yang benar-benar gagal
- **Isi — pengantar:** video menunjukkan siklus lengkap pada **Skenario 5**, satu-satunya yang berhasil
  dieksploitasi. Memilih jalur yang gagal, bukan yang sudah aman, agar siklus serangan → deteksi → mitigasi →
  verifikasi terlihat utuh.
- **Isi — alur lima tahap (kartu berderet):**
  1. **Serang** — kredensial `kabita_device` dibaca dari `.env`; publish 9999 (ditolak), 299 kg, 0,1 kg, topik
     liar, lalu 20 pesan beruntun
  2. **Deteksi** — Squert diperiksa: **0 alert**; penyebab ditelusuri ke sensor (snort mati, unified2 0 byte);
     jejak alternatif di `mosquitto.log` dan log backend
  3. **Analisis** — validasi rentang ada (0–300) tetapi bukan kewajaran biologis; tidak ada ACL topik, tidak ada
     rate limit; `bobot_log` 60 → 83 baris
  4. **Mitigasi** — rotasi kredensial 24 byte base64 + sinkronisasi `.env`; rancangan ACL topik dan validasi
     kewajaran (C.4a/b/c)
  5. **Verifikasi** — serangan diulang: kredensial lama ditolak, topik liar ditolak ACL, nilai 299 ditandai
     anomali; sanitasi data palsu
- **Isi — dua kartu bawah:**
  - *Yang ditampilkan di layar:* nama host dan IP sesuai IP plan — `PBL-K4-01-Target-KABITA 192.168.4.5`,
    `PBL-K4-02-Attacker-Kali 192.168.4.100`, `PBL-K4-03-Monitoring-Onion 192.168.4.200`
  - *Yang tidak diklaim:* tahap mitigasi yang belum dieksekusi ditampilkan sebagai rancangan dengan kriteria
    lulus eksplisit, bukan sebagai hasil yang sudah tercapai
- **Yang diucapkan:** sebelum memutar video, sebut urutan lima tahap supaya dosen bisa mengikuti; setelah video,
  satu kalimat penutup — "siklus tertutup pada empat tahap, dan bagian deteksi yang tidak tertutup justru jadi
  temuan utama."
- **Catatan penyelarasan:** slide ini menyebut "sanitasi 23 baris"; kenyataan setelah 23 November 2026 adalah
  **77 → 14 baris**. Berkas buktinya `docs/blueteam/evidence/skenario5-sanitasi-database.txt`.

---

## Slide 7 — Hasil deteksi & mitigasi: Skenario 1–2

- **Kategori:** kisi-kisi butir 5 (slide 1 dari 3)
- **Durasi:** 2:00
- **Judul di layar:** Skenario 1–2: permukaan serang dan brute force
- **Kiri — Skenario 1 Reconnaissance (nmap):**
  - Kutipan layar: `80/open (nginx 1.28.3)`, `443/closed`, `1883/open (mqtt)`, `2222/open (OpenSSH 10.2p1)`,
    `Ignored State: filtered (65531)`
  - Tabel tahap: Serang (scanned in 133–144 s dari 192.168.4.100) · Deteksi **0 alert, dua lapis kegagalan** ·
    Analisis (Snort mati; ET Open tidak punya signature untuk scan pelan & *filtered* — bahkan bila pipeline
    hidup, pola ini lolos; deteksi harus dari **agregasi**, bukan konten) · Respons (rule threshold >50 SYN/60 s
    per src_ip, `sid:1000001`, + tutup UFW 443) · Verifikasi **Menunggu** (rule dipasang → alert Squert)
- **Kanan — Skenario 2 Brute force SSH:**
  - Kutipan layar: `[ERROR] target ssh://192.168.4.5:2222/ does not support password authentication
    (method reply 4)`, `fail2ban: Total failed 8 · Currently banned 1 · 192.168.4.100`
  - Tabel tahap: Serang (Hydra **0 percobaan**; uji pengganti 8 login akun tak dikenal) · Deteksi host
    **Terdeteksi** fail2ban, ban selektif tcp/2222 · Deteksi IDS **0 alert** meski 8 kegagalan auth · Analisis
    (key-only membuat jalur tebak-sandi **tidak ada**, sehingga fail2ban tak punya bahan; pertanyaan "fail2ban
    saat password salah" **tidak dapat dijawab Hydra**) · Respons (perketat `maxretry=4`, `bantime=3600` +
    `bantime.increment`) · Verifikasi **Menunggu** (ban pada percobaan ke-4)
- **Yang diucapkan:** dua skenario ini menahan serangan pada percobaan pertama, tetapi keduanya juga lolos dari
  deteksi IDS. Tertahan bukan berarti terdeteksi.

---

## Slide 8 — Hasil deteksi & mitigasi: Skenario 3–4

- **Kategori:** kisi-kisi butir 5 (slide 2 dari 3)
- **Durasi:** 2:00
- **Judul di layar:** Skenario 3–4: aplikasi web dan broker IoT
- **Kiri — Skenario 3 SQL injection:**
  - Tabel tahap: Serang (4 payload manual → **400**; sqlmap 1.295 request → *not injectable*) · Deteksi
    **0 alert**, tetapi jejak **lengkap** di `access.log` (1.295 UA sqlmap, 1.101 respons 400) · Analisis
    (**dua lapis independen:** `strconv.Atoi` menolak sebelum kueri; parameterized query `$1`;
    `log_statement` PostgreSQL bersih = payload tidak pernah sampai DB) · Respons (bukan perubahan kode —
    **dokumentasi** mengapa endpoint aman, plus rsyslog forwarding D.2) · Verifikasi **Tuntas**
  - Koreksi penting: 12 respons 200 yang tercatat semuanya URL bersih yang ditambahi query string karangan
    sqlmap — bukan bukti injeksi. Menyimpulkan "lolos" dari satu angka 200 adalah kesalahan pembacaan yang
    sengaja dihindari
- **Kanan — Skenario 4 MQTT tanpa kredensial:**
  - Tabel tahap: Serang (publish anonim, subscribe anonim, user/pass karangan → 3/3 ditolak) · Deteksi broker
    **Tercatat** (4 entri `not authorised`, tanpa alert) · Deteksi IDS **0 alert** (ET Open tidak mencakup
    MQTT) · Analisis (TCP handshake **diterima** karena port sengaja terbuka, penolakan di level broker/CONNACK;
    tidak ada pesan mencapai `processReading`) · Respons (alert eksplisit untuk `connect_status` gagal berulang
    dari satu IP) · Verifikasi **Tuntas** (`bobot_log` tidak bertambah)
  - Korelasi yang mungkin: log broker memuat client-id `nmap` — sisa Skenario 1. Bahan korelasi antar-skenario
    *ada* dalam satu berkas log, tetapi tidak ada sistem yang melakukannya otomatis
- **Yang diucapkan:** dua skenario ini memberi pelajaran berbeda — yang satu meninggalkan jejak lengkap tapi
  tidak ada yang membacanya, yang satu hanya tercatat di log broker tanpa alert.
- **Pertanyaan yang harus siap:** "kalau `access.log` punya semua jejak, apakah itu sudah deteksi?" → bukan.
  Log adalah bahan mentah; deteksi butuh aturan yang membaca dan memberi peringkat.

---

## Slide 9 — Skenario 5 dan akar kegagalan deteksi

- **Kategori:** kisi-kisi butir 5 (slide 3 dari 3)
- **Durasi:** 2:00
- **Judul di layar:** Skenario 5 dan akar kegagalan deteksi
- **Kiri — Skenario 5 (badge "insiden nyata"):**
  - Kutipan layar per payload: `9999 → broker 0, backend TOLAK` · `299 → TERSIMPAN (mustahil)` ·
    `0.1 → TERSIMPAN (mustahil)` · `21.5 → TERSIMPAN (wajar, kontrol)` · `kabita/sensor-liar → DITERIMA
    (tanpa ACL)` · `20 pesan beruntun → semua exit 0, tanpa throttle` · `bobot_log: 60 → 83 baris`,
    `berat > 300 kg: 0`
  - Tabel tahap: Deteksi **0 alert**, hanya log informasional `reading tersimpan` · Analisis (validasi **ada**
    0 < berat ≤ 300 tetapi itu batas **teknis**, bukan kewajaran biologis; tidak ada ACL topik, tidak ada rate
    limit, tidak ada penandaan anomali) · **Akar konseptual** (seluruh model ancaman MQTT bertumpu pada **satu
    asumsi**: kredensial tetap rahasia; begitu gugur, tidak ada pertahanan kedua) · Respons (rotasi kredensial
    24 byte base64 + `.env`; rancangan C.4a/b/c; sanitasi data) · Verifikasi (sebagian)
- **Kanan — rantai kegagalan pipeline deteksi (kutipan terminal):**
  ```
  $ ps -eo comm | grep -E '^(snort|barnyard2)$'
  barnyard2                    <- snort MATI
  $ ls -l .../snort-1/ | tail -1
  0 Jun 19 2020 snort.unified2.1592591088   <- 0 byte
  $ grep unified2 snort.conf
  output unified2: filename snort.unified2  <- path RELATIF
  $ find /nsm/sensor_data -name 'snort.unified2*' -newermt 2026-11-01 | wc -l
  0                            <- tidak ada berkas baru
  ```
  - Kartu **Empat mata rantai yang putus:** (1) **Snort mati** — sensor tidak menyaring paket sama sekali
    (eth0 tetap promiscuous) · (2) **Output relatif** — unified2 ditulis ke direktori kerja proses, bukan
    direktori sensor · (3) **Barnyard2 salah direktori** — membaca `seconion-import/`, bukan
    `seconion-eth0/` · (4) **Tidak ada log forwarding** — log aplikasi tidak pernah sampai ke sensor :514
- **Yang diucapkan:** ini slide terpenting. Bukan karena satu serangan berhasil, tapi karena empat mata rantai
  deteksi putus sekaligus — dan itu menjelaskan mengapa kelima skenario bernilai 0 alert.
- **Pertanyaan yang harus siap:** "apakah bisa diperbaiki sekarang?" → bisa, dan urutannya jelas: start snort,
  benahi path output, arahkan barnyard2 ke direktori sensor, tambah log forwarding. Belum dieksekusi karena
  berada di luar lingkup Fase 2; masuk rekomendasi D.1/D.2.

---

## Slide 10 — Kendala & pembelajaran

- **Kategori:** kisi-kisi butir 6 (1 slide)
- **Durasi:** 1:15
- **Judul di layar:** Lima pelajaran yang mengubah cara kami bekerja
- **Isi — lima kartu:**
  1. **Sensor yang terpasang bukan sensor yang bekerja.** Security Onion di-deploy sejak Minggu 1–3 dan selalu
     dianggap "sudah ada". Pipeline alert ternyata tidak pernah menulis satu event pun — baru diketahui setelah
     seluruh rangkaian serangan selesai. Kapabilitas deteksi harus diuji dengan serangan yang diketahui, bukan
     dengan memeriksa status layanan.
  2. **Kontrol dinilai dari sisi penyerang, bukan dari checklist.** "8/8 selesai" tidak berarti apa pun dengan
     sendirinya. Yang memberi nilai adalah angka: Hydra berhenti sebelum 1 percobaan, 1.295 request sqlmap tanpa
     injeksi, broker menolak 3 upaya anonim.
  3. **Nilai temuan negatif setara temuan alert.** Menuliskan "25 menit penyerangan menghasilkan nol alert"
     memberi informasi yang jauh lebih berguna daripada menyusun narasi bahwa sistem aman.
  4. **Asumsi tersembunyi adalah celah sesungguhnya.** Dua kegagalan terbesar bukan bug, tetapi asumsi yang tak
     pernah diuji: *"ada sensor berarti ada deteksi"* dan *"kredensial tetap rahasia"*. Keduanya masuk akal,
     keduanya salah. Kebiasaan baru: setiap kontrol disertai daftar asumsi yang harus benar agar ia bekerja.
  5. **Defense in depth diukur per jalur, bukan per sistem.** Secara agregat Target Node tampak berlapis. Per
     jalur: SSH punya 2 lapis, SQL punya 2 lapis, MQTT punya **1** lapis. Rata-rata sistem menutupi jalur yang
     paling tipis — dan penyerang selalu memilih jalur paling tipis.
- **Kartu tambahan — kendala operasional:** tidak ada jalur jaringan dari host ke Kali (harus
  `VBoxManage guestcontrol`) · SSH ke Monitoring Node tidak menjawab (harus konsol VM) · eksekusi tanpa GUI
  sehingga bukti berbentuk `.txt` keluaran perintah, bukan screenshot · push ke GitHub ter-throttle di jaringan
  kampus.
- **Yang diucapkan:** pelajaran nomor 5 adalah yang paling mengubah cara kami menilai sistem sendiri.

---

## Slide 11 — Rekomendasi lanjutan untuk sistem IoT asli

- **Kategori:** kisi-kisi butir 7 (1 slide, di luar penilaian)
- **Durasi:** 1:15
- **Judul di layar:** Rekomendasi untuk sistem IoT asli — di luar penilaian PBL
- **Isi — tabel prioritas (kolom: Prioritas · Rekomendasi · Alasan dari lab):**
  - **P1** Validasi kewajaran di backend, bukan di perangkat. Gateway/simulator bisa dikompromikan; backend
    harus jadi wasit terakhir yang tahu kambing tidak berbobot 299 kg. Idealnya aturan per jenis ternak.
    *Alasan: 299 kg & 0,1 kg lolos sebagai data sah*
  - **P1** Kredensial per perangkat, bukan per aplikasi. Satu kredensial bersama = satu kebocoran mengompromikan
    seluruh armada; kredensial per node memungkinkan pencabutan selektif.
    *Alasan: satu `kabita_device` membuka seluruh jalur tulis*
  - **P2** Perlakukan data sensor sebagai tidak tepercaya sampai divalidasi. Sertakan metadata asal (node,
    waktu, urutan) agar anomali dapat dikarantinakan tanpa menghapus data mentah.
    *Alasan: investigasi butuh data asli, bukan data yang sudah dibersihkan*
  - **P2** Bangun deteksi dari agregasi, bukan signature konten. Pola paling sering di lapisan IoT adalah
    volume: banyak koneksi gagal, banyak 400, publish beruntun.
    *Alasan: 1.295 request & 20 publish dalam < 1 s tidak terdeteksi ET Open*
  - **P3** Detection drill terjadwal. Kirim serangan yang diketahui, pastikan alert muncul, baru lanjut ke
    pengujian yang lebih kompleks. *Alasan: pipeline mati berbulan-bulan tanpa diketahui*
- **Isi — kartu kanan:**
  - *Prinsip yang dibawa keluar:* kutipan dosen — "bukan dinilai dari seberapa rumit serangan, tapi dari
    seberapa utuh siklus pertahanan yang bisa dibuktikan". Di lab ini empat dari lima siklus utuh; yang belum
    utuh justru bagian paling menentukan nilai sebuah SOC: **deteksi**.
  - *Yang sudah layak diteruskan sekarang:* A.1, A.2, B.1, B.3, C.2, C.3 dapat direplikasi ke sistem asli tanpa
    perubahan arsitektur — keenamnya terbukti menahan serangan nyata di lab, bukan teori.
- **Yang diucapkan:** ini bagian refleksi, di luar penilaian — tapi justru di sini proyek lab menyentuh sistem
  yang nyata.

---

## Slide 12 — Penutup & indeks artefak

- **Kategori:** penutup, mendukung kriteria *Kelengkapan Artefak GitHub* (15%)
- **Durasi:** 0:45
- **Judul di layar:** Yang dapat dibuka dosen saat presentasi
- **Isi — kiri, tabel artefak Fase 3:**
  | Artefak | Path |
  | :--- | :--- |
  | Incident Report final (NIST SP 800-61r2) | `docs/final/incident_report.pdf` |
  | Video demo Purple Team Loop | `https://youtu.be/Qn6f1lt6bEY` (YouTube unlisted, 7:12) |
  | Slide presentasi ini | `docs/presentation-final/slides.pdf` |
  | Logbook & tautan seluruh fase | `README.md` |
- **Isi — jejak audit lengkap:** `docs/design/` (topologi, IP plan, konfigurasi VM) · `docs/blueteam/`
  (hardening checklist + bukti A.1–C.3) · `docs/redteam/` (attack plan + bukti kelima skenario + diagnostik IDS) ·
  `docs/purple-team-log.md` (lima tahap × lima skenario, timestamp UTC)
- **Isi — kanan:**
  - *Tiga angka yang merangkum proyek:* **8/8** kontrol hardening selesai dan **5/8**-nya terbukti menahan
    serangan nyata · **4/5** skenario gagal total dari sisi penyerang · **0** alert dari seluruh rangkaian
    serangan — dan angka terakhir itulah pekerjaan rumah terbesar.
  - *Batas lingkup:* seluruh demo, video, dan laporan hanya berdasarkan simulasi pada **replika** di lab
    `192.168.4.0/24`, bukan sistem IoT nyata milik Mitra. Tidak ada satu pun uji coba diarahkan ke infrastruktur
    produksi KABITA.
  - **Terima kasih — kami menerima pertanyaan.** Olan · Anggi · Raka · Zidan
- **Yang diucapkan:** tutup dengan batas lingkup, bukan dengan pujian pada diri sendiri. Kalimat "tidak ada satu
  pun uji coba ke produksi" menjawab pertanyaan etika sebelum ditanyakan.

---

## Ringkasan alokasi waktu

| Slide | Isi | Durasi |
| :--- | :--- | ---: |
| 1 | Pembuka | 0:20 |
| 2 | Perjalanan Fase 1–3 | 1:30 |
| 3 | Eksekutif — apa yang terjadi | 1:45 |
| 4 | Eksekutif — peta 5 skenario | 1:45 |
| 5 | Status akhir hardening | 1:15 |
| 6 | Demo Purple Team Loop | 3:00 |
| 7 | Skenario 1–2 | 2:00 |
| 8 | Skenario 3–4 | 2:00 |
| 9 | Skenario 5 + akar kegagalan deteksi | 2:00 |
| 10 | Kendala & pembelajaran | 1:15 |
| 11 | Rekomendasi lanjutan | 1:15 |
| 12 | Penutup & indeks artefak | 0:45 |
| | **Total** | **18:50** |

Sisa 1–6 menit dari jendela 20 menit dapat dipakai bila pemutaran video melewati batas, atau bila dosen
menyela dengan pertanyaan di tengah presentasi.

## Siapa membawakan apa

Sesuai pembagian peran Bagian VIII panduan, dan agar kriteria *Kerja Sama & Penguasaan Materi* (15%) terlihat:

| Slide | Pembicara | Alasan |
| :--- | :--- | :--- |
| 1–2 | Olan (Lead) | koordinasi & konsistensi antar-bagian |
| 3–5 | Anggi (Blue Team) | preparation, hardening, klasifikasi insiden |
| 6 | Raka / Zidan (Red Team) | demo dijalankan Red Team, tahap verifikasi |
| 7–9 | Anggi (Blue) + Raka (Red) bergantian | serangan oleh Red, analisis & mitigasi oleh Blue |
| 10–11 | Olan (Lead) | refleksi lintas-peran |
| 12 | Olan | penutup & indeks artefak |

## Tiga hal yang perlu diperhatikan saat presentasi

1. **Angka sanitasi sudah diselaraskan** — slide 6 dan 9 kini menyebut **77 → 14 baris** (bukan lagi "23 baris").
   Bila dosen menanyakan angka absolut 60/83, jawab dengan **delta +23 baris dalam satu run** dan sebut bahwa
   60 sudah tercemar dua gelombang uji sebelumnya. Bukti: `docs/blueteam/evidence/skenario5-sanitasi-database.txt`.
2. **Slide 5 menyebut C.4 "belum dieksekusi"** — masih akurat, jangan diubah. Siapkan jawaban bahwa perbaikan
   C.4a/b/c masuk lingkup Fase 3 halaman 14–15 Incident Report.
3. **Kisi-kisi butir 5 menyebut "ketiga skenario"** sedangkan proyek menjalankan lima. Sebutkan sekali di awal
   agar 3 slide untuk butir ini tidak terlihat sebagai slide berlebih.
