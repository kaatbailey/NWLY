#!/usr/bin/env python3
"""
NWLY / T4 step 4 -- decode captured GridMate Carrier datagrams.

This is the step-4 completion check. The layout below was read out of
GridMate/Carrier/Carrier.cpp at fork commit 413ecaf -- NOT guessed from a
hexdump. Running it against a capture confirms source and wire agree.

Source of every field (Carrier.cpp line numbers at 413ecaf):

  kCarrierEndian = BigEndian                                   line 58
  WriteDataGramHeader: writes m_flowControl.m_sequenceNumber   line 2869-2873
  WriteMessageHeader:  flags, then dataSize, then optionals    line 3494-3541

  Message flag bits (Carrier.cpp lines 86-93):
    MF_RELIABLE         = 1 << 0   (0x01)
    MF_UNUSED           = 1 << 1   (0x02)   must be 0
    MF_CHUNKS           = 1 << 2   (0x04)
    MF_SQUENTIAL_ID     = 1 << 3   (0x08)
    MF_SQUENTIAL_REL_ID = 1 << 4   (0x10)
    MF_DATA_CHANNEL     = 1 << 5   (0x20)
    MF_UNUSED           = 1 << 6   (0x40)   must be 0
    MF_CONNECTING       = 1 << 7   (0x80)

  Per-message field order, all big-endian (WriteMessageHeader):
    flags        u8   always
    dataSize     u16  always
    channel      u8   only if MF_DATA_CHANNEL
    numChunks    u16  only if MF_CHUNKS
    sequenceNum  u16  only if NOT MF_SQUENTIAL_ID
    relSeqNum    u16  only if NOT MF_SQUENTIAL_REL_ID
    payload      dataSize bytes

  Note the inverted sense: the MF_SQUENTIAL_* flags mean "this value is
  implied by the previous message, so it is NOT on the wire". Reading them
  the obvious way round desynchronises the parse immediately.

Usage:
    ./decode_carrier.py build/carrier_plaintext.pcap
    ./decode_carrier.py build/carrier_plaintext.pcap --max 8

Needs tshark (wireshark-cli) to read the pcap.
"""

import argparse
import struct
import subprocess
import sys

MF = [
    (0x01, "RELIABLE"),
    (0x02, "UNUSED_1"),
    (0x04, "CHUNKS"),
    (0x08, "SEQUENTIAL_ID"),
    (0x10, "SEQUENTIAL_REL_ID"),
    (0x20, "DATA_CHANNEL"),
    (0x40, "UNUSED_6"),
    (0x80, "CONNECTING"),
]


def flag_names(f):
    return "|".join(n for b, n in MF if f & b) or "none"


def u16(b, o):
    return struct.unpack_from(">H", b, o)[0]


WAKEUP = 0x47   # 'G', AZ_SOCKET_WAKEUP_MSG_VALUE, SocketDriver.cpp:55


def decode(payload):
    """Returns (lines, ok). ok is False if the parse desynchronised."""
    out = []

    # Single 'G' addressed to the socket's own port: SocketDriver's self-wakeup,
    # sent by StopWaitForData() (SocketDriver.cpp:1449-1470) to break the recv
    # thread out of its blocking wait. Receive side drops it as an "internal
    # wake up message" (line 1423). Not Carrier protocol -- do not try to parse
    # it, and exclude it when diffing against retail.
    if len(payload) == 1 and payload[0] == WAKEUP:
        return ["  SocketDriver self-wakeup byte ('G') -- not a Carrier datagram"], True

    if len(payload) < 2:
        return ["  too short for a datagram header"], False

    seq = u16(payload, 0)
    out.append(f"  datagram seq = {seq}")
    o = 2
    n = 0

    while o < len(payload):
        if o + 3 > len(payload):
            out.append(f"  +{o}: {len(payload) - o} trailing byte(s), no room for a message header")
            return out, False
        flags = payload[o]
        if flags & 0x42:
            out.append(f"  +{o}: flags 0x{flags:02x} sets a reserved bit -- parse desynchronised")
            return out, False
        size = u16(payload, o + 1)
        p = o + 3
        parts = [f"size={size}"]

        if flags & 0x20:
            if p >= len(payload):
                return out + [f"  +{o}: truncated at channel"], False
            parts.append(f"channel={payload[p]}")
            p += 1
        if flags & 0x04:
            if p + 2 > len(payload):
                return out + [f"  +{o}: truncated at numChunks"], False
            parts.append(f"chunks={u16(payload, p)}")
            p += 2
        if not (flags & 0x08):
            if p + 2 > len(payload):
                return out + [f"  +{o}: truncated at seqNum"], False
            parts.append(f"msgSeq={u16(payload, p)}")
            p += 2
        if not (flags & 0x10):
            if p + 2 > len(payload):
                return out + [f"  +{o}: truncated at relSeqNum"], False
            parts.append(f"relSeq={u16(payload, p)}")
            p += 2

        if p + size > len(payload):
            out.append(f"  +{o}: msg {n} claims {size} payload bytes, only {len(payload) - p} left")
            return out, False

        data = payload[p:p + size]
        out.append(f"  msg {n}: flags=0x{flags:02x} [{flag_names(flags)}] " + " ".join(parts))
        out.append(f"          payload {data.hex(' ') if size else '(empty)'}")
        o = p + size
        n += 1

    out.append(f"  -> {n} message(s), consumed all {len(payload)} bytes")
    return out, True


def read_pcap(path):
    try:
        r = subprocess.run(
            ["tshark", "-r", path, "-Y", "udp", "-T", "fields",
             "-e", "udp.srcport", "-e", "udp.dstport", "-e", "data.data"],
            capture_output=True, text=True, check=True)
    except FileNotFoundError:
        sys.exit("tshark not found. Install it: sudo pacman -S wireshark-cli")
    except subprocess.CalledProcessError as e:
        sys.exit(f"tshark failed:\n{e.stderr}")

    out = []
    for line in r.stdout.splitlines():
        f = line.split("\t")
        if len(f) < 3 or not f[2].strip():
            continue
        # tshark may emit several data fields for one frame; take the first.
        hexstr = f[2].split(",")[0].replace(":", "").strip()
        try:
            out.append((f[0], f[1], bytes.fromhex(hexstr)))
        except ValueError:
            continue
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pcap")
    ap.add_argument("--max", type=int, default=6, help="datagrams to decode (default 6)")
    args = ap.parse_args()

    pkts = read_pcap(args.pcap)
    if not pkts:
        sys.exit("No UDP payloads found in that capture.")

    print(f"{len(pkts)} datagrams with payload\n")
    ok_count = 0
    for i, (sp, dp, payload) in enumerate(pkts[:args.max]):
        print(f"=== #{i}  {sp} -> {dp}  {len(payload)} bytes ===")
        print("  raw:", payload.hex(" "))
        lines, ok = decode(payload)
        print("\n".join(lines))
        ok_count += ok
        print()

    shown = min(args.max, len(pkts))
    print(f"{ok_count}/{shown} decoded cleanly against the layout read from Carrier.cpp.")
    if ok_count == shown:
        print("Source and wire agree. Step 4 completion criterion met.")
    else:
        print("Some datagrams did not decode. Either the layout reading is wrong,")
        print("or those frames are a variant (compression hint / ack block) not yet")
        print("covered here. Record which, and check Carrier.cpp GenerateDataGram.")


if __name__ == "__main__":
    main()
