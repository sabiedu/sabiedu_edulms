// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // Ensure file-based routing is enabled
  pages: true,
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/icon', '@nuxt/image', '@nuxtjs/tailwindcss'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
    }
  }
})