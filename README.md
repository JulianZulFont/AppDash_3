# AppDash - Visualización de Rentas en EE.UU.

Este proyecto es un dashboard interactivo desarrollado con **Plotly Dash** para analizar la evolución de los precios de alquiler en las 100 ciudades más pobladas de Estados Unidos, utilizando el índice **ZORI (Zillow Observed Rent Index)**.

## Características

El dashboard incluye varias pestañas de análisis:
- **Serie histórica**: Visualización del cambio de precios a lo largo del tiempo por ciudad.
- **Top ciudades**: Ranking de las ciudades con mayores rentas en la última fecha disponible.
- **Precio vs Crecimiento**: Análisis de correlación entre el precio actual y el crecimiento porcentual.
- **Heatmap**: Mapa de calor que muestra la evolución de rentas por ciudad y año.
- **Mapa por estado**: Visualización geográfica de la renta promedio por estado.
- **Tablas y modelos**: Vista detallada de los datos y modelos de regresión.

## Tecnologías utilizadas

- **Python 3.12**
- **Dash / Plotly**: Para el framework web y gráficos interactivos.
- **Pandas**: Para el procesamiento y limpieza de datos.

## Instalación y Uso Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/JulianZulFont/AppDash_3.git
   cd AppDash_3
   ```

2. **Crear un entorno virtual:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # En Windows
   source .venv/bin/activate # En Linux/Mac
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Variables de Entorno:**
   Crea un archivo `.env` basado en `.env.example`:
   ```env
   CENSUS_API_KEY=tu_api_key_aqui
   DEBUG=True
   PORT=8050
   ```

5. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```
   La aplicación estará disponible en `http://127.0.0.1:8050/`.

## Docker

Para ejecutar la aplicación usando Docker:

1. **Construir la imagen:**
   ```bash
   docker build -t appdash .
   ```

2. **Ejecutar el contenedor:**
   ```bash
   docker run -p 8080:8050 --env-file .env appdash
   ```
   La aplicación estará disponible en `http://127.0.0.1:8080/`.
