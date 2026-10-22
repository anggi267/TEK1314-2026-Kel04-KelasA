// Middleware sederhana: dashboard butuh cookie login. Sengaja lemah (cookie tanpa signature).
export default defineNuxtRouteMiddleware((to) => {
  if (process.server) return
  if (to.path === '/login') return
  const user = useCookie('kabita_user')
  if (!user.value) return navigateTo('/login')
})
