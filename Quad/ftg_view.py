import socket, struct, time, math
import numpy as np
import matplotlib.pyplot as plt

MCAST_GRP = "239.255.0.1"
MCAST_PORT = 5600
IFACE_IP = "192.168.50.185"   # <- dein PC

MAX_RANGE_MM = 6000
MIN_RANGE_MM = 150
BUBBLE_MM = 400
SMOOTH_K = 5
FOV_DEG = 120

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
    out = np.copy(arr).astype(np.float32)
    kernel = np.ones(k, dtype=np.float32) / k
    out = np.convolve(out, kernel, mode="same")
    return out

def extract_scan_from_message(msg: bytes):
    best = None  # (count, offset, vals)
    for off in range(0, 33):
        if off + 400 > len(msg):
            break
        n = (len(msg) - off) // 2
        if n < 200:
            continue
        vals = np.frombuffer(msg[off:off+2*n], dtype="<u2").astype(np.int32)
        ok = np.mean((vals >= 50) & (vals <= 8000))
        if ok > 0.60:
            if best is None or n > best[0]:
                best = (n, off, vals)
    if best is None:
        return None

    total, off, vals = best

    angles_full = (np.arange(total) / total) * 360.0 - 180.0
    mask = (angles_full >= -FOV_DEG/2) & (angles_full <= FOV_DEG/2)
    fov_vals = vals[mask]
    fov_ang = angles_full[mask]
    if fov_vals.size < 50:
        return None
    return fov_vals, fov_ang

def follow_the_gap(ranges_mm, angles_deg):
    r = np.array(ranges_mm, dtype=np.float32)

    r = np.clip(r, 0, MAX_RANGE_MM)
    r[r == 0] = MAX_RANGE_MM
    r[r < MIN_RANGE_MM] = MIN_RANGE_MM

    r = moving_average(r, SMOOTH_K)

    closest_i = int(np.argmin(r))
    dist = max(float(r[closest_i]), 1.0)

    # bubble angle
    bubble_ang = math.degrees(math.atan2(BUBBLE_MM, dist))
    bubble = r.copy()
    bubble[np.abs(angles_deg - angles_deg[closest_i]) <= bubble_ang] = MIN_RANGE_MM

    ok = bubble > MIN_RANGE_MM

    # largest gap
    best_len = -1
    best = (0, -1)
    i = 0
    n = len(ok)
    while i < n:
        if ok[i]:
            j = i
            while j < n and ok[j]:
                j += 1
            if (j - i) > best_len:
                best_len = (j - i)
                best = (i, j-1)
            i = j
        else:
            i += 1

    gs, ge = best
    if ge < gs:
        return 0.0, closest_i, bubble, (0,0), 0

    aim_i = int(np.argmax(bubble[gs:ge+1]) + gs)
    aim_angle = float(angles_deg[aim_i])
    steer = max(-1.0, min(1.0, aim_angle / (FOV_DEG/2)))
    return steer, closest_i, bubble, (gs, ge), aim_i

def polar_to_xy(r_mm, ang_deg):
    a = np.deg2rad(ang_deg)
    x = (r_mm * np.cos(a)) / 1000.0
    y = (r_mm * np.sin(a)) / 1000.0
    return x, y

def main():
    sock = join_multicast()
    print(f"[OK] Listening on {IFACE_IP} for {MCAST_GRP}:{MCAST_PORT}")

    plt.ion()
    fig, ax = plt.subplots()
    ax.set_aspect("equal", "box")
    ax.set_title("LiDAR Follow-the-Gap (live)")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_xlim(0, MAX_RANGE_MM/1000.0)
    ax.set_ylim(-MAX_RANGE_MM/2000.0, MAX_RANGE_MM/2000.0)
    ax.grid(True)

    # artists
    scan_scatter = ax.scatter([], [], s=6)
    bubble_scatter = ax.scatter([], [], s=10)
    gap_line, = ax.plot([], [], linewidth=3)
    aim_point, = ax.plot([], [], marker="o", markersize=10)
    steer_arrow = ax.arrow(0, 0, 1, 0, width=0.02)  # will be replaced

    last = time.time()

    while True:
        data, _ = sock.recvfrom(8192)
        scan = extract_scan_from_message(data)
        if scan is None:
            continue

        ranges, angles = scan
        steer, closest_i, bubble, (gs, ge), aim_i = follow_the_gap(ranges, angles)

        # points
        x, y = polar_to_xy(ranges, angles)
        xb, yb = polar_to_xy(bubble, angles)

        scan_scatter.set_offsets(np.c_[x, y])
        bubble_scatter.set_offsets(np.c_[xb, yb])

        # gap highlight
        if ge >= gs:
            xg, yg = polar_to_xy(ranges[gs:ge+1], angles[gs:ge+1])
            gap_line.set_data(xg, yg)
        else:
            gap_line.set_data([], [])

        # aim point
        xa, ya = polar_to_xy(ranges[aim_i], angles[aim_i])
        aim_point.set_data([xa], [ya])

        # steer arrow (remove old + draw new)
        try:
            steer_arrow.remove()
        except Exception:
            pass
        # arrow direction based on aim angle
        a = math.radians(float(angles[aim_i]))
        dx = math.cos(a) * 1.5
        dy = math.sin(a) * 1.5
        steer_arrow = ax.arrow(0, 0, dx, dy, width=0.03)

        now = time.time()
        if now - last > 0.15:
            ax.set_title(f"LiDAR Follow-the-Gap | steer={steer:+.2f} | closest={int(ranges[closest_i])}mm")
            fig.canvas.draw()
            fig.canvas.flush_events()
            last = now

if __name__ == "__main__":
    main()
