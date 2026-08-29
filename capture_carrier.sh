#!/usr/bin/env bash
#
# NWLY / T4 step 4 -- capture the plaintext Carrier session in one command.
#
# Starts tcpdump on loopback, runs carrier_probe, stops the capture, and prints
# a summary. Replaces the two-terminal tcpdump dance.
#
# Usage, from anywhere:
#   ./capture_carrier.sh            plaintext -> build/carrier_plaintext.pcap
#   ./capture_carrier.sh --secure   DTLS      -> build/carrier_dtls.pcap
#
# It will ask for your sudo password once: capturing packets needs root.
# tcpdump producing no output is NORMAL -- it writes to the file, not the screen.

set -u

NWLY="${NWLY:-$HOME/Documents/NWLY}"
BUILD="$NWLY/build"
PROBE="$BUILD/carrier_probe"

MODE="plaintext"
PROBE_ARGS=()
for a in "$@"; do
    if [ "$a" = "--secure" ]; then MODE="dtls"; PROBE_ARGS=(--secure); fi
done
PCAP="$BUILD/carrier_${MODE}.pcap"

echo "=== NWLY carrier capture ($MODE) ==="
echo

# ---- checks ---------------------------------------------------------------
if [ ! -x "$PROBE" ]; then
    echo "ERROR: $PROBE not found or not executable."
    echo "  Build it first (see nwly_carrier_probe.cpp header for the command),"
    echo "  or set NWLY=/path/to/NWLY if your repo is elsewhere."
    exit 1
fi
if ! command -v tcpdump >/dev/null; then
    echo "ERROR: tcpdump not installed.  sudo pacman -S tcpdump"
    exit 1
fi

echo "probe : $PROBE"
echo "pcap  : $PCAP"
echo
echo "Asking for sudo -- packet capture needs root."
sudo -v || exit 1

# ---- capture --------------------------------------------------------------
rm -f "$PCAP"
sudo tcpdump -i lo -w "$PCAP" -U 'udp and (port 4427 or port 4428)' \
     >/dev/null 2>"$BUILD/.tcpdump.err" &
TCPDUMP_WRAPPER=$!

# tcpdump needs a moment to attach before the probe starts talking.
sleep 2
if ! sudo pgrep -f "tcpdump -i lo -w $PCAP" >/dev/null; then
    echo "ERROR: tcpdump failed to start:"
    cat "$BUILD/.tcpdump.err"
    exit 1
fi
echo "capturing on lo, ports 4427/4428 ..."
echo

# ---- run the probe --------------------------------------------------------
"$PROBE" "${PROBE_ARGS[@]}"
PROBE_RC=$?
echo

# Let the last retransmits land before tearing the capture down.
sleep 2
sudo pkill -f "tcpdump -i lo -w $PCAP" 2>/dev/null
wait "$TCPDUMP_WRAPPER" 2>/dev/null
sudo chown "$(id -u):$(id -g)" "$PCAP" 2>/dev/null
sleep 1

# ---- report ---------------------------------------------------------------
echo "=== capture ==="
if [ ! -s "$PCAP" ]; then
    echo "ERROR: $PCAP is empty. The probe may have finished before tcpdump attached."
    exit 1
fi
echo "wrote $PCAP ($(du -h "$PCAP" | cut -f1))"

if command -v tshark >/dev/null; then
    COUNT=$(tshark -r "$PCAP" 2>/dev/null | wc -l)
    echo "$COUNT datagrams captured"
    echo
    echo "first 6 payloads (UDP data only, hex):"
    # --disable-protocol dtls: without it tshark claims secure frames and
    # data.data comes back empty, so the summary shows len=0 for every real
    # datagram. Harmless for plaintext captures.
    tshark -r "$PCAP" --disable-protocol dtls \
        -T fields -e udp.srcport -e udp.dstport -e data.data \
        2>/dev/null | head -6 | while IFS=$'\t' read -r sp dp hex; do
            printf "  %s->%s len=%s\n     %s\n" \
                "$sp" "$dp" "$(( ${#hex} / 2 ))" \
                "$(echo "$hex" | fold -w2 | head -20 | tr '\n' ' ')"
        done
else
    echo "(install wireshark-cli for a decoded summary: sudo pacman -S wireshark-cli)"
fi

echo
echo "probe exit code: $PROBE_RC"
if [ "$PROBE_RC" -eq 0 ]; then
    echo "capture complete: $PCAP"
    echo "decode it with:  ./decode_carrier.py $PCAP"
else
    echo "probe FAILED -- capture kept for diagnosis."
fi
exit "$PROBE_RC"
