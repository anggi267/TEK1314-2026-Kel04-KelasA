import { Pool } from 'pg'

let pool: Pool | undefined

/** Pool PostgreSQL bersama untuk seluruh server route. */
export function db(): Pool {
  if (!pool) {
    const cfg = useRuntimeConfig()
    pool = new Pool({
      connectionString: process.env.NUXT_DATABASE_URL || cfg.databaseUrl,
      max: 5,
      idleTimeoutMillis: 30000
    })
  }
  return pool
}

/** Query parameterized (dipakai pada endpoint yang ditulis dengan aman). */
export async function q<T = any>(sql: string, params: unknown[] = []): Promise<T[]> {
  const res = await db().query(sql, params as any[])
  return res.rows as T[]
}
