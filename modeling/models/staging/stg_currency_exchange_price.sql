WITH staging AS 
(
SELECT
    CAST(dates AS DATE) AS date, 
    UPPER(currency_code) AS currency_code,
    rate
FROM 
    {{source('portfolio', 'raw_currency_exchange_price')}}
)

SELECT * FROM staging