# Foe Foundry

Foe Foundry is a Python/JavaScript web application that procedurally generates 5e-compatible monster statblocks with unique powers. It uses Poetry for Python dependency management, npm for JavaScript dependencies, MkDocs for documentation, and Vite for frontend assets.

The site is mostly static html generated via MkDocs, with a FastAPI backend for dynamic monster generation and a Whoosh-powered search API. There are some progressive enhancement JS scripts, as well as custom Lit.js based components for interactive features like the monster builder and statblock rendering. These are compiled using vite and included in the static site.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap, Build, and Test the Repository

**Environment Setup:**
- Install Poetry: `pip install poetry`
- Set environment variables: `export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8 && export SITE_URL=http://127.0.0.1:8080/ && export PUPPETEER_SKIP_DOWNLOAD=true`
- Install Python dependencies: `poetry install` -- takes 15 seconds
- Install npm dependencies: `PUPPETEER_SKIP_DOWNLOAD=true npm ci` -- takes 2 seconds

**Build Commands:**
- Full build: `./scripts/build_site.sh` -- takes 96 seconds. NEVER CANCEL. Set timeout to 180+ seconds.
  - Data preparation: ~20 seconds (poetry run python -m foe_foundry_data + foe_foundry_search)
  - MkDocs build: ~63 seconds
  - Vite build: ~0.5 seconds
- Fast build (development): `./scripts/build_site.sh --fast` -- takes 4 seconds. Skips data preparation and MkDocs build.
- Run tests: `SITE_URL=http://127.0.0.1:8080/ poetry run pytest` -- takes 6 minutes 25 seconds. NEVER CANCEL. Set timeout to 480+ seconds.

**Run the Application:**
- Start web server: `poetry run python -m foe_foundry_site` (serves on http://127.0.0.1:8080)
- Fast server mode: `poetry run python -m foe_foundry_site --fast`

## Validation

**ALWAYS manually validate any new code via these scenarios after making changes:**

### Critical User Scenarios to Test:
1. **Homepage loads**: `curl -s http://127.0.0.1:8080/` should return HTML with "Foe Foundry" title
2. **Powers API works**: `curl -s http://127.0.0.1:8080/api/v1/powers/random` should return JSON array of power objects
3. **Monster generator page loads**: `curl -s http://127.0.0.1:8080/generate/` should return HTML
4. **Search functionality**: Access `/powers/all/` and verify content loads
5. **Build completes without errors**: Both fast and full builds must complete successfully

### Test Environment Requirements:
- Always set `SITE_URL=http://127.0.0.1:8080/` when running tests
- Always set locale variables: `LC_ALL=en_US.UTF-8` and `LANG=en_US.UTF-8`
- Always set `PUPPETEER_SKIP_DOWNLOAD=true` for npm operations

### Validation Commands:
- After any Python code changes: `poetry run pytest -x` (stop on first failure for faster feedback)
- After build script changes: Test both `./scripts/build_site.sh` and `./scripts/build_site.sh --fast`
- After API changes: Test the web server starts and key endpoints respond correctly

## Common Tasks

### Environment Variables Required:
```bash
export PATH=$PATH:$HOME/.local/bin
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export SITE_URL=http://127.0.0.1:8080/
export PUPPETEER_SKIP_DOWNLOAD=true
```

### Repository Structure:
```
.
├── foe_foundry/          # Core Python package (monster generation logic)
├── foe_foundry_data/     # Data models and Jinja templates
├── foe_foundry_search/   # Whoosh search functionality
├── foe_foundry_site/     # FastAPI web application
├── docs/                 # MkDocs documentation source
├── scripts/              # Build and utility scripts
├── tests/                # Python tests
├── data/                 # Monster/power data files
├── models/               # ML models (large files)
├── site/                 # Generated static site output
├── cache/                # Generated data cache
├── package.json          # npm dependencies (Vite, Lit, Puppeteer)
└── pyproject.toml        # Poetry Python dependencies
```

### Key Files:
- `scripts/build_site.sh` - Main build script
- `mkdocs.yml` - Documentation configuration
- `vite.config.mjs` - Frontend build configuration
- `pyproject.toml` - Python dependencies and project config

### Development Workflow:
1. Make changes to Python code in `foe_foundry/`, `foe_foundry_data/`, etc.
2. Run fast build for rapid feedback: `./scripts/build_site.sh --fast`
3. Test locally: `poetry run python -m foe_foundry_site --fast`
4. Run subset of tests: `poetry run pytest tests/foe_foundry/ -x`
5. Before committing: Run full build and full test suite

### Known Issues and Workarounds:
- **Puppeteer fails**: Always use `PUPPETEER_SKIP_DOWNLOAD=true` for npm operations
- **Locale errors**: Always set `LC_ALL=en_US.UTF-8` and `LANG=en_US.UTF-8`
- **Poetry sync deprecation**: Warning about `--sync` can be ignored, or use `poetry sync` instead
- **SITE_URL errors**: Tests require `SITE_URL=http://127.0.0.1:8080/` environment variable
- **Whoosh warnings**: SyntaxWarnings from Whoosh library can be ignored
- **Monster generation errors**: Some API endpoints may return errors without full data preparation

### Dependencies Not Included:
- **wkhtmltopdf**: Required for PDF generation (pdfkit), install with `sudo apt install wkhtmltopdf`
- **Ghostscript**: Required for print.sh script, install with `sudo apt install ghostscript`
- **Code formatting**: No black/flake8 configured - manual formatting required

### Performance Notes:
- **Full build**: 96 seconds (never cancel, expect MkDocs to take majority of time)
- **Fast build**: 4 seconds (good for development iterations)
- **Tests**: 6+ minutes (comprehensive test suite, never cancel)
- **Poetry install**: 15 seconds (when deps cached)
- **npm ci**: 2 seconds (when Puppeteer skipped)

### Build Timeouts (NEVER CANCEL):
- Poetry operations: 300+ seconds
- Full build: 180+ seconds minimum
- Tests: 480+ seconds minimum
- Any build that appears hung: Wait at least 120 seconds before investigating

Always run the full build and test suite before finalizing changes to ensure nothing is broken.