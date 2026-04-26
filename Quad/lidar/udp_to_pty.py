import socket, os, pty

MCAST_GRP = "239.255.0.1"
MCAST_PORT = 5600

# PTY anlegen
master_fd, slave_fd = pty.openpty()
slave_name = os.ttyname(slave_fd)
print("PTY device:", slave_name)

# Multicast socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", MCAST_PORT))

mreq = socket.inet_aton(MCAST_GRP) + socket.inet_aton("0.0.0.0")
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

while True:
    data, _ = sock.recvfrom(65535)
    os.write(master_fd, data)
