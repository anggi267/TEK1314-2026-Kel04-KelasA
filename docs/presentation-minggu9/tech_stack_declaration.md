# Deklarasi Tech Stack & Replikasi — KABITA

**Produk IoT:** KABITA — pencatatan berat badan dan pakan kambing.
**Kelompok 4 / Kelas A:** Olan (Lead), Anggi (Blue), Raka & Zidan (Red).

## 1. Komponen asli → replika

| # | Komponen KABITA asli | Teknologi asli (asumsi terdokumentasi) | Replika di Target Node | Catatan |
|---|---|---|---|---|
| 1 | Timbangan badan kambing | load cell + HX711, kirim via WiFi | tidak ada perangkat; ingest lewat `POST /api/telemetri` | data dikirim `curl` |
| 2 | Timbangan pakan | timbangan digital | field `pakan_kg` pada payload yang sama | 1 catatan = berat + pakan |
| 3 | Identitas kambing | ear tag / RFID | kolom `rfid` (`KMB-001`…`KMB-006`) | 6 kambing contoh |
| 4 | Backend aplikasi | Nuxt (Node.js) | **Nuxt 4 + Nitro**, Node 22, systemd | SSR + API dalam satu proses |
| 5 | Basis data | PostgreSQL | **PostgreSQL 18**, DB `kabita` | 5 tabel |
| 6 | Dashboard operator | web | halaman `/` (kartu ringkasan + tabel) | tema gelap, tanpa framework CSS |
| 7 | Autentikasi operator | sesi/cookie | `POST /api/login` → cookie `kabita_user` | sengaja lemah (tanpa signature) |
| 8 | Reverse proxy / TLS | nginx + TLS | tidak dipakai (Nuxt langsung `:80`) | keputusan: satu lapisan lebih sedikit |

## 2. Alasan pemilihan

1. **Nuxt 4** — aplikasi dan API dalam satu proses (Nitro), sehingga replika ringan (2 GB RAM)
   namun tetap menyerupai produk asli.
2. **PostgreSQL 18** — sesuai produk asli; memberi bahan skenario yang realistis (SQL injection,
   hak akses role, log query).
3. **Tanpa broker MQTT** — KABITA mengirim data lewat HTTP; menghapus MQTT mengurangi komponen
   yang harus diamankan tanpa mengurangi realisme.
4. **Tanpa nginx** — Nitro bisa langsung melayani `:80`; permukaan serangan lebih kecil dan
   konfigurasi lebih mudah dipertanggungjawabkan.
5. **Data sintetis** — 2 kandang, 6 kambing, 60 catatan telemetri (10 hari).

## 3. Risiko yang diperkenalkan sengaja (bahan Fase 2)

| Risiko | Endpoint | Skenario | Ditutup oleh |
|---|---|---|---|
| SQL injection | `GET /api/telemetri`, `POST /api/login` | RT-03 | C-2 |
| Kredensial lemah + plaintext | tabel `users` | RT-02, RT-03 | A-1, C-2 |
| Token device statis, tanpa rotasi | `POST /api/telemetri?token=` | RT-03 | C-3 |
| Telemetri tanpa validasi rentang | `POST /api/telemetri` | RT-03 | C-3 |
| Cookie sesi tanpa tanda tangan | `kabita_user` | RT-04 | A-1, C-1 |
| Tanpa TLS | port 80 | RT-01, RT-05 | C-1 |
| SSH password auth | port 22 | RT-02 | A-2 |

## 4. Pemetaan ke rubrik

| Kriteria | Bobot | Yang mendukung |
|---|---|---|
| Ketepatan tech stack & replikasi | 20% | tabel bagian 1, `docs/design/replica_setup.md` |
| Progres hardening nyata | 30% | `docs/blueteam/hardening_checklist.md` + `evidence/` |
| Konsistensi arsitektur Minggu 4 | 20% | subnet & IP tidak berubah (`docs/design/ip_plan.md`) |
| Eksekusi & analisis siklus | 30% | `docs/redteam/attack_plan.md`, `docs/purple-team-log.md` |
