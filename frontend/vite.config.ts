import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // 开发服务器配置
  server: {
    port: 3000,
    host: true,
    proxy: {
      // 代理API请求到后端
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      },
      // WebSocket代理
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true
      }
    }
  },

  // 构建配置
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          // 将大型库分离为单独的chunk
          vendor: ['react', 'react-dom'],
          material: ['@mui/material', '@mui/icons-material'],
          three: ['three', '@react-three/fiber', '@react-three/drei'],
          router: ['react-router-dom'],
          redux: ['@reduxjs/toolkit', 'react-redux'],
          query: ['@tanstack/react-query'],
          utils: ['lodash', 'date-fns', 'axios']
        }
      }
    },
    // 增加chunk大小警告阈值
    chunkSizeWarningLimit: 1000
  },

  // 路径别名
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@services': resolve(__dirname, 'src/services'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@types': resolve(__dirname, 'src/types'),
      '@assets': resolve(__dirname, 'src/assets'),
      '@styles': resolve(__dirname, 'src/styles')
    }
  },

  // 预览服务器配置
  preview: {
    port: 3000,
    host: true
  },

  // 优化配置
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      '@mui/material',
      '@mui/icons-material',
      'three',
      '@react-three/fiber',
      '@react-three/drei',
      'axios',
      'socket.io-client'
    ]
  },

  // 环境变量配置
  envPrefix: 'REACT_APP_',

  // CSS配置
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  },

  // 定义全局变量
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    global: 'globalThis'
  },

  // 测试配置
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts']
  }
}) 