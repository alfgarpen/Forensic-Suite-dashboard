# Automatización del Proyecto en el Arranque

Para que el proyecto funcione completamente al encender el equipo, necesitamos dos cosas:
1. **El Dashboard (Web):** Que esté siempre encendido para ver los reportes.
2. **El Análisis Automático:** Que se ejecute una vez al arrancar para generar un reporte fresco.

## Instalación Automática (Recomendado)

He creado un script que configura ambos servicios automáticamente. Solo tienes que ejecutar:

```bash
sudo bash scripts/setup_services.sh
```

## ¿Qué instala este script?

El script configura dos servicios de **systemd**:

### 1. `forensic-dashboard.service`
Mantiene el servidor Flask (`app.py`) funcionando en segundo plano. 
- **Estado:** `systemctl status forensic-dashboard`
- **Logs:** `journalctl -u forensic-dashboard -f`

### 2. `forensic-startup.service`
Ejecuta el pipeline de análisis completo cada vez que se arranca el sistema.
- **Estado:** `systemctl status forensic-startup`
- **Logs:** `journalctl -u forensic-startup -f`

---

## Verificación
Una vez instalado, puedes reiniciar tu ordenador o simplemente arrancar los servicios manualmente para probar:

```bash
sudo systemctl start forensic-dashboard
sudo systemctl start forensic-startup
```

El dashboard estará disponible en: **http://localhost:5001**

---
> [!TIP]
> Si el dashboard no carga, asegúrate de que el puerto 5001 no esté ocupado por otra aplicación. Puedes cambiar el puerto en `app.py` si es necesario.
