"""Gambar diagram topologi revisi Minggu 9 (target = Ubuntu Server)."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1600, 980
BG = (255, 255, 255)
INK = (24, 32, 40)
GREY = (110, 122, 134)
GREEN = (11, 107, 79)
RED = (155, 34, 38)
BLUE = (27, 79, 138)
LINE = (60, 72, 84)

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)

FONTS = r'C:\Windows\Fonts'
def font(name, size):
    for f in (name, 'segoeui.ttf', 'arial.ttf'):
        p = os.path.join(FONTS, f)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

f_title = font('segoeuib.ttf', 40)
f_sub = font('segoeui.ttf', 21)
f_box = font('segoeuib.ttf', 24)
f_txt = font('segoeui.ttf', 20)
f_small = font('segoeui.ttf', 17)
f_mono = font('consola.ttf', 19)
f_tag = font('segoeuib.ttf', 16)

d.text((60, 44), 'Topologi Jaringan — PBL Keamanan Siber Kelompok 4 (Kelas A)', font=f_title, fill=INK)
d.text((60, 96), 'Revisi Minggu 9: Target Node memakai Ubuntu Server (replika backend IoT), segmen Internal Network pbl-kel4',
       font=f_sub, fill=GREY)
d.line([(60, 132), (1540, 132)], fill=(214, 222, 228), width=2)


def box(x, y, w, h, title, lines, color):
    d.rounded_rectangle([x, y, x + w, y + h], radius=16, outline=color, width=3, fill=(250, 252, 251))
    tag_w = d.textlength(title, font=f_box) + 34
    d.rounded_rectangle([x + 20, y - 18, x + 20 + tag_w, y + 20], radius=10, fill=color)
    d.text((x + 37, y - 12), title, font=f_box, fill=(255, 255, 255))
    yy = y + 30
    for ln, fn, cl in lines:
        d.text((x + 26, yy), ln, font=fn, fill=cl)
        yy += 32


# kolom kiri: attacker
box(70, 230, 400, 250, 'Attacker Node', [
    ('Kali Linux 2026.2', f_txt, INK),
    ('192.168.4.100', f_mono, RED),
    ('Red Team', f_txt, GREY),
    ('nmap · Metasploit · sqlmap', f_small, GREY),
    ('hydra · hping3 · mosquitto', f_small, GREY),
], RED)

# kolom kanan: target
box(1130, 230, 400, 250, 'Target Node', [
    ('Ubuntu Server LTS 26.04', f_txt, INK),
    ('192.168.4.5', f_mono, BLUE),
    ('replika backend IoT', f_txt, GREY),
    ('nginx + PHP + DVWA  :80', f_small, GREY),
    ('MariaDB  :3306   Mosquitto  :1883', f_small, GREY),
], BLUE)

# tengah: switch / segmen
sw_x, sw_y, sw_w, sw_h = 600, 250, 400, 130
d.rounded_rectangle([sw_x, sw_y, sw_x + sw_w, sw_y + sw_h], radius=14, fill=(232, 243, 238), outline=GREEN, width=3)
d.text((sw_x + 26, sw_y + 24), 'Internal Network', font=f_box, fill=GREEN)
d.text((sw_x + 26, sw_y + 58), "pbl-kel4  ·  192.168.4.0/24", font=f_mono, fill=INK)
d.text((sw_x + 26, sw_y + 92), 'VirtualBox virtual switch', font=f_small, fill=GREY)

# garis penghubung
d.line([(470, 355), (600, 320)], fill=LINE, width=3)
d.line([(1000, 320), (1130, 355)], fill=LINE, width=3)

# monitoring di bawah tengah
box(600, 640, 400, 210, 'Monitoring Node', [
    ('Security Onion 3.2', f_txt, INK),
    ('192.168.4.200', f_mono, GREEN),
    ('Blue Team', f_txt, GREY),
    ('Zeek · Suricata · Kibana', f_small, GREY),
    ('NIC1 promisc allow-all', f_small, GREY),
], GREEN)
d.line([(800, 380), (800, 640)], fill=LINE, width=3)
d.text((818, 470), 'mirror / promiscuous', font=f_small, fill=GREY)
d.text((818, 496), '(trafik Attacker → Target)', font=f_small, fill=GREY)

# catatan adapter
d.rounded_rectangle([70, 640, 540, 850], radius=14, outline=(206, 214, 220), width=2, fill=(250, 251, 252))
d.text((94, 662), 'Adapter kedua (di luar segmen lab)', font=f_tag, fill=INK)
for i, t in enumerate([
    'Attacker  : NIC2 = NAT',
    'Target     : NIC2 = NAT',
    'Monitoring: NIC2 = Host-only 192.168.56.1',
    '→ untuk update paket & akses web UI',
]):
    d.text((94, 700 + i * 30), t, font=f_small, fill=GREY)

d.rounded_rectangle([1130, 640, 1530, 850], radius=14, outline=(206, 214, 220), width=2, fill=(250, 251, 252))
d.text((1154, 662), 'Kelemahan yang disengaja', font=f_tag, fill=INK)
for i, t in enumerate([
    'password lemah iotadmin',
    'MQTT anonymous tanpa ACL',
    'SQLi pada api.php / DVWA',
    'MySQL terbuka di semua iface',
]):
    d.text((1154, 700 + i * 30), '• ' + t, font=f_small, fill=GREY)

d.text((60, 905), 'Semua pengujian hanya di segmen 192.168.4.0/24 — tidak ada scanning ke sistem Mitra atau internet.',
       font=f_small, fill=GREY)

out = r'D:\materi kuliah\Keamanan Siber\PBL\docs\design\topology-v2.png'
img.save(out, dpi=(150, 150))
print('SAVED', out, img.size)
