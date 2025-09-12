# Code Formatting Guide

This project uses **Ruff** for Python code formatting and linting to ensure consistent code style across all contributors, including both manual editing and GitHub Copilot agents.

## Quick Start

```bash
# Format all Python code
python scripts/format_code.py

# Check formatting without making changes  
python scripts/format_code.py --check

# Alternative shell script
./scripts/format.sh --check
```

## Why Ruff?

Ruff is configured as the default Python formatter in VS Code settings and provides:

- **Fast formatting** (faster than Black)
- **Import organization** (replaces isort)
- **Linting** (replaces flake8 for basic checks)
- **VS Code integration** (matches manual editing behavior)
- **Black compatibility** (same formatting style)

## Configuration

The Ruff configuration is in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
indent-width = 4
target-version = "py312"

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "I"]  # Basic errors + import sorting
ignore = ["F401"]  # Allow unused imports in __init__.py

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

## Integration Points

### VS Code
- Configured in `.vscode/settings.json`
- Format on save enabled
- Organize imports on save enabled

### Pre-commit Hook
- Automatically checks formatting before commits
- Located in `.git/hooks/pre-commit`
- Prevents commits with formatting issues

### GitHub Copilot Instructions
- Updated in `.github/copilot-instructions.md`
- Instructs agents to run formatting after code changes

## Commands Reference

### Basic Usage
```bash
# Format all code
python scripts/format_code.py

# Check only (CI/pre-commit)
python scripts/format_code.py --check

# Only run linting (imports, etc)
python scripts/format_code.py --lint-only
```

### Shell Wrapper
```bash
# Equivalent to Python script
./scripts/format.sh
./scripts/format.sh --check
```

### Direct Ruff Commands
```bash
# Format specific files
poetry run ruff format file1.py file2.py

# Format all Python directories
poetry run ruff format foe_foundry/ tests/ scripts/

# Check formatting
poetry run ruff format --check .

# Lint and fix issues
poetry run ruff check --fix .
```

## For Contributors

### Manual Editing (VS Code)
- Code is automatically formatted on save
- Imports are automatically organized on save
- No additional action needed

### GitHub Copilot Agents
- **MUST** run `python scripts/format_code.py` after making Python changes
- This ensures consistency with manual editing

### Command Line Development
- Run `python scripts/format_code.py` before committing
- Pre-commit hook will catch formatting issues

## Troubleshooting

### "Command not found" errors
Make sure you're in the project root and have installed dependencies:
```bash
cd /path/to/foe_foundry
poetry install
```

### Formatting conflicts
If manual and automated formatting differ:
1. Update your VS Code Ruff extension
2. Check `.vscode/settings.json` matches the expected configuration
3. Run `python scripts/format_code.py` to normalize to project standards

### Pre-commit hook not working
```bash
# Reinstall the hook
chmod +x .git/hooks/pre-commit
```