import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss()
  ],

  base: '/assets/buy_new/frontend/',

  build: {
    outDir: '../buy_new/public/frontend',
    emptyOutDir: true,
    manifest: true
  },

  server: {
    host: '0.0.0.0',
    port: 5173,

    proxy: {
      '/api': {
        target: 'http://buynew.localhost:8000',
        changeOrigin: true
      },
      '/assets': {
        target: 'http://buynew.localhost:8000',
        changeOrigin: true
      },
      '/files': {
        target: 'http://buynew.localhost:8000',
        changeOrigin: true
      }
    }
  }
})