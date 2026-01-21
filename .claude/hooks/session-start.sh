#!/bin/bash
set -euo pipefail

# Only run in remote Claude Code environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "Setting up development environment..."

# Install GitHub CLI (gh) if not present
if ! command -v gh &> /dev/null; then
  echo "Installing GitHub CLI..."
  sudo apt-get update -qq
  sudo apt-get install -y -qq gh
  echo "GitHub CLI installed: $(gh --version | head -n1)"
fi

# Set up Python virtual environment and install dependencies
if [ -f "$CLAUDE_PROJECT_DIR/requirements.txt" ]; then
  echo "Setting up Python environment..."

  # Create venv if it doesn't exist
  if [ ! -d "$CLAUDE_PROJECT_DIR/.venv" ]; then
    python3 -m venv "$CLAUDE_PROJECT_DIR/.venv"
  fi

  # Activate venv for this script
  source "$CLAUDE_PROJECT_DIR/.venv/bin/activate"

  # Install dependencies
  pip install --quiet --upgrade pip
  pip install --quiet -r "$CLAUDE_PROJECT_DIR/requirements.txt"

  # Persist the venv activation for the session
  echo "source \"$CLAUDE_PROJECT_DIR/.venv/bin/activate\"" >> "$CLAUDE_ENV_FILE"

  echo "Python dependencies installed"
fi

echo "Development environment ready!"
