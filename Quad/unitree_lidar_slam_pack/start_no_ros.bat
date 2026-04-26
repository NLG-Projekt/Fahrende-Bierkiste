@echo off
setlocal

echo ==========================================
echo   Unitree LiDAR – NO ROS Debug Start (WSL)
echo ==========================================
echo.

echo [1/2] Starte MAVLink-Relay in WSL (log: ~/mav_relay.log)...
start "WSL MAV Relay" cmd /k ^
"wsl -d Ubuntu -- bash -lc 'bash ~/unitree_lidar_slam/start_pipeline.sh; exec bash'"

timeout /t 2 >nul

echo.
echo [2/2] Teste ob auf UDP 5602 saubere MAVLink2 Frames ankommen...
start "WSL 5602 Test" cmd /k ^
"wsl -d Ubuntu -- bash -lc 'python3 -c \"import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.bind((\\\"0.0.0.0\\\",5602)); print(\\\"wait on 5602\\\"); \
d,_=s.recvfrom(4096); print(\\\"got\\\",len(d),\\\"first_byte\\\",hex(d[0])); \
print(\\\"OK: expect 0xfd for MAVLink2\\\")\"; exec bash'"

echo.
echo Fertig. Lass beide WSL Fenster offen.
endlocal
