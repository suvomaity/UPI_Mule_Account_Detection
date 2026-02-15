import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

/**
 * Vite Configuration for UPI Mule Detection Frontend
 *
 * PORT CONFIGURATION NOTES:
 * ════════════════════════════════════════════════════════════
 *
 * Current Port: 3000 (instead of Vite's default 5173)
 *
 * Reasons for Port 3000:
 * 1. Industry Standard: Port 3000 is the de facto standard for local
 *    React/Node dev servers (used by Create React App, Next.js, etc.)
 * 2. Developer Familiarity: Most developers expect React apps on :3000
 * 3. Reduced Confusion: No need to explain why the app is on :5173
 * 4. Consistency: Makes instructions simpler for team members
 *
 * Backend Port: 8000 (FastAPI default)
 *
 * To change frontend port, update 'server.port' below or run:
 *   npm run dev -- --port 5173
 *
 * ════════════════════════════════════════════════════════════
 */

export default defineConfig({
  base: '/UPI_Mule_Account_Detection/',
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@services': path.resolve(__dirname, './src/services'),
      '@types': path.resolve(__dirname, './src/types'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@contexts': path.resolve(__dirname, './src/contexts'),
      '@config': path.resolve(__dirname, './src/config'),
    },
  },
  server: {
    port: 3000, // Keep at 3000 for developer familiarity (vs Vite default 5173)
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})

