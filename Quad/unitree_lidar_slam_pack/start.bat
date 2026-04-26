@echo off
setlocal
set PY=python
set HERE=%~dp0

echo [start] 1) Starting Windows multicast forwarder...
echo [start]    Edit "%HERE%config.json" (wlan_ip + dest_ip) if needed.
start "Unitree Forwarder" cmd /k "%PY% "%HERE%windows_forwarder.py""

echo.
echo [start] 2) Copying WSL tools into Ubuntu home: ~/unitree_lidar_slam
wsl -d Ubuntu -- bash -lc "mkdir -p ~/unitree_lidar_slam && rm -rf ~/unitree_lidar_slam/*"
wsl -d Ubuntu -- bash -lc "cp -r /mnt/c/Users/%USERNAME%/OneDrive/Desktop/Code-Projekte/Quad/lidar/wsl/* ~/unitree_lidar_slam/ 2>/dev/null || true"

echo.
echo [start] 3) Starting MAVLink reassembler in WSL (log: ~/mav_relay.log)
start "WSL MAV Relay" cmd /k "wsl -d Ubuntu -- bash -lc 'bash ~/unitree_lidar_slam/start_pipeline.sh; exec bash'"

echo.
echo [start] Done. Keep the forwarder window open while using LiDAR.
endlocal
