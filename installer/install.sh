#!/bin/bash

# Forensic Suite Linux Installer
# Requires sudo/root privileges

set -e

echo "=== Forensic Suite Linux Installation ==="

# 0. Fix line endings for all shell scripts
echo "[*] Ensuring correct line endings for scripts..."
find "$(dirname "$0")" -name "*.sh" -exec sed -i 's/\r$//' {} +

# 1. Install system dependencies
echo "[*] Updating package list and installing dependencies..."
sudo apt-get update -y
sudo apt-get install -y python3-venv python3-pip build-essential libpcre3 libpcre3-dev git

# 2. Run the core setup script
echo "[*] Running core setup script..."
python3 "$(dirname "$0")/setup.py"

# 3. Setup Systemd Services
BASE_DIR=$(realpath "$(dirname "$0")/..")
USER_NAME=$(whoami)

echo "[*] Configuring Systemd services for user: $USER_NAME..."

# Dashboard Service
DASHBOARD_SERVICE="/etc/systemd/system/forensicsuite-dashboard.service"
echo "    - Creating $DASHBOARD_SERVICE"
sudo sed -e "s|PLACEHOLDER_BASE_DIR|$BASE_DIR|g" \
         -e "s|PLACEHOLDER_USER|$USER_NAME|g" \
         "$BASE_DIR/installer/forensic-dashboard.service" | sudo tee "$DASHBOARD_SERVICE" > /dev/null

# Startup Analysis Service
STARTUP_SERVICE="/etc/systemd/system/forensicsuite-startup.service"
echo "    - Creating $STARTUP_SERVICE"
sudo sed -e "s|PLACEHOLDER_BASE_DIR|$BASE_DIR|g" \
         -e "s|PLACEHOLDER_USER|root|g" \
         "$BASE_DIR/installer/forensicsuite-startup.service" | sudo tee "$STARTUP_SERVICE" > /dev/null

# Remote Transfer Service
REMOTE_SERVICE="/etc/systemd/system/forensicsuite-remote.service"
echo "    - Creating $REMOTE_SERVICE"
sudo cp "$BASE_DIR/installer/forensicsuite-remote.service" "$REMOTE_SERVICE"
sudo sed -i "s|User=alfongp|User=$USER_NAME|g" "$REMOTE_SERVICE"
sudo sed -i "s|/home/alfongp/Documentos/Forensic-Suite-dashboard|$BASE_DIR|g" "$REMOTE_SERVICE"

# 4. Finalize
echo "[*] Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable forensicsuite-dashboard.service
sudo systemctl enable forensicsuite-startup.service
sudo systemctl enable forensicsuite-remote.service
sudo systemctl start forensicsuite-dashboard.service
sudo systemctl start forensicsuite-remote.service

echo "=== Installation Finished ==="
echo "Dashboard should be available at http://localhost:5001"
echo "Check status with: systemctl status forensicsuite-dashboard"
