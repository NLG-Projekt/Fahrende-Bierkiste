#!/usr/bin/env bash
set -euo pipefail

# NOTE:
# This script only automates cloning + building a ROS2 Point-LIO port.
# It DOES NOT install ROS2 for you.

WS_DIR="${HOME}/unitree_slam_ws"
SRC_DIR="${WS_DIR}/src"
REPO_URL="https://github.com/dfloreaa/point_lio_ros2.git"
PKG_DIR="${SRC_DIR}/point_lio_ros2"

if [ ! -d /opt/ros ]; then
  echo "[slam] ROS2 not found under /opt/ros."
  echo "[slam] Install ROS2 first (Ubuntu 24.04: Jazzy recommended), then re-run."
  exit 1
fi

if [ -f /opt/ros/jazzy/setup.bash ]; then
  source /opt/ros/jazzy/setup.bash
elif [ -f /opt/ros/humble/setup.bash ]; then
  source /opt/ros/humble/setup.bash
else
  SETUP="$(ls -1 /opt/ros/*/setup.bash 2>/dev/null | head -n 1 || true)"
  if [ -z "$SETUP" ]; then
    echo "[slam] Could not find /opt/ros/*/setup.bash"
    exit 1
  fi
  source "$SETUP"
fi

mkdir -p "${SRC_DIR}"
cd "${WS_DIR}"

if [ ! -d "${PKG_DIR}" ]; then
  echo "[slam] Cloning ${REPO_URL} ..."
  git clone --depth 1 "${REPO_URL}" "${PKG_DIR}"
else
  echo "[slam] Repo exists, pulling latest ..."
  git -C "${PKG_DIR}" pull --ff-only || true
fi

if ! command -v colcon >/dev/null 2>&1; then
  echo "[slam] colcon not found. Install it:"
  echo "       sudo apt install -y python3-colcon-common-extensions"
  exit 1
fi

echo "[slam] Building workspace..."
colcon build --symlink-install

echo
echo "[slam] Built."
echo "[slam] Next:"
echo "  source ${WS_DIR}/install/setup.bash"
echo "  Then follow the repo README inside:"
echo "    ${PKG_DIR}"
