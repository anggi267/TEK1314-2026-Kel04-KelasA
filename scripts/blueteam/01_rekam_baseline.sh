#!/usr/bin/env bash
# Rekam kondisi AWAL (before) Target Node sebelum hardening.
# Jalankan DI DALAM VM target:  sudo bash 01_rekam_baseline.sh [folder-output]
# Default output: ../../docs/blueteam/evidence/before
set -u
OUT="${1:-$(dirname "$0")/../../docs/blueteam/evidence/before}"
mkdir -p "$OUT"
STAMP="$(date -Is)"
HOST="$(hostname)"

w() { # w <namafile> <perintah...>
  local f="$OUT/$1"; shift
  { echo "# host=$HOST tanggal=$STAMP"; echo "# cmd: $*"; echo; "$@" 2>&1; } > "$f"
  echo "  -> $f"
}

echo "[*] Merekam baseline ke: $OUT"

# identitas & waktu (penting untuk keaslian bukti)
{ echo "host=$HOST"; echo "date=$STAMP"; uname -a; } > "$OUT/00_identitas.txt"
echo "  -> $OUT/00_identitas.txt"

w "01_port_listening.txt"        netstat -tulpn
w "02_service_running.txt"       service --status-all
w "03_sshd_config_before.txt"    cat /etc/ssh/sshd_config
w "04_ufw_status_before.txt"     ufw status verbose
w "05_mysql_users_before.txt"    mysql -u root -e "SELECT user,host,password FROM mysql.user;"
w "06_ftp_banner_before.txt"     sh -c 'printf "QUIT\r\n" | nc -w 3 127.0.0.1 21'
w "07_pkg_versions.txt"          sh -c 'dpkg -l | egrep -i "openssh|apache|mysql|vsftpd|samba"'

cat <<'EOT'

[*] Selesai. Langkah manual yang masih perlu screenshot:
    - A2_before_password_login_ok.png   (ssh dengan password berhasil)
    - B1_before_nmap_full.png           (nmap -p- dari Kali)
EOT
