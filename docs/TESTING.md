# Development and Testing Setup

## Network Isolation in Testing

The test environment is configured to prevent network calls that would otherwise occur when installing browser automation dependencies:

### Problem Solved
Previously, running `npm install` or `npm test` would trigger network calls to:
- `googlechromelabs.github.io` (for Chrome browser downloads)
- `https://storage.googleapis.com/chrome-for-testing-public/` (for Chrome binaries)

These downloads were occurring due to Puppeteer's automatic browser installation during package setup.

### Solution Implemented
1. **Puppeteer Download Prevention**: Added `preinstall` script that sets `PUPPETEER_SKIP_DOWNLOAD=true`
2. **Test Script Configuration**: All test commands explicitly set the environment variable
3. **Clear Separation**: Documented which tools require browsers vs which don't

## Scripts for Development vs Testing

### Testing Scripts (No Browser Downloads Required)
```bash
npm test                    # Run all tests once (skips browser downloads)
npm run test:watch         # Watch mode for development
npm run test:ui            # Interactive UI for debugging  
npm run test:coverage      # Generate coverage report
npm run install:test       # Explicit test-only installation
```

### Development Scripts (Require Browser Downloads)
```bash
npm run install:dev        # Install all dependencies including browsers
npm run record_monster     # Record video demos (requires Playwright browsers)
./scripts/print.sh         # Generate PDFs (requires Puppeteer Chrome)
```

## Local Development Tools

The following scripts are for local development only and require browser installations:

- **`scripts/print-to-pdf.js`**: Uses Puppeteer to generate PDF exports of monster pages
- **`scripts/print.sh`**: Wrapper script for PDF generation with local server  
- **`scripts/record-monster/`**: Uses Playwright to record video demonstrations

These tools are **not needed for testing** and are excluded from the test environment to prevent unnecessary network calls.

## Complete Network Isolation in Tests

All tests run with complete network isolation:
- **API calls** to `foefoundry.com` are mocked in `tests/setup.ts`
- **SVG icon loading** is mocked to return test content
- **Browser downloads** are skipped via environment configuration
- **Components** use dependency injection for mock vs real stores

This ensures tests can run independently without requiring a backend server, browser downloads, or any external network access.

## Configuration Details

The network isolation is achieved through:

1. **Package.json preinstall script** - Sets `PUPPETEER_SKIP_DOWNLOAD=true` during installation
2. **Test command environment variables** - All test scripts ensure the skip flag is set
3. **Vitest configuration** - Test environment explicitly sets the skip flag
4. **Fetch mocking** - Global fetch mock in test setup prevents any remaining network calls

This configuration allows the test suite to run completely offline while preserving the ability to use browser automation tools for local development when needed.