# Skema IP & Penamaan VM

Subnet lab: **192.168.4.0/24** (Internal Network `pbl-kel4`, tanpa DHCP).

| Node | Nama VM | IP lab | Gateway | Adapter 2 |
|---|---|---|---|---|
| Attacker | `PBL-K4-02-Attacker-Kali` | 192.168.4.100/24 | — | NAT (dhcp) |
| Target | `PBL-K4-01-Target-Ubuntu` | 192.168.4.5/24 | — | NAT 10.0.3.15 + forward 2222→22 |
| Monitoring | `PBL-K4-03-Monitoring-Onion` | 192.168.4.200/24 | — | Host-only 192.168.56.1 |