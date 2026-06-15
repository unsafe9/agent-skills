#!/usr/bin/env bash
# Open Codex app via deep link with an optional workspace and prompt.
set -euo pipefail

DIR="$PWD"
PROMPT=""
PROMPT_FILE=""
ORIGIN_URL=""
THREAD_ID=""
PRINT_ONLY=false

usage() {
  cat <<'EOF'
Usage: codex-app-handoff.sh (--prompt <text> | --prompt-file <file> | --thread-id <uuid>) [options]

Options:
  --dir, -d          Local workspace directory for codex://threads/new. Default: current directory
  --prompt          Initial composer text for a new Codex app thread
  --prompt-file     Handoff brief path. The composer will ask Codex to read this file
  --origin-url      Git remote URL used to match a workspace root
  --thread-id       Existing Codex local thread UUID to open
  --print-only      Print the deep link instead of opening it
  --help, -h        Show this help
EOF
}

absolute_file() {
  local file=$1
  local parent base
  parent="$(dirname -- "$file")"
  base="$(basename -- "$file")"
  printf '%s/%s' "$(CDPATH= cd -- "$parent" && pwd -P)" "$base"
}

build_new_thread_url() {
  python3 - "$PROMPT" "$DIR" "$ORIGIN_URL" <<'PY'
import sys
from urllib.parse import quote, urlencode

prompt, path, origin_url = sys.argv[1:4]
params = []
if prompt:
    params.append(("prompt", prompt))
if path:
    params.append(("path", path))
if origin_url:
    params.append(("originUrl", origin_url))

query = urlencode(params, quote_via=quote)
print("codex://threads/new" + (f"?{query}" if query else ""))
PY
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --dir|-d) DIR="$2"; shift 2 ;;
    --prompt) PROMPT="$2"; shift 2 ;;
    --prompt-file) PROMPT_FILE="$2"; shift 2 ;;
    --origin-url) ORIGIN_URL="$2"; shift 2 ;;
    --thread-id) THREAD_ID="$2"; shift 2 ;;
    --print-only) PRINT_ONLY=true; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown: $1" >&2; exit 1 ;;
  esac
done

if [[ -n "$THREAD_ID" ]]; then
  if [[ -n "$PROMPT" || -n "$PROMPT_FILE" || -n "$ORIGIN_URL" ]]; then
    echo "Error: --thread-id cannot be combined with prompt or origin options" >&2
    exit 1
  fi
  URL="codex://threads/${THREAD_ID}"
else
  if [[ -n "$PROMPT" && -n "$PROMPT_FILE" ]]; then
    echo "Error: use only one of --prompt or --prompt-file" >&2
    exit 1
  fi
  if [[ -z "$PROMPT" && -z "$PROMPT_FILE" ]]; then
    echo "Error: --prompt or --prompt-file is required" >&2
    exit 1
  fi
  if [[ ! -d "$DIR" ]]; then
    echo "Error: --dir must be an existing directory: $DIR" >&2
    exit 1
  fi

  DIR="$(CDPATH= cd -- "$DIR" && pwd -P)"
  if [[ -n "$PROMPT_FILE" ]]; then
    [[ -f "$PROMPT_FILE" ]] || { echo "Error: prompt file not found: $PROMPT_FILE" >&2; exit 1; }
    PROMPT_FILE="$(absolute_file "$PROMPT_FILE")"
    PROMPT="Read the handoff brief at ${PROMPT_FILE} and continue the task from there."
  fi
  URL="$(build_new_thread_url)"
fi

if [[ "$PRINT_ONLY" == true ]]; then
  printf '%s\n' "$URL"
  exit 0
fi

if command -v open >/dev/null 2>&1; then
  open "$URL"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 &
else
  echo "Error: neither open nor xdg-open is available" >&2
  exit 1
fi

printf '%s\n' "$URL"
