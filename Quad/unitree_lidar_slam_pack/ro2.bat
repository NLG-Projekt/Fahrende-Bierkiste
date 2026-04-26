@echo off
setlocal

echo ==========================================
echo   ROS2 Installation fuer WSL (Ubuntu)
echo ==========================================
echo.
echo Dieses Fenster bleibt offen.
echo Wenn Fehler kommen: Screenshot schicken.
echo.

pause

cmd /k wsl -d Ubuntu -- bash -lc "set -e; \
echo '[ROS] update'; \
sudo apt update; \
sudo apt install -y curl gnupg lsb-release; \
echo '[ROS] key'; \
sudo mkdir -p /usr/share/keyrings; \
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo tee /usr/share/keyrings/ros-archive-keyring.gpg >/dev/null; \
echo '[ROS] repo'; \
CODENAME=\$(lsb_release -cs); \
echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu \$CODENAME main\" | sudo tee /etc/apt/sources.list.d/ros2.list >/dev/null; \
sudo apt update; \
echo '[ROS] install jazzy'; \
sudo apt install -y ros-jazzy-desktop python3-colcon-common-extensions python3-rosdep; \
echo '[ROS] rosdep'; \
sudo rosdep init 2>/dev/null || true; \
rosdep update; \
echo '[ROS] bashrc'; \
grep -qxF \"source /opt/ros/jazzy/setup.bash\" ~/.bashrc || echo \"source /opt/ros/jazzy/setup.bash\" >> ~/.bashrc; \
echo '[ROS] DONE. Close this window, open a new WSL terminal.'; \
exec bash"

endlocal
