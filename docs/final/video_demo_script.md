# Naskah & Shot List — Video Demo Purple Team Loop (Fase 3)

**PBL TEK1314 Kelompok 4** · Durasi target **6 menit 30 detik** (batas panduan 5–8 menit)
Format akhir **`.mp4`** · Simpan sebagai `docs/final/video_demo.mp4`
Alternatif bila berkas terlalu besar: unggah ke YouTube/Drive *unlisted*, cantumkan tautan di `README.md`

---

## Prinsip perekaman

1. **Satu siklus penuh wajib terlihat**: serangan dijalankan → terdeteksi/tidak → mitigasi → serangan diulang
   → digagalkan. Panduan Bagian VI menuntut ini secara eksplisit.
2. **Pilih Skenario 5 (MQTT kredensial bocor)**, bukan skenario yang sudah aman. Ini satu-satunya jalur yang
   benar-benar berhasil dieksploitasi, sehingga siklusnya utuh dan jujur — bukan klaim pada sistem yang
   tidak pernah gagal.
3. **Tampilkan nama host & IP** di setiap segmen (`PBL-K4-01-Target-KABITA 192.168.4.5`,
   `PBL-K4-02-Attacker-Kali 192.168.4.100`, `PBL-K4-03-Monitoring-Onion 192.168.4.200`) sebagai bukti
   infrastruktur kelompok sendiri.
4. **Sensor nilai sandi.** Sebelum merekam, siapkan terminal dengan `PS1` yang tidak menampilkan riwayat
   perintah berisi password. Gunakan `mosquitto_pub -P "$MQTT_PASS"` dengan variabel, bukan literal.
5. **Jangan mempercepat rekaman menjadi tidak terbaca.** Jika perlu memotong bagian menunggu, gunakan
   *jump cut* dengan kartu teks ("+ 30 detik"), bukan kecepatan 4×.

---

## Persiapan sebelum merekam (di luar rekaman)

```bash
# Di Target Node — siapkan variabel kredensial agar tidak muncul di layar
export MQTT_PASS=$(sudo grep '^MQTT_PASSWORD=' /opt/kabita-backend/.env | cut -d= -f2-)
export PGUSER=$(sudo grep '^DB_USER=' /opt/kabita-backend/.env | cut -d= -f2-)
export PGPASSWORD=$(sudo grep '^DB_PASSWORD=' /opt/kabita-backend/.env | cut -d= -f2-)
export PGDATABASE=$(sudo grep '^DB_NAME=' /opt/kabita-backend/.env | cut -d= -f2-)

# Ukur keadaan awal (angka ini akan menjadi pembanding di video)
psql -h 127.0.0.1 -tAc 'select count(*) from bobot_log'
```

Catat hasilnya. Pada eksekusi 4 November 2026 nilainya **60**.

Alat perekam: OBS Studio (satu scene per VM, atau satu scene dengan tiga window) atau `VBoxManage
controlvm <vm> recording start` untuk rekaman langsung dari VirtualBox. OBS lebih disarankan agar ketiga VM
dapat ditata berdampingan dalam satu frame.

---

## Timeline & naskah

### 00:00 – 00:20 · Pembuka (kartu judul)

**Visual:** kartu judul statis, bukan rekaman.

**Teks di layar:**
> PBL TEK1314 Keamanan Siber — Kelompok 4
> **Purple Team Loop: Skenario 5 — Kredensial MQTT Bocor**
> Serangan → Deteksi → Analisis → Mitigasi → Verifikasi
> Target: 192.168.4.5 (replika lab) · Attacker: 192.168.4.100 · Monitoring: 192.168.4.200

**Narasi:**
> "Kami akan menunjukkan satu siklus Purple Team Loop penuh pada skenario yang benar-benar berhasil
> dieksploitasi di lab kami: penyalahgunaan kredensial MQTT yang bocor. Kami memilih jalur yang gagal, bukan
> jalur yang sudah aman, supaya siklus mitigasinya terlihat utuh."

---

### 00:20 – 00:50 · Peta topologi (kartu + sorotan)

**Visual:** `docs/design/topology.png`, atau tiga jendela VM ditata berdampingan dengan label host.

**Teks di layar:** nama VM + IP masing-masing node.

**Narasi:**
> "Tiga node pada segmen 192.168.4.0/24. Target Node menjalankan Nginx, backend Golang, broker Mosquitto, dan
> PostgreSQL. Attacker Node adalah Kali. Monitoring Node adalah Security Onion dengan sensor pasif di eth0.
> Target Node di sini adalah replika, bukan sistem produksi Mitra."

---

### 00:50 – 01:20 · Baseline (rekaman terminal Target Node)

**Dijalankan di:** Target Node (`192.168.4.5`) via SSH

```bash
psql -h 127.0.0.1 -tAc 'select count(*) from bobot_log'
psql -h 127.0.0.1 -c "select id, berat_kg, dicatat_pada from bobot_log order by id desc limit 3"
```

**Teks di layar:** "Baseline: 60 baris di bobot_log"

**Narasi:**
> "Sebelum serangan, tabel bobot_log berisi 60 baris. Angka ini akan kita bandingkan lagi setelah serangan
> untuk mengukur dampaknya secara kuantitatif."

---

### 01:20 – 02:20 · TAHAP 1 — Serangan (rekaman terminal Kali)

**Dijalankan di:** Attacker Node (`192.168.4.100`)

**Shot 1 — publish nilai di luar rentang (ditolak aplikasi):**
```bash
mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
  -t kabita/readings -m '{"tag_rfid":"RFID-002","berat_kg":9999}'
```

**Teks di layar:** "9999 kg — broker menerima, aplikasi menolak"

**Shot 2 — publish nilai di dalam rentang tetapi mustahil secara biologis:**
```bash
mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
  -t kabita/readings -m '{"tag_rfid":"RFID-002","berat_kg":299}'

mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
  -t kabita/readings -m '{"tag_rfid":"RFID-002","berat_kg":0.1}'
```

**Teks di layar:** "299 kg & 0,1 kg — keduanya TERSIMPAN"

**Shot 3 — publish ke topik liar:**
```bash
mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
  -t 'kabita/sensor-liar' -m '{"tag_rfid":"RFID-002","berat_kg":50}'
```

**Teks di layar:** "Topik tak dikenal — DITERIMA (tidak ada ACL)"

**Shot 4 — banjir pesan:**
```bash
for i in $(seq 1 20); do
  mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
    -t kabita/readings -m "{\"tag_rfid\":\"RFID-002\",\"berat_kg\":$((10+i))}"
done
echo "20 pesan terkirim tanpa jeda"
```

**Teks di layar:** "20 pesan dalam < 1 detik — tanpa throttle"

**Narasi:**
> "Dengan kredensial yang sah, seluruh publish diterima broker. Aplikasi menolak 9999 karena di luar rentang,
> tetapi 299 kilogram dan 0,1 kilogram masuk sebagai data sah. Topik yang tidak dipakai aplikasi mana pun juga
> diterima, dan dua puluh pesan terkirim tanpa dijeda."

---

### 02:20 – 02:50 · TAHAP 2 — Deteksi (rekaman konsol Security Onion)

**Dijalankan di:** Monitoring Node (`192.168.4.200`) — konsol VM / browser Chromium

**Aksi:** buka `https://192.168.4.200/squert/`, set interval ke seluruh hari ini, tekan **F5**.

**Teks di layar:** "Squert: queued 0 · total events 0 · filtered by object: NO · filtered by sensor: NO"

**Shot tambahan — diagnostik sensor (terminal di Onion):**
```bash
ps -eo comm | sort -u | grep -E '^(snort|barnyard2)$'
ls -l /nsm/sensor_data/seconion-eth0/snort-1/ | tail -1
find /nsm/sensor_data -name 'snort.unified2*' -newermt 2026-11-01 | wc -l
```

**Teks di layar:** "snort MATI · unified2 0 byte sejak 2020 · 0 berkas baru"

**Narasi:**
> "Ini bagian penting dan kami sampaikan apa adanya: Security Onion tidak mencatat satu pun alert. Squert
> menunjukkan nol event untuk seluruh hari, tanpa filter objek maupun sensor — jadi ini bukan masalah tampilan.
> Penyebabnya ada di sensor: proses snort tidak berjalan, berkas unified2 berukuran nol byte dan bertanggal
> 2020, dan tidak ada berkas baru. Pipeline alert belum menulis apa pun."

---

### 02:50 – 03:20 · TAHAP 2b — Jejak alternatif di Target Node

**Dijalankan di:** Target Node (`192.168.4.5`)

```bash
sudo journalctl -u kabita-backend --since '-10 min' | grep -i mqtt | tail -6
```

**Teks di layar:** "Backend mencatat `reading tersimpan` — log informasional, bukan alert"

**Narasi:**
> "Satu-satunya jejak yang tersedia ada di Target Node sendiri: log backend mencatat setiap reading tersimpan
> sebagai log informasional. Tidak ada mekanisme yang menandainya sebagai anomali, dan log ini tidak pernah
> dikirim ke sensor karena belum ada rsyslog forwarding."

---

### 03:20 – 03:50 · TAHAP 3 — Analisis (rekaman query database)

**Dijalankan di:** Target Node (`192.168.4.5`)

```bash
psql -h 127.0.0.1 -tAc 'select count(*) from bobot_log'
psql -h 127.0.0.1 -c "select id, berat_kg, to_char(dicatat_pada,'HH24:MI:SS') as jam \
  from bobot_log where berat_kg >= 250 or berat_kg <= 1 order by id desc limit 6"
psql -h 127.0.0.1 -tAc 'select count(*) from bobot_log where berat_kg > 300'
```

**Teks di layar:** "60 → 83 baris · id 61 = 299 kg · id 62 = 0,1 kg · berat > 300 kg: 0"

**Narasi:**
> "Dampaknya terukur: tabel bertambah dari 60 menjadi 83 baris. Ada validasi rentang nol sampai tiga ratus
> kilogram — itu sebabnya 9999 ditolak — tetapi itu batas teknis, bukan batas kewajaran biologis. Kambing 299
> kilogram lolos sebagai data sah. Tidak ada ACL topik, tidak ada rate limit, dan tidak ada penandaan anomali."

---

### 03:50 – 04:40 · TAHAP 4 — Mitigasi (rekaman konfigurasi)

**Dijalankan di:** Target Node (`192.168.4.5`)

**Shot 1 — rotasi kredensial:**
```bash
NEW_MQTT_PASS=$(openssl rand -base64 24 | tr -d '\n')
sudo mosquitto_passwd -b /etc/mosquitto/passwd kabita_device "$NEW_MQTT_PASS"
sudo sed -i "s|^MQTT_PASSWORD=.*|MQTT_PASSWORD=$NEW_MQTT_PASS|" /opt/kabita-backend/.env
sudo systemctl restart mosquitto && sudo systemctl restart kabita-backend
```

**Teks di layar:** "Kredensial dirotasi 24 byte base64 · .env disinkronkan · layanan restart"

**Shot 2 — ACL topik (C.4a):**
```bash
sudo tee /etc/mosquitto/acl >/dev/null <<'EOF'
user kabita_device
topic write kabita/readings
topic read kabita/readings
EOF
grep -q 'acl_file' /etc/mosquitto/mosquitto.conf || \
  echo "acl_file /etc/mosquitto/acl" | sudo tee -a /etc/mosquitto/mosquitto.conf
sudo systemctl restart mosquitto
```

**Teks di layar:** "C.4a — kabita_device dibatasi ke kabita/readings saja"

**Shot 3 — sanitasi data (bila dijalankan):**
```bash
psql -h 127.0.0.1 -c "select id, berat_kg, dicatat_pada from bobot_log where id between 61 and 83 order by id" \
  > /tmp/data_palsu_skenario5.txt
psql -h 127.0.0.1 -c "delete from bobot_log where id between 61 and 83 returning id, berat_kg"
psql -h 127.0.0.1 -tAc 'select count(*) from bobot_log'
```

**Teks di layar:** "DELETE 23 · sisa 60 baris"

**Narasi:**
> "Mitigasi yang kami terapkan: rotasi kredensial yang bocor, sinkronisasi ke berkas env backend, lalu ACL
> topik supaya akun perangkat hanya bisa menulis ke topik readings. Data uji yang masuk kami catat dulu ke
> berkas bukti, baru dihapus, sehingga tabel kembali ke 60 baris. Untuk validasi kewajaran nilai dan rate
> limit, kami tampilkan rancangannya sebagai kontrol C.4b dan C.4c."

---

### 04:40 – 05:40 · TAHAP 5 — Verifikasi (rekaman ulang dari Kali)

**Dijalankan di:** Attacker Node (`192.168.4.100`)

**Shot 1 — kredensial lama harus ditolak:**
```bash
mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS_LAMA" \
  -t kabita/readings -m '{"tag_rfid":"RFID-002","berat_kg":45}'
```

**Teks di layar:** "Kredensial lama → Connection Refused: not authorised"

**Shot 2 — topik liar harus ditolak ACL:**
```bash
mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
  -t 'kabita/sensor-liar' -m '{"tag_rfid":"RFID-002","berat_kg":50}'
```

**Teks di layar:** "Topik liar → ditolak ACL"

**Shot 3 — kontrol negatif, nilai wajar harus tetap diterima:**
```bash
mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
  -t kabita/readings -m '{"tag_rfid":"RFID-002","berat_kg":21.5}'
```

**Teks di layar:** "21,5 kg → diterima (tidak ada false positive)"

**Narasi:**
> "Verifikasi: kredensial lama yang dipegang penyerang sekarang ditolak broker. Publish ke topik liar ditolak
> ACL. Dan yang paling penting, nilai wajar 21,5 kilogram tetap diterima — mitigasi kami tidak memutus operasi
> normal."

---

### 05:40 – 06:10 · Verifikasi efek ban fail2ban (opsional, jika waktu cukup)

**Dijalankan di:** Kali lalu Target Node

```bash
# Kali
for u in test1 test2 test3 test4 test5; do
  ssh -p 2222 -o StrictHostKeyChecking=no -o ConnectTimeout=3 $u@192.168.4.5 exit
done

# Target Node
sudo fail2ban-client status sshd
```

**Teks di layar:** "Ban aktif pada percobaan ke-4 · 192.168.4.100 terblokir"

---

### 06:10 – 06:30 · Penutup (kartu)

**Teks di layar:**
> **Siklus tertutup:** serangan → nol alert (temuan) → analisis akar masalah → mitigasi → verifikasi
> Incident Report: `docs/final/incident_report.pdf` · Slide: `docs/presentation-final/slides.pdf`
> Replika lab `192.168.4.0/24` — bukan sistem produksi Mitra

**Narasi:**
> "Satu siklus penuh terbukti: serangan berhasil, tidak terdeteksi karena pipeline alert belum jalan,
> akar masalah dianalisis, mitigasi diterapkan, dan serangan yang sama digagalkan. Yang masih terbuka adalah
> pemulihan pipeline IDS itu sendiri — dan itu kami tulis sebagai temuan utama di Incident Report."

---

## Daftar berkas bukti yang sebaiknya tampil di video

| Segmen | Berkas pendukung |
| :--- | :--- |
| Baseline & dampak | `docs/redteam/evidence/skenario5-serang.txt` (bagian keadaan sebelum/sesudah) |
| Deteksi nol | `docs/redteam/evidence/security-onion-squert-0-event.png`, `security-onion-pipeline-ids.png` |
| Diagnostik pipeline | `docs/redteam/evidence/security-onion-hasil-pemeriksaan.txt` |
| Aturan ban | `docs/redteam/evidence/skenario2-fail2ban-rule.txt` |

---

## Checklist sebelum menyerahkan

- [ ] Durasi 5–8 menit, resolusi minimal 720p, berformat `.mp4`
- [ ] Satu siklus penuh terlihat: serang → deteksi → mitigasi → verifikasi
- [ ] Nama host dan IP terbaca di layar (bukti infrastruktur sendiri)
- [ ] Tidak ada nilai sandi yang terbaca di layar
- [ ] Ada narasi (voice-over) **atau** teks penjelas di setiap tahap
- [ ] Berkas tersimpan di `docs/final/video_demo.mp4` **atau** tautan unlisted dicantumkan di `README.md`
- [ ] Commit dengan pesan deskriptif: `docs: add final incident report, demo video, and final presentation slides`
