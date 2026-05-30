-- models/gold/fct_discount_impact.sql
--
-- Objetivo: ¿A partir de qué nivel de descuento empezamos a perder dinero?
-- Granularidad: una fila por (discount_bucket, category)

{{ config(
    materialized = 'table',
    tags         = ['gold', 'discount']
) }}

with silver as (

    select * from {{ ref('stg_orders') }}

),

bucketed as (

    select
        *,
        -- Agrupar descuentos en rangos para análisis
        case
            when discount = 0               then '0%'
            when discount between 0.01 and 0.10 then '1-10%'
            when discount between 0.11 and 0.20 then '11-20%'
            when discount between 0.21 and 0.30 then '21-30%'
            when discount between 0.31 and 0.40 then '31-40%'
            else                                    '40%+'
        end as discount_bucket,

        -- Orden para el bucket (para graficar en orden)
        case
            when discount = 0               then 1
            when discount between 0.01 and 0.10 then 2
            when discount between 0.11 and 0.20 then 3
            when discount between 0.21 and 0.30 then 4
            when discount between 0.31 and 0.40 then 5
            else                                    6
        end as discount_bucket_order

    from silver

)

select
    discount_bucket,
    discount_bucket_order,
    category,

    count(distinct order_id)            as total_orders,
    round(sum(sales), 2)                as total_sales,
    round(sum(profit), 2)               as total_profit,
    round(avg(profit_margin) * 100, 2)  as avg_profit_margin_pct,
    round(avg(discount) * 100, 2)       as avg_discount_pct,

    -- ¿Este bucket genera pérdida?
    case
        when sum(profit) < 0 then true
        else false
    end as is_loss_bucket

from bucketed
group by
    discount_bucket,
    discount_bucket_order,
    category
order by
    category,
    discount_bucket_order
