import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [react()],
  envDir: path.resolve(__dirname, '..'), // Point to backoffice directory for .env file
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
  },
  // Remove server config since backend will serve the built files
  // server: {
  //   port: 3001,
  //   proxy: {
  //     '/api': {
  //       target: 'http://localhost:5001',
  //       changeOrigin: true
  //     }
  //   }
  // }
})
