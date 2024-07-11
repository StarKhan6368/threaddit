import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    proxy: {
      "/api": {
        target: "https://elegant-manifestation-production.up.railway.app",
        changeOrigin: true,
        secure: false,
        ws: true,
      },
    },
  },
});
