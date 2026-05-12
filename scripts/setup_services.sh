#!/bin/bash
# setup_services.sh - Instala los servicios de systemd para el proyecto

# Verificar si se ejecuta como root
if [ "$EUID" -ne 0 ]; then
  echo "Por favor, ejecuta este script con sudo."
  exit 1
fi

PROJECT_DIR="/home/hackerguarro/Documentos/Forensic-Suite-dashboard"
SYSTEMD_DIR="/etc/systemd/system"

echo "[*] Instalando servicios en $SYSTEMD_DIR..."

# 1. Copiar archivos de servicio
cp "$PROJECT_DIR/forensic-dashboard.service" "$SYSTEMD_DIR/"

# 2. Crear el servicio de startup si no existe (basado en el guide)
cat <<EOF > "$SYSTEMD_DIR/forensic-startup.service"
[Unit]
Description=Generación de Reporte Forense Automático al Arranque
After=network.target

[Service]
Type=oneshot
ExecStart=$PROJECT_DIR/scripts/startup_analysis.sh
User=root
Group=root
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# 3. Asegurar permisos de ejecución en scripts y propiedad correcta
chmod +x "$PROJECT_DIR/scripts/startup_analysis.sh"
chown -R hackerguarro:hackerguarro "$PROJECT_DIR"

# 4. Recargar systemd
systemctl daemon-reload

# 5. Habilitar servicios
systemctl enable forensic-dashboard.service
systemctl enable forensic-startup.service

# 6. Iniciar dashboard ahora
systemctl start forensic-dashboard.service

echo "[+] Instalación completada con éxito."
echo "[+] El Dashboard está corriendo en http://localhost:5001"
echo "[+] El reporte automático se ejecutará en cada arranque."
echo "[*] Puedes ver el estado con: systemctl status forensic-dashboard"
