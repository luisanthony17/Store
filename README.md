# Global Superstore Profitability Pipeline

## Pregunta de negocio
**¿Qué mercados y categorías de productos están generando pérdidas a pesar de tener alto volumen de ventas, y cuál es el impacto del descuento en el profit?**

## Arquitectura

```
CSV (Global Superstore)
        │
        ▼
┌─────────────────────────────────────────┐
│        Azure Data Lake Storage Gen2     │
│                                         │
│  Bronze ──► Silver ──► Gold             │
│  (raw)     (limpia)   (métricas)        │
└─────────────────────────────────────────┘
        │                    │
        ▼                    ▼
  Databricks CE         Azure SQL DB
  (PySpark + dbt)       (tablas Gold)
                             │
                             ▼
                         Power BI
                      (dashboard final)
```

## Stack tecnológico

| Herramienta | Uso |
|---|---|
| PySpark (Databricks CE) | Ingesta y transformación Bronze → Silver |
| dbt | Transformaciones Silver → Gold |
| Azure Data Lake Gen2 | Almacenamiento por capas en Parquet |
| Azure SQL Database | Destino final para consumo |
| Power BI | Visualización y dashboard |
| GitHub Actions | CI: correr tests de dbt en cada push |

## Estructura del proyecto

```
global-superstore-pipeline/
├── notebooks/
│   ├── 01_bronze/
│   │   └── 01_ingest_bronze.py       # Ingesta CSV → Parquet raw
│   ├── 02_silver/
│   │   └── 02_clean_silver.py        # Limpieza y tipado
│   └── 03_gold/
│       └── 03_metrics_gold.py        # Carga a Azure SQL
├── dbt/
│   ├── models/
│   │   ├── silver/
│   │   │   └── stg_orders.sql        # Staging limpio
│   │   └── gold/
│   │       ├── fct_profitability.sql # Métricas por mercado/categoría
│   │       └── fct_discount_impact.sql # Impacto de descuentos
│   └── tests/                        # Tests de calidad de datos
├── docs/
│   └── architecture.md               # Decisiones de diseño
├── tests/                            # Tests de pipelines Python
├── requirements.txt
└── .gitignore
```

## Cómo ejecutar

### 1. Prerrequisitos
- Cuenta Databricks Community Edition
- Azure Student (Data Lake + SQL Database)
- Python 3.9+
- dbt-spark instalado

### 2. Configuración
```bash
git clone https://github.com/TU_USUARIO/global-superstore-pipeline
cd global-superstore-pipeline
pip install -r requirements.txt
```

### 3. Orden de ejecución
```
01_ingest_bronze.py   →   02_clean_silver.py   →   dbt run   →   03_metrics_gold.py
```

## Hallazgos principales
## Estado del proyecto
- [x] Bronze — completado (51,290 filas, 4 años, particionado por Year)
- [ ] Silver — pendiente
- [ ] Gold — pendiente
- [ ] Power BI — pendiente

## Autor
Tu Nombre — [LinkedIn](#) · [GitHub](#)
