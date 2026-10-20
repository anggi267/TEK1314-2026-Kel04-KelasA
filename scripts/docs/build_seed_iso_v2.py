"""Seed cloud-init v2: set password iotadmin=123, NOPASSWD sudo, dan IP statis lab."""
import pycdlib
from io import BytesIO

PWHASH = "$6$22j.uvjmS4E1mT2k$xv6lYlqpGCEc/.328sF/rQ1uu.7DIkMQTZEZRvNm6CwcoieK8kLVhpdditnKdn.kU67lvHU2J8nPSv4QitBGv0"

NETPLAN = """network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: false
      addresses: [192.168.4.5/24]
      optional: true
"""

user_data = f"""#cloud-config
# Seed operasional (v2): password lab, NOPASSWD sudo, IP statis.
# instance-id berubah agar cloud-init menjalankan ulang modul per-instance.
chpasswd:
  expire: false
  list: |
    iotadmin:123
ssh_pwauth: true
write_files:
  - path: /etc/netplan/60-pbl-lab.yaml
    owner: root:root
    permissions: '0600'
    content: |
      network:
        version: 2
        ethernets:
          enp0s3:
            dhcp4: false
            addresses: [192.168.4.5/24]
            optional: true
  - path: /etc/sudoers.d/90-pbl-nopasswd
    owner: root:root
    permissions: '0440'
    content: |
      iotadmin ALL=(ALL) NOPASSWD:ALL
runcmd:
  - [ netplan, apply ]
  - [ sh, -c, "ip -4 -br a > /var/log/pbl-netplan-apply.log 2>&1" ]
  - [ sh, -c, "echo applied-at $(date -Is) >> /var/log/pbl-netplan-apply.log" ]
"""

meta_data = """instance-id: pbl-k4-target-2604-v2
local-hostname: target-iot
"""

iso = pycdlib.PyCdlib()
iso.new(interchange_level=3, joliet=3, rock_ridge='1.09', vol_ident='CIDATA')


def add(path, name, content):
    data = content.encode()
    iso.add_fp(BytesIO(data), len(data), iso_path=path, joliet_path='/' + name, rr_name=name)


add('/USER_DAT.;1', 'user-data', user_data)
add('/META_DAT.;1', 'meta-data', meta_data)

out = r'D:\VirtualBox\seed-cidata-v2.iso'
iso.write(out)
iso.close()
print('OK', out)
