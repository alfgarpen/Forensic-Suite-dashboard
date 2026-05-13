# Forensic Suite Dashboard 🕵️‍♂️💻

Forensic Suite Dashboard es una solución forense integral, completamente automatizada y profesional. Diseñada para transformar el análisis forense de sistemas en una experiencia de "un solo clic", permite realizar adquisiciones de memoria, análisis con Volatility 3 y generación de reportes detallados de forma automática.

## 🌟 Características Principales

- **Instalación en Un Solo Clic**: Scripts automatizados para Linux y Windows que configuran todo el entorno.
- **Arquitectura Profesional**: Separación clara entre backend, frontend, servicios y datos persistentes.
- **Integración con Volatility 3**: Descarga y configuración automática del motor de análisis.
- **Servicios Persistentes**: Ejecución en segundo plano mediante `systemd` (Linux) y servicios de Windows.
- **Dashboard Web Moderno**: Interfaz intuitiva para gestionar todo el ciclo de vida forense.
- **Gestión de Logs**: Sistema de logs con rotación automática para auditoría y depuración.
- **Reportes Automáticos**: Generación de reportes HTML profesionales listos para compartir.

## 📂 Estructura del Proyecto

El proyecto ha sido reorganizado para máxima escalabilidad y robustez:

```text
ForensicSuite/
├── backend/            # Lógica central Flask y motor forense
├── frontend/           # Plantillas Jinja2 y archivos estáticos (CSS/JS)
├── installer/          # Scripts de instalación y configuración (.sh, .ps1, .py)
├── scripts/            # Utilidades de análisis y reportes
├── uploads/            # Volcados de memoria subidos
├── artifacts/          # Resultados JSON y datos intermedios
├── reports/            # Reportes HTML finales generados
├── logs/               # Registros del sistema con rotación automática
├── volatility3/        # Instalación integrada de Volatility 3
├── config/             # Archivos de configuración y settings
└── runtime/            # Entorno virtual de Python (venv)
```

## 🚀 Instalación Rápida

### 🐧 Linux (Recomendado)

El instalador configurará las dependencias de Python, descargará Volatility 3 y creará un servicio de sistema para que la suite esté siempre disponible.

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd Forensic-Suite-dashboard

# Ejecutar el instalador (requiere sudo)
chmod +x installer/install.sh
sudo ./installer/install.sh
```

El dashboard estará disponible automáticamente en `http://localhost:5001`.

### 🪟 Windows

1. Abre PowerShell como **Administrador**.
2. Navega a la carpeta del proyecto.
3. Ejecuta:
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope Process
   .\installer\install.ps1
   ```

## 🛠️ Uso y Comandos

### Dashboard Web
Una vez instalado, el sistema arranca automáticamente. Simplemente abre tu navegador en:
`http://localhost:5001`

### Logs del Sistema
Puedes monitorear el estado de la suite en tiempo real:
- **Backend**: `logs/backend.log`
- **Análisis**: `logs/analysis.log`
- **Errores**: `logs/errors.log`

### Servicios (Linux)
Gestiona la suite como un servicio estándar del sistema:
```bash
sudo systemctl status forensicsuite
sudo systemctl restart forensicsuite
```

## 📊 Ciclo de Vida Forense

1.  **Instalación**: El sistema se autoconfigura en cualquier equipo.
2.  **Adquisición**: Sube o captura volcados de memoria directamente desde el dashboard.
3.  **Análisis Automático**: Volatility 3 procesa los datos usando los plugins configurados.
4.  **Reporte**: Se genera un archivo HTML profesional en la carpeta `reports/` de forma instantánea.

---
**Desarrollado para profesionales forenses que buscan velocidad, robustez y automatización total.**
