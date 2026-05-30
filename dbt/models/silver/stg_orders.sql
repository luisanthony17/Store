-- models/silver/stg_orders.sql
--
-- Objetivo: Exponer la capa Silver de Databricks como fuente para los modelos Gold.
-- Este modelo no transforma, solo referencia la tabla Silver ya procesada por PySpark.

{{ config(
    materialized = 'view',
    tags         = ['silver', 'staging']
) }}

select
    row_id,
    order_id,
    ship_mode,
    customer_id,
    customer_name,
    segment,
    city,
    state,
    country,
    region,
    market,
    market2,
    product_id,
    product_name,
    category,
    sub_category,
    sales,
    quantity,
    discount,
    profit,
    shipping_cost,
    order_priority,
    profit_margin,
    year,
    week_num

from {{ source('silver', 'orders') }}

-- Filtro de calidad básico: solo registros con ventas positivas
where sales > 0
