WITH staging AS 
(
SELECT
    CAST(dates as DATE) as dates, 
    currency_code,
    rate
FROM 
    {{source('portfolio', 'raw_currency_exchange_price')}}
)

SELECT * FROM staging