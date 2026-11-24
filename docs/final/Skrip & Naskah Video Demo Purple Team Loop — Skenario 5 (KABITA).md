# Skrip & Naskah Video Demo Purple Team Loop — Skenario 5 (KABITA)

Kelompok 4 · TEK1314 Keamanan Siber · Fase 3 (Minggu 14–15)

**Cara memakai dokumen ini:** setiap bagian berisi tiga hal yang selalu berurutan: **Layar** (apa yang
ditampilkan), **Perintah** (yang diketik atau ditempel), dan **Narasi** (yang diucapkan). Durasi total
sekitar 7 menit, sesuai ketentuan 5–8 menit.

**Semua nilai sudah terverifikasi dari eksekusi 4 November 2026** — tidak ada lagi placeholder yang perlu
ditebak:

| Hal | Nilai pasti | Sumber |
| :--- | :--- | :--- |
| Broker | `192.168.4.5:1883`, topik `kabita/readings` | `redteam/evidence/skenario5-serang.txt` |
| User perangkat | `kabita_device` (password dibaca dari `.env`, jangan diketik di layar) | sama |
| Field JSON | **`tag_rfid`** dan `berat_kg` — *bukan* `tag_id` | sama |
| Skema `bobot_log` | `id, kambing_id, berat_kg, dicatat_pada` — **tidak ada** `tag_id`/`created_at` | `blueteam/evidence/skenario5-sanitasi-database.txt` |
| Database | `kabita_db` | sama |
| Service backend | `kabita-backend` | sama |
| Topologi | `docs/design/topology.png` | repo |

Yang masih perlu diputuskan sendiri saat merekam hanya satu: **apakah backend sudah memakai user MQTT
terpisah**. Bila backend memakai `kabita_device` yang sama dengan perangkat, mengaktifkan ACL akan memutus
subscriber-nya (lihat Bagian 6).

## Persiapan sebelum rekam (tidak ikut direkam)

**Layar:** tidak ada, ini persiapan di belakang layar.

**Perintah** (di Target Node, lewat `ssh -p 2222 -i ~/.ssh/kabita_lab iotadmin@192.168.56.101`):

```bash
# 1. Lepas ban fail2ban untuk IP Kali (sisa uji Skenario 2)
sudo fail2ban-client set sshd unbanip 192.168.4.100

# 2. Pastikan semua service sehat
systemctl is-active kabita-backend mosquitto postgresql nginx

# 3. Siapkan kredensial sebagai variabel shell — JANGAN diketik literal di layar
export MQTT_PASS=$(sudo grep '^MQTT_PASSWORD=' /opt/kabita-backend/.env | cut -d= -f2-)

# 4. Ukur baseline. Setelah sanitasi 23 Nov 2026 nilainya 14 baris.
sudo -u postgres psql -X -P pager=off -d kabita_db -c \
  'select count(*) from bobot_log'

# 5. Jendela monitor 1: data masuk live (biarkan terbuka sepanjang rekaman)
watch -n 2 "sudo -u postgres psql -X -P pager=off -d kabita_db -c \
  \"select id, kambing_id, berat_kg, to_char(dicatat_pada,'HH24:MI:SS') as jam \
  from bobot_log order by id desc limit 8;\""

# 6. Jendela monitor 2: log broker live
sudo tail -f /var/log/mosquitto/mosquitto.log
```

**Jangan hapus data apa pun lagi.** Tabel sudah bersih 14 baris (13 riwayat sah + id 37 dari 2 Nov yang
tidak cocok pola serangan). Dump lengkap sebelum penghapusan ada di
`docs/blueteam/evidence/skenario5-sanitasi-database.txt`.

Rekam per bagian (bukan sekali jalan) supaya mudah diulang, lalu sambungkan saat edit. Tempel perintah
dari berkas teks, jangan diketik langsung.

## Bagian 1 — Pembuka: identitas lab (0:00–0:40)

**Layar:** tampilkan `docs/design/topology.png` beberapa detik, lalu pindah ke terminal tiap VM bergantian
(Kali, Target, Security Onion) agar nama host dan IP terlihat jelas. Ini bukti bahwa infrastruktur milik
kelompok sendiri.

**Perintah** (jalankan di tiap VM):

```bash
hostname; ip -4 -br a; date
```

**Narasi:**

> "Kami Kelompok 4. Ini infrastruktur simulasi KABITA, sistem pencatat bobot kambing berbasis RFID.
> Topologinya terdiri dari Attacker Kali di 192.168.4.100, Target Server di 192.168.4.5, dan Security Onion
> di 192.168.4.200. Ini adalah replika dengan data dummy, bukan sistem asli milik mitra."

## Bagian 2 — Kondisi awal (0:40–1:00)

**Layar:** Jendela monitor 1 di Target Node yang menampilkan isi `bobot_log` dengan data normal. Biarkan
terlihat 5–10 detik.

**Perintah:** tidak ada perintah baru, jendela `watch` dari persiapan sudah berjalan.

**Narasi:**

> "Ini kondisi awal. Tabel bobot_log berisi data pembacaan bobot yang normal. Kita akan lihat apa yang
> terjadi pada tabel ini saat diserang."

> **Catatan kejujuran data** (pakai bila dosen bertanya soal angka): pada eksekusi 4 November tabel berisi
> 60 baris, tetapi 60 itu sudah tercemar dua gelombang uji sebelumnya — 13 baris riwayat sah ditambah 21
> baris dari 28 Oktober dan 21 baris dari 4 November 14:53. Setelah sanitasi menyeluruh, baseline bersih
> adalah **14 baris**. Yang penting untuk video adalah **delta satu kali eksekusi: +23 baris**, bukan angka
> absolutnya.

## Bagian 3 — Tahap 1: Serang / Baseline (1:00–2:15)

**Layar:** terminal Kali (prompt dan IP 192.168.4.100 terlihat). Jalankan serangan, lalu arahkan kamera atau
potong ke Jendela monitor 1 untuk menunjukkan baris palsu yang muncul.

**Perintah** (di Kali):

```bash
hostname; ip -4 -br a; date

# Shot 1 — nilai di luar rentang: broker menerima, aplikasi menolak
mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
  -t kabita/readings -m '{"tag_rfid":"RFID-002","berat_kg":9999}'

# Shot 2 — nilai di dalam rentang tapi mustahil biologis: TERSIMPAN
mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
  -t kabita/readings -m '{"tag_rfid":"RFID-002","berat_kg":299}'

mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
  -t kabita/readings -m '{"tag_rfid":"RFID-002","berat_kg":0.1}'

# Shot 3 — topik liar: DITERIMA karena tidak ada ACL
mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
  -t 'kabita/sensor-liar' -m '{"tag_rfid":"RFID-002","berat_kg":50}'
```

Opsional, untuk menunjukkan **tidak ada rate limit** (skala kecil, terkontrol):

```bash
for i in $(seq 1 20); do
  mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
    -t kabita/readings -m "{\"tag_rfid\":\"RFID-002\",\"berat_kg\":$((10+i))}"
done
echo "20 pesan terkirim tanpa jeda"
```

**Narasi:**

> "Tahap 1, serangan. Red Team berperan sebagai penyerang yang memegang kredensial perangkat. Ia mengirim
> data bobot 299 kilogram dan 0,1 kilogram ke topic kabita/readings. Perhatikan tabel di sebelah: data palsu
> ini masuk. Serangan berhasil, karena validasi rentang 0 sampai 300 kilogram tidak cukup untuk menahan
> nilai yang tidak masuk akal tapi masih berada di dalam rentang. Topik liar juga diterima, dan dua puluh
> pesan terkirim tanpa dijeda."

## Bagian 4 — Tahap 2: Deteksi (2:15–2:50)

**Layar:** konsol Security Onion (192.168.4.200), buka `https://192.168.4.200/squert/`, interval seluruh
hari ini, tekan F5. **Sengaja tampilkan hasil nol apa adanya** — ini temuan, bukan kegagalan.

**Perintah** (query Hunt bila konsol web dipakai):

```
destination.ip: 192.168.4.5 AND destination.port: 1883
```

**Perintah diagnostik sensor** (terminal di Onion) — ini yang membuktikan nol alert bukan masalah tampilan:

```bash
ps -eo comm | sort -u | grep -E '^(snort|barnyard2)$'
ls -l /nsm/sensor_data/seconion-eth0/snort-1/ | tail -1
find /nsm/sensor_data -name 'snort.unified2*' -newermt 2026-11-01 | wc -l
```

**Teks di layar:** "Squert 0 event · snort tidak berjalan · unified2 0 byte sejak 2020 · 0 berkas baru"

**Narasi:**

> "Tahap 2, deteksi. Di Security Onion tidak ada satu pun alert. Squert menunjukkan nol event untuk seluruh
> hari, tanpa filter objek maupun sensor — jadi ini bukan masalah tampilan. Penyebabnya ada di sensor:
> proses snort tidak berjalan, berkas unified2 berukuran nol byte dan bertanggal 2020, dan tidak ada berkas
> baru. Pipeline alert belum menulis apa pun. Serangan ini lolos tanpa dikenali, dan itu temuan penting
> yang kami tulis sebagai temuan utama di Incident Report."

## Bagian 4b — Jejak alternatif di Target Node (opsional, 2:50–3:20)

**Layar:** terminal Target Node.

**Perintah:**

```bash
sudo journalctl -u kabita-backend --since '-10 min' | grep -i mqtt | tail -6
```

**Narasi:**

> "Satu-satunya jejak ada di Target Node sendiri: log backend mencatat setiap reading tersimpan sebagai log
> informasional. Tidak ada mekanisme yang menandainya sebagai anomali, dan log ini tidak pernah dikirim ke
> sensor karena belum ada rsyslog forwarding."

## Bagian 5 — Tahap 3: Analisis akar masalah (3:20–3:50)

**Layar:** satu slide atau catatan singkat berisi tiga celah (boleh diambil dari bagian analisis di Incident
Report), lalu tampilkan dampak terukur dari database.

**Perintah** (di Target Node):

```bash
sudo -u postgres psql -X -P pager=off -d kabita_db -c \
  "select id, kambing_id, berat_kg, to_char(dicatat_pada,'HH24:MI:SS') as jam \
   from bobot_log where berat_kg >= 250 or berat_kg <= 1 order by id desc limit 6"

# Bukti bahwa validasi hanya batas teknis, bukan kewajaran biologis
sudo -u postgres psql -X -P pager=off -d kabita_db -tAc \
  'select count(*) from bobot_log where berat_kg > 300'
```

**Narasi:**

> "Tahap 3, analisis. Ada tiga akar masalah. Pertama, tidak ada ACL per-topic di broker MQTT. Kedua, tidak
> ada pembatasan laju publish. Ketiga, nilai anomali yang masih di dalam rentang diterima tanpa penandaan.
> Dampaknya terukur: 299 kilogram dan 0,1 kilogram tersimpan sebagai data sah, sementara nol baris di atas
> 300 kilogram — bukti bahwa yang bekerja hanya batas teknis, bukan batas kewajaran biologis."

## Bagian 6 — Tahap 4: Respons / Mitigasi (3:50–5:30)

**Layar:** terminal Target Node. Tunjukkan konfigurasi **sebelum**, lalu rotasi kredensial, lalu pembuatan
ACL, lalu status service setelah restart.

**Perintah — konfigurasi sebelum mitigasi:**

```bash
cat /etc/mosquitto/conf.d/*.conf
```

**Perintah — rotasi kredensial bocor (ini mitigasi paling penting untuk Skenario 5):**

```bash
NEW_MQTT_PASS=$(openssl rand -base64 24 | tr -d '\n')
sudo mosquitto_passwd -b /etc/mosquitto/passwd kabita_device "$NEW_MQTT_PASS"
sudo sed -i "s|^MQTT_PASSWORD=.*|MQTT_PASSWORD=$NEW_MQTT_PASS|" /opt/kabita-backend/.env
sudo systemctl restart mosquitto && sudo systemctl restart kabita-backend
```

**Perintah — buat ACL per-topic (kontrol C.4a):**

```bash
sudo tee /etc/mosquitto/acl > /dev/null <<'EOF'
# Perangkat hanya boleh PUBLISH ke topik readings
user kabita_device
topic write kabita/readings

# Backend (subscriber) hanya boleh membaca — ganti namanya bila sudah ada
user kabita_backend
topic read kabita/readings
EOF

sudo chown root:mosquitto /etc/mosquitto/acl
sudo chmod 640 /etc/mosquitto/acl
grep -q 'acl_file' /etc/mosquitto/mosquitto.conf || \
  echo 'acl_file /etc/mosquitto/acl' | sudo tee -a /etc/mosquitto/mosquitto.conf
sudo systemctl restart mosquitto
```

**PENTING — uji di luar rekaman dulu.** Setelah `acl_file` aktif, subscriber kehilangan hak baca bila
memakai user tanpa entri `topic read`. Bila backend memakai `kabita_device` yang sama dengan perangkat,
beri juga `topic read kabita/readings` untuk user itu, atau buat user backend terpisah. Kalau salah,
data asli ikut terputus — regresi lebih buruk daripada insidennya.

**Perintah — mitigasi di backend Golang (`processReading`):** tambahkan (1) rate limit per tag, tolak
pembacaan dari tag yang sama bila jedanya terlalu singkat, dan (2) penandaan anomali, tandai atau tolak bila
selisih dengan pembacaan terakhir tag itu melebihi ambang wajar. Rate limit paling masuk akal di backend
karena Mosquitto tidak punya fitur ini secara bawaan. Setelah kode diubah:

```bash
git diff
sudo systemctl restart kabita-backend
systemctl status kabita-backend --no-pager | head -5
sudo journalctl -u kabita-backend -n 20 --no-pager | grep -i mqtt
```

**Teks di layar:** "kredensial dirotasi · ACL aktif · layanan tetap active"

**Narasi:**

> "Tahap 4, respons. Ini konfigurasi broker sebelum mitigasi — tidak ada ACL sama sekali. Kami merotasi
> kredensial yang bocor, menyinkronkannya ke berkas env backend, lalu menambahkan ACL: perangkat hanya
> boleh publish ke topic kabita/readings, dan backend hanya boleh membaca. Di backend Golang, ini perubahan
> kodenya: pembatasan laju per tag dan penandaan perubahan bobot yang tidak wajar. Layanan dijalankan ulang
> dan statusnya aktif normal. Kontrol ini kami catat sebagai C.4 pada hardening checklist."

## Bagian 7 — Tahap 5: Verifikasi (5:30–6:40)

**Layar:** terminal Kali (ulangi serangan), lalu Jendela monitor 1 dan log backend di Target Node, lalu
Security Onion.

**Perintah — di Kali (tiga shot pembuktian):**

```bash
date

# Shot 1 — kredensial LAMA yang dipegang penyerang harus ditolak
mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS_LAMA" \
  -t kabita/readings -m '{"tag_rfid":"RFID-002","berat_kg":299}'

# Shot 2 — topik liar harus ditolak ACL
mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
  -t 'kabita/sensor-liar' -m '{"tag_rfid":"RFID-002","berat_kg":50}'

# Shot 3 — kontrol negatif: nilai wajar HARUS tetap diterima
mosquitto_pub -h 192.168.4.5 -p 1883 -u kabita_device -P "$MQTT_PASS" \
  -t kabita/readings -m '{"tag_rfid":"RFID-002","berat_kg":21.5}'
```

**Perintah — di Target Node (bukti hasil):**

```bash
sudo journalctl -u kabita-backend --since "2 min ago" --no-pager | tail -20
```

Lalu arahkan kamera ke Jendela monitor 1 (tidak ada baris 299 kg / 0,1 kg baru, atau baris ditandai/ditolak),
dan terakhir ke Security Onion untuk menunjukkan kondisi pada waktu verifikasi.

**Teks di layar:** "kredensial lama → not authorised · topik liar → ditolak ACL · 21,5 kg → diterima"

**Narasi:**

> "Tahap 5, verifikasi. Kredensial lama yang dipegang penyerang sekarang ditolak broker. Publish ke topik
> liar ditolak ACL. Tapi yang paling penting: nilai wajar 21,5 kilogram tetap diterima — mitigasi kami tidak
> memutus operasi normal. Perhatikan tabel: tidak ada baris 299 kilogram baru. Ini jejaknya di log backend,
> dan ini aktivitasnya di Security Onion. Serangan yang tadinya berhasil sekarang gagal."

## Bagian 8 — Penutup (6:40–7:00)

**Layar:** tabel ringkasan hasil kelima skenario (S1–S5) dalam satu slide atau tampilan dokumen.

**Perintah:** tidak ada.

**Narasi:**

> "Ringkasnya, dari lima skenario serangan, satu celah nyata ditemukan dan sudah ditutup, yaitu injeksi data
> lewat MQTT. Empat skenario lain terbukti aman dari sisi penyerang. Yang masih terbuka adalah pemulihan
> pipeline IDS Security Onion — dan itu kami tulis sebagai temuan utama di Incident Report. Terima kasih."

## Checklist sebelum menekan tombol rekam

- [ ] `MQTT_PASS` sudah diekspor sebagai variabel; **tidak ada password terbaca di layar**
- [ ] `tag_rfid` (bukan `tag_id`) dan `kambing_id`/`dicatat_pada` (bukan `created_at`) dipakai di semua perintah
- [ ] IP Kali sudah di-unban, tabel `bobot_log` sudah 14 baris bersih (jangan hapus apa pun lagi)
- [ ] ACL dan mitigasi backend sudah diuji di luar rekaman dan **tidak memutus data asli**
- [ ] Zoom terminal besar, `date` selalu terlihat agar waktunya cocok dengan alert Security Onion
- [ ] Semua perintah sudah disiapkan di berkas teks untuk di-paste
- [ ] Durasi total 5–8 menit, resolusi minimal 720p, hasil akhir `.mp4` di `docs/final/video_demo.mp4`
- [ ] Cadangan: bila live demo berisiko saat presentasi, putar videonya

## Daftar berkas bukti yang sebaiknya tampil di video

| Segmen | Berkas pendukung |
| :--- | :--- |
| Baseline & dampak | `docs/redteam/evidence/skenario5-serang.txt` |
| Sanitasi data | `docs/blueteam/evidence/skenario5-sanitasi-database.txt` |
| Deteksi nol | `docs/redteam/evidence/security-onion-squert-0-event.png`, `security-onion-pipeline-ids.png` |
| Diagnostik pipeline | `docs/redteam/evidence/security-onion-hasil-pemeriksaan.txt` |
| Aturan ban | `docs/redteam/evidence/skenario2-fail2ban-rule.txt` |
