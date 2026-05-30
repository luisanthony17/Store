-- models/gold/fct_profitability.sql
--
-- Objetivo: Responder la pregunta de negocio principal.
-- ¿Qué mercados y categorías generan pérdidas a pesar de tener alto volumen de ventas?
--
-- Granularidad: una fila por (market, category, year)

{{ config(
    materialized = 'table',
    tags         = ['gold', 'profitability']
) }}

with silver as (

    select * from {{ ref('stg_orders') }}

),

aggregated as (

    select
        market,
        category,
        sub_category,
        year,

        -- Volumen
        count(distinct order_id)                        as total_orders,
        sum(quantity)                                   as total_units_sold,

        -- Financiero
        round(sum(sales), 2)                            as total_sales,
        round(sum(profit), 2)                           as total_profit,
        round(sum(shipping_cost), 2)                    as total_shipping_cost,

        -- Ratios
        round(avg(profit_margin) * 100, 2)              as avg_profit_margin_pct,
        round(avg(discount) * 100, 2)                   as avg_discount_pct,

        -- Clasificación de salud financiera
        case
            when sum(profit) < 0                        then 'perdida'
            when avg(profit_margin) < 0.05              then 'margen_critico'
            when avg(profit_margin) between 0.05 and 0.15 then 'margen_bajo'
            else                                             'saludable'
        end                                             as profit_health

    from silver
    group by
        market,
        category,
        sub_category,
        year

)

select
    *,
    -- Ranking de peor a mejor por mercado (útil para el dashboard)
    rank() over (
        partition by market, year
        order by total_profit asc
    ) as rank_worst_profit_in_market

from aggregated
order by
    total_profit asc
