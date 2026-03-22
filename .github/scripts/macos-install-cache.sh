#!/usr/bin/env bash
set -eu
echo "Restoring Octave Cellar from cache archive..."
tar -xf ~/brew-octave-cellar.tar -C /
echo "Linking octave..."
brew link octave
# Set Qt plugin path so octave can find the cocoa platform plugin
QT_PREFIX=$(brew --prefix qtbase 2>/dev/null || echo "/opt/homebrew/opt/qtbase")
echo "QT_QPA_PLATFORM_PLUGIN_PATH=$QT_PREFIX/share/qt/plugins/platforms" >> "$GITHUB_ENV"
echo "Set QT_QPA_PLATFORM_PLUGIN_PATH=$QT_PREFIX/share/qt/plugins/platforms"
