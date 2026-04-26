import socket, struct

MCAST_GRP = "239.255.0.1"
MCAST_PORT = 5600

# Wichtig: an die Quadnet-WLAN-IP binden, nicht LAN
WLAN_IP = "192.168.50.185"   # <-- HIER DEINE WLAN-IP IM QUADNET

DEST_IP = "172.19.201.255"
DEST_PORT = 5600


rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
rx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
rx.bind(("", MCAST_PORT))

mreq = struct.pack("4s4s", socket.inet_aton(MCAST_GRP), socket.inet_aton(WLAN_IP))
rx.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Forwarding multicast on", WLAN_IP, "-> localhost:", DEST_PORT)
while True:
    data, addr = rx.recvfrom(65535)
    tx.sendto(data, (DEST_IP, DEST_PORT))
