import socket
import struct
import numpy as np
import open3d as o3d

MCAST_GRP = "239.255.0.1"
PORT = 5600
IFACE_IP = "192.168.50.185"   # <- dein PC

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", PORT))

mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print("Listening LiDAR stream...")

pcd = o3d.geometry.PointCloud()
vis = o3d.visualization.Visualizer()
vis.create_window(window_name="LiDAR")

vis.add_geometry(pcd)

while True:
    data, _ = sock.recvfrom(65535)

    pts = []
    for i in range(0, len(data)-3, 4):
        d = struct.unpack("<H", data[i:i+2])[0]
        angle = struct.unpack("<H", data[i+2:i+4])[0] / 100.0

        rad = np.deg2rad(angle)
        x = np.cos(rad) * d
        y = np.sin(rad) * d
        pts.append([x, y, 0])

    if len(pts) == 0:
        continue

    pcd.points = o3d.utility.Vector3dVector(np.array(pts))

    vis.update_geometry(pcd)
    vis.poll_events()
    vis.update_renderer()
