Unitree LiDAR -> WSL -> SLAM (starter pack)

Files:
- windows_forwarder.py + config.json
  Receive multicast (Quadnet WiFi) and forward to WSL as unicast.

- wsl/mav_relay.py
  Reassembles MAVLink2 stream and outputs clean frames on UDP port 5602 (localhost).

- wsl/start_pipeline.sh
  Starts mav_relay in background (log: ~/mav_relay.log).

- wsl/run_slam.sh
  Clones + builds a ROS2 Point-LIO port (requires ROS2 + colcon).

How to use (minimal):
1) On Windows: edit config.json (wlan_ip, dest_ip)
2) Run start.bat (keeps forwarder open)
3) In WSL: bash ~/unitree_lidar_slam/wsl/start_pipeline.sh
4) Confirm frames on 5602:
   python3 -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.bind(('0.0.0.0',5602)); d,_=s.recvfrom(4096); print('got',len(d),hex(d[0]))"
