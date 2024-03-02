#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

# Check if the virtual environment itself exists, not just the activation script
if [ ! -d "venv" ]; then
  # Create a virtual environment if it doesn't exist
  python3 -m venv venv
fi

# Activate the virtual environment
# No need to check if it exists now; it is either found or newly created above
source venv/bin/activate

# Check if the requirements are already installed by attempting to list them
# Install required packages if pip freeze shows nothing (assuming requirements.txt is exhaustive)
if ! pip freeze > /dev/null; then
  pip install -r requirements.txt
fi

# Run the Python script
python chat_interface.py

# Wait for a key press before exiting
read -p "Press any key to continue . . . " -n1 -s
echo # Adds a newline for cleaner terminal output