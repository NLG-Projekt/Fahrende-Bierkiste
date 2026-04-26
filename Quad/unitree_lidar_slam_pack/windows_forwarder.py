import socket, struct, json, os, time

"""
Unitree LiDAR multicast forwarder (Windows).

- Receives UDP multicast on your Quadnet WiFi interface
- Forwards packets as unicast to WSL (or any host)

Edit CONFIG below OR create a config.json next to this file.
"""

DEFAULT_CONFIG = {
    "mcast_group": "239.255.0.1",
    "mcast_port": 5600,

    # IMPORTANT: set this to your Quadnet WLAN IPv4 on Windows (ipconfig)
    "wlan_ip": "192.168.50.185",

    # Destination: set to your WSL reachable IP that worked for you
    "dest_ip": "172.19.201.255",
    "dest_port": 5600,
}

def load_config():
    cfg = DEFAULT_CONFIG.copy()
    cfg_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    return cfg

def main():
    cfg = load_config()
    mcast_grp = cfg["mcast_group"]
    mcast_port = int(cfg["mcast_port"])
    wlan_ip = cfg["wlan_ip"]
    dest = (cfg["dest_ip"], int(cfg["dest_port"]))

    rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    rx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    rx.bind(("", mcast_port))

    mreq = struct.pack("4s4s", socket.inet_aton(mcast_grp), socket.inet_aton(wlan_ip))
    rx.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"[forwarder] listening mcast {mcast_grp}:{mcast_port} on iface {wlan_ip}")
    print(f"[forwarder] forwarding -> {dest[0]}:{dest[1]}")

    pkts = 0
    t0 = time.time()
    while True:
        data, addr = rx.recvfrom(65535)
        tx.sendto(data, dest)
        pkts += 1
        if pkts % 500 == 0:
            dt = time.time() - t0
            print(f"[forwarder] {pkts} pkts ({pkts/dt:.1f}/s) last={len(data)} bytes from {addr}")

if __name__ == "__main__":
    main()
