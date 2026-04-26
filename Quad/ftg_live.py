import socket, struct, time, math
from collections import deque

MCAST_GRP = "239.255.0.1"
MCAST_PORT = 5600
IFACE_IP = "192.168.50.185"   # <- dein PC

# ---- Follow-the-Gap Params (einfach gehalten) ----
MAX_RANGE_MM = 6000          # clamp
MIN_RANGE_MM = 150           # ignore super nahe/invalid
BUBBLE_MM = 400              # safety bubble um nächstes Hindernis
SMOOTH_K = 5                 # gleitender Mittelwert
FOV_DEG = 120                # wir nutzen nur Frontbereich
STEER_MAX = 1.0              # normalisiert -1..+1

def join_multicast():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", MCAST_PORT))
    mreq = socket.inet_aton(MCAST_GRP) + socket.inet_aton(IFACE_IP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock

def u16_le(buf, off):
    return buf[off] | (buf[off+1] << 8)

def moving_average(arr, k):
    if k <= 1:
        return arr
    out = [0]*len(arr)
    half = k//2
    for i in range(len(arr)):
        s = 0
        c = 0
        for j in range(i-half, i+half+1):
            if 0 <= j < len(arr):
                s += arr[j]
                c += 1
        out[i] = s//c
    return out

def follow_the_gap(ranges_mm, angles_deg):
    # clamp/clean
    r = []
    for x in ranges_mm:
        if x == 0 or x > MAX_RANGE_MM:
            r.append(MAX_RANGE_MM)
        elif x < MIN_RANGE_MM:
            r.append(MIN_RANGE_MM)
        else:
            r.append(x)

    # smooth
    r = moving_average(r, SMOOTH_K)

    # find closest point (front)
    closest_i = min(range(len(r)), key=lambda i: r[i])

    # bubble: set near obstacle region to MIN
    bubble = []
    for i in range(len(r)):
        bubble.append(r[i])

    # approximate: bubble in index-space using angle step
    # bubble angle approx = atan(BUBBLE / dist)
    dist = max(r[closest_i], 1)
    bubble_ang = math.degrees(math.atan2(BUBBLE_MM, dist))
    # indices within bubble_ang
    for i, a in enumerate(angles_deg):
        if abs(a - angles_deg[closest_i]) <= bubble_ang:
            bubble[i] = MIN_RANGE_MM

    # find largest gap (continuous region where range > MIN)
    best = (0, -1)  # start,end
    cur_start = None
    for i in range(len(bubble)):
        if bubble[i] > MIN_RANGE_MM:
            if cur_start is None:
                cur_start = i
        else:
            if cur_start is not None:
                if i-1 - cur_start > best[1]-best[0]:
                    best = (cur_start, i-1)
                cur_start = None
    if cur_start is not None:
        if (len(bubble)-1) - cur_start > best[1]-best[0]:
            best = (cur_start, len(bubble)-1)

    gs, ge = best
    if ge < gs:
        return 0.0, closest_i, (0,0)

    # aim point: max range within the best gap
    aim_i = max(range(gs, ge+1), key=lambda i: bubble[i])

    # steering: map aim angle to -1..1
    aim_angle = angles_deg[aim_i]
    steer = max(-STEER_MAX, min(STEER_MAX, aim_angle / (FOV_DEG/2)))

    return steer, closest_i, (gs, ge)

def extract_scan_from_message(msg: bytes):
    """
    Heuristik basierend auf deinem Dump:
    - es gibt Messages die viele little-endian uint16 enthalten (Ranges)
    - wir suchen nach einem Bereich, der wie '00 f0 00 xx 00 yy ...' aussieht.
    Startversion: finde längsten Block von uint16 der "plausibel" ist.
    """
    # interpret entire payload as u16 array starting from some offset
    best = None  # (count, offset)
    # try offsets 0..32 to find plausible sequence
    for off in range(0, 33, 1):
        if off+200 > len(msg):
            break
        n = (len(msg) - off) // 2
        vals = []
        ok = 0
        for i in range(n):
            v = u16_le(msg, off + 2*i)
            vals.append(v)
            # plausibility: many values in 50..8000
            if 50 <= v <= 8000:
                ok += 1
        # require at least 200 u16s and >60% plausible
        if n >= 200 and ok / n > 0.60:
            if best is None or n > best[0]:
                best = (n, off, vals)

    if best is None:
        return None

    n, off, vals = best

    # take a front FOV slice assuming 360 deg scan:
    # angles mapping: assume evenly spaced over 360
    # We'll center front at 0 deg and take [-FOV/2, +FOV/2]
    total = n
    # create angles for full 360
    # index->angle in [-180,180)
    angles_full = [((i / total) * 360.0) - 180.0 for i in range(total)]
    # pick front window around 0 deg
    fov = []
    ang = []
    for v, a in zip(vals, angles_full):
        if -FOV_DEG/2 <= a <= FOV_DEG/2:
            fov.append(v)
            ang.append(a)
    if len(fov) < 50:
        return None
    return fov, ang

def main():
    sock = join_multicast()
    print(f"[OK] Listening on {IFACE_IP} for {MCAST_GRP}:{MCAST_PORT}")

    buf = bytearray()
    last_print = time.time()
    steer_hist = deque(maxlen=10)

    while True:
        data, addr = sock.recvfrom(8192)
        buf.extend(data)

        # crude framing: keep buffer bounded
        if len(buf) > 200000:
            buf = buf[-100000:]

        # try to parse scans out of raw stream by sliding window
        # We'll attempt on the newest ~4KB chunk boundary
        # (startversion, not perfect but should work if frames are contained in packets often)
        scan = extract_scan_from_message(data)
        if scan is None:
            continue

        ranges, angles = scan
        steer, closest_i, (gs, ge) = follow_the_gap(ranges, angles)
        steer_hist.append(steer)

        # print at ~10 Hz
        now = time.time()
        if now - last_print > 0.1:
            avg = sum(steer_hist)/len(steer_hist)
            print(f"steer={avg:+.2f}  closest={ranges[closest_i]}mm  gap=[{gs},{ge}]  n={len(ranges)}")
            last_print = now

if __name__ == "__main__":
    main()
