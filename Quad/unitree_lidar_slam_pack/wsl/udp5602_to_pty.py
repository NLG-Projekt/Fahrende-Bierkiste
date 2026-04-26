import socket, os, pty, tty, termios, time

IN_PORT = 5602

master_fd, slave_fd = pty.openpty()
slave_name = os.ttyname(slave_fd)

# RAW mode for binary stream (important)
tty.setraw(slave_fd)
attrs = termios.tcgetattr(slave_fd)
attrs[3] = attrs[3] & ~(termios.ECHO | termios.ICANON | termios.ISIG)
termios.tcsetattr(slave_fd, termios.TCSANOW, attrs)

print("PTY serial port:", slave_name)

rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx.bind(("0.0.0.0", IN_PORT))

cnt = 0
t0 = time.time()

while True:
    data, _ = rx.recvfrom(65535)
    os.write(master_fd, data)
    cnt += 1
    if cnt % 500 == 0:
        dt = time.time() - t0
        print(f"wrote {cnt} frames to PTY ({cnt/dt:.1f}/s)")
