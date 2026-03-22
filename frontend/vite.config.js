import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const rootDir = path.resolve(__dirname, '..')

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, rootDir, '')
  const fromEnv = (env.ZEDREQ_URL || env.VITE_ZEDREQ_URL || '').replace(/\/$/, '')
  const devFallback = mode === 'development' ? 'http://localhost:3000' : ''
  const zedreqUrl = fromEnv || devFallback

  const zedreqEmail =
    (env.ZEDREQ_EMAIL || env.VITE_ZEDREQ_EMAIL || env.VITE_COMPANY_EMAIL || '').trim() ||
    'zed.req@yahoo.com'

  return {
    plugins: [react()],
    envDir: rootDir,
    define: {
      'import.meta.env.VITE_ZEDREQ_URL': JSON.stringify(zedreqUrl),
      'import.meta.env.VITE_ZEDREQ_EMAIL': JSON.stringify(zedreqEmail),
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
        },
      },
    },
  }
})
