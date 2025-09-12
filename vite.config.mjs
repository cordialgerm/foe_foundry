import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
    // Load env file from project root
    const env = loadEnv(mode, process.cwd(), '');

    return {
        root: 'foe_foundry_ui/', // Set the root directory for your project
        envDir: '../', // Look for .env files in the project root
        build: {
            outDir: '../site', // Output directory for the bundled files
            emptyOutDir: false,   // don't clear stuff that other scripts built
            rollupOptions: {
                input: 'foe_foundry_ui/vite.html', // entry point for the application
                output: {
                    entryFileNames: 'scripts/main.js', // Output JS files
                    chunkFileNames: 'scripts/[name].js', // Output chunk files
                    assetFileNames: 'assets/[name][extname]', // Output asset files
                },
            }
        },
    };
});
