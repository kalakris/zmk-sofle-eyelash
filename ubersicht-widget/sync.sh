#!/bin/bash
# Sync the keymap widget to Übersicht
# Run this after making changes to the widget or pulling updates

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIDGET_SOURCE="$SCRIPT_DIR/keymap.widget"
WIDGET_DEST="$HOME/Library/Application Support/Übersicht/widgets/keymap.widget"

echo "Syncing keymap widget..."

# Remove existing and copy fresh
rm -rf "$WIDGET_DEST"
cp -r "$WIDGET_SOURCE" "$WIDGET_DEST"

# Refresh Übersicht
osascript -e 'tell application "Übersicht" to refresh' 2>/dev/null || true

echo "Done!"
