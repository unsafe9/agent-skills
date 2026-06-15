#!/usr/bin/env bash
# Launch an agent CLI in a tmux window.
# Usage: tmux-handoff.sh --agent <claude|codex> -w <name> (-p <file> | --prompt <text>) [-s <session>] [-d <dir>] [--skip-permissions] [--agent-args '<flags>']
set -euo pipefail

SESSION="work"
WINDOW=""
PROMPT_FILE=""
PROMPT=""
DIR="$PWD"
SKIP_PERMS=false
AGENT="claude"
AGENT_ARGS=""
DRY_RUN=false

shell_quote() {
  printf '%q' "$1"
}

join_quoted() {
  local out="" arg
  for arg in "$@"; do
    if [[ -n "$out" ]]; then
      out+=" "
    fi
    out+="$(shell_quote "$arg")"
  done
  printf '%s' "$out"
}

absolute_file() {
  local file=$1
  local parent base
  parent="$(dirname -- "$file")"
  base="$(basename -- "$file")"
  printf '%s/%s' "$(CDPATH= cd -- "$parent" && pwd -P)" "$base"
}

usage() {
  cat <<'EOF'
Usage: tmux-handoff.sh --agent <claude|codex> -w <name> (-p <file> | --prompt <text>) [options]

Options:
  --agent                Agent CLI to launch: claude, codex. Default: claude
  --session, -s          tmux session name. Default: work
  --window, -w           tmux window name
  --prompt-file, -p      Prompt file path
  --prompt               Inline prompt text
  --dir, -d              Working directory for the tmux window. Default: current directory
  --skip-permissions     Add the matching dangerous bypass flag for the selected agent
  --agent-args           Extra CLI flags for the selected agent as a raw string
  --claude-args          Extra Claude Code flags as a raw string
  --codex-args           Extra Codex CLI flags as a raw string
  --dry-run              Print the tmux target and command without launching
  --help, -h             Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --agent) AGENT="$2"; shift 2 ;;
    --session|-s) SESSION="$2"; shift 2 ;;
    --window|-w) WINDOW="$2"; shift 2 ;;
    --prompt-file|-p) PROMPT_FILE="$2"; shift 2 ;;
    --prompt) PROMPT="$2"; shift 2 ;;
    --dir|-d) DIR="$2"; shift 2 ;;
    --skip-permissions) SKIP_PERMS=true; shift ;;
    --agent-args|--claude-args|--codex-args) AGENT_ARGS="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$WINDOW" ]]; then
  echo "Error: --window is required" >&2; exit 1
fi
if [[ -z "$PROMPT_FILE" && -z "$PROMPT" ]]; then
  echo "Error: --prompt-file or --prompt is required" >&2; exit 1
fi
if [[ -n "$PROMPT_FILE" && -n "$PROMPT" ]]; then
  echo "Error: use only one of --prompt-file or --prompt" >&2; exit 1
fi
if [[ ! -d "$DIR" ]]; then
  echo "Error: --dir must be an existing directory: $DIR" >&2; exit 1
fi

WINDOW="${WINDOW//[.:]/-}"
DIR="$(CDPATH= cd -- "$DIR" && pwd -P)"

case "$AGENT" in
  claude|claude-code|claude_code)
    AGENT="claude"
    if [[ -n "$PROMPT_FILE" ]]; then
      [[ -f "$PROMPT_FILE" ]] || { echo "Error: prompt file not found: $PROMPT_FILE" >&2; exit 1; }
      PROMPT_FILE="$(absolute_file "$PROMPT_FILE")"
      CMD="$(join_quoted claude "@$PROMPT_FILE")"
    else
      CMD="$(join_quoted claude "$PROMPT")"
    fi
    [[ "$SKIP_PERMS" == true ]] && CMD+=" --dangerously-skip-permissions"
    ;;
  codex|codex-cli|codex_cli)
    AGENT="codex"
    if [[ -n "$PROMPT_FILE" ]]; then
      [[ -f "$PROMPT_FILE" ]] || { echo "Error: prompt file not found: $PROMPT_FILE" >&2; exit 1; }
      PROMPT_FILE="$(absolute_file "$PROMPT_FILE")"
      CMD="codex \"\$(cat -- $(shell_quote "$PROMPT_FILE"))\""
    else
      CMD="$(join_quoted codex "$PROMPT")"
    fi
    [[ "$SKIP_PERMS" == true ]] && CMD+=" --dangerously-bypass-approvals-and-sandbox"
    ;;
  *)
    echo "Error: --agent must be claude or codex" >&2; exit 1
    ;;
esac

[[ -n "$AGENT_ARGS" ]] && CMD+=" $AGENT_ARGS"

if [[ "$DRY_RUN" == true ]]; then
  printf 'target=%s:%s\n' "$SESSION" "$WINDOW"
  printf 'dir=%s\n' "$DIR"
  printf 'agent=%s\n' "$AGENT"
  printf 'command=%s\n' "$CMD"
  exit 0
fi

if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux new-session -d -s "$SESSION" -n "$WINDOW" -c "$DIR"
else
  tmux new-window -t "$SESSION" -n "$WINDOW" -c "$DIR"
fi

tmux send-keys -t "${SESSION}:${WINDOW}" "$CMD" Enter
echo "${SESSION}:${WINDOW}"
