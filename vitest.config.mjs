import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json'],
      include: ['docs/src/**/*.ts'],
      exclude: ['docs/src/**/*.test.ts', 'tests/**/*', 'docs/src/**/*.d.ts']
    },
    // Ensure test environment skips browser downloads
    env: {
      PUPPETEER_SKIP_DOWNLOAD: 'true'
    }
  },
  esbuild: {
    target: 'es2020'
  },
  resolve: {
    alias: {
      '@': '/docs/src'
    }
  }
});