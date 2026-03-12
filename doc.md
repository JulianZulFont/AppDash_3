# Entrega trabajo final
Realizado por:
- Mabby Dayana Puello Lopez
- Nicolas Esteban Cardenas Cortes
- Julian Norbey Zuluaga Fontecha

## 1. Introducción
El presente proyecto nace del interés por comprender a fondo la crisis de vivienda
en  los  Estados  Unidos,  un  fenómeno  que  ha  pasado  de  ser  una  estadística
económica a una problemática crítica social. Para ello, hemos desarrollado un panel
interactivo basado en el Zillow Observed Rent Index (ZORI). El propósito no es
solo mostrar cifras, sino construir una narrativa visual que explique cómo la renta se
ha transformado en un desafío financiero para millones de personas en las 100
principales ciudades del país.

## 2.  Alcance Temporal y Naturaleza de los Datos
Para las observaciones y análisis se siguen los siguientes parámetros:
- **Periodo de Análisis**: El estudio se centra en el periodo entre enero de 2015 y diciembre de 2024.
- **Naturaleza de la Información**: Se utiliza una serie histórica de promedios mensuales. Aunque el índice ZORI original incluye proyecciones a 2026, el análisis se ha acotado a 2024 para garantizar la paridad con los datos de ingresos del Censo de EE.UU. (ACS 5-Year Estimates).
- **Segmentación**: Para asegurar la relevancia estadística y el rendimiento visual, el modelo se enfoca exclusivamente en las **100 áreas metropolitanas con mayor rango de tamaño (SizeRank)**.


## 3. Modelado
Para garantizar que la herramienta fuera dinámica y precisa, implementamos un
proceso de ingeniería de datos que transformó la información en elementos
visuales:
- **Extracción de Datos Socioeconómicos (census.py)**:
    * **Fuente**: API oficial del *United States Census Bureau* (American Community Survey 5-Year Estimates).
    * **Requisitos**: El proceso requiere una clave de API (`CENSUS_API_KEY`) configurada en un archivo `.env` en la raíz del proyecto.
    * **Automatización**: El script recorre los años desde 2015 hasta 2024, realizando peticiones HTTP para obtener el ingreso medio por hogar (`B19013_001E`) filtrando exclusivamente por incorporaciones tipo "city".
    * **Almacenamiento**: Los resultados se descargan y persisten localmente en la carpeta `/data/` bajo la convención de nombres `census_YYYY.csv` (por ejemplo: `census_2021.csv`).
    * **Nota de Replicación**: Los datos ya se encuentran pre-procesados en la carpeta `/data/`, por lo que **no es necesario ejecutar este script** para el funcionamiento del dashboard. En caso de requerir una actualización manual de los datos, se debe ejecutar el comando `python census.py`.
- **Limpieza y Normalización (clean.py)**: 
    * **Estado Previo de los Datos**: El archivo original `data-raw/city-zori.csv` presenta una estructura de "formato ancho" con los siguientes metadatos y series temporales:

        | Columna | Tipo de Dato | Descripción |
        | :--- | :--- | :--- |
        | RegionID | Int (ID) | Identificador único regional de Zillow. |
        | SizeRank | Int | Ranking de la ciudad basado en su tamaño/población. |
        | RegionName | String | Nombre de la ciudad o área metropolitana. |
        | RegionType | String | Clasificación del área (usualmente "msa" o ciudad). |
        | StateName | String | Nombre completo del Estado. |
        | State | String | Abreviatura de 2 letras del Estado. |
        | Metro | String | Nombre del área metropolitana a la que pertenece. |
        | CountyName | String | Nombre del condado asociado. |
        | YYYY-MM-DD | Float/Numeric | Columnas dinámicas (una por mes) con el índice de renta. |

    * **Fuente de Renta**: Se utiliza el archivo `data-raw/city-zori.csv`, obtenido de [Zillow Research](https://www.zillow.com/research/data/). La configuración de descarga específica es: *ZORI (Smoothed): All Homes Plus Multifamily Time Series ($)* con geografía por *City*.
    * **Procesamiento de Rentas (clean_data)**:
        - **Limpieza**: Eliminación de registros con datos nulos en columnas críticas (Fecha, Ciudad, Estado, Precio).
        - **Transformación de Estructura (Melting)**: El dataset original de Zillow viene en un "formato ancho" donde cada mes es una columna diferente. Para facilitar el análisis de series de tiempo, se eliminan estas cientos de columnas de fechas (`YYYY-MM-DD`) y se transponen en múltiples filas nuevas, consolidando la información en dos variables maestras: `Date` (la fecha) y `RentIndex` (el valor). Esto permite que cada observación sea un registro único y cronológico.
        - **Segmentación**: Filtrado de las **100 ciudades principales** basado en la variable `SizeRank`.
        - **Alcance Temporal**: Restricción de los datos al periodo **2015-2024** para asegurar consistencia con las fuentes censales.
    * **Integración de Ingresos (add_census_data)**:
        - **Carga Iterativa**: Lectura secuencial de los archivos `census_YYYY.csv` generados previamente.
        - **Parseo de Identificadores**: Separación del campo `NAME` (ej: "Houston city, Texas") en componentes individuales de Ciudad y Estado.
        - **Limpieza de Nombres**: Eliminación del sufijo " city" para garantizar la coincidencia exacta con el dataset de rentas.
        - **Estandarización Geográfica**: Uso de un diccionario de mapeo interno para convertir nombres de estados a siglas (ej: "California" -> "CA").
        - **Fusión (Merge)**: Integración de ambos datasets utilizando [Ciudad, Estado, Año] como llaves de unión.
        - **Cálculos Financieros**: Conversión del ingreso anual a base mensual y cálculo del índice de asequibilidad (`RentIndexPct`).
    * **Exportación Final**: El resultado consolidado se guarda en `data/city-zori-long.csv`.
    * **Estado Posterior de los Datos**: El archivo resultante presenta una estructura de "formato largo", optimizado para visualizaciones dinámicas:

        | Columna | Tipo de Dato | Descripción |
        | :--- | :--- | :--- |
        | RegionID | Int | Identificador original de Zillow. |
        | SizeRank | Int | Ranking de tamaño (Top 100 filtrado). |
        | RegionName | String | Nombre de la ciudad. |
        | RegionType | String | Tipo de región (msa/ciudad). |
        | StateName | String | Nombre completo del Estado. |
        | State | String | Sigla del Estado (2 letras). |
        | Metro | String | Área metropolitana. |
        | CountyName | String | Condado asociado. |
        | Date | Datetime | Fecha de la observación (YYYY-MM-DD). |
        | RentIndex | Float | Valor del índice de renta (ZORI). |
        | Fecha_ES | String | Mes y año en español (ej: "enero 2024"). |
        | Year | Int | Año de la observación. |
        | MedianIncome | Float | Ingreso medio mensual (Censo / 12). |
        | RentIndexPct | Float | Porcentaje de ingreso destinado a renta. |

    * **Comando de Ejecución**: Para replicar este proceso de limpieza e integración, ejecute `python clean.py`.
- **Carga e Integración (data_loader.py)**: Este módulo actúa como la capa de servicios de datos para el dashboard. A diferencia de los scripts anteriores, **este archivo no se ejecuta manualmente**; es importado automáticamente por la aplicación durante el arranque para preparar el estado del tablero. Sus funciones principales incluyen:
    * **Carga Inicial**: Lectura del dataset consolidado y conversión de tipos de datos para asegurar el correcto funcionamiento de los filtros temporales.
    * **Generación de Opciones**: Construcción dinámica del listado de ciudades y estados para alimentar los componentes de selección (*dropdowns*) del usuario.
    * **Cálculos en Memoria**: 
        - **Crecimientos Históricos**: Cálculo interactivo de la variación de rentas (absoluta y porcentual) entre el primer y último periodo disponible por ciudad.
        - **Agregaciones Regionales**: Cálculo de promedios de renta por Estado para alimentar la visualización geográfica (mapas).

## 4. Dashboard
El  tablero  (app.py)  no  es  solo  una  interfaz  visual,  es  el  punto  central  de  la
experiencia del usuario. Su estructura modular permite una navegación intuitiva
y escalable:
- **Estructura del Proyecto**:
    * /data/: Archivos optimizados (city-zori-long.csv) para carga rápida.
    * /callbacks/: Lógica de interacción que permite filtrar por ciudad o año
en tiempo real.
    * /components/layouts/: Organización visual mediante pestañas (tabs) y
componentes gráficos.
    * /utils/: Funciones especializadas de formato y generación de gráficos.
- **Interactividad y Visualización**: El usuario tiene acceso a mapas de calor,
gráficos de dispersión y líneas de tiempo con Hover informativo lo que
permite una exploración profunda de los datos.

Buscando dar respuesta a interrogantes de negocio y sociales:
- **Crecimiento de Rentas**: Identificamos qué ciudades presentan tendencias alcistas agresivas en comparación con su base histórica.

- **Ciclos Económicos**: Visualización de periodos de aceleración (pico post-pandemia) y estabilización reciente.

- **Brecha de Asequibilidad**: Al cruzar el ingreso promedio con el precio de alquiler, el tablero expone visualmente qué porcentaje del presupuesto familiar se consume en vivienda, revelando dónde el mercado está desplazando a la población local.

## 5. Conclusión
Este informe demuestra que la combinación de un modelado de datos técnicos
(ETL) con una interfaz de storytelling efectiva permite transformar datos fríos en
conclusiones  estratégicas.  La  arquitectura  modular  en Python/Dash y  el
despliegue  en AWS garantizan  una  herramienta  profesional,  capaz  de
evolucionar con nuevos datos censales o proyecciones económicas futuras.
