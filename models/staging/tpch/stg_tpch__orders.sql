with 
orders as (
    select * from {{ source('tpch', 'orders') }}
),

final as (
    select
    o_orderkey      as order_id,
    o_custkey       as customer_id,
    o_orderstatus   as order_status,
    o_totalprice    as total_price,
    o_orderdate     as order_date,
    o_orderpriority as order_priority,
    _loaded_at
from orders
)

select * from final