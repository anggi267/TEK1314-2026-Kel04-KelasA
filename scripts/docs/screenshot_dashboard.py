#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ambil screenshot dashboard KABITA dari Windows (host) tanpa GUI di Ubuntu Server.

Cara kerja:
  1. buka SSH tunnel lokal 127.0.0.1:8090 -> 127.0.0.1:80 di Target Node
     (lewat port-forward 2222 yang sudah ada; ufw tidak perlu diubah)
  2. jalankan Chrome headless
  3. set cookie sesi lab, buka halaman, simpan PNG ke docs/blueteam/evidence/

Prasyarat host: `pip install paramiko websocket-client` dan Chrome terpasang.
Pemakaian: python scripts/docs/screenshot_dashboard.py
"""
import base64
import json
import os
import select
import socketserver
import subprocess
import sys
import threading
import time
import urllib.request

try:
    import paramiko
    import websocket
except ImportError:
    sys.exit('Pasang dulu: pip install paramiko websocket-client')

HOST, PORT = '127.0.0.1', 2222
USER, PASSWORD = 'iotadmin', '123'
LOCAL_PORT = 8090
CHROME_CANDIDATES = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]
HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.normpath(os.path.join(HERE, '..', '..', 'docs', 'blueteam', 'evidence'))
DEBUG_PORT = 9333


# ---------------------------------------------------------------- tunnel
def start_tunnel():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASSWORD,
                   timeout=20, allow_agent=False, look_for_keys=False)
    transport = client.get_transport()

    class Forward(socketserver.BaseRequestHandler):
        def handle(self):
            chan = transport.open_channel('direct-tcpip', ('127.0.0.1', 80),
                                          self.request.getpeername())
            while True:
                r, _, _ = select.select([self.request, chan], [], [], 1)
                if self.request in r:
                    data = self.request.recv(4096)
                    if not data:
                        break
                    chan.sendall(data)
                if chan in r:
                    data = chan.recv(4096)
                    if not data:
                        break
                    self.request.sendall(data)
            chan.close()

    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    srv = Server(('127.0.0.1', LOCAL_PORT), Forward)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return client, srv


# ---------------------------------------------------------------- chrome
def start_chrome():
    exe = next((p for p in CHROME_CANDIDATES if os.path.exists(p)), None)
    if not exe:
        sys.exit('Chrome/Edge tidak ditemukan di path standar.')
    profile = os.path.join(os.environ.get('TEMP', '.'), 'kabita-cdp-profile')
    os.makedirs(profile, exist_ok=True)
    proc = subprocess.Popen(
        [exe, '--headless=new', f'--remote-debugging-port={DEBUG_PORT}',
         f'--user-data-dir={profile}', '--window-size=1440,1000', '--hide-scrollbars',
         '--force-device-scale-factor=1', '--remote-allow-origins=*', 'about:blank'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{DEBUG_PORT}/json/version', timeout=1)
            return proc
        except Exception:
            time.sleep(0.5)
    proc.terminate()
    sys.exit('Chrome headless tidak siap.')


class CDP:
    def __init__(self):
        with urllib.request.urlopen(f'http://127.0.0.1:{DEBUG_PORT}/json/list', timeout=5) as r:
            pages = [t for t in json.load(r) if t['type'] == 'page']
        self.ws = websocket.create_connection(pages[0]['webSocketDebuggerUrl'], timeout=30)
        self.seq = 0

    def send(self, method, **params):
        self.seq += 1
        mid = self.seq
        self.ws.send(json.dumps({'id': mid, 'method': method, 'params': params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get('id') == mid:
                if 'error' in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get('result', {})

    def wait_load(self, timeout=25):
        end = time.time() + timeout
        while time.time() < end:
            self.ws.settimeout(max(1, end - time.time()))
            try:
                if json.loads(self.ws.recv()).get('method') == 'Page.loadEventFired':
                    return True
            except Exception:
                return False
        return False


def shoot(cdp, name):
    res = cdp.send('Page.captureScreenshot', format='png', captureBeyondViewport=True)
    path = os.path.join(EVIDENCE, name)
    os.makedirs(EVIDENCE, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(base64.b64decode(res['data']))
    print(f'  {name}  ({os.path.getsize(path) // 1024} KB)')


def main():
    print('[1/4] SSH tunnel', HOST, PORT, '->', LOCAL_PORT)
    client, srv = start_tunnel()
    print('[2/4] Chrome headless')
    chrome = start_chrome()
    try:
        cdp = CDP()
        cdp.send('Page.enable')
        cdp.send('Network.enable')
        base = f'http://127.0.0.1:{LOCAL_PORT}'

        print('[3/4] halaman login + dashboard')
        cdp.send('Page.navigate', url=f'{base}/login')
        cdp.wait_load()
        time.sleep(1.5)
        shoot(cdp, 'BUKTI_login.png')

        cdp.send('Network.setCookie', name='kabita_user', value='admin',
                 domain='127.0.0.1', path='/', url=f'{base}/')
        cdp.send('Page.navigate', url=f'{base}/')
        cdp.wait_load()
        time.sleep(2.5)
        shoot(cdp, 'BUKTI_dashboard.png')
        print('[4/4] selesai — tersimpan di docs/blueteam/evidence/')
    finally:
        chrome.terminate()
        srv.shutdown()
        client.close()


if __name__ == '__main__':
    main()
