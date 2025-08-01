#!/bin/bash

# BrowserGeist Example Runner
# Activates virtual environment and runs Python examples

if [ $# -eq 0 ]; then
    echo "Usage: ./run_example.sh <example_script.py>"
    echo "Example: ./run_example.sh examples/browser_automation_demo.py"
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Run the example
python3 "$@"
