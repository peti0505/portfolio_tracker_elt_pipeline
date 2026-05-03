SELECT
    date_id
FROM
    {{ref('fact_transactions')}}
WHERE 
    date_id > {{generate_date_id('current_date()')}}