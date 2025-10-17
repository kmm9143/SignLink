import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
    plugins: [react()],
    resolve: { alias: { src: path.resolve(__dirname, 'src') } },
    server: {
        port: 51233, // match the origin your browser uses
        proxy: {
            '/auth': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                secure: false,
                // optional: preserve path by default; use rewrite if backend expects different prefix
                // rewrite: (path) => path.replace(/^\/auth/, '/auth')
            },
            '/settings': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                secure: false,
            },
            '/image': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                secure: false,
            },
            '/video': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                secure: false,
            },
        },
    },
});