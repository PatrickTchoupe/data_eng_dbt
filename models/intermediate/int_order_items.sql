with orders as (
    select * from {{ ref('stg_tpch__orders') }}
),

line_items as (
    select * from {{ ref('stg_tpch__lineitem') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['li.order_id', 'li.line_number']) }} as order_item_key,

    li.order_id,
    li.line_number,
    o.customer_id,
    li.part_id,
    li.supplier_id,

    o.order_date,
    li.ship_date,
    li.return_flag,
    li.quantity,

    li.extended_price                                                     as gross_amount,
    {{ discounted_amount('li.extended_price', 'li.discount_percentage') }} as discount_amount,
    li.extended_price
      - {{ discounted_amount('li.extended_price', 'li.discount_percentage') }} as net_amount,

    greatest(li._loaded_at, o._loaded_at) as _loaded_at

from line_items li
join orders o on li.order_id = o.order_id