{% macro discounted_amount(extended_price, discount_percentage, scale=2) %}
    round({{ extended_price }} * {{ discount_percentage }}, {{ scale }})
{% endmacro %}