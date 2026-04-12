#!/bin/bash

# A script to automatically format and lint a Python project directory.

# Exit immediately if a command exits with a non-zero status.
set -e

# The directory containing your Python code.
# Use "." for the current directory.
PROJECT_DIR="."

echo "Running Ruff to automatically fix linting issues..."
# --fix will make changes directly to the files.
# The . after --fix specifies the target directory.
python3 -m ruff check --fix $PROJECT_DIR

echo "Running Black to format the code..."
# The . at the end specifies the target directory.
python3 -m black $PROJECT_DIR

echo "Automation complete. Code is formatted and linted."
echo "Please review the logical changes before committing."
