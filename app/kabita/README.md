# KABITA — replika backend (Nuxt + PostgreSQL)

Replika backend untuk Target Node PBL TEK1314 Kelompok 4. Domain: **pencatatan berat badan dan
pakan kambing** (produk asli: KABITA). Aplikasi ini **bukan** aplikasi sengaja-rentan seperti
DVWA: sebagian besar kode ditulis wajar, dan **lima kelemahan spesifik dipertahankan** agar
skenario Fase 2 punya sasaran nyata (lihat tabel di bawah).

## Stack

| Lapisan | Teknologi |
|---|---|
| Framework | Nuxt 4 (SSR) + Nitro server (`node-server`) |
| Runtime | Node.js 22 (VM), dijalankan `node .output/server/index.mjs` |
| Basis data | PostgreSQL 18, database `kabita`, user `kabita` |
| Reverse proxy | Nginx :80 → Nitro :3000 (hanya localhost) |
| Proses | systemd unit `kabita.service` |

## Struktur

```
app/kabita/
├── app/                     # sisi Nuxt 4 (srcDir default)
│   ├── app.vue              # shell + tema gelap
│   ├── middleware/auth.global.ts
│   └── pages/{index,login}.vue
├── server/
│   ├── utils/db.ts          # pool pg + helper q()
│   └── api/{kambing,ringkasan,telemetri,login}.get|post.ts
├── db/{schema,seed}.sql
├── nuxt.config.ts
└── package.json
```

## Endpoint

| Method | Path | Fungsi |
|---|---|---|
| GET | `/` | dashboard: kartu ringkasan + tabel berat/pakan terakhir per kambing |
| GET | `/login` | formulir login operator |
| POST | `/api/login` | `{username,password}` → set cookie `kabita_user` |
| GET | `/api/kambing` | daftar kambing + penimbangan terakhir |
| GET | `/api/telemetri?kambing=<id>&limit=<n>` | riwayat telemetri |
| POST | `/api/telemetri?token=<device-token>` | ingest dari timbangan: `{rfid,berat_kg,pakan_kg}` |
| GET | `/api/ringkasan` | angka kartu dashboard |

## Kelemahan yang SENGAJA dipertahankan

| # | Kelemahan | Letak | Skenario | Ditutup oleh |
|---|---|---|---|---|
| 1 | SQL injection (query dirangkai dari input) | `server/api/telemetri.get.ts`, `server/api/login.post.ts` | RT-03 | C-2 (prepared statement) |
| 2 | Kredensial lemah + password plaintext | tabel `users` (`admin/admin123`) | RT-02, RT-03 | A-1, C-2 |
| 3 | Token device statis lewat query string, tanpa rotasi & tanpa rate limit | `/api/telemetri?token=` | RT-03 | C-3 |
| 4 | Telemetri diterima tanpa validasi rentang (berat/pakan liar) | `telemetri.post.ts` | RT-03 | C-3 + rule validasi |
| 5 | Tanpa TLS pada dashboard | nginx :80 | RT-01/RT-05 | (temuan, dicatat) |

Selain itu SSH masih memakai password auth untuk `iotadmin` (kelemahan #6, skenario RT-02).

## Menjalankan

```bash
# host: build
cd app/kabita && npm install && npm run build

# deploy ke target node (upload .output, buat DB, nginx, systemd)
python scripts/docs/deploy_kabita.py

# hanya menyiapkan/menyegarkan database
python scripts/docs/deploy_kabita.py --db-only
```

Data yang dipakai adalah **data sintetis** (2 kandang, 6 kambing, 10 hari riwayat). Tidak ada data
peternakan nyata.
