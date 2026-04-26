@echo off
setlocal

echo ==========================================
echo   Unitree LiDAR – SLAM Start (WSL)
echo ==========================================
echo.

echo [1/3] Starte MAVLink-Relay in WSL...
start "WSL MAV Relay" cmd /k ^
"wsl -d Ubuntu -- bash -lc 'bash ~/unitree_lidar_slam/start_pipeline.sh; exec bash'"

timeout /t 3 >nul

echo.
echo [2/3] Baue / starte SLAM (ROS2 erforderlich)...
start "WSL SLAM" cmd /k ^
"wsl -d Ubuntu -- bash -lc 'bash ~/unitree_lidar_slam/run_slam.sh; exec bash'"

echo.
echo [3/3] Fertig.
echo - Dieses Fenster kannst du schließen
echo - Die WSL-Fenster offen lassen
echo.

endlocal
