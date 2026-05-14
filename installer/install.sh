#!/bin/bash

# Forensic Suite - Robust Linux Installer
# This script prepares the system, installs dependencies, and sets up systemd services.
# Supports installation in any directory (portable).

set -e

echo "=========================================="
echo "      Forensic Suite - Installer          "
echo "=========================================="

# 0. Environment Setup
BASE_DIR=$(realpath "$(dirname "$0")/..")
USER_NAME=$(whoami)
SERVICE_DIR="/etc/systemd/system"

echo "[*] Base Directory: $BASE_DIR"
echo "[*] Current User:   $USER_NAME"

# 1. System Dependencies
echo "[*] Checking system dependencies..."
sudo apt-get update -y
sudo apt-get install -y python3-venv python3-pip build-essential libpcre3 libpcre3-dev git curl

# 2. Python Environment & Project Structure
echo "[*] Running core setup (venv, folders, volatility)..."
python3 "$BASE_DIR/installer/setup.py"

# 3. Systemd Services Configuration
echo "[*] Configuring system services..."

SERVICES=("forensicsuite-dashboard.service" "forensicsuite-startup.service" "forensicsuite-remote.service")

# Map of service files in installer/ to system names
declare -A SERVICE_MAP
SERVICE_MAP["forensicsuite-dashboard.service"]="forensic-dashboard.service"
SERVICE_MAP["forensicsuite-startup.service"]="forensicsuite-startup.service"
SERVICE_MAP["forensicsuite-remote.service"]="forensicsuite-remote.service"

for SVC_NAME in "${!SERVICE_MAP[@]}"; do
    SRC_FILE="$BASE_DIR/installer/${SERVICE_MAP[$SVC_NAME]}"
    DST_FILE="$SERVICE_DIR/$SVC_NAME"
    
    if [ -f "$SRC_FILE" ]; then
        echo "    - Installing $SVC_NAME"
        
        # Determine service user (startup service runs as root for memory access)
        RUN_USER="$USER_NAME"
        if [[ "$SVC_NAME" == *"startup"* ]]; then
            RUN_USER="root"
        fi

        # Apply placeholders
        sudo sed -e "s|PLACEHOLDER_BASE_DIR|$BASE_DIR|g" \
                 -e "s|PLACEHOLDER_USER|$RUN_USER|g" \
                 "$SRC_FILE" | sudo tee "$DST_FILE" > /dev/null
    else
        echo "    [!] Warning: Service template $SRC_FILE not found."
    fi
done

# 4. Finalize
echo "[*] Reloading systemd and enabling services..."
sudo systemctl daemon-reload

for SVC_NAME in "${!SERVICE_MAP[@]}"; do
    sudo systemctl enable "$SVC_NAME"
    sudo systemctl restart "$SVC_NAME" || echo "    [!] Error starting $SVC_NAME"
done

echo ""
echo "=========================================="
echo "       Installation Successful!           "
echo "=========================================="
echo ">> Dashboard: http://localhost:5001"
echo ">> Reports:   $BASE_DIR/reports"
echo ">> Logs:      $BASE_DIR/logs"
echo "=========================================="
