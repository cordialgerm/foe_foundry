import { defineConfig } from 'vite';

export default defineConfig({
    root: 'docs/generator-example', // Set the root directory for your project
    build: {
        outDir: '../../site', // Output directory for the bundled files
        emptyOutDir: false,   // don't clear stuff that other scripts built
        rollupOptions: {
            input: 'docs/generator-example/index.html' // entry point for the application
        }
    },
});
