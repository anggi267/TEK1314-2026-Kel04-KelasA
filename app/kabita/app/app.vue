<template>
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <span class="dot" />
        <strong>KABITA</strong>
        <span class="sub">Pencatatan Berat &amp; Pakan Kambing</span>
      </div>
      <nav>
        <NuxtLink to="/">Dashboard</NuxtLink>
        <NuxtLink to="/login">Login</NuxtLink>
      </nav>
    </header>
    <main><NuxtPage /></main>
    <footer>Replika backend — lab PBL TEK1314 Kelompok 4 · data sintetis</footer>
  </div>
</template>

<style>
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body {
  margin: 0; background: #0b1115; color: #e8eef2;
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
}
.shell { min-height: 100vh; display: flex; flex-direction: column; }
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 22px; border-bottom: 1px solid #1c2a33;
  background: linear-gradient(90deg, #0e1620, #101c22);
}
.brand { display: flex; align-items: center; gap: 8px; }
.brand strong { letter-spacing: .12em; color: #5ee6a8; }
.brand .sub { color: #7d8f9b; font-size: 12.5px; }
.dot { width: 9px; height: 9px; border-radius: 50%; background: #5ee6a8; box-shadow: 0 0 10px #5ee6a8; }
nav a { color: #9fb2bd; text-decoration: none; margin-left: 18px; font-size: 13px; }
nav a.router-link-active { color: #5ee6a8; }
main { flex: 1; padding: 22px; max-width: 1180px; width: 100%; margin: 0 auto; }
footer { padding: 12px 22px; color: #55656f; font-size: 11.5px; border-top: 1px solid #16222a; }
h1 { font-size: 19px; margin: 0 0 14px; font-weight: 600; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; margin-bottom: 18px; }
.card { background: #101a21; border: 1px solid #1c2a33; border-radius: 10px; padding: 14px 16px; }
.card .label { color: #7d8f9b; font-size: 11.5px; text-transform: uppercase; letter-spacing: .08em; }
.card .value { font-size: 24px; font-weight: 650; margin-top: 4px; color: #d8f5e6; }
.card .value small { font-size: 12px; color: #7d8f9b; font-weight: 400; }
table { width: 100%; border-collapse: collapse; font-size: 13px; background: #0f1820; border-radius: 10px; overflow: hidden; }
th, td { padding: 9px 12px; text-align: left; border-bottom: 1px solid #17242c; }
th { background: #12202a; color: #9fb2bd; font-weight: 600; font-size: 11.5px; text-transform: uppercase; letter-spacing: .06em; }
tr:last-child td { border-bottom: none; }
td.num { font-variant-numeric: tabular-nums; }
.pill { padding: 2px 8px; border-radius: 999px; font-size: 11px; background: #17303a; color: #7fd7c4; }
</style>
