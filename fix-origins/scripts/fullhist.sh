#!/bin/sh
# Create a bare repository that borrows every object from this checkout but has
# no shallow graft, so blame and log see history older than the graft point.
# The checkout itself is not modified. Prints the path to use as GIT_DIR.
#
# Usage (from the repo root):
#   export GIT_DIR=$(sh research/fix-origins/scripts/fullhist.sh <scratch>/fullhist.git)
set -e
dest=$1
objects=$(cd "$(git rev-parse --git-common-dir)/objects" && pwd)
[ -d "$dest" ] || git init -q --bare "$dest"
echo "$objects" > "$dest/objects/info/alternates"
GIT_DIR="$dest" git rev-parse --verify -q "${2:-HEAD}^{commit}" >/dev/null
echo "$dest"
