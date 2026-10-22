# Bukti Blue Team

| Folder | Isi |
|---|---|
| `baseline/` | `baseline_kabita.pcap` + `baseline_metrics.txt` — traffic normal 482 paket |
| `hardening/` | `before.txt` (pra-hardening) dan `after.txt` (setelah hardening + stack KABITA) |

## Aturan

1. Satu kontrol = minimal satu bukti **before** dan satu **after**.
2. Nama file: `<ID>_<before|after>_<topik>` (mis. `A2_after_password_auth_disabled.txt`).
3. Bukti berupa keluaran perintah (teks) atau tangkapan layar; sebutkan tanggal di dalam file.
4. Kontrol hanya boleh berstatus **Selesai** kalau kedua bukti ada.
