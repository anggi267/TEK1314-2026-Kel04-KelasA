# Deklarasi Tech Stack — KABITA (Kelompok 4)

| Komponen | Proyek IoT Asli (KABITA) | Direplikasi sebagai (Target Node) |
|---|---|---|
| Sistem Operasi backend | — | Ubuntu 26.04 LTS |
| Database | PostgreSQL | PostgreSQL 16 (apt, listen hanya localhost) |
| Backend API | Golang | Golang (REST API, port 8080 internal, proxied via Nginx) |
| Protokol komunikasi sensor | MQTT | MQTT (`kabita/readings`, QoS 1, auth user/password) + HTTP REST `POST /api/v1/readings` sebagai fallback — keduanya lewat satu fungsi validasi `processReading` |
| Dashboard/monitoring | Vue/React | Build statis Vue/React, disajikan via Nginx |