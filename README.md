# Forensic Suite Dashboard

Forensic Suite Dashboard es una aplicación web y de línea de comandos (CLI) diseñada para facilitar el análisis forense de sistemas. Proporciona una interfaz unificada para realizar tareas de adquisición de memoria, análisis de volcados mediante plugins dinámicos y generación de reportes detallados.

## Estructura del Proyecto

El proyecto está organizado en una arquitectura modular que separa el servidor API, la lógica de análisis (Core/Servicios), la interfaz web y la interfaz de línea de comandos.

### Componentes Principales

*   **`app.py`**: El punto de entrada principal para el servidor web. Inicia una aplicación Flask y registra los "blueprints" (rutas) de la API. Se ejecuta por defecto en el puerto `5001`.
*   **`cli.py`**: El punto de entrada principal para la interfaz de línea de comandos. Utiliza la librería `click` para definir y manejar los comandos.
*   **`forensic_suite/`**: El paquete principal que contiene la lógica de negocio.
    *   **`api/`**: Contiene la lógica del servidor web Flask.
        *   **`routes.py`**: Define los endpoints de la API (ej. `/api/acquire`, `/api/analyze`, `/api/report`) y las rutas para la interfaz web.
        *   **`controllers/api_controller.py`**: Actúa como intermediario entre las rutas de la API y los servicios de análisis subyacentes. Maneja la recepción de datos y la orquestación de tareas.
    *   **`cli/`**: Contiene la lógica específica de la línea de comandos.
        *   **`commands.py`**: Define los comandos disponibles (ej. `acquire`, `analyze`, `report`, `pipeline`) y cómo interactúan con el Core.
    *   **`core/`**: Contiene el motor principal de análisis forense.
        *   **`acquisition.py`**: Lógica para adquirir volcados de memoria y generar hashes criptográficos.
        *   **`analysis_engine.py`**: El motor encargado de procesar los volcados de memoria utilizando los plugins disponibles y generar resultados.
        *   **`reporting.py`**: Lógica para generar reportes en formato HTML basados en los resultados del análisis.
    *   **`plugins/`**: Contiene los plugins de análisis individuales (ej. listado de procesos, búsqueda de conexiones de red). Estos son descubiertos y cargados dinámicamente.
    *   **`services/`**: Contiene servicios de soporte.
        *   **`volatility_service.py`**: Gestiona el descubrimiento, carga y ejecución dinámica de los plugins de análisis ubicados en el directorio `plugins/`.
    *   **`utils/`**: Utilidades genéricas, como la lectura/escritura de archivos JSON (`file_utils.py`).
*   **`templates/`**: Contiene las plantillas HTML para la interfaz web (Dashboard).
*   **`data/`**: Directorio utilizado por defecto para almacenar volcados de memoria, resultados de análisis (`results.json`) y reportes (`report.html`).

## Cómo Funciona

El sistema ofrece dos formas principales de interacción: a través de la CLI o mediante el Dashboard Web.

### 1. Interfaz de Línea de Comandos (CLI)

La CLI (`cli.py`) proporciona comandos granulares para ejecutar cada fase del análisis forense o ejecutar un "pipeline" completo.

*   **`acquire`**: Adquiere un volcado de memoria y genera su hash (MD5, SHA1 o SHA256).
*   **`analyze`**: Ejecuta el motor de análisis (`AnalysisEngine`) sobre un volcado de memoria, utilizando los plugins especificados o todos los disponibles.
*   **`report`**: Toma los resultados JSON del análisis y utiliza el módulo `Reporting` para generar un reporte HTML.
*   **`pipeline`**: Orquesta las tres fases anteriores (Adquisición -> Análisis -> Reporte) en un solo flujo continuo.

La CLI se comunica directamente con las clases en `forensic_suite/core/` para realizar el trabajo pesado.

### 2. Dashboard Web (API)

El servidor Flask (`app.py`) expone una API REST que permite controlar el proceso de análisis desde una interfaz web.

1.  El usuario interactúa con la interfaz en el navegador.
2.  La interfaz envía peticiones HTTP (POST, GET) a los endpoints definidos en `routes.py`.
3.  Las rutas delegan la ejecución a `ApiController`.
4.  `ApiController` llama a los mismos componentes del Core (`Acquisition`, `AnalysisEngine`, `Reporting`) que utiliza la CLI.
5.  El `VolatilityService` es crucial aquí, ya que permite al frontend consultar la lista de plugins disponibles y luego solicitar al motor que ejecute plugins específicos.

## Instalación y Ejecución

Se proporcionan scripts de conveniencia para automatizar la instalación de dependencias y la ejecución de la aplicación.

### En Windows

1.  **Instalación**: Ejecuta `install.bat`. Este script verificará si Python está instalado, creará un entorno virtual (`.venv`) e instalará los paquetes listados en `requirements.txt`.
2.  **Ejecución (Web)**: Ejecuta `run.bat`. Esto activará el entorno virtual e iniciará el servidor Flask en `http://localhost:5001`.
3.  **Ejecución (CLI)**:
    ```cmd
    call .venv\Scripts\activate.bat
    python cli.py --help
    ```

### En Linux/macOS

1.  **Instalación**: Ejecuta `bash install.sh`. (Similar al .bat de Windows).
2.  **Ejecución (Web)**: Ejecuta `bash run.sh`.
3.  **Ejecución (CLI)**:
    ```bash
    source .venv/bin/activate
    python3 cli.py --help
    ```

## Flujo de Trabajo Típico

Ya sea usando la CLI o la web, un flujo de trabajo típico de análisis implica:

1.  **Adquisición**: Se obtiene una imagen de la memoria RAM del sistema objetivo y se guarda en el directorio `data/`.
2.  **Análisis**: El motor de análisis lee la imagen de memoria. El `VolatilityService` carga dinámicamente los plugins necesarios y los ejecuta contra la imagen. Los resultados se estructuran y se guardan como un archivo JSON.
3.  **Reporte**: El módulo de reportes toma los datos en formato JSON y los procesa a través de plantillas para generar un reporte HTML fácil de leer.
