<template>
  <section>
    <h1>Dashboard kandang</h1>

    <div class="cards">
      <div class="card"><div class="label">Kambing terdaftar</div><div class="value">{{ ringkasan?.jumlah_kambing ?? '—' }} <small>ekor</small></div></div>
      <div class="card"><div class="label">Rata-rata berat (7 hari)</div><div class="value">{{ ringkasan?.rata_berat ?? '—' }} <small>kg</small></div></div>
      <div class="card"><div class="label">Pakan hari ini</div><div class="value">{{ ringkasan?.pakan_hari_ini ?? '—' }} <small>kg</small></div></div>
      <div class="card"><div class="label">Penimbangan hari ini</div><div class="value">{{ ringkasan?.catatan_hari_ini ?? '—' }} <small>catatan</small></div></div>
    </div>

    <table>
      <thead>
        <tr><th>RFID</th><th>Nama</th><th>Kelamin</th><th>Kandang</th><th>Berat terakhir</th><th>Pakan terakhir</th><th>Waktu</th></tr>
      </thead>
      <tbody>
        <tr v-for="k in daftar" :key="k.id">
          <td><span class="pill">{{ k.rfid }}</span></td>
          <td>{{ k.nama }}</td>
          <td>{{ k.jenis_kelamin === 'J' ? 'Jantan' : 'Betina' }}</td>
          <td>{{ k.kandang }}</td>
          <td class="num">{{ k.berat_kg ?? '—' }} kg</td>
          <td class="num">{{ k.pakan_kg ?? '—' }} kg</td>
          <td class="num">{{ format(k.terakhir) }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
const { data: ring } = await useFetch('/api/ringkasan')
const { data: kam } = await useFetch('/api/kambing')
const ringkasan = computed(() => ring.value as any)
const daftar = computed(() => ((kam.value as any)?.data ?? []) as any[])

function format(ts?: string) {
  if (!ts) return '—'
  const d = new Date(ts)
  return d.toLocaleString('id-ID', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}
</script>
