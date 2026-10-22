<template>
  <section style="max-width: 380px; margin: 40px auto;">
    <h1>Masuk operator</h1>
    <form class="card" @submit.prevent="submit">
      <label class="label">Username</label>
      <input v-model="username" autocomplete="username" />
      <label class="label" style="margin-top:10px;">Password</label>
      <input v-model="password" type="password" autocomplete="current-password" />
      <button type="submit" :disabled="loading">{{ loading ? 'Memeriksa…' : 'Masuk' }}</button>
      <p v-if="error" style="color:#ff8a8a; font-size:12.5px;">{{ error }}</p>
      <p v-if="ok" style="color:#5ee6a8; font-size:12.5px;">Berhasil masuk sebagai {{ ok }}</p>
    </form>
  </section>
</template>

<script setup lang="ts">
const username = ref('')
const password = ref('')
const error = ref('')
const ok = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true; error.value = ''; ok.value = ''
  try {
    const res = await $fetch<{ ok: boolean; user?: { username: string }; error?: string }>('/api/login', {
      method: 'POST', body: { username: username.value, password: password.value }
    })
    ok.value = res.user?.username || ''
    await navigateTo('/')
  } catch (e: any) {
    error.value = e?.data?.error || 'gagal login'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
input { width: 100%; padding: 9px 11px; margin-top: 5px; border-radius: 8px; border: 1px solid #24343f; background: #0b141a; color: #e8eef2; font-size: 13.5px; }
button { margin-top: 14px; width: 100%; padding: 10px; border: 0; border-radius: 8px; background: #1f9d6b; color: #05120c; font-weight: 650; cursor: pointer; }
button:disabled { opacity: .6; cursor: default; }
label.label { display: block; }
</style>
