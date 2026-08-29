#!/usr/bin/env bash
#
# NWLY / T1 — evidence dump. Follow-up to t1_fingerprint.sh.
#
# The counts tell you a family is present; T1's definition of done requires the
# SPECIFIC strings that prove it. This prints the unique matches per family so
# they can go in the findings document verbatim, and so single-hit families can
# be judged as real or as substring noise.
#
# READ-ONLY. Does not launch the game.
#
# Usage:
#   ./t1_evidence.sh
#   ./t1_evidence.sh --game "/path/to/New World" --out t1_evidence.txt

set -u
GAME=""
OUT=""
TARGET=""

while [ $# -gt 0 ]; do
    case "$1" in
        --game)   GAME="$2"; shift 2 ;;
        --out)    OUT="$2"; shift 2 ;;
        --binary) TARGET="$2"; shift 2 ;;
        -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
done

if [ -z "$GAME" ]; then
    for base in "$HOME/.steam/steam/steamapps/common" \
                "$HOME/.local/share/Steam/steamapps/common" \
                /mnt/*/SteamLibrary/steamapps/common \
                /run/media/*/SteamLibrary/steamapps/common; do
        for d in "$base"/*New*World*; do [ -d "$d" ] && GAME="$d" && break 2; done
    done
fi
[ -d "$GAME" ] || { echo "ERROR: game dir not found; pass --game"; exit 1; }
[ -n "$TARGET" ] || TARGET="$GAME/Bin64/NewWorld.exe"
[ -f "$TARGET" ] || { echo "ERROR: not found: $TARGET"; exit 1; }

run() {
echo "=========================================================="
echo " T1 EVIDENCE — $(basename "$TARGET")"
echo " $TARGET"
echo " $(date '+%Y-%m-%d %H:%M')"
echo "=========================================================="

TMP=$(mktemp)
echo "extracting strings (171M binary, this takes a moment)..." >&2
strings -a -n 6 "$TARGET" > "$TMP"
echo "  $(wc -l < "$TMP") strings extracted"
echo

dump() {
    local label="$1" pat="$2" limit="$3"
    echo "--- $label ---"
    local hits; hits=$(grep -aoE "$pat" "$TMP" | sort | uniq -c | sort -rn)
    if [ -z "$hits" ]; then echo "  (none)"; else
        echo "$hits" | head -"$limit" | sed 's/^/  /'
        local n; n=$(echo "$hits" | wc -l)
        [ "$n" -gt "$limit" ] && echo "  ... $((n - limit)) more distinct"
    fi
    echo
}

# Whole tokens with surrounding context so substring noise is visible.
dump "GridMate family (decisive for T1)" \
     '[A-Za-z0-9_:]*(GridMate|CarrierThread|SecureSocketDriver|SocketDriver|ReplicaChunkDescriptor|ReplicaChunk|ReplicaMgr|DefaultHandshake|DefaultTrafficControl|GridSession|Marshaler)[A-Za-z0-9_:]*' 40

dump "O3DE AzNetworking family (would falsify GridMate)" \
     '[A-Za-z0-9_:]*(AzNetworking|NetBindComponent|IConnectionListener|MultiplayerComponent|NetworkEntity|NetworkInput|ConnectionData)[A-Za-z0-9_:]*' 20

dump "third-party netcode / serialization" \
     '[A-Za-z0-9_:.]*(RakNet|yojimbo|google::protobuf|flatbuffers|msgpack|libenet|enet_host)[A-Za-z0-9_:.]*' 20

dump "socket API (transport shape)" \
     '(WSASendTo|WSARecvFrom|WSASend|WSARecv|sendto|recvfrom|closesocket|WS2_32\.dll|ws2_32\.dll)' 20

dump "crypto library (feeds T2)" \
     '(OpenSSL [0-9][^ ]*|BoringSSL|libsodium|mbedtls|SSL_read|SSL_write|DTLSv1|dtls1_)' 20

dump "AZ baseline (survives a rewrite — NOT proof on its own)" \
     '(AzFramework|SerializeContext|BehaviorContext|ComponentApplication|AzCore|EBus)' 12

echo "--- Carrier / Replica context (is the GridMate shape really there?) ---"
grep -aoE '[A-Za-z0-9_]*(Carrier|Replica|Handshake|Datagram|DataSet)[A-Za-z0-9_]*' "$TMP" \
  | sort | uniq -c | sort -rn | head -30 | sed 's/^/  /'
echo
rm -f "$TMP"
}

if [ -n "$OUT" ]; then run 2>&1 | tee "$OUT"; echo; echo "saved: $OUT"; else run; fi
