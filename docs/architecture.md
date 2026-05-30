# Decisiones de arquitectura

## Problema de negocio
¿Qué mercados y categorías de productos están generando pérdidas a pesar de tener alto volumen de ventas, y cuál es el impacto del descuento en el profit?

---

## Decisiones tomadas

### 1. Por qué Parquet y no Delta Lake
Databricks Community Edition tiene soporte limitado para Delta Lake en DBFS. Se eligió Parquet por compatibilidad y portabilidad. En un entorno de producción con Databricks Premium se usaría Delta Lake para tener ACID transactions y time travel.

### 2. Por qué particionamos Bronze por `Year`
El dataset cubre múltiples años (2011-2014). Particionar por año permite que Spark lea solo el año relevante cuando el análisis es por periodo, reduciendo el I/O significativamente.

### 3. La columna `ji_lu-shu`
Columna presente en el CSV original sin documentación clara. Se conserva intacta en Bronze (regla: no modificar nada) y se descarta a partir de Silver por no tener valor analítico identificado.

### 4. Las fechas `Order Date` y `Ship Date`
En el CSV original llegan como `00:00.0` en lugar de una fecha válida. Esto indica que Excel corrompió el formato durante la exportación. Se conservan como string con sufijo `_raw` en Silver. Para análisis temporal se usa la columna `Year` y `week_num` que sí están íntegras.

### 5. Por qué dbt para Gold y no PySpark directo
dbt permite escribir las transformaciones de negocio en SQL puro con versionado, tests y documentación automática. Los analistas de negocio pueden leer y modificar estos modelos sin saber PySpark. Es el estándar de la industria para la capa semántica.

### 6. Granularidad de `fct_profitability`
Se eligió (market, category, year) como granularidad porque responde directamente a la pregunta de negocio. Se podría bajar a nivel de sub_category o producto, pero aumenta la complejidad del dashboard sin añadir claridad en la primera versión.

---

## Pendientes conocidos
- [ ] Resolver el problema de fechas con el CSV original correcto
- [ ] Migrar almacenamiento de Parquet a Delta Lake cuando se tenga Databricks Premium
- [ ] Agregar capa de streaming para datos en tiempo real (Proyecto 3 del roadmap)
