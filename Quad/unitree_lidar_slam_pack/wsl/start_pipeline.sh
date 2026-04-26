#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[pipeline] Starting MAVLink reassembler (5600 -> 5602)..."
python3 "${BASE_DIR}/mav_relay.py" > "${HOME}/mav_relay.log" 2>&1 &
echo "[pipeline] mav_relay pid=$!"
echo "[pipeline] Log: tail -f ~/mav_relay.log"
echo
echo "[pipeline] MAVLink clean frames now available on UDP :5602 (localhost)"
