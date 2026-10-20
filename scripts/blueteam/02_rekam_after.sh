#!/usr/bin/env bash
# Rekam kondisi SESUDAH (after) hardening Target Node.
# Jalankan DI DALAM VM target:  sudo bash 02_rekam_after.sh [folder-output]
# Default output: ../../docs/blueteam/evidence/after
set -u
OUT="${1:-$(dirname "$0")/../../docs/blueteam/evidence/after}"
mkdir -p "$OUT"
STAMP="$(date -Is)"
HOST="$(hostname)"

w() {
  local f="$OUT/$1"; shift
  { echo "# host=$HOST tanggal=$STAMP"; echo "# cmd: $*"; echo; "$@" 2>&1; } > "$f"
  echo "  -> $f"
}

echo "[*] Merekam kondisi after ke: $OUT"

{ echo "host=$HOST"; echo "date=$STAMP"; uname -a; } > "$OUT/00_identitas.txt"

w "01_port_listening.txt"       netstat -tulpn
w "02_service_running.txt"      service --status-all
w "03_sshd_config_after.txt"    cat /etc/ssh/sshd_config
w "04_ufw_status_after.txt"     ufw status verbose
w "05_mysql_users_after.txt"    mysql -u root -e "SELECT user,host,password FROM mysql.user;"
w "06_mysql_grants_app.txt"     mysql -u root -e "SHOW GRANTS FOR 'pbl_app'@'localhost';"
w "07_ftp_attempt_after.txt"    sh -c 'printf "QUIT\r\n" | nc -w 3 127.0.0.1 21'
w "08_authlog_failed.txt"       sh -c 'grep -c "Failed password" /var/log/auth.log || echo 0'
w "09_env_permissions.txt"      sh -c 'ls -l /var/www/pbl/.env 2>/dev/null || echo "belum ada .env"'

cat <<'EOT'

[*] Selesai. Screenshot yang masih perlu diambil manual:
    - A1_after_root_login_denied.png
    - A2_after_password_login_denied.png / A2_after_key_login_ok.png
    - B2_after_nmap_vs_before.png
    - C2_after_sqlmap_protected.png
EOT
