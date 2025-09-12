#!/usr/bin/env python3
"""
Code formatting script using Ruff to ensure consistent code formatting.

This script can be used by both developers and GitHub Copilot agents to maintain
consistent code style across the project.
"""

import subprocess
import sys
from pathlib import Path


def run_ruff_format(check_only: bool = False) -> bool:
    """
    Run Ruff formatter on the codebase.

    Args:
        check_only: If True, only check formatting without making changes

    Returns:
        True if no formatting issues found, False otherwise
    """
    cmd = ["poetry", "run", "ruff", "format"]
    if check_only:
        cmd.append("--check")

    # Add all Python package directories
    python_dirs = [
        "foe_foundry",
        "foe_foundry_data",
        "foe_foundry_search",
        "foe_foundry_site",
        "foe_foundry_agent",
        "scripts",
        "tests",
        "docs_gen",
    ]

    # Only add directories that exist
    existing_dirs = [d for d in python_dirs if Path(d).exists()]
    cmd.extend(existing_dirs)

    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False


def run_ruff_check_and_fix() -> bool:
    """
    Run Ruff linting with auto-fixes (organize imports, etc.).

    Returns:
        True if no issues found, False otherwise
    """
    cmd = ["poetry", "run", "ruff", "check", "--fix"]

    # Add all Python package directories
    python_dirs = [
        "foe_foundry",
        "foe_foundry_data",
        "foe_foundry_search",
        "foe_foundry_site",
        "foe_foundry_agent",
        "scripts",
        "tests",
        "docs_gen",
    ]

    # Only add directories that exist
    existing_dirs = [d for d in python_dirs if Path(d).exists()]
    cmd.extend(existing_dirs)

    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False


def main():
    """Main entry point for the formatting script."""
    import argparse

    parser = argparse.ArgumentParser(description="Format Python code using Ruff")
    parser.add_argument(
        "--check", action="store_true", help="Check formatting without making changes"
    )
    parser.add_argument(
        "--lint-only",
        action="store_true",
        help="Only run linting/import organization, skip formatting",
    )

    args = parser.parse_args()

    success = True

    if not args.lint_only:
        print("Running Ruff formatter...")
        if not run_ruff_format(check_only=args.check):
            success = False
            if args.check:
                print("❌ Code formatting issues found!")
            else:
                print("❌ Formatting failed!")
        else:
            if args.check:
                print("✅ Code formatting looks good!")
            else:
                print("✅ Code formatted successfully!")

    if not args.check:  # Only run linting when not in check mode
        print("\nRunning Ruff linting and import organization...")
        if not run_ruff_check_and_fix():
            success = False
            print("❌ Linting issues found!")
        else:
            print("✅ Code linting passed!")

    if success:
        print("\n🎉 All formatting checks passed!")
        sys.exit(0)
    else:
        print("\n💥 Some formatting issues need attention!")
        sys.exit(1)


if __name__ == "__main__":
    main()
