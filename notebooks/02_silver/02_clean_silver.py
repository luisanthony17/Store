# Databricks notebook source
# MAGIC %md
# MAGIC # Capa Silver — Limpieza y Tipado
# MAGIC
# MAGIC **Objetivo:** Leer Bronze y producir una tabla limpia, bien tipada y sin duplicados.
# MAGIC
# MAGIC **Qué hacemos aquí (y por qué):**
# MAGIC - Castear tipos correctos (Sales, Profit → double; fechas → date)
# MAGIC - Renombrar columnas a snake_case estandarizado
# MAGIC - Manejar nulos con lógica de negocio
# MAGIC - Eliminar duplicados
# MAGIC - Descartar columnas sin valor analítico

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuración

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, DateType

BRONZE_PATH = "dbfs:/mnt/superstore/bronze/orders"
SILVER_PATH = "dbfs:/mnt/superstore/silver/orders"

df_bronze = spark.read.parquet(BRONZE_PATH)
print(f"Filas leídas desde Bronze: {df_bronze.count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Renombrar columnas a snake_case
# MAGIC
# MAGIC Estandarizamos nombres para que dbt y SQL sean predecibles.

# COMMAND ----------

df = (
    df_bronze
    .withColumnRenamed("Row ID",        "row_id")
    .withColumnRenamed("Order ID",       "order_id")
    .withColumnRenamed("Order Date",     "order_date_raw")
    .withColumnRenamed("Ship Date",      "ship_date_raw")
    .withColumnRenamed("Ship Mode",      "ship_mode")
    .withColumnRenamed("Customer ID",    "customer_id")
    .withColumnRenamed("Customer Name",  "customer_name")
    .withColumnRenamed("Segment",        "segment")
    .withColumnRenamed("City",           "city")
    .withColumnRenamed("State",          "state")
    .withColumnRenamed("Country",        "country")
    .withColumnRenamed("Region",         "region")
    .withColumnRenamed("Market",         "market")
    .withColumnRenamed("Market2",        "market2")
    .withColumnRenamed("Product ID",     "product_id")
    .withColumnRenamed("Product Name",   "product_name")
    .withColumnRenamed("Category",       "category")
    .withColumnRenamed("Sub-Category",   "sub_category")
    .withColumnRenamed("Sales",          "sales")
    .withColumnRenamed("Quantity",       "quantity")
    .withColumnRenamed("Discount",       "discount")
    .withColumnRenamed("Profit",         "profit")
    .withColumnRenamed("Shipping Cost",  "shipping_cost")
    .withColumnRenamed("Order Priority", "order_priority")
    .withColumnRenamed("Year",           "year")
    .withColumnRenamed("weeknum",        "week_num")
)

# Descartamos columna sin descripción de negocio clara
df = df.drop("ji_lu-shu")

print("Columnas renombradas y 'ji_lu-shu' descartada.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Castear tipos correctos

# COMMAND ----------

df = (
    df
    .withColumn("sales",         F.col("sales").cast(DoubleType()))
    .withColumn("profit",        F.col("profit").cast(DoubleType()))
    .withColumn("discount",      F.col("discount").cast(DoubleType()))
    .withColumn("quantity",      F.col("quantity").cast(IntegerType()))
    .withColumn("shipping_cost", F.col("shipping_cost").cast(DoubleType()))
    .withColumn("year",          F.col("year").cast(IntegerType()))
    .withColumn("week_num",      F.col("week_num").cast(IntegerType()))
    .withColumn("row_id",        F.col("row_id").cast(IntegerType()))
)

# Nota: order_date y ship_date vienen corruptas en el CSV original ("00:00.0")
# Se conservan como string con sufijo _raw. Se registra en docs/architecture.md
print("Tipos casteados.")
print("\nMuestra de tipos numéricos:")
df.select("order_id","sales","profit","discount","quantity").show(3)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Manejar nulos

# COMMAND ----------

# Diagnóstico de nulos antes de actuar
print("Nulos por columna (columnas analíticas clave):")
df.select(
    [F.sum(F.col(c).isNull().cast("int")).alias(c)
     for c in ["sales","profit","discount","quantity","category","market","region"]]
).show()

# Regla: si sales o profit son nulos, la fila no tiene valor analítico → eliminar
filas_antes = df.count()
df = df.filter(F.col("sales").isNotNull() & F.col("profit").isNotNull())
filas_despues = df.count()
print(f"Filas eliminadas por nulos en sales/profit: {filas_antes - filas_despues:,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Eliminar duplicados

# COMMAND ----------

# Un pedido es único por order_id + product_id
filas_antes = df.count()
df = df.dropDuplicates(["order_id", "product_id"])
filas_despues = df.count()
print(f"Duplicados eliminados: {filas_antes - filas_despues:,}")
print(f"Filas Silver finales : {filas_despues:,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Columna derivada: profit_margin

# COMMAND ----------

# profit_margin = profit / sales (evitar división por cero)
df = df.withColumn(
    "profit_margin",
    F.when(F.col("sales") != 0, F.col("profit") / F.col("sales"))
     .otherwise(None)
)

print("Columna 'profit_margin' agregada.")
df.select("order_id","sales","profit","profit_margin","discount").show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Escritura Silver

# COMMAND ----------

(
    df
    .write
    .mode("overwrite")
    .partitionBy("year", "category")
    .parquet(SILVER_PATH)
)

print(f"Silver escrito en: {SILVER_PATH}")
print("Particionado por: year, category")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resumen Silver
# MAGIC
# MAGIC | Transformación | Resultado |
# MAGIC |---|---|
# MAGIC | Columnas renombradas | snake_case estandarizado |
# MAGIC | Tipos correctos | sales, profit, discount → double |
# MAGIC | Nulos en sales/profit | Eliminados |
# MAGIC | Duplicados | Eliminados por order_id + product_id |
# MAGIC | Nueva columna | profit_margin |
# MAGIC | Columna descartada | ji_lu-shu (sin valor analítico) |
# MAGIC
# MAGIC **Siguiente paso:** `dbt run` → modelos Gold con métricas de negocio.
