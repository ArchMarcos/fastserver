import { defineConfig } from "vite";
import { resolve } from "path";

function apiProxy(target) {
  return {
    target,
    changeOrigin: true,
    // Não faz proxy de arquivos .html — serve como estático
    bypass(req) {
      if (req.url.includes(".html")) {
        return req.url;
      }
    },
  };
}

export default defineConfig({
  root: ".",
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, "index.html"),
        login: resolve(__dirname, "auth/login.html"),
        register: resolve(__dirname, "auth/register.html"),
        "client-dashboard": resolve(__dirname, "client/dashboard.html"),
        "merchant-dashboard": resolve(__dirname, "merchant/dashboard.html"),
        "driver-dashboard": resolve(__dirname, "driver/dashboard.html"),
        location: resolve(__dirname, "location.html"),
      },
    },
  },
  server: {
    port: parseInt(process.env.VITE_DEV_PORT) || 5173,
    proxy: {
      "/auth": apiProxy("http://0.0.0.0:3101"),
      "/client": apiProxy("http://0.0.0.0:3101"),
      "/merchant": apiProxy("http://0.0.0.0:3101"),
      "/driver": apiProxy("http://0.0.0.0:3101"),
      "/ordem": apiProxy("http://0.0.0.0:3101"),
      "/notifications": apiProxy("http://0.0.0.0:3101"),
    },
  },
});
