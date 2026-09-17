# IP Plan - Kelompok 4

**Subnet Jaringan:** `192.168.4.0/24`
**Skenario:** Multi-service exploitation (Web & Database) menggunakan Metasploitable2

## Tabel Alokasi IP

| Hostname                | IP Address       | OS Direncanakan         | Peran         |
|--------------------------|------------------|--------------------------|---------------|
| Target Server (Korban)   | 192.168.4.5      | Metasploitable2          | Blue Team (setup) |
| Attacker Node             | 192.168.4.100    | Kali Linux               | Red Team      |
| Monitoring Node           | 192.168.4.200    | Security Onion           | Blue Team     |

## Catatan Tambahan

- Subnet `192.168.4.0/24` dipilih agar unik dan tidak bentrok dengan kelompok lain, sesuai Kontrak Kuliah Poin 3a.
- Monitoring Node (Security Onion) ditempatkan pada segmen yang sama agar dapat memantau seluruh trafik antara Attacker Node dan Target Node.
- Metasploitable2 dipilih sebagai Target Server karena menyediakan banyak service dengan celah keamanan default sekaligus dalam satu VM, antara lain:
  - **Web** - port 80 (DVWA bawaan, phpMyAdmin, Mutillidae)
  - **Database** - port 3306 (MySQL), 5432 (PostgreSQL)
  - **Service lain** - port 21 (FTP/vsftpd versi vulnerable), 23 (Telnet), 445 (Samba)
- Fokus service mana yang akan dieksploitasi (Web/DB/lainnya) akan ditentukan lebih lanjut oleh Red Team berdasarkan riset celah keamanan pada pertemuan ini.
