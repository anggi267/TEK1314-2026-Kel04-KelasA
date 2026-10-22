// GET /api/ringkasan — angka ringkas untuk kartu dashboard
export default defineEventHandler(async () => {
  const [row] = await q<{
    jumlah_kambing: string; rata_berat: string; pakan_hari_ini: string; catatan_hari_ini: string
  }>(`
    SELECT (SELECT count(*) FROM kambing) AS jumlah_kambing,
           (SELECT round(avg(berat_kg), 1) FROM telemetri WHERE ts > now() - interval '7 days') AS rata_berat,
           (SELECT coalesce(sum(pakan_kg), 0) FROM telemetri WHERE ts::date = current_date) AS pakan_hari_ini,
           (SELECT count(*) FROM telemetri WHERE ts::date = current_date) AS catatan_hari_ini`)
  return row
})
