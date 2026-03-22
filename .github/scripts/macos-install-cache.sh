#!/usr/bin/env bash
set -eu
echo "Restoring Octave Cellar from cache archive..."
tar -xf ~/brew-octave-cellar.tar -C /
echo "Linking octave..."
brew link octave
