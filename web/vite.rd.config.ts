// vite.plano.config.ts — build SEPARADO del bundle standalone de las herramientas RD
// (web/rd.html -> web/src/mainRd.tsx). Deliberadamente un config
// aparte de vite.config.ts (no un segundo entry en el mismo config) para que
// el build normal del hub (`npm run build` / `build:context`, que usa
// vite.config.ts) quede 100% intacto -- cero riesgo de que esto cambie el
// nombre/hash de dist/index.html que copy-context.mjs espera.
//
// outDir separado (dist-rd) por el mismo motivo: no mezclar con dist/.
import path from "path";
import { fileURLToPath } from "url";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
  plugins: [react(), tailwindcss(), viteSingleFile()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  build: {
    outDir: "dist-rd",
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve(__dirname, "rd.html"),
    },
  },
});
