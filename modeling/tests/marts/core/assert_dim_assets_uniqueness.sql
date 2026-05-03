SELECT
    ticker,
    asset_name,
    exchange_code,
    currency_code,
    count(*)
FROM 
    {{ref('dim_assets')}}
GROUP BY 1,2,3,4
HAVING count(*)>1