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

## Estado del proyecto
- [x] Bronze — completado
- [x] Silver — completado  
- [x] Gold — completado
- [x] Power BI — completado
- [x] Workflows — pipeline orquestado, corre diario 6am, duración 2m 9s, alertas configuradas
<img width="629" height="410" alt="Screenshot_6" src="https://github.com/user-attachments/assets/96c29541-328a-463f-9af5-df02ae107e44" />


## Hallazgos principales
- US Furniture es el mercado más crítico: $741K en ventas pero solo 2.47% de margen
- El descuento promedio de 17.39% en US Furniture está destruyendo el profit
- A mayor descuento, menor profit margin — relación clara visible en scatter plot
- 14 de 21 combinaciones mercado/categoría están en margen bajo o crítico<img width="1038" height="584" alt="Screenshot_4" src="https://github.com/user-attachments/assets/61429f64-5909-40aa-93e7-3a88e10af8fb" />


## Autor
Tu Nombre — [LinkedIn](#) · [GitHub](#)
