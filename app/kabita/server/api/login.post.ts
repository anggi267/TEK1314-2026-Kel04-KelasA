// POST /api/login { username, password }
// CATATAN LAB: password plaintext + query dirangkai langsung (SQL injection / auth bypass).
// Sengaja rentan untuk skenario RT-03.
export default defineEventHandler(async (event) => {
  const body = await readBody<{ username?: string; password?: string }>(event)
  const u = String(body?.username ?? '')
  const p = String(body?.password ?? '')

  const sql = `SELECT username, role FROM users WHERE username = '${u}' AND password = '${p}'`

  try {
    const rows = await q<{ username: string; role: string }>(sql)
    if (rows.length === 0) {
      setResponseStatus(event, 401)
      return { ok: false, error: 'kredensial salah' }
    }
    setCookie(event, 'kabita_user', rows[0].username, { path: '/', maxAge: 28800 })
    return { ok: true, user: rows[0] }
  } catch (err: any) {
    setResponseStatus(event, 500)
    return { ok: false, sql, error: err.message }
  }
})
