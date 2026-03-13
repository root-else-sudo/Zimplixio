import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: resolve(__dirname, '../Zimplixio_site/static/dist'),
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(__dirname, 'src/main.tsx'),
      output: {
        // No hashing — WhiteNoise handles cache-busting in production
        entryFileNames: 'framework-accordion.js',
        assetFileNames: (info) =>
          info.name?.endsWith('.css') ? 'framework-accordion.css' : '[name][extname]',
        // Single file, no code splitting
        manualChunks: undefined,
      },
    },
  },
});
