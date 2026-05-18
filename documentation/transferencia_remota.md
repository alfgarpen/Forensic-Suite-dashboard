# Guía: Conexión del Servidor de Reportes Remoto

Para que el sistema automático funcione, la Suite Forense puede conectarse a un servidor remoto mediante **SSH/SFTP utilizando autenticación por contraseña**. Este es el método más simple y rápido de configurar.

---

## Paso 1: Configurar la Suite Forense

Edita el archivo de configuración en tu equipo local para introducir los datos del servidor receptor.

**Archivo:** `config/remote_config.json`

```json
{
  "remote_host": "IP_DEL_SERVIDOR",
  "remote_port": 22,
  "remote_user": "USUARIO_DEL_SERVIDOR",
  "remote_password": "TU_CONTRASEÑA_SSH",
  "remote_path": "/ruta/donde/guardar/reportes/",
  "enabled": true,
  "auto_rename": true,
  "verify_integrity": true
}
```

### Campos disponibles:
- **`remote_host`**: La dirección IP o nombre de host del servidor remoto.
- **`remote_port`**: El puerto de SSH (por defecto, `22`).
- **`remote_user`**: El usuario con el que te conectarás al servidor.
- **`remote_password`**: La contraseña correspondiente a ese usuario.
- **`remote_path`**: La ruta absoluta o relativa en el servidor remoto donde se guardarán los reportes (ej. `~/reports/`).
- **`enabled`**: Cambiar a `true` para activar el servicio de monitoreo y envío automático.

---

## Paso 2: Reiniciar el Servicio Automático

Para aplicar la nueva configuración y que el demonio en segundo plano empiece a monitorear y enviar los reportes automáticamente, ejecuta:

```bash
sudo systemctl restart forensicsuite-remote.service
```

---

## Paso 3: Verificación

1. Dirígete a la pestaña **Transferencia Remota** en el Dashboard.
2. Genera un nuevo reporte en el sistema (o añade un archivo `.html` a la carpeta local `Documentos/Reportes/`).
3. En el log del Dashboard o en `logs/transfer.log` deberías ver el progreso automático:
   - `[INFO] Report detected: ...`
   - `[INFO] Transferencia iniciada`
   - `[INFO] Transferencia completada`
   - `[INFO] Verificación OK` (si la verificación de integridad está activada)

---

## Solución de problemas

- **Autenticación fallida:** Asegúrate de que el usuario y la contraseña introducidos en `remote_config.json` son correctos y que puedes conectarte manualmente desde una terminal con:
  ```bash
  ssh USUARIO_DEL_SERVIDOR@IP_DEL_SERVIDOR
  ```
- **Ruta no encontrada o sin permisos:** El usuario especificado debe tener permisos de lectura y escritura en la carpeta especificada en `remote_path`.
- **El servicio no inicia:** Puedes revisar los logs del sistema del servicio ejecutando:
  ```bash
  sudo journalctl -u forensicsuite-remote.service -n 50 -f
  ```
