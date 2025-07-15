import { defineConfig } from 'vite';

export default defineConfig({
    root: 'docs/generator-example', // Set the root directory for your project
    build: {
        outDir: 'js', // Output directory for the bundled files
        emptyOutDir: true,   // Clear the output directory before building
        rollupOptions: {
            input: 'docs/generator-example/src/main.ts' // entry point for the application
        }
    },
});
