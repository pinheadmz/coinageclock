#!/usr/bin/env bash
# Reads fun/help_list.txt, calls `bitcoin-cli help <cmd>` for every RPC command,
# and writes a combined help file suitable for use as a Claude skill reference.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT="$SCRIPT_DIR/help_list.txt"
OUTPUT="$SCRIPT_DIR/rpc_help.md"

# Allow overriding the bitcoin-cli invocation (e.g. with -regtest or custom datadir)
BITCOIN_CLI="${BITCOIN_CLI:-bitcoin-cli}"

if [[ ! -f "$INPUT" ]]; then
  echo "ERROR: $INPUT not found" >&2
  exit 1
fi

current_section=""
failed=()

{
  echo "# Bitcoin Core RPC Reference"
  echo ""
  echo "Auto-generated from \`bitcoin-cli help <command>\`."
  echo ""
} > "$OUTPUT"

while IFS= read -r line || [[ -n "$line" ]]; do
  # Skip blank lines
  [[ -z "$line" ]] && continue

  # Section header lines like "== Blockchain =="
  if [[ "$line" =~ ^==\ (.+)\ ==$ ]]; then
    current_section="${BASH_REMATCH[1]}"
    echo "" >> "$OUTPUT"
    echo "## $current_section" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    echo "  Section: $current_section"
    continue
  fi

  # First token on the line is the command name
  cmd="${line%% *}"
  [[ -z "$cmd" ]] && continue

  echo "  Fetching help for: $cmd"

  help_text="$($BITCOIN_CLI help "$cmd" 2>&1)" || {
    echo "  WARNING: bitcoin-cli help $cmd failed" >&2
    failed+=("$cmd")
    help_text="(help not available)"
  }

  {
    echo "### $cmd"
    echo ""
    echo '```'
    echo "$help_text"
    echo '```'
    echo ""
  } >> "$OUTPUT"

done < "$INPUT"

echo ""
echo "Done. Output written to: $OUTPUT"

if [[ ${#failed[@]} -gt 0 ]]; then
  echo "Commands that failed: ${failed[*]}"
fi
