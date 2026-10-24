# Hardening Checklist — Target Node (KABITA Replica)
Kelompok 4 — diperbarui 2026-10-23

| # | Kategori | Kontrol | Status | Bukti |
|---|---|---|---|---|
| A.1 | Access & Authentication | SSH key-based auth, `PermitRootLogin no`, `PasswordAuthentication no` | Selesai | `evidence/a1-sshd_config-after.txt`, `evidence/a1-login-password-rejected.txt` |
| A.2 | Access & Authentication | Port SSH custom (2222) + fail2ban rate-limit | Selesai | `evidence/a2-fail2ban-status.txt` |
| B.1 | Service & Attack Surface | UFW whitelist port 2222/80/443/1883, default deny — 1883 untuk MQTT broker, sengaja dibuka ke LAN tapi wajib auth (bukan anonymous) | Selesai | `evidence/b1-ufw-status.txt` (perbarui — sekarang termasuk 1883) |
| B.2 | Service & Attack Surface | Nonaktifkan service tak terpakai (ModemManager) + unattended-upgrades aktif | Selesai | `evidence/b2-services-after.txt`, `evidence/b2-unattended-upgrades.txt` |
| B.3 | Service & Attack Surface | PostgreSQL `listen_addresses=localhost`, akun default bersih | Selesai | `evidence/b3-ss-tlnp.txt`, `evidence/b3-pg-roles.txt` |
| C.1 | Data & Application | Kredensial DB via `.env` (mode 600), tidak hardcode | Selesai | `evidence/c1-env-permissions.txt` |
| C.2 | Data & Application | Validasi input (`tag_rfid`, `berat_kg`, `:id`) | Selesai | `evidence/c2-sqli-probe-400.txt` |
| C.3 | Data & Application | Least-privilege DB user + logging query mencurigakan | Selesai | `evidence/b3-pg-roles.txt`, `evidence/c3-log_statement.txt`, `evidence/c3-log-sample.txt` |

> **Catatan:** MQTT (1883/tcp) terekspos ke jaringan lab secara sengaja — alat/simulator perlu publish dari luar. Beda dari PostgreSQL (5432, localhost) dan API (8080, loopback) yang tertutup total. Mitigasinya: `allow_anonymous false` + `password_file`, bukan isolasi jaringan.