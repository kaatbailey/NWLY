#!/usr/bin/env bash
#
# NWLY / T1 — Engine fingerprint (static, strings-based).
#
# CHUNKS T1 asks: which engine family is the retail client, proven by specific
# strings/RTTI symbols, plus the transport shape from imports, plus a flag on
# protobuf/flatbuffers descriptors.
#
# This does the string half. It is NOT a substitute for Ghidra on the RTTI and
# import-table questions -- but a single mangled hit like .?AVCarrier@GridMate@@
# closes the chunk on its own, and finding that takes seconds here versus hours
# of Ghidra auto-analysis. Run this first; open Ghidra only if the answer is
# ambiguous or you need the import table properly enumerated.
#
# READ-ONLY. Opens the game files for reading and writes nothing to them.
# No hooking, no dynamic analysis, no launching the game -- T1's non-goals.
#
# Usage:
#   ./t1_fingerprint.sh                        # auto-detect Steam install
#   ./t1_fingerprint.sh --game "/path/to/New World"
#   ./t1_fingerprint.sh --out t1_scan.txt      # also save full output
#   ./t1_fingerprint.sh --min-size 1           # scan small binaries too (MB)

set -u

GAME=""
OUT=""
MIN_MB=1

while [ $# -gt 0 ]; do
    case "$1" in
        --game)     GAME="$2"; shift 2 ;;
        --out)      OUT="$2"; shift 2 ;;
        --min-size) MIN_MB="$2"; shift 2 ;;
        -h|--help)  sed -n '2,25p' "$0"; exit 0 ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
done

command -v strings >/dev/null || { echo "ERROR: 'strings' not found. sudo pacman -S binutils"; exit 1; }

# ---- locate the install ---------------------------------------------------
if [ -z "$GAME" ]; then
    echo "Looking for New World..."
    for base in \
        "$HOME/.steam/steam/steamapps/common" \
        "$HOME/.local/share/Steam/steamapps/common" \
        "$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common" \
        /mnt/*/SteamLibrary/steamapps/common \
        /run/media/*/SteamLibrary/steamapps/common
    do
        for d in "$base"/*New*World*; do
            [ -d "$d" ] && GAME="$d" && break 2
        done
    done
fi

if [ -z "$GAME" ] || [ ! -d "$GAME" ]; then
    echo "ERROR: could not find the New World install."
    echo "Pass it explicitly:  ./t1_fingerprint.sh --game \"/path/to/New World\""
    echo
    echo "To find it yourself:"
    echo "  find ~ /mnt /run/media -maxdepth 6 -type d -iname '*new world*' 2>/dev/null"
    exit 1
fi

echo "game: $GAME"
echo

# ---- pick binaries worth scanning -----------------------------------------
MAPFILE=$(mktemp)
find "$GAME" -type f \( -iname '*.exe' -o -iname '*.dll' \) \
     -size +"${MIN_MB}"M -printf '%s\t%p\n' 2>/dev/null | sort -rn > "$MAPFILE"

COUNT=$(wc -l < "$MAPFILE")
if [ "$COUNT" -eq 0 ]; then
    echo "ERROR: no .exe/.dll over ${MIN_MB}MB under that path."
    echo "Is that the right directory? Try --min-size 0"
    rm -f "$MAPFILE"; exit 1
fi
echo "$COUNT binaries over ${MIN_MB}MB:"
head -12 "$MAPFILE" | while IFS=$'\t' read -r sz p; do
    printf "  %6s  %s\n" "$(numfmt --to=iec "$sz")" "${p#$GAME/}"
done
[ "$COUNT" -gt 12 ] && echo "  ... and $((COUNT - 12)) more"
echo

# ---- fingerprint families (CHUNKS T1) -------------------------------------
GRIDMATE='GridMate|CarrierThread|SecureSocketDriver|SocketDriver|ReplicaChunkDescriptor|ReplicaChunk|ReplicaMgr|DefaultHandshake|DefaultTrafficControl|GridSession|Marshaler'
O3DE='AzNetworking|NetBindComponent|IConnectionListener|MultiplayerComponent|NetworkEntity|NetworkInput|ConnectionData'
AZBASE='AzFramework|SerializeContext|BehaviorContext|ComponentApplication|AZ_CRC|AzCore|EBus'
THIRD='RakNet|yojimbo|google::protobuf|flatbuffers|msgpack|libenet|enet_host'
NETAPI='WSASendTo|WSARecvFrom|sendto|recvfrom|WS2_32|closesocket'

run() {
echo "=========================================================="
echo " T1 ENGINE FINGERPRINT — $(date '+%Y-%m-%d %H:%M')"
echo " game: $GAME"
echo "=========================================================="
echo

TMP=$(mktemp)
declare -A TOT
for k in GRIDMATE O3DE AZBASE THIRD NETAPI; do TOT[$k]=0; done
RTTI_HITS=""

while IFS=$'\t' read -r sz path; do
    rel="${path#$GAME/}"
    strings -a -n 6 "$path" > "$TMP" 2>/dev/null || continue

    g=$(grep -acE "$GRIDMATE" "$TMP"); o=$(grep -acE "$O3DE" "$TMP")
    a=$(grep -acE "$AZBASE"   "$TMP"); t=$(grep -acE "$THIRD" "$TMP")
    n=$(grep -acE "$NETAPI"   "$TMP")
    TOT[GRIDMATE]=$(( TOT[GRIDMATE] + g )); TOT[O3DE]=$(( TOT[O3DE] + o ))
    TOT[AZBASE]=$((   TOT[AZBASE]   + a )); TOT[THIRD]=$(( TOT[THIRD] + t ))
    TOT[NETAPI]=$((   TOT[NETAPI]   + n ))

    if [ $((g + o + a + t)) -gt 0 ]; then
        printf "%-52s GM=%-5s O3DE=%-5s AZ=%-5s 3rd=%-5s net=%s\n" \
               "${rel:0:52}" "$g" "$o" "$a" "$t" "$n"
    fi

    # MSVC RTTI: a single .?AV<class>@GridMate@@ closes the chunk outright.
    r=$(grep -aoE '\.\?AV[A-Za-z0-9_]+@(GridMate|AzNetworking|AZ)@@' "$TMP" | sort -u)
    [ -n "$r" ] && RTTI_HITS="$RTTI_HITS$rel:\n$r\n"
done < "$MAPFILE"

echo
echo "=== totals ==="
printf "  GridMate family   : %s\n" "${TOT[GRIDMATE]}"
printf "  O3DE AzNetworking : %s\n" "${TOT[O3DE]}"
printf "  AZ baseline       : %s\n" "${TOT[AZBASE]}"
printf "  third-party net   : %s\n" "${TOT[THIRD]}"
printf "  socket API names  : %s\n" "${TOT[NETAPI]}"

echo
echo "=== RTTI mangled names (decisive if present) ==="
if [ -n "$RTTI_HITS" ]; then printf "%b" "$RTTI_HITS"; else
    echo "  none found — RTTI may be stripped, or names are not MSVC-mangled."
    echo "  Not evidence of absence. Confirm in Ghidra with the PE RTTI analyzer."
fi

echo
echo "=== verdict ==="
G=${TOT[GRIDMATE]}; O=${TOT[O3DE]}
if   [ "$G" -gt 0 ] && [ "$O" -eq 0 ]; then
    echo "  GridMate. The T4 reference build is the right baseline; T5 diff proceeds."
elif [ "$O" -gt 0 ] && [ "$G" -eq 0 ]; then
    echo "  O3DE AzNetworking, NOT GridMate. The T4 reference is the wrong shape."
    echo "  Re-scope before T5: the Carrier/DTLS assumption does not hold."
elif [ "$G" -gt 0 ] && [ "$O" -gt 0 ]; then
    echo "  BOTH present. Check whether the O3DE hits are real or substring noise"
    echo "  (e.g. 'ConnectionData' is a generic name). Look at the actual strings."
else
    echo "  NEITHER. Per CHUNKS: AZ baseline hits alone do NOT prove GridMate --"
    echo "  those survive a rewrite. If AZ=0 too, this may be packed/encrypted and"
    echo "  strings analysis is exhausted; Ghidra is the next step."
fi

if [ "${TOT[THIRD]}" -gt 0 ]; then
    echo
    echo "  *** third-party netcode/serialization strings present. If protobuf,"
    echo "      CHUNKS says flag it loudly: embedded FileDescriptorProto blobs may"
    echo "      hand over the message schema and make P2 far cheaper. Do NOT"
    echo "      extract them in T1 -- just record the flag."
fi
rm -f "$TMP"
}

if [ -n "$OUT" ]; then run 2>&1 | tee "$OUT"; echo; echo "saved: $OUT"; else run; fi
rm -f "$MAPFILE"
