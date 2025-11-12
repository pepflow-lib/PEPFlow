#!/usr/bin/env bash
#
# This script builds the project documentation and optionally serves it
# on a local web server for previewing.
#
# Usage:
#   scripts/build_doc.sh              (Builds the documentation)
#   scripts/build_doc.sh --serve      (Builds and then serves the documentation)
#   scripts/build_doc.sh --serve-only (Serves the documentation without building)

# --- Configuration ---
# Exit immediately if a command exits with a non-zero status.
set -Eeuo pipefail

# --- Variables ---
# Define directories and server port for easy modification.
readonly DOCS_DIR="docs"
readonly BUILD_DIR="${DOCS_DIR}/build/html"
readonly PORT=8000

# --- Functions ---

# Prints a usage message and exits.
usage() {
  cat << EOF
Usage: $(basename "$0") [OPTIONS]

Builds and/or serves the project documentation.
Default action is to build only.

Options:
  --serve         Build the documentation and then serve it locally.
  --serve-only    Serve existing documentation locally without building.
  -h, --help      Display this help message and exit.
EOF
  exit 1
}

# Builds the Sphinx/MkDocs documentation.
build_docs() {
  echo ">>> Building documentation..."
  if ! make -C "${DOCS_DIR}" html; then
    echo "❌ Error: Documentation build failed." >&2
    exit 1
  fi
  echo "✅ Documentation built successfully in '${BUILD_DIR}'"
}

# Serves the documentation on a local web server.
serve_docs() {
  # Check if the build directory exists before trying to serve.
  if [[ ! -d "${BUILD_DIR}" ]]; then
      echo "❌ Error: Build directory '${BUILD_DIR}' not found." >&2
      echo "    Please run the build first or check your DOCS_DIR configuration." >&2
      exit 1
  fi
  echo ">>> Starting local server at http://localhost:${PORT}"
  echo "    Serving files from '${BUILD_DIR}'"
  echo "    Press Ctrl+C to stop the server."
  python -m http.server --directory "${BUILD_DIR}" "${PORT}"
}

# --- Main Logic ---
main() {
  local build_flag=true
  local serve_flag=false

  # Parse command-line arguments.
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --serve)
        serve_flag=true
        shift # past argument
        ;;
      --serve-only)
        build_flag=false
        serve_flag=true
        shift # past argument
        ;;
      -h | --help)
        usage
        ;;
      *)
        echo "Unknown option: $1" >&2
        usage
        ;;
    esac
  done

  # --- Execution ---
  if [[ "${build_flag}" == true ]]; then
    build_docs
  fi

  if [[ "${serve_flag}" == true ]]; then
    serve_docs
  fi

  exit 0
}

# Run the main function, passing all script arguments to it.
main "$@"