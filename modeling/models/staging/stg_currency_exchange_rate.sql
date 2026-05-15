WITH staging AS 
(
SELECT
    CAST(dates AS DATE) AS date, 
    UPPER(currency_code) AS currency_code,
    --rate is not closing rate, so i avg the intraday rates
    AVG(rate) as rate
FROM 
    {{source('portfolio', 'raw_currency_exchange_price')}}
GROUP BY
    1,2
)

SELECT * FROM staging