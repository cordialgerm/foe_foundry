import { defineConfig } from 'vite';

export default defineConfig({
    root: 'docs/', // Set the root directory for your project
    build: {
        outDir: '../site', // Output directory for the bundled files
        emptyOutDir: false,   // don't clear stuff that other scripts built
        rollupOptions: {
            input: 'docs/generate.html' // entry point for the application
        }
    },
});
