#!/usr/bin/env bash
#
# NWLY / T4 step 2+3 — build libazcore.a and libgridmate.a from the Lumberyard fork.
#
# Uses the toolchain recipe confirmed in T4 step 1 (STATE §7):
#   -std=c++17 -include utility -fdelayed-template-parsing
# plus -DDTLS1_RT_HEARTBEAT=24 for the one OpenSSL-3 removal in
# SecureSocketDriver.cpp (see STATE §7 / test-log).
#
# NOTHING is written inside the Lumberyard tree. All objects and archives go to
# --out (default ./build), so the fork stays byte-identical to its pinned commit
# per CHARTER §3.
#
# Failures do NOT abort the build. ~45 AzCore TUs need Lumberyard's 3rdParty
# (rapidjson, Lua, zstd, jni, gmock) which is not in the repo; none of them are
# on GridMate's dependency surface. The script compiles what it can, archives
# that, and prints exactly what failed and why. Read the summary -- do not
# assume a nonzero failure count means the build is broken.
#
# Usage, from the NWLY repo:
#   ./build_gridmate.sh                       # build both archives
#   ./build_gridmate.sh --ly ~/src/lumberyard # different fork location
#   ./build_gridmate.sh -j 8                  # limit parallelism
#   ./build_gridmate.sh --clean               # wipe build dir first
#   ./build_gridmate.sh --azcore-only
#   ./build_gridmate.sh --show-failures       # full error text, not just causes

set -u -o pipefail

LY="${HOME}/Documents/lumberyard"
OUT="./build"
JOBS="$(nproc 2>/dev/null || echo 4)"
CLEAN=0
AZCORE_ONLY=0
SHOW_FAIL=0
CXX="${CXX:-clang++}"

while [ $# -gt 0 ]; do
    case "$1" in
        --ly)            LY="$2"; shift 2 ;;
        --out)           OUT="$2"; shift 2 ;;
        -j|--jobs)       JOBS="$2"; shift 2 ;;
        --clean)         CLEAN=1; shift ;;
        --azcore-only)   AZCORE_ONLY=1; shift ;;
        --show-failures) SHOW_FAIL=1; shift ;;
        -h|--help)       sed -n '2,32p' "$0"; exit 0 ;;
        *) echo "unknown option: $1  (try --help)" >&2; exit 2 ;;
    esac
done

LY="${LY/#\~/$HOME}"
FW="$LY/dev/Code/Framework"

# ---- sanity ---------------------------------------------------------------
if [ ! -d "$FW/AzCore/AzCore" ]; then
    echo "ERROR: no AzCore at $FW/AzCore/AzCore"
    echo "  --ly should point at the lumberyard repo root (the dir containing 'dev')."
    echo "  Currently: $LY"
    exit 1
fi
if [ ! -d "$FW/AzCore/Platform/Common" ]; then
    echo "ERROR: $FW/AzCore/Platform/Common is missing."
    echo "  Linux math headers reach into Platform/Common/SIMD. A sparse checkout"
    echo "  that omits it fails with a confusing error pointing at the Linux header."
    exit 1
fi
command -v "$CXX" >/dev/null || { echo "ERROR: $CXX not found"; exit 1; }
echo "$(printf '#include <openssl/ssl.h>\nint main(){return 0;}')" > /tmp/.nwly_ossl.cpp
if ! "$CXX" -fsyntax-only /tmp/.nwly_ossl.cpp 2>/dev/null; then
    echo "ERROR: OpenSSL headers not found. Install them (Arch: 'openssl' provides them)."
    rm -f /tmp/.nwly_ossl.cpp; exit 1
fi
rm -f /tmp/.nwly_ossl.cpp

[ "$CLEAN" = 1 ] && rm -rf "$OUT"
mkdir -p "$OUT/obj" "$OUT/logs"
OUT_ABS="$(cd "$OUT" && pwd)"

RECIPE=(-std=c++17 -include utility -fdelayed-template-parsing -w
        -DDTLS1_RT_HEARTBEAT=24 -fPIC -O1)
INC=(-I AzCore -I AzCore/Platform/Linux -I GridMate -I GridMate/Platform/Linux)

# Platforms that are not ours. Anything matching is never compiled.
# Platform dirs that are not ours. 'Apple' covers Platform/Common/Apple, shared
# by Mac and iOS, which pulls mach-o/*, mach/* and sys/sysctl.h -- none of which
# exist on Linux.
EXCLUDE='/(WinAPI|Windows|Android|Apple|AppleTV|Mac|iOS|Salem|Provo|Jasper)/|/Tests?/'
# StackTracer_UnixLike.cpp needs libunwind: optional, and not on GridMate's
# dependency surface. Drop this line and install libunwind if you later want
# symbolised AzCore stack traces.
EXCLUDE="$EXCLUDE|StackTracer_UnixLike"

echo "lumberyard : $LY"
echo "output     : $OUT_ABS"
echo "compiler   : $($CXX --version | head -1)"
echo "jobs       : $JOBS"
echo

# ---- one TU; never fails the run ------------------------------------------
compile_one() {
    local src="$1"
    local obj="$OUT_ABS/obj/$(echo "$src" | tr '/' '_' | sed 's/\.cpp$/.o/')"
    local log="$OUT_ABS/logs/$(echo "$src" | tr '/' '_' | sed 's/\.cpp$/.log/')"
    if [ -f "$obj" ] && [ "$obj" -nt "$src" ]; then
        echo "CACHED $src"; return 0
    fi
    if "$CXX" "${RECIPE[@]}" "${INC[@]}" -c "$src" -o "$obj" 2>"$log"; then
        echo "OK $src"
    else
        rm -f "$obj"
        echo "FAIL $src"
    fi
}
export -f compile_one
export OUT_ABS CXX
export RECIPE_STR="${RECIPE[*]}"
export INC_STR="${INC[*]}"

# bash arrays don't survive export; rebuild them inside the subshell
compile_one_wrapper() {
    local src="$1"
    local obj="$OUT_ABS/obj/$(echo "$src" | tr '/' '_' | sed 's/\.cpp$/.o/')"
    local log="$OUT_ABS/logs/$(echo "$src" | tr '/' '_' | sed 's/\.cpp$/.log/')"
    if [ -f "$obj" ] && [ "$obj" -nt "$src" ]; then echo "CACHED $src"; return 0; fi
    # shellcheck disable=SC2086
    if $CXX $RECIPE_STR $INC_STR -c "$src" -o "$obj" 2>"$log"; then
        echo "OK $src"
    else
        rm -f "$obj"; echo "FAIL $src"
    fi
}
export -f compile_one_wrapper

build_lib() {
    local label="$1" archive="$2"; shift 2
    local roots=("$@")
    echo "=== $label ==="

    local list="$OUT_ABS/.$label.files"
    find "${roots[@]}" -name '*.cpp' 2>/dev/null | grep -Ev "$EXCLUDE" | sort > "$list"
    local total; total=$(wc -l < "$list")
    echo "  $total translation units"

    local res="$OUT_ABS/.$label.result"
    xargs -a "$list" -d '\n' -P "$JOBS" -I{} bash -c 'compile_one_wrapper "$@"' _ {} > "$res"

    local ok fail cached
    ok=$(grep -c '^OK '     "$res" || true)
    fail=$(grep -c '^FAIL ' "$res" || true)
    cached=$(grep -c '^CACHED ' "$res" || true)
    echo "  compiled $ok, cached $cached, failed $fail"

    if [ "$fail" -gt 0 ]; then
        echo
        echo "  failures grouped by cause:"
        grep '^FAIL ' "$res" | sed 's/^FAIL //' | while read -r f; do
            local lg="$OUT_ABS/logs/$(echo "$f" | tr '/' '_' | sed 's/\.cpp$/.log/')"
            grep -m1 -E 'error:' "$lg" 2>/dev/null | sed 's/.*error: //'
        done | sort | uniq -c | sort -rn | sed 's/^/    /'
        if [ "$SHOW_FAIL" = 1 ]; then
            echo
            echo "  failing files:"
            grep '^FAIL ' "$res" | sed 's/^FAIL /    /'
        fi
    fi

    local objs=()
    while read -r f; do
        local o="$OUT_ABS/obj/$(echo "$f" | tr '/' '_' | sed 's/\.cpp$/.o/')"
        [ -f "$o" ] && objs+=("$o")
    done < "$list"

    if [ "${#objs[@]}" -eq 0 ]; then
        echo "  NOTHING BUILT -- no archive written"; return 1
    fi
    rm -f "$OUT_ABS/$archive"
    ar rcs "$OUT_ABS/$archive" "${objs[@]}"
    echo "  -> $OUT_ABS/$archive  ($(du -h "$OUT_ABS/$archive" | cut -f1), ${#objs[@]} objects)"
    echo
}

cd "$FW" || exit 1

build_lib azcore libazcore.a AzCore/AzCore AzCore/Platform/Linux AzCore/Platform/Common

if [ "$AZCORE_ONLY" = 0 ]; then
    build_lib gridmate libgridmate.a \
        GridMate/GridMate \
        GridMate/Platform/Linux \
        GridMate/Platform/Common/UnixLike \
        GridMate/Platform/Common/Unimplemented
fi

echo "=== done ==="
ls -la "$OUT_ABS"/*.a 2>/dev/null
cat <<EOF

Expected at this point: ~39 AzCore failures, all 'file not found' for rapidjson,
Lua, zstd or gmock. Those are Lumberyard 3rdParty deps that are not in the
repo and are not on GridMate's dependency surface (it uses std, Math, Driller,
Debug, Casting, State, Memory, EBus, Socket, RTTI, Preprocessor). If your
failures are that list, the build is healthy.

Anything else failing -- especially a real compile error rather than a missing
header -- is a finding. Re-run with --show-failures and record it in STATE §14.

Per-file error logs: $OUT_ABS/logs/
EOF
