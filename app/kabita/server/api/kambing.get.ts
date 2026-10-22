// GET /api/kambing — daftar kambing + penimbangan terakhir + pakan hari ini
export default defineEventHandler(async () => {
  const rows = await q(`
    SELECT k.id, k.rfid, k.nama, k.jenis_kelamin, kd.kode AS kandang,
           t.berat_kg, t.pakan_kg, t.ts AS terakhir
      FROM kambing k
      LEFT JOIN kandang kd ON kd.id = k.kandang_id
      LEFT JOIN LATERAL (
        SELECT berat_kg, pakan_kg, ts
          FROM telemetri
         WHERE kambing_id = k.id
         ORDER BY ts DESC
         LIMIT 1
      ) t ON true
     ORDER BY k.rfid`)
  return { jumlah: rows.length, data: rows }
})
