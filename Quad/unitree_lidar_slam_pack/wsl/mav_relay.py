import socket

IN_PORT = 5600
OUT_IP = "127.0.0.1"
OUT_PORT = 5602

MAV2_MAGIC = 0xFD

def mav2_frame_len(buf):
    if len(buf) < 10:
        return None
    payload_len = buf[1]
    incompat_flags = buf[2]
    flen = 10 + payload_len + 2
    if incompat_flags & 0x01:
        flen += 13
    return flen

rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx.bind(("0.0.0.0", IN_PORT))

tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

buffer = bytearray()
print(f"Reassembling MAVLink2 from UDP:{IN_PORT} -> UDP {OUT_IP}:{OUT_PORT}")

while True:
    data, _ = rx.recvfrom(65535)
    buffer.extend(data)

    while True:
        try:
            i = buffer.index(MAV2_MAGIC)
        except ValueError:
            if len(buffer) > 4096:
                buffer = buffer[-4096:]
            break

        if i > 0:
            del buffer[:i]

        flen = mav2_frame_len(buffer)
        if flen is None or len(buffer) < flen:
            break

        frame = bytes(buffer[:flen])
        del buffer[:flen]
        tx.sendto(frame, (OUT_IP, OUT_PORT))
