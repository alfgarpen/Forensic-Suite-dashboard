# Guía: Conexión del Servidor de Reportes Remoto

Para que el sistema automático funcione, el equipo que genera los reportes debe poder entrar al equipo remoto sin contraseña usando **SSH Keys**.

## Paso 1: Obtener tu Clave Pública
El sistema ya ha generado una clave de alta seguridad (`ed25519`) para ti. Ejecuta este comando en tu terminal para verla:

```bash
cat ~/.ssh/id_ed25519.pub
```

**Copia el texto completo** que empieza por `ssh-ed25519 ...`.

---

## Paso 2: Configurar el Servidor Remoto (Receptor)
En el equipo que va a recibir los reportes (el servidor), debes autorizar tu clave:

1. Entra al servidor remoto.
2. Edita el archivo de claves autorizadas:
   ```bash
   nano ~/.ssh/authorized_keys
   ```
3. Pega la clave que copiaste en el paso anterior en una línea nueva.
4. Guarda y sal (`Ctrl+O`, `Enter`, `Ctrl+X`).

> [!TIP]
> Si el servidor es nuevo, asegúrate de que la carpeta `.ssh` tiene permisos `700` y el archivo `authorized_keys` tiene `600`.

---

## Paso 3: Configurar la Suite Forense
Ahora debes decirle a la Suite a qué IP enviar los datos. Edita el archivo de configuración:

**Archivo:** `config/remote_config.json`

```json
{
    "remote_host": "IP_DEL_SERVIDOR",
    "remote_user": "USUARIO_DEL_SERVIDOR",
    "remote_path": "/ruta/donde/guardar/reportes/",
    "ssh_key_path": "/home/alfongp/.ssh/id_ed25519",
    "enabled": true
}
```

---

## Paso 4: Reiniciar el Servicio
Para que los cambios de configuración se apliquen al sistema de vigilancia automática:

```bash
sudo systemctl restart forensicsuite-remote.service
```

---

## Paso 5: Verificación
1. Ve a la pestaña **Transferencia Remota** en el Dashboard.
2. Genera un nuevo reporte (o mueve un archivo HTML a `Documentos/Reportes/`).
3. En el log del Dashboard deberías ver:
   - `[INFO] Detectado nuevo reporte...`
   - `[INFO] Conectando a SSH...`
   - `[SUCCESS] Transferencia completada: Reporte_XXX.html`

---

## Solución de problemas
- **Permisos denegados:** Asegúrate de que el usuario remoto tiene permisos de escritura en `remote_path`.
- **Host unreachable:** Verifica que puedes hacer `ping` a la IP del servidor y que el puerto 22 (SSH) está abierto.
