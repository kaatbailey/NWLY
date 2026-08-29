#!/usr/bin/env bash
# T4 bulk compile triage.
# Compiles every AzCore .cpp independently with the proven recipe and reports
# which fail and why, so failures get fixed in groups rather than one per probe.
#
# Usage:  bash triage.sh [azcore|gridmate]

set -uo pipefail

LY="${HOME}/Documents/lumberyard/dev/Code/Framework"
AZCORE="${LY}/AzCore"
GRIDMATE="${LY}/GridMate"
OUT=$(mktemp -d)
TARGET="${1:-azcore}"

FLAGS=(
  -std=c++17 -Wno-error -include utility -fdelayed-template-parsing
  -Wno-deprecated-literal-operator -Wno-deprecated-declarations
  -Wno-unused-parameter -Wno-unused-variable
  -I "${AZCORE}" -I "${AZCORE}/Platform/Linux"
)

if [[ "${TARGET}" == "gridmate" ]]; then
  FLAGS+=(-I "${GRIDMATE}" -I "${GRIDMATE}/Platform/Linux"
          -DAZ_TRAIT_GRIDMATE_TEST_WITH_SECURE_SOCKET_DRIVER=1)
  mapfile -t FILES < <(find "${GRIDMATE}/GridMate" "${GRIDMATE}/Platform/Linux" \
                            -name '*.cpp' 2>/dev/null)
else
  mapfile -t FILES < <(find "${AZCORE}/AzCore" "${AZCORE}/Platform/Linux" \
                            -name '*.cpp' 2>/dev/null)
fi

total=${#FILES[@]}
ok=0; fail=0
: > "${OUT}/failed.txt"
: > "${OUT}/errors.txt"

echo "Compiling ${total} ${TARGET} files..."
for f in "${FILES[@]}"; do
  if clang++ "${FLAGS[@]}" -fsyntax-only "$f" 2> "${OUT}/e.txt"; then
    ok=$((ok+1))
  else
    fail=$((fail+1))
    echo "$f" >> "${OUT}/failed.txt"
    { echo "=== $f"; grep -m5 'error:' "${OUT}/e.txt"; } >> "${OUT}/errors.txt"
  fi
  printf '\r  ok=%d fail=%d / %d' "$ok" "$fail" "$total"
done
echo

echo
echo "===== RESULT: ${ok}/${total} compiled, ${fail} failed ====="
if (( fail > 0 )); then
  echo
  echo "===== DISTINCT ERROR KINDS (most common first) ====="
  grep 'error:' "${OUT}/errors.txt" \
    | sed 's/.*error: //' | sed 's/'"'"'[^'"'"']*'"'"'/X/g' \
    | sort | uniq -c | sort -rn | head -20
  echo
  echo "Full detail:   ${OUT}/errors.txt"
  echo "Failed files:  ${OUT}/failed.txt"
fi
