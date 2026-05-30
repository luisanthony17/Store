# Databricks notebook source
# MAGIC %md
# MAGIC # Capa Bronze — Ingesta Raw
# MAGIC
# MAGIC **Objetivo:** Leer el CSV de Global Superstore y guardarlo como Parquet sin ninguna transformación.
# MAGIC
# MAGIC **Regla de oro de Bronze:** No modificar nada. Solo ingestar y auditar.
# MAGIC
# MAGIC **Pregunta de negocio que este pipeline responderá:**
# MAGIC ¿Qué mercados y categorías generan pérdidas a pesar de tener alto volumen de ventas?

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuración

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit, input_file_name
from datetime import datetime

# En Databricks CE el SparkSession ya existe como 'spark'
# Esta línea es solo para referencia local
# spark = SparkSession.builder.appName("bronze_ingestion").getOrCreate()

# Rutas — ajusta SOURCE_PATH con la ruta donde subiste el CSV en DBFS
SOURCE_PATH  = "dbfs:/FileStore/datasets/Global_Superstore.csv"
BRONZE_PATH  = "dbfs:/mnt/superstore/bronze/orders"
SOURCE_NAME  = "global_superstore_kaggle"

print(f"Fuente  : {SOURCE_PATH}")
print(f"Destino : {BRONZE_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Lectura del CSV

# COMMAND ----------

df_raw = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "false")   # Bronze: todo como string, sin asumir tipos
    .option("multiLine", "true")      # Necesario: hay Product Names con saltos de línea
    .option("quote", '"')
    .option("escape", '"')
    .csv(SOURCE_PATH)
)

print(f"Filas leídas  : {df_raw.count():,}")
print(f"Columnas      : {len(df_raw.columns)}")
df_raw.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Agregar metadatos de auditoría
# MAGIC
# MAGIC Estas columnas responden: ¿cuándo llegó este dato y de dónde?
# MAGIC No modificamos ningún valor original.

# COMMAND ----------

df_bronze = (
    df_raw
    .withColumn("_ingestion_timestamp", current_timestamp())
    .withColumn("_source_file", lit(SOURCE_NAME))
    .withColumn("_ingestion_year", lit(datetime.now().year))
)

print("Columnas agregadas: _ingestion_timestamp, _source_file, _ingestion_year")
df_bronze.select(
    "Order ID", "Sales", "Profit", "Discount",
    "_ingestion_timestamp", "_source_file"
).show(3, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Validaciones mínimas de Bronze
# MAGIC
# MAGIC Solo verificamos que el archivo llegó completo.
# MAGIC No filtramos ni corregimos nada.

# COMMAND ----------

total_filas = df_bronze.count()
total_columnas = len(df_bronze.columns)

assert total_filas > 0,  "ERROR: El DataFrame está vacío. Verifica la ruta del CSV."
assert total_columnas >= 27, f"ERROR: Se esperaban 27+ columnas, llegaron {total_columnas}."

print(f"Validación pasada: {total_filas:,} filas, {total_columnas} columnas")

# Documentar columna sospechosa encontrada en exploración
print("\nNOTA: La columna 'ji_lu-shu' tiene valores numéricos sin descripción clara.")
print("      Se conserva en Bronze tal como llegó. Se investigará en Silver.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Escritura como Parquet particionado por Year

# COMMAND ----------

(
    df_bronze
    .write
    .mode("overwrite")
    .partitionBy("Year")            # El dataset ya trae columna Year
    .parquet(BRONZE_PATH)
)

print(f"Bronze escrito exitosamente en: {BRONZE_PATH}")
print("Particionado por: Year")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Verificación post-escritura

# COMMAND ----------

df_verify = spark.read.parquet(BRONZE_PATH)

print(f"Filas en Bronze : {df_verify.count():,}")
print(f"Particiones     : ")
display(
    df_verify.groupBy("Year")
    .count()
    .orderBy("Year")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resumen
# MAGIC
# MAGIC | Paso | Estado |
# MAGIC |---|---|
# MAGIC | Lectura CSV | Completado |
# MAGIC | Metadatos de auditoría | Agregados |
# MAGIC | Validaciones de integridad | Pasadas |
# MAGIC | Escritura Parquet (Bronze) | Completada |
# MAGIC
# MAGIC **Siguiente paso:** `02_clean_silver.py` — limpieza de tipos, nulos y deduplicación.
