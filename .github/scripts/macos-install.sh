#!/usr/bin/env bash
set -eu
ls /opt/homebrew/Cellar | sort > /tmp/brew_before.txt
echo "Installing octave..."
brew install octave
echo "Creating Cellar cache archive..."
NEW_FORMULAE=$(comm -13 /tmp/brew_before.txt <(ls /opt/homebrew/Cellar | sort))
PATHS=()
while IFS= read -r f; do
  [ -d "/opt/homebrew/Cellar/$f" ] && PATHS+=("/opt/homebrew/Cellar/$f")
  [ -e "/opt/homebrew/opt/$f" ] && PATHS+=("/opt/homebrew/opt/$f")
done <<< "$NEW_FORMULAE"
sudo tar -cf ~/brew-octave-cellar.tar "${PATHS[@]}"
echo "Cache archive created: ~/brew-octave-cellar.tar"
