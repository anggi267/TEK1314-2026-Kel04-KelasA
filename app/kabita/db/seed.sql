-- Data awal replika KABITA: 2 kandang, 6 kambing, 2 timbangan, 10 hari telemetri
INSERT INTO kandang (kode, nama) VALUES
  ('KDG-01', 'Kandang A — Pejantan'),
  ('KDG-02', 'Kandang B — Indukan');

INSERT INTO kambing (rfid, nama, jenis_kelamin, tgl_lahir, kandang_id) VALUES
  ('KMB-001', 'Bagas',   'J', '2024-03-11', 1),
  ('KMB-002', 'Rambo',   'J', '2024-05-02', 1),
  ('KMB-003', 'Sinta',   'B', '2024-01-19', 2),
  ('KMB-004', 'Mawar',   'B', '2024-06-27', 2),
  ('KMB-005', 'Bima',    'J', '2025-02-14', 1),
  ('KMB-006', 'Lestari', 'B', '2025-04-08', 2);

INSERT INTO devices (kode, token, kandang_id) VALUES
  ('KABITA-TIMBANG-01', 'KBT-DEV-01-7f3c9a', 1),
  ('KABITA-TIMBANG-02', 'KBT-DEV-02-2b8e4d', 2);

-- kredensial lemah & plaintext (disengaja)
INSERT INTO users (username, password, role) VALUES
  ('admin',    'admin123',    'admin'),
  ('operator', 'operator123', 'operator');

-- 10 hari riwayat penimbangan + pemberian pakan
INSERT INTO telemetri (kambing_id, berat_kg, pakan_kg, ts)
SELECT k.id,
       ROUND((22 + random() * 18)::numeric, 2),
       ROUND((0.8 + random() * 1.4)::numeric, 2),
       now() - (d || ' days')::interval - (random() * 4 || ' hours')::interval
FROM kambing k
CROSS JOIN generate_series(0, 9) AS d;
