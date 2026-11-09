import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
// https://vitejs.dev/config/
export default defineConfig(function (_a) {
    var _b;
    var mode = _a.mode;
    var env = loadEnv(mode, '.', '');
    var proxyTarget = (_b = env.VITE_PROXY_TARGET) !== null && _b !== void 0 ? _b : 'http://localhost:8000';
    return {
        plugins: [react()],
        server: {
            port: 5173,
            host: true,
            proxy: {
                '/api': {
                    target: proxyTarget,
                    changeOrigin: true,
                },
                '/health': {
                    target: proxyTarget,
                    changeOrigin: true,
                },
            },
        },
    };
});
