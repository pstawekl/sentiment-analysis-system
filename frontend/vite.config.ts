import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: false, // Nie zmieniaj origin, gdy target to 127.0.0.1
        secure: false,
        ws: true, // WebSocket support
      },
    },
  },
})

