import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The FastAPI backend's CORS list (see backend/main.py) allows
// http://localhost:3000 and http://localhost:5173 — this dev server
// runs on 5173 by default, so no backend changes are needed.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
