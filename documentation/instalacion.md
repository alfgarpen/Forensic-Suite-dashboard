# Guía de Instalación: Forensic Suite Dashboard

Esta guía detalla los pasos para instalar la suite forense en cualquier sistema basado en Linux (Ubuntu/Debian recomendado).

## Requisitos Previos
- Sistema operativo Linux.
- Acceso con privilegios `sudo`.
- Conexión a internet (para descargar dependencias).

---

## Instalación Paso a Paso

### 1. Clonar o descargar el proyecto
Si estás instalando en un equipo nuevo, asegúrate de tener todos los archivos en una carpeta (por ejemplo, `/home/usuario/Forensic-Suite`).

### 2. Ejecutar el script de instalación
El script automatizado se encarga de todo: crear el entorno virtual, instalar librerías de Python, descargar Volatility 3 y configurar los servicios del sistema.

```bash
# Dar permisos de ejecución
chmod +x installer/install.sh

# Ejecutar como root/sudo
sudo ./installer/install.sh
```

---

## Servicios Instalados
El instalador configura tres servicios automáticos que se inician con el sistema:

1. **`forensicsuite-dashboard`**: La interfaz web (puerto 5001).
2. **`forensicsuite-startup`**: Análisis automático al arrancar el equipo.
3. **`forensicsuite-remote`**: Vigilancia y transferencia de reportes por SSH.

### Comandos útiles de gestión:
- **Ver estado:** `systemctl status forensicsuite-dashboard`
- **Reiniciar todo:** `sudo systemctl restart forensicsuite-*`
- **Ver logs de error:** `journalctl -u forensicsuite-dashboard -f`

---

## Estructura de Carpetas Post-Instalación
- `/backend`: Código fuente de la lógica y API.
- `/frontend`: Plantillas HTML y assets.
- `/data`: Almacenamiento de volcados de memoria (`.raw`).
- `/reports`: Informes finales generados.
- `/logs`: Registros de actividad y transferencia.
- `/runtime`: Entorno virtual de Python (aislado).

---

## Configuración Remota (Opcional)
Si deseas enviar los reportes automáticamente a otro servidor, consulta la guía:
👉 [Guía de Transferencia Remota](./transferencia_remota.md)
