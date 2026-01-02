/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";
import istanbul from "vite-plugin-istanbul";
import tsconfigPaths from "vite-tsconfig-paths";
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { storybookTest } from '@storybook/addon-vitest/vitest-plugin';

const dirname = typeof __dirname !== 'undefined' ? __dirname : path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [
    TanStackRouterVite(),
    react(),
    tsconfigPaths(),
    istanbul({
      cypress: true,
      requireEnv: false
    })
  ],
  resolve: {
    alias: {
      "@": path.resolve(dirname, "src"),
      // Fix for MUI imports in Node 24
      // '@mui/system': '@mui/system/esm',
      // '@mui/material': '@mui/material/esm',
    }
  },
  // Fix for dynamic imports in Cypress and CI
  optimizeDeps: {
    include: [
      '@mui/material',
      '@mui/system',
      '@tanstack/react-router',
    ],
    esbuildOptions: {
      target: 'esnext',
    },
  },
  build: {
    target: 'esnext',
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
  // Help with module resolution in CI
  server: {
    fs: {
      strict: false,
    },
  },
  test: {
    projects: [{
      extends: true,
      plugins: [
        storybookTest({
          configDir: path.join(dirname, '.storybook')
        })
      ],
      test: {
        name: 'storybook',
        browser: {
          enabled: true,
          headless: true,
          provider: 'playwright',
          instances: [{
            browser: 'chromium'
          }]
        },
        setupFiles: ['.storybook/vitest.setup.ts']
      }
    }]
  }
});