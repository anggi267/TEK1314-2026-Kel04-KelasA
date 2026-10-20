"""Bangun seed ISO cloud-init (NoCloud/CIDATA) untuk autoinstall Ubuntu Server."""
import pycdlib
from io import BytesIO

PWHASH = "$6$22j.uvjmS4E1mT2k$xv6lYlqpGCEc/.328sF/rQ1uu.7DIkMQTZEZRvNm6CwcoieK8kLVhpdditnKdn.kU67lvHU2J8nPSv4QitBGv0"

user_data = f"""#cloud-config
autoinstall:
  version: 1
  locale: en_US.UTF-8
  keyboard:
    layout: us
  timezone: Asia/Jakarta
  identity:
    hostname: target-iot
    username: iotadmin
    password: "{PWHASH}"
  ssh:
    install-server: true
    allow-pw: true
  storage:
    layout:
      name: direct
  apt:
    geoip: false
    fallback: offline-install
  late-commands:
    - curtin in-target -- timedatectl set-timezone Asia/Jakarta
    - curtin in-target -- systemctl enable ssh
  shutdown: poweroff
"""

meta_data = """instance-id: pbl-k4-target-2604
local-hostname: target-iot
"""

iso = pycdlib.PyCdlib()
iso.new(interchange_level=3, joliet=3, rock_ridge='1.09', vol_ident='CIDATA')

def add(path, name, content):
    data = content.encode()
    iso.add_fp(BytesIO(data), len(data), iso_path=path,
               joliet_path='/' + name, rr_name=name)

add('/USER_DAT.;1', 'user-data', user_data)
add('/META_DAT.;1', 'meta-data', meta_data)

out = r'D:\VirtualBox\seed-cidata.iso'
iso.write(out)
iso.close()
print('OK', out)
