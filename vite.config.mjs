import { defineConfig, loadEnv } from 'vite';
import { glob } from 'glob';
import path from 'path';

export default defineConfig(({ mode }) => {
    // Load env file from project root
    const env = loadEnv(mode, process.cwd(), '');

    // Find all page TypeScript files
    const pageFiles = glob.sync('foe_foundry_ui/src/pages/*.ts');
    
    // Create input object with main entry and page entries
    const input = {
        main: 'foe_foundry_ui/vite.html' // Main entry point
    };
    
    // Add each page file as an entry point
    pageFiles.forEach(file => {
        const name = path.basename(file, '.ts');
        input[name] = file;
    });

    return {
        root: 'foe_foundry_ui/', // Set the root directory for your project
        envDir: '../', // Look for .env files in the project root
        build: {
            outDir: '../site', // Output directory for the bundled files
            emptyOutDir: false,   // don't clear stuff that other scripts built
            rollupOptions: {
                input: input, // Multiple entry points
                output: {
                    entryFileNames: (chunkInfo) => {
                        // Main bundle keeps the same name pattern for now (we'll add hashing later)
                        if (chunkInfo.name === 'main') {
                            return 'scripts/main-[hash].js';
                        }
                        // Page-specific bundles
                        return 'scripts/[name]-[hash].js';
                    },
                    chunkFileNames: 'scripts/[name]-[hash].js', // Output chunk files with hash
                    assetFileNames: (assetInfo) => {
                        // CSS files go to css/ directory with hash
                        if (assetInfo.name && assetInfo.name.endsWith('.css')) {
                            return 'css/[name]-[hash][extname]';
                        }
                        // Other assets go to assets/ directory
                        return 'assets/[name]-[hash][extname]';
                    },
                },
            }
        },
    };
});
