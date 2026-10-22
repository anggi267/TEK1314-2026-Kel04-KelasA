-- Skema replika KABITA (PostgreSQL) — lab PBL TEK1314 Kelompok 4
-- Catatan: beberapa kolom sengaja lemah untuk kebutuhan skenario Fase 2
--   * users.password disimpan plaintext (C-2)
--   * devices.token statis, tidak pernah dirotasi (C-2/C-3)

DROP TABLE IF EXISTS telemetri, devices, users, kambing, kandang CASCADE;

CREATE TABLE kandang (
  id       serial PRIMARY KEY,
  kode     text NOT NULL UNIQUE,
  nama     text NOT NULL
);

CREATE TABLE kambing (
  id            serial PRIMARY KEY,
  rfid          text NOT NULL UNIQUE,
  nama          text NOT NULL,
  jenis_kelamin char(1) NOT NULL DEFAULT 'J',
  tgl_lahir     date,
  kandang_id    integer REFERENCES kandang(id) ON DELETE SET NULL
);

CREATE TABLE telemetri (
  id        bigserial PRIMARY KEY,
  kambing_id integer NOT NULL REFERENCES kambing(id) ON DELETE CASCADE,
  berat_kg  numeric(5,2) NOT NULL CHECK (berat_kg > 0),
  pakan_kg  numeric(4,2) NOT NULL DEFAULT 0 CHECK (pakan_kg >= 0),
  sumber    text NOT NULL DEFAULT 'timbangan',
  ts        timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_telemetri_kambing_ts ON telemetri (kambing_id, ts DESC);

CREATE TABLE devices (
  id        serial PRIMARY KEY,
  kode      text NOT NULL UNIQUE,
  token     text NOT NULL,
  kandang_id integer REFERENCES kandang(id) ON DELETE SET NULL,
  aktif     boolean NOT NULL DEFAULT true
);

CREATE TABLE users (
  id       serial PRIMARY KEY,
  username text NOT NULL UNIQUE,
  password text NOT NULL,
  role     text NOT NULL DEFAULT 'operator'
);
