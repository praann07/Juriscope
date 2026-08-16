import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/chat': 'http://localhost:8000',
      '/upload': 'http://localhost:8000',
      '/session': 'http://localhost:8000',
      '/sessions': 'http://localhost:8000',
      '/sources': 'http://localhost:8000',
      '/api/health': {
        target: 'http://localhost:8000',
        rewrite: () => '/'
      }
    }
  }
})
