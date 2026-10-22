# Purple Team Log — Fase 2

**Kelompok 4 · TEK1314 Kelas A**
Setiap skenario di `docs/redteam/attack_plan.md` harus melewati 5 tahap siklus tertutup
(Bagian X panduan). Log ini dimutakhirkan sampai **Minggu 11** dan menjadi isi utama
Vulnerability Assessment Report.

**Status saat commit Minggu 9:** semua entri `RENCANA`. Kolom bukti baru diisi setelah
eksekusi di Fase 2 — jangan diisi dengan asumsi.

Legenda status: `RENCANA` → `DIJALANKAN` → `TERVERIFIKASI`.

---

## RT-01 · Reconnaissance (nmap full TCP + service/OS fingerprint)

| Tahap | Red Team | Blue Team | Bukti | Status |
|---|---|---|---|---|
| 1. Serang (baseline) | `nmap -sS -p- -T4 --min-rate 1000 192.168.4.5` | Amati apakah scan terdeteksi | `redteam/evidence/rt01/rt01_nmap_full.txt`, `rt01_alert_baseline.png` | RENCANA |
| 2. Deteksi | — | Cek Zeek `Port_Scan` notice & alert Suricata ET SCAN; catat bila **tidak** muncul | `rt01_zeek_notice.png` / `rt01_no_alert.md` | RENCANA |
| 3. Analisis | Jelaskan tujuan: memetakan 20+ port & versi usang (nginx, MariaDB, Mosquitto, OpenSSH) | Root cause: tidak ada rate limit/firewall → pemindaian bebas; deteksi bergantung threshold | `rt01_analysis.md` | RENCANA |
| 4. Respons | — | Terapkan B-1 (matikan service tak terpakai) + B-2 (ufw default deny) | `blueteam/evidence/B1_after_nmap_full.png`, `B2_after_ufw_status.png` | RENCANA |
| 5. Verifikasi | Ulangi scan yang sama | Konfirmasi jumlah port terbuka turun & scan tetap terdeteksi | `rt01_nmap_after.txt`, `rt01_alert_after.png` | RENCANA |

## RT-02 · Exploitation — kredensial lemah & eskalasi SSH

| Tahap | Red Team | Blue Team | Bukti | Status |
|---|---|---|---|---|
| 1. Serang (baseline) | `hydra -l iotadmin -P rockyou.txt ssh://192.168.4.5 -t 4 -f` | Cek `auth.log` & alert brute-force | `rt02/rt02_hydra_baseline.txt`, `rt02_alert_baseline.png` | RENCANA |
| 2. Deteksi | — | Cari pola `Failed password` berulang lalu `Accepted password`; Zeek `conn.log` koneksi pendek beruntun | `rt02_authlog.png`, `rt02_conn_log.png` | RENCANA |
| 3. Analisis | Teknik: password lemah + password auth aktif + user punya sudo | Root cause: kredensial lemah (kelemahan disengaja #1), tidak ada rate limit | `rt02_analysis.md` | RENCANA |
| 4. Respons | — | A-2 key-only, A-4 fail2ban, B-3 password kuat, A-1 nonaktifkan root login | `A2_after_password_login_denied.png`, `A4_after_fail2ban_banned.png` | RENCANA |
| 5. Verifikasi | Ulangi hydra & login manual | Ditahan/di-ban; password auth ditolak; `sudo -l` tidak lagi penuh | `rt02_hydra_after.txt`, `rt02_alert_after.png` | RENCANA |

## RT-03 · Web/API — pencurian device token & injeksi telemetri palsu

| Tahap | Red Team | Blue Team | Bukti | Status |
|---|---|---|---|---|
| 1. Serang (baseline) | `curl -X POST /api/v1/<token>/telemetry -d '{"berat_kg":99.9}'` setelah token didapat dari dashboard publik/sniffing | Cek rule HTTP pada URI `/api/v1/`, amati anomali nilai telemetri | `rt03/rt03_inject_baseline.txt`, `rt03_alert_baseline.png` | RENCANA |
| 2. Deteksi | — | Identifikasi `POST /api/v1/*/telemetry` dari IP non-gateway + nilai di luar rentang wajar | `rt03_http_log.png`, `rt03_telemetry_anomaly.png` | RENCANA |
| 3. Analisis | Tujuan: memalsukan berat/pakan kambing (integritas data peternakan) | Root cause: token statis tanpa rotasi, telemetri diterima tanpa validasi rentang, tanpa TLS | `rt03_analysis.md` | RENCANA |
| 4. Respons | — | C-2 rotasi token + rule chain validasi (`berat_kg` 5–120, `pakan_kg` 0–10), B-2 batasi 8080, ganti akun default | `C2_after_token_rotated_401.png`, `C2_after_range_rejected.png` | RENCANA |
| 5. Verifikasi | Ulangi injeksi dengan token lama & nilai ekstrem | Token lama 401; nilai ekstrem ditolak rule chain; alert tetap tercatat | `rt03_inject_after.txt`, `rt03_alert_after.png` | RENCANA |

## RT-04 · Web/API/IoT — MQTT spoof publish memakai device token

| Tahap | Red Team | Blue Team | Bukti | Status |
|---|---|---|---|---|
| 1. Serang (baseline) | `mosquitto_pub -u <token> -t v1/devices/me/telemetry -m '{"berat_kg":12.0}'` | Amati apakah ada alert (kemungkinan **tidak ada** — temuan penting) | `rt04/rt04_pub_baseline.txt`, `rt04_no_alert.md` | RENCANA |
| 2. Deteksi | — | Cek Zeek MQTT log; catat ketiadaan rule bawaan untuk transport ThingsBoard | `rt04_zeek_mqtt.png` | RENCANA |
| 3. Analisis | Teknik: token statis sebagai username, password kosong, tanpa TLS | Root cause: MQTT tanpa TLS + token tidak dirotasi (kesalahan umum deployment ThingsBoard) | `rt04_analysis.md` | RENCANA |
| 4. Respons | — | C-2 TLS MQTT (8883) + rotasi token, B-2 batasi 1883, **rule alert kustom MQTT** | `C2_after_mqtt_tls_required.png`, `rule_mqtt_alert.png` | RENCANA |
| 5. Verifikasi | Ulangi publish dengan token lama / tanpa TLS | `not authorized` / TLS diminta; alert kustom muncul | `rt04_pub_after_denied.txt`, `rt04_alert_after.png` | RENCANA |

## RT-05 · Availability — SYN flood terkontrol (60 detik)

| Tahap | Red Team | Blue Team | Bukti | Status |
|---|---|---|---|---|
| 1. Serang (baseline) | `sudo timeout 60 hping3 -S --flood -p 80 192.168.4.5` | Ukur dampak dengan `curl` berkala | `rt05/rt05_hping3.txt`, `rt05_curl_latency_baseline.txt` | RENCANA |
| 2. Deteksi | — | ET DOS SYN flood; Zeek `conn.log` banyak state `S0` | `rt05_alert.png` | RENCANA |
| 3. Analisis | Teknik: banjir SYN tanpa handshake selesai | Root cause: tidak ada rate limit / SYN cookies | `rt05_analysis.md` | RENCANA |
| 4. Respons | — | `ufw limit 80/tcp`, `iptables -m limit`, aktifkan `syncookies` | `rt05_after_iptables_limit.png` | RENCANA |
| 5. Verifikasi | Ulangi hping3 | `curl` tetap `200 OK`; paket berlebih di-drop; alert tercatat | `rt05_curl_after.txt`, `rt05_alert_after.png` | RENCANA |

---

## Rekap siklus tertutup (diisi Minggu 11)

| Skenario | Berhasil di Tahap 1? | Terdeteksi Tahap 2? | Mitigasi Tahap 4 | Gagal/terblokir di Tahap 5? | Kesimpulan |
|---|---|---|---|---|---|
| RT-01 | — | — | B-1, B-2 | — | — |
| RT-02 | — | — | A-1, A-2, A-4, B-3 | — | — |
| RT-03 | — | — | C-2, C-3 | — | — |
| RT-04 | — | — | C-2, A-2, B-2 + rule | — | — |
| RT-05 | — | — | ufw limit, syncookies | — | — |

**Aturan penilaian internal:** setiap serangan yang berhasil di Tahap 1 **wajib** gagal atau
terblokir di Tahap 5. Bila masih berhasil, siklus ditandai `TERBUKA` dan menjadi temuan
prioritas di Vulnerability Assessment Report.
