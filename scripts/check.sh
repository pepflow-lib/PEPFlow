#!/usr/bin/env bash
#
# quality.sh: A script to format, lint, type-check, and test the codebase.
#
# This script runs a series of checks to ensure code quality and correctness.
# It is designed to be run from the root of the project repository.
#
# Usage:
#   scripts/check.sh            # Run all checks: format, lint, type-check, and test.
#   scripts/check.sh format     # Only format the code.
#   scripts/check.sh lint       # Only lint and auto-fix the code.
#   scripts/check.sh typecheck  # Only run the type checker.
#   scripts/check.sh test       # Only run tests.

# --- Configuration ---
# Exit immediately if a command exits with a non-zero status.
set -Eeuo pipefail

# --- Variables & Colors ---
# Use tput for compatibility, with fallbacks for non-interactive shells.
if tput setaf 1 > /dev/null 2>&1; then
    readonly C_GREEN=$(tput setaf 2)
    readonly C_YELLOW=$(tput setaf 3)
    readonly C_BOLD=$(tput bold)
    readonly C_RESET=$(tput sgr0) # No Color
else
    # Provide fallback values if tput is not available
    readonly C_GREEN=""
    readonly C_YELLOW=""
    readonly C_BOLD=""
    readonly C_RESET=""
fi

# --- Helper Functions ---
info() {
    echo -e "${C_YELLOW}${C_BOLD}>>> $1${C_RESET}"
}

success() {
    echo -e "${C_GREEN}${C_BOLD}✅ $1${C_RESET}"
}

# --- Task Functions ---
run_format() {
    info "Running formatters (isort & ruff format)..."
    isort .
    ruff format .
}

run_lint() {
    info "Running linter (ruff check --fix)..."
    ruff check . --fix
}

run_typecheck() {
    info "Running type checker..."
    uvx ty check 
}

run_tests() {
    info "Running tests (pytest)..."
    pytest .
}

# --- Main Logic ---
main() {
    # Default to 'all' if no argument is provided.
    local command="${1:-all}"

    case "$command" in
        all)
            run_format
            run_lint
            run_typecheck
            run_tests
            ;;
        format)
            run_format
            ;;
        lint)
            run_lint
            ;;
        typecheck)
            run_typecheck
            ;;
        test)
            run_tests
            ;;
        *)
            echo "Error: Unknown command '$command'" >&2
            echo "Usage: $0 [all|format|lint|typecheck|test]" >&2
            exit 1
            ;;
    esac

    echo
    success "All selected checks passed successfully!"
}

# Run the main function, passing all script arguments to it.
main "$@"