// GET /api/telemetri?kambing=<id>&limit=<n>
// CATATAN LAB: nilai `kambing` disisipkan langsung ke SQL (string concatenation).
// Ini kelemahan yang SENGAJA dipertahankan sebagai sasaran skenario RT-03 (SQL injection).
// Perbaikannya (prepared statement) dijadwalkan pada kontrol C-2 di Fase 2.
export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const kambing = String(query.kambing ?? '1')
  const limit = Number.parseInt(String(query.limit ?? '50'), 10) || 50

  const sql = `SELECT t.id, t.kambing_id, k.rfid, k.nama, t.berat_kg, t.pakan_kg, t.sumber, t.ts
                 FROM telemetri t
                 JOIN kambing k ON k.id = t.kambing_id
                WHERE t.kambing_id = ${kambing}
                ORDER BY t.ts DESC
                LIMIT ${limit}`

  try {
    const rows = await q(sql)
    return { sql, jumlah: rows.length, data: rows }
  } catch (err: any) {
    setResponseStatus(event, 500)
    return { sql, error: err.message }
  }
})
