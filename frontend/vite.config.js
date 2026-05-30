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

  const STARTUP_TRUTHY = new Set(['true', '1', 'yes'])
  const startupRaw = (env.STARTUP_STATUS || env.VITE_STARTUP_STATUS || '').trim().toLowerCase()
  const startupStatus = STARTUP_TRUTHY.has(startupRaw)

  const repoPackageRoot = path.resolve(__dirname, '..')

  return {
    plugins: [react()],
    envDir: rootDir,
    resolve: {
      alias: {
        // ZedReq/privacy.txt and terms.txt (sibling of frontend/)
        '@repoLegal': repoPackageRoot,
      },
    },
    define: {
      'import.meta.env.VITE_ZEDREQ_URL': JSON.stringify(zedreqUrl),
      'import.meta.env.VITE_ZEDREQ_EMAIL': JSON.stringify(zedreqEmail),
      'import.meta.env.VITE_STARTUP_STATUS': JSON.stringify(startupStatus),
    },
    server: {
      port: 3000,
      fs: {
        allow: [path.resolve(__dirname), repoPackageRoot],
      },
      proxy: {
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
        },
      },
    },
  }
})
