# Runbook Per Role — Fase 2 (Minggu 10–11)

**Kelompok 4 · TEK1314 Kelas A**
Dokumen ini adalah urutan kerja operasional: siapa mengerjakan apa, dalam urutan apa, dengan
perintah apa, dan bukti apa yang harus di-commit. Rujukan aturan tetap
`docs/blueteam/hardening_checklist.md`, `docs/redteam/attack_plan.md`, `docs/purple-team-log.md`.

**Prinsip urutan:** satu skenario harus **tuntas siklusnya** (serang → deteksi → analisis →
mitigasi → uji ulang) sebelum skenario berikutnya dimulai. Jangan menyerang 3 skenario dulu
baru memitigasi semuanya — bukti Tahap 5 akan kacau karena kondisi hardening berubah di tengah.

---

## 0. Peta sesi & pembagian waktu

| Sesi | Kapan | Durasi | Isi | Pimpinan |
|---|---|---|---|---|
| **S0** | sebelum presentasi Minggu 9 | 60' | Push repo, verifikasi akses dosen, gladi slide | Lead |
| **S1** | Minggu 10 | 150' | Snapshot, baseline normal, hardening prioritas (5 kontrol) | Blue |
| **S2** | Minggu 10 | 90' | Loop RT-01 (recon) → deteksi → mitigasi → verifikasi | Red mulai, Blue tutup |
| **S3** | Minggu 10/11 | 120' | Loop RT-02 (brute-force SSH) → deteksi → mitigasi → verifikasi | Red mulai, Blue tutup |
| **S4** | Minggu 11 | 150' | Loop RT-03 (SQLi) + RT-04 (MQTT) | Red + Blue |
| **S5** | Minggu 11 | 60' | Loop RT-05 (SYN flood), rekap, Vulnerability Assessment Report | Blue |

**Aturan koordinasi antar-role (wajib):**

1. Red **memberi tahu jam mulai/selesai** tiap serangan ke Blue (chat/timestamp) — tanpa ini,
   Blue tidak bisa menyaring log pada rentang waktu yang benar.
2. Blue **mengonfirmasi** "sudah kurekam" sebelum Red lanjut ke skenario berikutnya.
3. Semua perubahan config oleh Blue **di-commit dulu** sebelum Red menguji ulang (Tahap 5),
   supaya diff-nya bisa dirujuk.
4. Snapshot VM sebelum tiap sesi: nama `snap-<sesi>-<tanggal>`; rollback hanya bila VM rusak.

---

## 1. LEAD — Olan

### S0 · Sebelum presentasi (60 menit)

| # | Langkah | Perintah / aksi | Selesai bila |
|---|---|---|---|
| L1 | Pastikan commit Minggu 9 sudah ada | `git log --oneline -n 3` | commit `docs: add minggu-9 ...` terlihat |
| L2 | Push ke GitHub (kredensial belum tersimpan di laptop Raka) | `cd "D:\materi kuliah\Keamanan Siber\PBL" && git push origin main` | `git status` bersih & remote `origin/main` = lokal |
| L3 | Verifikasi repo bisa dibuka dosen | buka `https://github.com/anggi267/TEK1314-2026-Kel04-KelasA` di mode incognito | `docs/presentation-minggu9/slides.pdf` bisa diunduh tanpa login |
| L4 | Bila repo privat: undang dosen/asisten sebagai collaborator | GitHub → Settings → Collaborators → Add people | dosen menerima undangan (screenshot undangan = bukti) |
| L5 | Cek semua file wajib ada di repo | lihat tabel "Deliverable Minggu 9" di `README.md` | 8 artefak tercentang |
| L6 | Tetapkan pembagian bicara 20 menit | isi tabel di bawah | tiap orang tahu menitnya |
| L7 | Gladi 2× dengan timer | `slides.pdf` dibuka fullscreen, stopwatch | selesai ≤20 menit |
| L8 | Siapkan fallback bila GitHub/lab down | PDF + screenshot di flashdisk & HP | bisa tampil tanpa internet |

**Pembagian bicara (20 menit):**

| Menit | Slide | Pembicara |
|---|---|---|
| 0–3 | 1 Konteks & peran | Olan |
| 3–7 | 2 Tech stack & replikasi | Anggi (Blue) |
| 7–10 | 3 Arsitektur & IP | Anggi (Blue) |
| 10–14 | 4 Hardening & baseline | Anggi (Blue) |
| 14–16 | 5 Live demo | Anggi (Blue) |
| 16–19 | 6 Attack plan Fase 2 | Raka (Red) |
| 19–20 | 7 Kendala & penutup | Olan |

### S1–S5 · Selama Fase 2

| # | Langkah | Bukti |
|---|---|---|
| L9 | Buka tiap sesi dengan cek snapshot + tulis jam mulai di `docs/logbook.md` | baris logbook |
| L10 | Catat persetujuan Rules of Engagement (ROE) sebelum Red menyerang: "disetujui, tanggal, jam" | komentar di `docs/redteam/attack_plan.md` atau commit message |
| L11 | Jaga timebox tiap sesi; kalau Blue belum selesai hardening, Red **tidak** mulai | — |
| L12 | Tiap akhir sesi: rapat 10 menit, isi tabel rekap di `docs/purple-team-log.md` | tabel rekap terisi |
| L13 | Commit akhir sesi dengan pesan deskriptif, mis. `docs: close purple loop RT-01 after ufw deny` | `git log` |
| L14 | Minggu 11: susun kerangka Vulnerability Assessment Report (outline dulu, isi dari log) | `docs/reports/va-report.md` |

**Yang TIDAK dikerjakan Lead:** mengeksekusi hardening atau serangan. Kalau Lead ikut
mengetik, timebox dan pencatatan akan jatuh — dan itu justru 10% nilai kerja sama.

---

## 2. BLUE TEAM — Anggi Permana Putra

### S0 · Persiapan tanpa VM (45 menit, bisa sebelum Minggu 10)

| # | Langkah | Detail |
|---|---|---|
| B0.1 | Baca ulang checklist | `docs/blueteam/hardening_checklist.md` — hafalkan 5 kontrol prioritas: A-2, B-1, B-2, B-3, C-1 |
| B0.2 | Siapkan folder bukti | `docs/blueteam/evidence/before/`, `.../after/`, `.../baseline/` |
| B0.3 | Siapkan kunci SSH di laptop | `ssh-keygen -t ed25519 -f ~/.ssh/pbl_kel4 -N ""` |
| B0.4 | Pastikan bisa login ke Security Onion & tahu query dasar | Hunt: `event.dataset:conn source.ip:192.168.4.100` |
| B0.5 | Siapkan template `baseline_summary.md` (tabel kosong) | RTT, jitter, request/menit, jumlah paket |
| B0.6 | Siapkan catatan insiden gaya NIST (kolom: waktu, sumber, teknik, dampak, tindakan) | dipakai S2–S5 |

### S1 · Baseline & hardening prioritas (150 menit)

**Urutan ini penting — salah urutan = terkunci dari VM sendiri.**

| # | Langkah | Perintah | Bukti |
|---|---|---|---|
| B1.1 | Snapshot target **sebelum** apa pun | VirtualBox/VMware snapshot `snap-s1-<tanggal>` | screenshot nama snapshot |
| B1.2 | Pastikan NIC di Internal Network `pbl-kel4` & IP guest benar | `ip -brief a` di tiap VM, `ping 192.168.4.5`, `nmap -sn 192.168.4.0/24` | screenshot `ip a` + ping |
| B1.3 | Rekam baseline normal 15 menit (belum ada serangan) | `ping -i 5 192.168.4.5` + 10× buka dashboard + query API tiap 10 s + capture tcpdump di sensor | `baseline_minggu9.pcap`, `baseline_summary.md` |
| B1.4 | Jalankan perekam baseline | `sudo bash scripts/blueteam/01_rekam_baseline.sh` | `evidence/before/00..07` |
| B1.5 | **A-2** pasang SSH key, uji login key **sebelum** mematikan password | `ssh-copy-id -i ~/.ssh/pbl_kel4.pub iotadmin@192.168.4.5` lalu `ssh -i ~/.ssh/pbl_kel4 iotadmin@192.168.4.5` | `A2_after_key_login_ok.png` |
| B1.6 | **A-2** matikan password auth, **buka sesi SSH lama jangan ditutup** | `sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config; sudo /etc/init.d/ssh restart` | `A2_after_password_login_denied.png` |
| B1.7 | **B-2** siapkan rule ufw **sebelum** `enable` (port 2222 wajib allow) | lihat blok perintah di checklist B-2 | `B2_after_ufw_status.png` |
| B1.8 | Uji dari Kali: SSH 2222 masih bisa, port lain tertutup | `nmap -sS -p1-1024 192.168.4.5` | `B2_before_nmap_vs_after_nmap.png` |
| B1.9 | **B-1** matikan service tak terpakai (telnet, rsh, tftp, smtp, ircd, distccd, tomcat) | checklist B-1 | `B1_after_nmap_full.txt` (jumlah port turun) |
| B1.10 | **B-3** patch paket & hapus kredensial default | `apt upgrade` + `mysql_secure_installation` + ganti password `iotadmin` (cek `apt list --upgradable` kosong) | `B3_after_apt_upgraded.txt`, `B3_after_mysql_secure.png` |
| B1.11 | **C-1** pindahkan kredensial aplikasi ke `.env` (chmod 600) | checklist C-1 | `C1_after_env_file_chmod600.png` |
| B1.12 | Rekam kondisi after | `sudo bash scripts/blueteam/02_rekam_after.sh` | `evidence/after/00..09` |
| B1.13 | Update status checklist + commit | ubah kolom Status hanya untuk yang buktinya lengkap | commit `feat(blueteam): baseline + 5 hardening controls with evidence` |
