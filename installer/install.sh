#!/bin/bash

# Forensic Suite Linux Installer
# Requires sudo/root privileges

set -e

echo "=== Forensic Suite Linux Installation ==="

# 1. Install system dependencies
echo "[*] Updating package list and installing dependencies..."
sudo apt-get update -y
sudo apt-get install -y python3-venv python3-pip build-essential libpcre3 libpcre3-dev

# 2. Run the core setup script
echo "[*] Running core setup script..."
python3 "$(dirname "$0")/setup.py"

# 3. Setup Systemd Service
echo "[*] Configuring Systemd service..."
BASE_DIR=$(realpath "$(dirname "$0")/..")
SERVICE_FILE="/etc/systemd/system/forensicsuite.service"
USER_NAME=$(whoami)

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Forensic Suite Dashboard Service
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$BASE_DIR/backend
ExecStart=$BASE_DIR/runtime/bin/python $BASE_DIR/backend/app.py
Restart=always
Environment=PYTHONPATH=$BASE_DIR/backend

[Install]
WantedBy=multi-user.target
EOF

# 4. Setup Startup Analysis Service
echo "[*] Configuring Startup Analysis service..."
STARTUP_SERVICE="/etc/systemd/system/forensicsuite-startup.service"
sudo cp "$BASE_DIR/installer/forensicsuite-startup.service" "$STARTUP_SERVICE"

echo "[*] Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable forensicsuite.service
sudo systemctl enable forensicsuite-startup.service
sudo systemctl start forensicsuite.service

echo "=== Installation Finished ==="
echo "Dashboard should be available at http://localhost:5001"
