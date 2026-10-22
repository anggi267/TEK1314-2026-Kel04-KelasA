// POST /api/telemetri?token=<device-token>
// Body: { "rfid": "KMB-001", "berat_kg": 32.4, "pakan_kg": 1.8 }
// CATATAN LAB: token statis lewat query string, tanpa rate limit, dan TANPA validasi rentang
// nilai (berat/pakan liar diterima). Sengaja rentan untuk RT-03 (injeksi telemetri palsu).
export default defineEventHandler(async (event) => {
  const token = String(getQuery(event).token ?? '')
  const body = await readBody<{ rfid?: string; berat_kg?: number; pakan_kg?: number }>(event)

  const dev = await q<{ id: number; kode: string }>(
    'SELECT id, kode FROM devices WHERE token = $1 AND aktif = true', [token]
  )
  if (dev.length === 0) {
    setResponseStatus(event, 401)
    return { error: 'token tidak valid' }
  }

  if (!body?.rfid) {
    setResponseStatus(event, 400)
    return { error: 'rfid wajib' }
  }

  const goat = await q<{ id: number }>('SELECT id FROM kambing WHERE rfid = $1', [body.rfid])
  if (goat.length === 0) {
    setResponseStatus(event, 404)
    return { error: 'kambing tidak terdaftar' }
  }

  const inserted = await q(
    `INSERT INTO telemetri (kambing_id, berat_kg, pakan_kg, sumber)
     VALUES ($1, $2, $3, $4)
     RETURNING id, kambing_id, berat_kg, pakan_kg, ts`,
    [goat[0].id, body.berat_kg ?? 0, body.pakan_kg ?? 0, dev[0].kode]
  )

  return { ok: true, device: dev[0].kode, data: inserted[0] }
})
