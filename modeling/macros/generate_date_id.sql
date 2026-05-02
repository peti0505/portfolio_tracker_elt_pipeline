{%macro generate_date_id(column_name)%}
    CAST(REPLACE(CAST({{column_name}} AS STRING),'-','') AS INTEGER)
{%endmacro%}