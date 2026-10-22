// Nuxt config — replika backend KABITA (lab PBL TEK1314 Kelompok 4)
export default defineNuxtConfig({
  compatibilityDate: '2026-10-01',
  ssr: true,
  devtools: { enabled: false },
  runtimeConfig: {
    // dipakai server-side; bisa ditimpa env NUXT_DATABASE_URL
    databaseUrl: 'postgresql://kabita:kabita@127.0.0.1:5432/kabita',
    deviceToken: 'KBT-DEV-01-7f3c9a',
    public: {
      appName: 'KABITA — Berat & Pakan Kambing'
    }
  },
  nitro: {
    // replika: tidak ada rate limit, tidak ada CSRF, token device statis (disengaja)
    preset: 'node-server'
  },
  app: {
    head: {
      title: 'KABITA — Pencatatan Berat & Pakan Kambing',
      meta: [{ name: 'viewport', content: 'width=device-width, initial-scale=1' }]
    }
  }
})
