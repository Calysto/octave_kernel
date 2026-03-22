#!/usr/bin/env bash
set -eu
ls /opt/homebrew/Cellar | sort > /tmp/brew_cellar_before.txt
ls /opt/homebrew/opt | sort > /tmp/brew_opt_before.txt
echo "Installing octave..."
brew install octave
echo "Creating Cellar cache archive..."
NEW_CELLAR=$(comm -13 /tmp/brew_cellar_before.txt <(ls /opt/homebrew/Cellar | sort))
NEW_OPT=$(comm -13 /tmp/brew_opt_before.txt <(ls /opt/homebrew/opt | sort))
PATHS=()
while IFS= read -r f; do
  [ -d "/opt/homebrew/Cellar/$f" ] && PATHS+=("/opt/homebrew/Cellar/$f")
done <<< "$NEW_CELLAR"
while IFS= read -r f; do
  [ -e "/opt/homebrew/opt/$f" ] && PATHS+=("/opt/homebrew/opt/$f")
done <<< "$NEW_OPT"
tar -cf ~/brew-octave-cellar.tar "${PATHS[@]}"
echo "Cache archive created with ${#PATHS[@]} entries"
