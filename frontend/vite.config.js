import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // 允许局域网访问
    port: 5173,      // 前端端口
    proxy: {
      // 代理配置：当前端请求以 /api 开头时，转发到 Django 后端
      '/api': {
        target: 'http://127.0.0.1:8000', 
        changeOrigin: true,
      }
    }
  }
})