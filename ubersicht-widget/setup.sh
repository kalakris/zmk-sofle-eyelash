#!/bin/bash
# Setup script for ZMK Keymap Desktop Overlay
# Uses Übersicht to display the keymap SVG on your macOS desktop

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIDGET_SOURCE="$SCRIPT_DIR/keymap.widget"
WIDGET_DEST="$HOME/Library/Application Support/Übersicht/widgets/keymap.widget"

echo "=== ZMK Keymap Desktop Overlay Setup ==="

# Check if Übersicht is installed
if [ ! -d "/Applications/Übersicht.app" ]; then
    echo "Installing Übersicht..."
    if command -v brew &> /dev/null; then
        brew install --cask ubersicht
    else
        echo "Error: Homebrew not found. Please install Übersicht manually from:"
        echo "  https://tracesof.net/uebersicht/"
        exit 1
    fi
else
    echo "Übersicht is already installed."
fi

# Create widgets directory if it doesn't exist
mkdir -p "$HOME/Library/Application Support/Übersicht/widgets"

# Remove existing widget if present (symlink or directory)
if [ -e "$WIDGET_DEST" ] || [ -L "$WIDGET_DEST" ]; then
    echo "Removing existing keymap widget..."
    rm -rf "$WIDGET_DEST"
fi

# Copy the widget
echo "Copying widget..."
cp -r "$WIDGET_SOURCE" "$WIDGET_DEST"

# Add Übersicht to login items (if not already added)
if ! osascript -e 'tell application "System Events" to get the name of every login item' | grep -q "Übersicht"; then
    echo "Adding Übersicht to login items..."
    osascript -e 'tell application "System Events" to make login item at end with properties {path:"/Applications/Übersicht.app", hidden:false}'
else
    echo "Übersicht is already in login items."
fi

# Launch Übersicht
echo "Launching Übersicht..."
open -a "Übersicht"

# Give it a moment to start, then refresh
sleep 2
osascript -e 'tell application "Übersicht" to refresh' 2>/dev/null || true

echo ""
echo "=== Setup complete! ==="
echo "Your keymap should now be visible at the bottom-right of your desktop."
echo ""
echo "To update the widget after changes, run: $SCRIPT_DIR/sync.sh"
echo ""
echo "To customize the overlay, edit: $WIDGET_SOURCE/index.jsx"
echo "  - Adjust 'scale(0.8)' to change size"
echo "  - Adjust 'opacity: 0.85' to change transparency"
echo "  - Adjust 'bottom/right' values to change position"
