#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

# Check if the virtual environment directory exists
if [ ! -d ".venv/bin/activate" ]; then
  # Create a virtual environment if it doesn't exist
  python3 -m venv .venv
  # Activate the virtual environment
  source .venv/bin/activate
  # Install required packages
  pip install -r requirements.txt
else
  # Activate the virtual environment
  source .venv/bin/activate
fi

# Run the Python script
python chat_interface.py

# Wait for a key press before exiting
read -p "Press any key to continue . . . " -n1 -s