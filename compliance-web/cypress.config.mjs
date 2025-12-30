import { defineConfig } from "cypress";

import react from "@vitejs/plugin-react-swc";
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";
import istanbul from "vite-plugin-istanbul";
import tsconfigPaths from "vite-tsconfig-paths";

import path from "node:path";
import { fileURLToPath } from "node:url";

const dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  component: {
    devServer: {
      framework: "react",
      bundler: "vite",
      viteConfig: {
        plugins: [
          TanStackRouterVite(),
          react(),
          tsconfigPaths(),
          istanbul({ cypress: true, requireEnv: false }),
        ],
        resolve: {
          alias: {
            "@": path.resolve(dirname, "src"),
          },
        },
      },
    },
  },
});
