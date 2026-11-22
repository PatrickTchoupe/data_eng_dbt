with 

customers as (
    select * from {{ source('tpch', 'customer') }}
),

final as (
    select 
        c_custkey      as customer_id,
        c_name         as customer_name,
        c_address      as customer_address,
        c_nationkey    as nation_id,
        c_phone        as customer_phone,
        c_acctbal      as customer_account_balance,
        c_mktsegment   as customer_market_segment,
        c_comment      as customer_comment,
        _loaded_at
    from customers
)   

select * from final