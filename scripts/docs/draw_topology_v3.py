#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Gambar topologi lab PBL Kelompok 4 (3 node, stack KABITA) -> docs/design/topology-v2.png"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1700, 950
BG = (11, 17, 21)
PANEL = (18, 28, 36)
EDGE = (34, 52, 64)
GREEN = (94, 230, 168)
NAVY = (120, 180, 235)
AMBER = (245, 190, 110)
TXT = (232, 238, 242)
MUTED = (140, 158, 172)

FONT_DIR = r'C:\Windows\Fonts'
def font(name, size):
    for f in (name, 'segoeui.ttf'):
        p = os.path.join(FONT_DIR, f)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

F_TITLE = font('segoeuib.ttf', 34)
F_SUB = font('segoeui.ttf', 17)
F_NODE = font('segoeuib.ttf', 23)
F_IP = font('consola.ttf', 17)
F_SMALL = font('segoeui.ttf', 15)
F_TAG = font('segoeuib.ttf', 14)

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)


def rr(box, r=16, fill=PANEL, outline=EDGE, width=2):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def center_text(box, text, f, fill=TXT, dy=0):
    x0, y0, x1, y1 = box
    w = d.textlength(text, font=f)
    d.text(((x0 + x1 - w) / 2, y0 + dy), text, font=f, fill=fill)


# judul
d.text((60, 44), 'Topologi Lab PBL TEK1314 — Kelompok 4', font=F_TITLE, fill=TXT)
d.text((60, 90), 'Replika backend IoT KABITA (berat & pakan kambing) · subnet 192.168.4.0/24',
       font=F_SUB, fill=MUTED)

# node boxes
node_w, node_h = 430, 250
y_top = 210
xs = [70, 635, 1200]

nodes = [
    ('Attacker Node', 'Kali Linux 2026.2', '192.168.4.100', NAVY,
     ['nmap · hydra · sqlmap', 'hping3 · curl · whatweb', 'menjalankan skenario RT-01…RT-05']),
    ('Target Node', 'Ubuntu Server 26.04.1', '192.168.4.5', GREEN,
     ['KABITA — Nuxt 4 + Nitro (:80)', 'PostgreSQL 18 (:5432, lokal)', 'systemd kabita · ufw · fail2ban']),
    ('Monitoring Node', 'Security Onion 2.x', '192.168.4.200', AMBER,
     ['sensor pasif (promiscuous)', 'tcpdump · Zeek · Suricata', 'deteksi & bukti trafik lab']),
]

for (title, os_name, ip, accent, lines), x in zip(nodes, xs):
    box = (x, y_top, x + node_w, y_top + node_h)
    rr(box)
    d.rounded_rectangle((x, y_top, x + node_w, y_top + 46), radius=16, fill=accent)
    d.rectangle((x, y_top + 30, x + node_w, y_top + 46), fill=accent)
    center_text((x, y_top, x + node_w, y_top + 46), title, F_NODE, fill=(10, 20, 16), dy=9)

    d.text((x + 22, y_top + 62), os_name, font=F_SMALL, fill=MUTED)
    d.text((x + 22, y_top + 86), ip, font=F_IP, fill=accent)
    yy = y_top + 122
    for ln in lines:
        d.text((x + 22, yy), ln, font=F_SMALL, fill=TXT)
        yy += 27

# switch / segmen lab
sw_y = 560
sw_box = (x_left := 150, sw_y, W - 150, sw_y + 96)
rr(sw_box, r=18, fill=(16, 26, 33), outline=(46, 78, 92))
center_text((sw_box[0], sw_y + 10, sw_box[2], sw_y + 46),
            'Internal Network VirtualBox  "pbl-kel4"', F_NODE, fill=GREEN)
center_text((sw_box[0], sw_y + 52, sw_box[2], sw_y + 82),
            '192.168.4.0/24 · tanpa DHCP · tanpa rute internet', F_SMALL, fill=MUTED)

# garis node -> switch
for x in xs:
    cx = x + node_w // 2
    d.line([(cx, y_top + node_h), (cx, sw_y)], fill=(58, 92, 108), width=3)
    d.ellipse((cx - 5, sw_y - 5, cx + 5, sw_y + 5), fill=GREEN)

# catatan adapter kedua
note_y = 700
rr((150, note_y, W - 150, note_y + 120), r=14, fill=(14, 22, 28), outline=(30, 44, 54))
d.text((176, note_y + 12), 'Akses administrasi (di luar segmen lab)', font=F_TAG, fill=AMBER)
d.text((176, note_y + 36),
       'Adapter kedua tiap VM (NAT / host-only) hanya untuk administrasi & pembaruan paket:',
       font=F_SMALL, fill=MUTED)
d.text((176, note_y + 62),
       'Target 10.0.3.15 + port-forward 2222→22 (SSH admin)   ·   Kali NAT   ·   Onion host-only 192.168.56.1',
       font=F_SMALL, fill=TXT)
d.text((176, note_y + 88),
       'Tidak ada jalur dari lab ke internet — seluruh uji terisolasi.',
       font=F_SMALL, fill=TXT)

# legenda
leg_y = 850
for i, (label, col) in enumerate([('Attacker', NAVY), ('Target', GREEN), ('Monitoring', AMBER)]):
    bx = 150 + i * 260
    d.rounded_rectangle((bx, leg_y, bx + 16, leg_y + 16), radius=4, fill=col)
    d.text((bx + 26, leg_y - 2), label, font=F_TAG, fill=MUTED)

d.text((W - 560, leg_y - 2), 'PBL TEK1314 · Kelompok 4 · 2026', font=F_SMALL, fill=(90, 106, 118))

out = os.path.join('docs', 'design', 'topology-v2.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out)
print('saved', out, img.size)
