#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Deploy replika KABITA (Nuxt + PostgreSQL) ke Target Node lewat SSH.

Pemakaian:
    python scripts/docs/deploy_kabita.py            # upload .output + setup DB + nginx + systemd
    python scripts/docs/deploy_kabita.py --db-only   # hanya buat/seed database

Prasyarat di guest: postgresql, nginx, nodejs (>=20), sudo NOPASSWD untuk user deploy.
Build `.output` dilakukan di host: `cd app/kabita && npm run build`.
"""
import argparse
import os
import posixpath
import stat
import sys

import paramiko

HOST, PORT = '127.0.0.1', 2222
USER, PASSWORD = 'iotadmin', '123'
REMOTE = '/opt/kabita'
DB_NAME, DB_USER, DB_PASS = 'kabita', 'kabita', 'kabita_lab_2026'
HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.normpath(os.path.join(HERE, '..', '..', 'app', 'kabita'))

UNIT = f"""[Unit]
Description=KABITA backend (Nuxt/Nitro) - replika lab PBL
After=network-online.target postgresql.service
Wants=network-online.target

[Service]
Type=simple
User={USER}
WorkingDirectory={REMOTE}
Environment=NODE_ENV=production
Environment=PORT=80
Environment=HOST=0.0.0.0
Environment=NUXT_DATABASE_URL=postgresql://{DB_USER}:{DB_PASS}@127.0.0.1:5432/{DB_NAME}
ExecStart=/usr/bin/node {REMOTE}/.output/server/index.mjs
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
"""

def connect():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=PORT, username=USER, password=PASSWORD,
              timeout=25, allow_agent=False, look_for_keys=False)
    return c


def run(c, cmd, timeout=300, check=True):
    _, out, err = c.exec_command(cmd, timeout=timeout)
    text = out.read().decode(errors='replace') + err.read().decode(errors='replace')
    code = out.channel.recv_exit_status()
    if check and code != 0:
        raise RuntimeError(f'perintah gagal (exit {code}): {cmd}\n{text.strip()}')
    return text.strip()


def upload_tree(sftp, local_dir, remote_dir):
    run_ssh = None  # placeholder agar linter tenang
    sftp_mkdirs(sftp, remote_dir)
    count = 0
    for root, dirs, files in os.walk(local_dir):
        rel = os.path.relpath(root, local_dir).replace('\\', '/')
        target = remote_dir if rel == '.' else posixpath.join(remote_dir, rel)
        sftp_mkdirs(sftp, target)
        for f in files:
            lp = os.path.join(root, f)
            sftp.put(lp, posixpath.join(target, f))
            count += 1
    return count


def sftp_mkdirs(sftp, path):
    parts, cur = [p for p in path.split('/') if p], ''
    for p in parts:
        cur += '/' + p
        try:
            sftp.stat(cur)
        except IOError:
            sftp.mkdir(cur)


def write_remote(c, path, content, tmp='/tmp/_kabita_upload'):
    sftp = c.open_sftp()
    with sftp.file(tmp, 'w') as f:
        f.write(content)
    sftp.close()
    run(c, f'sudo -n install -m 644 {tmp} {path}')


def setup_db(c):
    db_sql = open(os.path.join(APP, 'db', 'schema.sql'), encoding='utf-8').read()
    seed_sql = open(os.path.join(APP, 'db', 'seed.sql'), encoding='utf-8').read()
    sftp = c.open_sftp()
    for name, body in (('schema.sql', db_sql), ('seed.sql', seed_sql)):
        with sftp.file(f'/tmp/{name}', 'w') as f:
            f.write(body)
    sftp.close()

    run(c, f"""sudo -n -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='{DB_USER}'" | grep -q 1 ||
               sudo -n -u postgres psql -c "CREATE ROLE {DB_USER} LOGIN PASSWORD '{DB_PASS}'" """)
    run(c, f"""sudo -n -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'" | grep -q 1 ||
               sudo -n -u postgres createdb -O {DB_USER} {DB_NAME} """)
    run(c, f'sudo -n -u postgres psql -q -d {DB_NAME} -f /tmp/schema.sql')
    run(c, f'sudo -n -u postgres psql -q -d {DB_NAME} -f /tmp/seed.sql')
    # objek dibuat oleh role postgres -> beri hak akses ke role aplikasi
    run(c, f'sudo -n -u postgres psql -q -d {DB_NAME} -c "GRANT ALL ON SCHEMA public TO {DB_USER}; '
           f'GRANT ALL ON ALL TABLES IN SCHEMA public TO {DB_USER}; '
           f'GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO {DB_USER};"')
    sql = ("SELECT (SELECT count(*) FROM kambing)||' kambing, '||"
           "(SELECT count(*) FROM telemetri)||' telemetri, '||"
           "(SELECT count(*) FROM devices)||' device'")
    counts = run(c, f"""sudo -n -u postgres psql -d {DB_NAME} -tAc "{sql}" """)
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db-only', action='store_true')
    ap.add_argument('--skip-upload', action='store_true')
    a = ap.parse_args()

    c = connect()
    try:
        print('[1/6] database');          print('   ', setup_db(c))
        if a.db_only:
            return
        if not a.skip_upload:
            outdir = os.path.join(APP, '.output')
            if not os.path.isdir(outdir):
                sys.exit('Folder .output belum ada — jalankan `npm run build` di app/kabita dulu.')
            print('[2/6] upload .output')
            run(c, f'sudo -n mkdir -p {REMOTE} && sudo -n chown -R {USER}:{USER} {REMOTE}')
            sftp = c.open_sftp()
            n = upload_tree(sftp, outdir, f'{REMOTE}/.output')
            sftp.close()
            print(f'    {n} file terkirim ke {REMOTE}/.output')
        print('[3/4] systemd unit');      write_remote(c, '/etc/systemd/system/kabita.service', UNIT)
        run(c, 'sudo -n systemctl daemon-reload && sudo -n systemctl enable --now kabita.service')
        print('[4/4] restart & verifikasi')
        run(c, 'sudo -n systemctl restart kabita.service'); run(c, 'sleep 3')
        print('   ', run(c, "curl -s -o /dev/null -w 'GET / -> %{http_code}\\n' http://127.0.0.1/"))
        print('   ', run(c, "curl -s http://127.0.0.1/api/ringkasan"))
        print('   ', run(c, 'systemctl is-active kabita postgresql 2>&1'))
    finally:
        c.close()


if __name__ == '__main__':
    main()
