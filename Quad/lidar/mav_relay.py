cat > ~/lidar/mav_relay.py <<'PY'
import socket

IN_PORT = 5600
OUT_IP = "127.0.0.1"
OUT_PORT = 5602

# MAVLink2: magic=0xFD, header_len=10, checksum_len=2, signature optional (13 bytes) wenn incompat flag gesetzt
MAV2_MAGIC = 0xFD

def mav2_frame_len(buf, start):
    # braucht mindestens 10 bytes header ab start
    if start + 10 > len(buf):
        return None
    payload_len = buf[start+1]
    incompat_flags = buf[start+2]
    # header (10) + payload + checksum (2)
    base = 10 + payload_len + 2
    # signature: wenn incompat_flags bit0 gesetzt (signed)
    if incompat_flags & 0x01:
        base += 13
    return base

rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx.bind(("0.0.0.0", IN_PORT))

tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

buffer = bytearray()
print(f"Reassembling MAVLink2 from UDP:{IN_PORT} -> UDP {OUT_IP}:{OUT_PORT}")

while True:
    data, _ = rx.recvfrom(65535)
    buffer.extend(data)

    # versuche so viele Frames wie möglich zu extrahieren
    while True:
        try:
            i = buffer.index(MAV2_MAGIC)
        except ValueError:
            # kein magic im buffer -> buffer begrenzen
            if len(buffer) > 4096:
                buffer = buffer[-4096:]
            break

        # schneide alles vor magic weg
        if i > 0:
            del buffer[:i]

        frame_len = mav2_frame_len(buffer, 0)
        if frame_len is None:
            break  # noch nicht genug bytes

        if len(buffer) < frame_len:
            break  # frame noch nicht komplett

        frame = bytes(buffer[:frame_len])
        del buffer[:frame_len]

        # sende frame als einzelnes UDP packet weiter
        tx.sendto(frame, (OUT_IP, OUT_PORT))
PY
