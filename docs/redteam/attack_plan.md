# Attack Plan Fase 2 — KABITA (Kelompok 4)

| Kategori | Skenario | Tools | Target di Replika |
|---|---|---|---|
| Reconnaissance | Port/service scan + OS fingerprinting | `nmap -sV -O -p- 192.168.4.5` | Seluruh port terbuka Target Node |
| Exploitation / Akses | Brute-force login SSH (port 2222) | Hydra + wordlist | Layanan SSH Target Node |
| Web/API/Protokol IoT | Uji SQL injection pada parameter `id` di `GET /api/v1/kambing/:id/riwayat` | sqlmap / uji manual | Endpoint API Golang |
| Web/API/Protokol IoT | Publish MQTT tanpa kredensial ke broker (harus ditolak) | `mosquitto_pub` (tanpa -u/-P) | Mosquitto broker :1883 |
| Web/API/Protokol IoT | Publish MQTT dengan kredensial bocor — payload palsu masuk `bobot_log` | `mosquitto_pub -u kabita_device -P <bocor>` | Mosquitto broker → tabel `bobot_log` |