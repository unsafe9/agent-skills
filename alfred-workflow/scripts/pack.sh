#!/bin/bash
# Package an Alfred workflow folder into a .alfredworkflow file.
# A .alfredworkflow is a zip of the folder CONTENTS (info.plist at archive root).
# Usage: pack.sh <workflow-dir> [output.alfredworkflow]
set -euo pipefail

dir="${1:?usage: pack.sh <workflow-dir> [output.alfredworkflow]}"
[ -f "$dir/info.plist" ] || { echo "ERROR: $dir/info.plist not found" >&2; exit 1; }

if [ $# -ge 2 ]; then
  out="$2"
else
  name=$(plutil -extract name raw "$dir/info.plist" 2>/dev/null || basename "$dir")
  out="$PWD/$(echo "$name" | tr ' /' '--').alfredworkflow"
fi
case "$out" in /*) ;; *) out="$PWD/$out";; esac

rm -f "$out"
(cd "$dir" && zip -r -q "$out" . -x "prefs.plist" -x ".*" -x "*/.*" -x "*.alfredworkflow")
echo "$out"
