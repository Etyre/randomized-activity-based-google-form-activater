#!/bin/bash

# Setup script for randomized presence checker

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="$SCRIPT_DIR/com.user.presencechecker.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "Setting up randomized presence checker..."

# Make Python script executable
chmod +x "$SCRIPT_DIR/presence_checker.py"

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Copy plist to LaunchAgents
cp "$PLIST_FILE" "$LAUNCH_AGENTS_DIR/"

# Load the launch agent
launchctl load "$LAUNCH_AGENTS_DIR/com.user.presencechecker.plist"

echo "Setup complete!"
echo ""
echo "The presence checker is now running in the background."
echo "To stop it: launchctl unload ~/Library/LaunchAgents/com.user.presencechecker.plist"
echo "To start it: launchctl load ~/Library/LaunchAgents/com.user.presencechecker.plist"
echo ""
echo "Logs will be written to:"
echo "  $SCRIPT_DIR/presence_checker.log"
echo "  $SCRIPT_DIR/presence_checker_error.log"
echo ""
echo "IMPORTANT: Replace 'https://forms.gle/your-survey-link-here' with your actual survey URL"
echo "You can do this by editing the plist file at:"
echo "  $LAUNCH_AGENTS_DIR/com.user.presencechecker.plist"